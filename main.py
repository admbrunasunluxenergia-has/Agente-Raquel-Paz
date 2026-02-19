import os
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from agent import gerar_resposta

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE")
CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL")

@app.get("/")
def health():
    return {
        "status": "ok",
        "agent": "Raquel Paz",
        "version": "2.1"
    }

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("📩 Payload recebido:", data)

    if not data.get("isGroup") and data.get("text"):

        numero = data.get("phone")
        mensagem = data.get("text", {}).get("message")

        print("📞 Número:", numero)
        print("💬 Mensagem:", mensagem)

        if not mensagem:
            print("⚠️ Mensagem vazia")
            return {"status": "no message"}

        try:
            resposta = gerar_resposta(mensagem)
            print("🤖 Resposta gerada:", resposta)
        except Exception as e:
            print("❌ Erro OpenAI:", e)
            return {"status": "openai error"}

        # EXECUTANDO DIRETO
        enviar_whatsapp(numero, resposta)
        registrar_crm(numero, mensagem)

    return {"status": "received"}
