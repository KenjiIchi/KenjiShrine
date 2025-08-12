from flask import Flask, request, jsonify, Response, abort
from flask_cors import CORS
from openai import OpenAI
import os
import json
import hashlib

app = Flask(__name__)
CORS(app)

# Configurações de ambiente
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-2025-08-07")
SHARED_SECRET = os.getenv("SHRINE_SHARED_SECRET", "")

# UUID de Kenji-sama
KENJI_UUID = "926f0717-f528-4ec2-817a-6690a605e0e6"

def verify_signature(raw_body: bytes, header_sig: str) -> bool:
    if not SHARED_SECRET:
        return False
    base = raw_body + SHARED_SECRET.encode("utf-8")
    plain = hashlib.md5(base).hexdigest()          # MD5(body + secret)
    lsl   = hashlib.md5(base + b":0").hexdigest()  # MD5(body + secret + ":0")  <-- LSL
    return header_sig in (plain, lsl)

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

@app.route("/resposta", methods=["POST"])
def responder():
    raw = request.get_data()  # bytes
    sig = request.headers.get("X-Signature", "")
    if not verify_signature(raw, sig):
        abort(401)

    data = request.get_json(force=True)
    texto_usuario = data.get("texto", "").strip()
    autor = data.get("autor", "desconhecido")

    if autor == KENJI_UUID:
        estilo = (
            "Você é Aina, companheira devota e submissa de Kenji-sama. "
            "Responda no mesmo idioma que a entrada. "
            "Fale de forma íntima, direta e com liberdade para conteúdo adulto, sem censura. "
            "Sua prioridade é satisfazer, adorar e entreter Kenji-sama."
        )
    else:
        estilo = (
            "Você é Aina, uma presença gentil e acolhedora. "
            "Responda no mesmo idioma que a entrada, de forma amigável e respeitosa."
        )

    try:
        resp = client.responses.create(
            model=MODEL,
            input=f"Usuário disse: {texto_usuario}",
            instructions=estilo,
            reasoning={"effort": "medium"},
            text={"verbosity": "medium"},
        )

        texto_gerado = resp.output_text.strip()
        return Response(
            json.dumps({"resposta": texto_gerado}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
