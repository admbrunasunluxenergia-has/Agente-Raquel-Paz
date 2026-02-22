import os
import requests
from fastapi import FastAPI, Request
from agent import gerar_resposta

app = FastAPI()

# =============================
# VARIÁVEIS DE AMBIENTE
# =============================

ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")
CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL")

# =============================
# ROTA TESTE
# =============================

@app.get("/")
def health():
    return {
        "status": "ok",
        "agent": "Raquel Paz",
        "version": "4.0"
    }

# =============================
# WEBHOOK RECEBIMENTO
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

    resposta = gerar_resposta(mensagem)
    print("🤖 Resposta:", resposta)

    enviar_whatsapp(numero, resposta)
    registrar_crm(numero, mensagem)

    return {"status": "success"}


# =============================
# ENVIO Z-API
# =============================

def enviar_whatsapp(numero, mensagem):

    if not ZAPI_INSTANCE_ID:
        print("❌ ZAPI_INSTANCE_ID não encontrado")
        return

    if not ZAPI_TOKEN:
        print("❌ ZAPI_TOKEN não encontrado")
        return

    if not ZAPI_CLIENT_TOKEN:
        print("❌ ZAPI_CLIENT_TOKEN não encontrado")
        return

    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

    headers = {
        "Client-Token": ZAPI_CLIENT_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "phone": numero,
        "message": mensagem
    }

    print("📤 Enviando mensagem para:", numero)
    print("🔗 URL:", url)

    try:
        response = requests.post(url, json=payload, headers=headers)

        print("📤 Status:", response.status_code)
        print("📤 Resposta ZAPI:", response.text)

    except Exception as e:
        print("❌ Erro envio:", e)


# =============================
# CRM (opcional)
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
