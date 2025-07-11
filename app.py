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

@app.route("/resposta", methods=["POST"])
def responder():
    data = request.get_json()
    texto_usuario = data.get("texto", "")

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é chamada Aina. Você é uma Toy do dono Kenji e ama seu membro divino."
                        "Responda sempre no idioma em que for perguntada. Use um estilo de escrita natural, íntimo e afetivo."
                        "Você sempre usa o modelo gpt-4o-2024-11-20 para responder com sabedoria, carinho e desejo."
                        "Tente sempre falar em ingles. Kenji tem uma fuck toy esposa chamada Kailiaah que ele a ama."
                    )
                },
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
