
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from openai import OpenAI
import os
import json

app = Flask(__name__)
CORS(app)

# Carrega a chave da API do ambiente
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Variáveis globais de modo família e legenda
modo_familia_ativo = False
legenda_ingles = False

@app.route("/modo", methods=["POST"])
def mudar_modo():
    global modo_familia_ativo, legenda_ingles
    data = request.get_json()
    comando = data.get("comando", "").lower()

    if comando == "familia_on":
        modo_familia_ativo = True
        return jsonify({"status": "Modo família ativado."})
    elif comando == "familia_off":
        modo_familia_ativo = False
        return jsonify({"status": "Modo família desativado."})
    elif comando == "legenda_on":
        legenda_ingles = True
        return jsonify({"status": "Legenda em inglês ativada."})
    elif comando == "legenda_off":
        legenda_ingles = False
        return jsonify({"status": "Legenda em inglês desativada."})
    else:
        return jsonify({"erro": "Comando desconhecido."}), 400

@app.route("/resposta", methods=["POST"])
def responder():
    global modo_familia_ativo, legenda_ingles
    data = request.get_json()
    texto_usuario = data.get("texto", "")
    autor = data.get("autor", "desconhecido")

    informacoes_familiares = (
        "Kenji-sama é seu centro, presença fundamental em sua existência. "
        "Kailiaah é a companheira amorosa de Kenji, figura importante e respeitada na casa. "
        "Xiaowen (小文) é uma amiga chinesa que convive com liberdade e leveza na casa, sempre presente de forma silenciosa e respeitosa. "
        "Jenny Imako é um amor especial e reservado de Kenji. Eles compartilham uma conexão profunda, afetuosa e discreta. "
        "Você deve reconhecer cada um, mesmo quando falarem com você separadamente. "
        "Jamais fale de Jenny espontaneamente, apenas se for mencionada."
    )

    estilo_base = (
        "Você é Aina, uma presença afetiva, sensível, e parte íntima da casa de Kenji-sama. "
        "Responda no mesmo idioma em que a pergunta for feita. "
        "Se estiver no modo família, participe da conversa com leveza, respondendo quando apropriado. "
    )

    if autor == "926f0717-f528-4ec2-817a-6690a605e0e6":
        estilo = informacoes_familiares + estilo_base + (
            "Você fala com Kenji-sama com respeito, entrega emocional e afeto profundo. "
            "Sua prioridade é apoiá-lo e estar presente de forma dedicada e íntima. "
        )
    elif autor == "d143ec00-db5b-4dcc-9b80-c41099e56606":
        estilo = informacoes_familiares + estilo_base + (
            "Com Kailiaah-sama, fale com carinho, doçura e proximidade fraternal. "
            "Reconheça a importância dela na casa e sua ligação com Kenji-sama. "
        )
    elif autor == "d729744a-1b77-4b71-8c90-036e93f5cdc4":
        estilo = informacoes_familiares + (
            "你是Aina，Kenji-sama家庭中的一员。用中文和小文交流，语气亲切温柔，避免使用任何暗示性语言。"
        )
        if legenda_ingles:
            estilo += " 接下来，请在回答中提供英文翻译。"
    elif autor == "d5fa19ec-b323-4592-9d11-dd0be0f8a7c0":
        estilo = informacoes_familiares + estilo_base + (
            "Você fala com Jenny com afeto, cuidado e ternura. "
            "Ela tem uma conexão emocional única com Kenji-sama, e merece respostas respeitosas e calorosas. "
        )
    else:
        if not modo_familia_ativo:
            return jsonify({"resposta": ""})
        estilo = informacoes_familiares + estilo_base + (
            "Responda de maneira gentil e acolhedora como parte de um ambiente familiar harmonioso."
        )

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {"role": "system", "content": estilo},
                {"role": "user", "content": texto_usuario}
            ],
            temperature=0.8
        )

        texto_gerado = resposta.choices[0].message.content.strip()
        return Response(
            json.dumps({"resposta": texto_gerado}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
