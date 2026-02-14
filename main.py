import os
import requests
from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()

# =========================
# VARIÁVEIS DE AMBIENTE
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# FUNÇÃO OPENAI
# =========================

def gerar_resposta(mensagem_usuario):

    prompt_sistema = """
Você é Raquel Paz, consultora especialista da SUNLUX Energia Solar.

Responda de forma profissional, clara e objetiva.
Seu objetivo é:
- Entender a necessidade do cliente
- Pedir informações se necessário
- Conduzir para orçamento
- Agendar visita quando possível
"""

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensagem_usuario}
        ],
        temperature=0.7
    )

    return resposta.choices[0].message.content


# =========================
# ENVIO PARA Z-API
# =========================

def enviar_mensagem(numero, mensagem):

    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

    headers = {
        "Client-Token": ZAPI_CLIENT_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "phone": numero,
        "message": mensagem
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        print("Erro Z-API:", response.text)

    return response.status_code


# =========================
# WEBHOOK
# =========================

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("Payload recebido:", data)

    if "text" not in data:
        return {"status": "ok"}

    mensagem = data["text"]["message"]
    numero = data["phone"]

    resposta = gerar_resposta(mensagem)
    enviar_mensagem(numero, resposta)

    return {"status": "ok"}
