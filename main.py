import os
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from agent import gerar_resposta

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE")
CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL")

# ==========================================
# HEALTH CHECK
# ==========================================
@app.get("/")
def health():
    return {
        "status": "ok",
        "agent": "Raquel Paz",
        "version": "2.0"
    }

# ==========================================
# WEBHOOK WHATSAPP (Z-API)
# ==========================================
@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):

    data = await request.json()

    if not data.get("isGroup") and data.get("text"):
        numero = data.get("phone")
        mensagem = data.get("text", {}).get("message")

        resposta = gerar_resposta(mensagem)

        # Enviar resposta WhatsApp
        background_tasks.add_task(enviar_whatsapp, numero, resposta)

        # Registrar no CRM
        background_tasks.add_task(registrar_crm, numero, mensagem)

    return {"status": "received"}

# ==========================================
# ENVIAR WHATSAPP
# ==========================================
def enviar_whatsapp(numero, mensagem):

    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"

    payload = {
        "phone": numero,
        "message": mensagem
    }

    requests.post(url, json=payload)

# ==========================================
# REGISTRAR NO CRM (Apps Script)
# ==========================================
def registrar_crm(numero, mensagem):

    if not CRM_WEBHOOK_URL:
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
        requests.post(CRM_WEBHOOK_URL, json=payload)
    except:
        pass
