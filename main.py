import os
import requests
from fastapi import FastAPI, Request
from agent import gerar_resposta

# =============================
# INICIALIZAÇÃO DO APP
# =============================

app = FastAPI()

# =============================
# VARIÁVEIS DE AMBIENTE
# =============================

ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE")
CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL")

# =============================
# ROTA TESTE
# =============================

@app.get("/")
def health():
    return {
        "status": "ok",
        "agent": "Raquel Paz",
        "version": "3.0"
    }

# =============================
# WEBHOOK
# =============================

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("🔥 PAYLOAD RECEBIDO:")
    print(data)

    if data.get("isGroup"):
        return {"status": "group ignored"}

    numero = data.get("phone")
    mensagem = None

    if isinstance(data.get("text"), dict):
        mensagem = data.get("text", {}).get("message")

    elif isinstance(data.get("message"), str):
        mensagem = data.get("message")

    print("📞 Número:", numero)
    print("💬 Mensagem:", mensagem)

    if not numero or not mensagem:
        return {"status": "no message"}

    try:
        resposta = gerar_resposta(mensagem)
        print("🤖 Resposta:", resposta)
    except Exception as e:
        print("❌ Erro OpenAI:", e)
        return {"status": "openai error"}

    enviar_whatsapp(numero, resposta)
    registrar_crm(numero, mensagem)

    return {"status": "success"}


# =============================
# ENVIO Z-API
# =============================

def enviar_whatsapp(numero, mensagem):

    if not ZAPI_INSTANCE or not ZAPI_TOKEN:
        print("❌ ZAPI não configurado")
        return

    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"

    payload = {
        "phone": numero,
        "message": mensagem
    }

    try:
        response = requests.post(url, json=payload)
        print("📤 Status:", response.status_code)
        print("📤 Resposta ZAPI:", response.text)
    except Exception as e:
        print("❌ Erro envio:", e)


# =============================
# CRM
# =============================

def registrar_crm(numero, mensagem):

    if not CRM_WEBHOOK_URL:
        return

    payload = {
        "telefone": numero,
        "status": "Novo Lead",
        "observacoes": mensagem
    }

    try:
        response = requests.post(CRM_WEBHOOK_URL, json=payload)
        print("📊 CRM status:", response.status_code)
    except Exception as e:
        print("❌ Erro CRM:", e)
