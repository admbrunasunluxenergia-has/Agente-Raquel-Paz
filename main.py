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
async def webhook(request: Request, background_tasks: BackgroundTasks):

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

        background_tasks.add_task(enviar_whatsapp, numero, resposta)
        background_tasks.add_task(registrar_crm, numero, mensagem)

    return {"status": "received"}


def enviar_whatsapp(numero, mensagem):

    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"

    payload = {
        "phone": numero,
        "message": mensagem
    }

    response = requests.post(url, json=payload)

    print("📤 Envio WhatsApp status:", response.status_code)
    print("📤 Resposta ZAPI:", response.text)


def registrar_crm(numero, mensagem):

    if not CRM_WEBHOOK_URL:
        print("⚠️ CRM_WEBHOOK_URL não configurado")
        return

    payload = {
        "nome": "",
        "telefone": numero,
        "cidade": "",
        "grupo": "",
        "consumo": "",
        "valor_proposta": "",
        "status": "Novo Lead",
        "observacoes": mensagem
    }

    try:
        response = requests.post(CRM_WEBHOOK_URL, json=payload)
        print("📊 CRM status:", response.status_code)
    except Exception as e:
        print("❌ Erro CRM:", e)
