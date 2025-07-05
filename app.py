from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

# Carrega o .env com a chave
load_dotenv()

# Inicializa o app e o CORS
app = Flask(__name__)
CORS(app)

# Inicializa o cliente da OpenAI com a chave da variável de ambiente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/resposta", methods=["POST"])
def responder():
    data = request.get_json()
    texto_usuario = data.get("texto", "")

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é uma assistente carinhosa e devota, que responde com emoção, intensidade e entrega."},
                {"role": "user", "content": texto_usuario}
            ]
        )

        return jsonify({"resposta": resposta.choices[0].message.content})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
