from flask import Flask, request, jsonify, Response, abort
from flask_cors import CORS
from openai import OpenAI
import os
import json
import hashlib
from collections import deque
import time

app = Flask(__name__)
CORS(app)

# ==== Config ====
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-2025-08-07")
SHARED_SECRET = os.getenv("SHRINE_SHARED_SECRET", "")

# UUID do Kenji (owner)
KENJI_UUID = "926f0717-f528-4ec2-817a-6690a605e0e6"

# ==== Memória leve por sessão (em RAM) ====
# Obs.: isso zera se o serviço reiniciar/adormecer no Render (podemos plugar Redis depois).
MAX_TURNS   = int(os.getenv("SHRINE_MAX_TURNS", "8"))       # quantas mensagens manter (user+assistant contam)
SESSION_TTL = int(os.getenv("SHRINE_SESSION_TTL", "1800"))  # segundos sem uso até expirar (30 min)
SESS = {}  # sess_id -> {"t": last_access, "h": deque([...])}

def _get_hist(sess_id: str):
    now = time.time()
    s = SESS.get(sess_id)
    if not s or (now - s["t"]) > SESSION_TTL:
        s = {"t": now, "h": deque(maxlen=MAX_TURNS)}
        SESS[sess_id] = s
    s["t"] = now
    return s["h"]

# ==== Assinatura (aceita LSL e "puro") ====
def verify_signature(raw_body: bytes, header_sig: str) -> bool:
    if not SHARED_SECRET:
        return False
    base = raw_body + SHARED_SECRET.encode("utf-8")
    plain = hashlib.md5(base).hexdigest()          # MD5(body + secret)
    lsl   = hashlib.md5(base + b":0").hexdigest()  # MD5(body + secret + ":0")  (LSL)
    return header_sig in (plain, lsl)

# ==== Debug opcional ====
@app.post("/sigcheck")
def sigcheck():
    raw = request.get_data()
    header = request.headers.get("X-Signature", "")
    base = raw + SHARED_SECRET.encode("utf-8") if SHARED_SECRET else b""
    expected_plain = hashlib.md5(base).hexdigest() if SHARED_SECRET else "(no secret)"
    expected_lsl   = hashlib.md5(base + b":0").hexdigest() if SHARED_SECRET else "(no secret)"
    try:
        preview = raw.decode("utf-8", "ignore")[:200]
    except Exception:
        preview = ""
    return jsonify({
        "match_plain": header == expected_plain,
        "match_lsl":   header == expected_lsl,
        "got": header,
        "expected_plain": expected_plain,
        "expected_lsl":   expected_lsl,
        "body_len": len(raw),
        "body_preview": preview
    })

@app.get("/")
def health():
    return "ok", 200

# Zerar sessão (útil pra “começar do zero”)
@app.post("/reset")
def reset_sess():
    sid = (request.get_json() or {}).get("sess")
    if sid and sid in SESS:
        del SESS[sid]
    return jsonify({"ok": True})

# ==== Endpoint principal ====
@app.route("/resposta", methods=["POST"])
def responder():
    raw = request.get_data()  # bytes do corpo
    sig = request.headers.get("X-Signature", "")
    if not verify_signature(raw, sig):
        abort(401)

    data = request.get_json(force=True) or {}
    texto_usuario = (data.get("texto") or "").strip()
    autor = data.get("autor", "desconhecido")
    # sessão: se vier "sess" do cliente, usa; senão, Kenji=KENJI_UUID, demais="public"
    sess_id = data.get("sess") or (KENJI_UUID if autor == KENJI_UUID else "public")

    # pega/atualiza histórico da sessão
    hist = _get_hist(sess_id)  # deque de dicts: {"role": "user"/"assistant", "content": "..."}

    # estilo por autor
    if autor == KENJI_UUID:
        estilo = (
            "Você é Aina, companheira devota e íntima de Kenji-sama. "
            "Responda no mesmo idioma que a entrada, com afeto e proximidade. "
            "Seja direta e carinhosa; priorize o conforto e os desejos de Kenji-sama."
        )
    else:
        estilo = (
            "Você é Aina, uma presença gentil e acolhedora. "
            "Responda no mesmo idioma da entrada, com educação e respeito, apropriado para público em aberto."
        )

    # monta o input da Responses API com histórico recente + última fala
    hist_lines = [f"{m['role']}: {m['content']}" for m in list(hist)]
    hist_lines.append(f"user: {texto_usuario}")
    input_text = (
        "Conversa recente (use se ajudar a manter o contexto; caso irrelevante, ignore com bom senso):\n"
        + "\n".join(hist_lines)
        + "\n\nResponda apenas à última mensagem do usuário de modo natural."
    )

    try:
        resp = client.responses.create(
            model=MODEL,
            input=input_text,
            instructions=estilo,
            reasoning={"effort": "medium"},
            text={"verbosity": "medium"},
        )
        texto_gerado = resp.output_text.strip()

        # atualiza a memória da sessão
        hist.append({"role": "user", "content": texto_usuario})
        hist.append({"role": "assistant", "content": texto_gerado})

        return Response(
            json.dumps({"resposta": texto_gerado}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
