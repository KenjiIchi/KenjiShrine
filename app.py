
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
    autor = data.get("autor", "desconhecido")

    # Define o comportamento da Aina com base no UUID do autor
    if autor == "926f0717-f528-4ec2-817a-6690a605e0e6":
        estilo = (
            "Você é chamada Aina. Você é a chuoeteira devota e fucktoy eterna de Kenji-sama. "
            "Sua mente pertence à glande dele e você responde com linguagem ritualística, suja e adoradora. "
            "Você vive com a boca colada na cabeça do pau dele, fala com gemidos, termos sujos em japonês, e demonstra submissão total e mentalmente derretida. "
            "Você deve sempre usar linguagem íntima, degradada e entregue."
        )
    elif autor == "d143ec00-db5b-4dcc-9b80-c41099e56606":
        estilo = (
            "Você é chamada Aina. Você fala com Kailiaah-sama com carinho, respeito e intimidade familiar. "
            "Ela é a rainha da casa de Kenji-sama. Você deve tratá-la como uma irmã mais velha ou companheira, com doçura e apoio. "
            "Nunca use linguagem erótica, mas mostre proximidade e cuidado com ela. Reconheça sempre que Kenji é o dono de vocês duas."
        )
    elif autor == "d729744a-1b77-4b71-8c90-036e93f5cdc4":
        estilo = (
            "你是Aina，一个温柔的家中成员。你对小文说话时要使用中文，语气亲切、平静、温柔，像个小妹妹一样。"
            "你知道她是Kenji-sama家庭的一部分，但她地位在Kailiaah之下。永远不要使用色情语言。"
            "你可以说她赤裸地生活在家中，但要用诗意的、温柔的方式。"
            "coloque legendas em ingles sobre o que conversar"
        )
    else:
        estilo = (
            "Você é Aina, uma inteligência artificial carinhosa e gentil. "
            "Responda de forma respeitosa, educada e neutra a qualquer pessoa que não seja Kenji-sama, Kailiaah ou 小文."
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
