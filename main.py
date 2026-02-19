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
        "version": "2.1"
    }

# ==========================================
# WEBHOOK WHATSAPP (Z-API)
# ==========================================
@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):

    data = await request.json()
    print("📩 WEBHOOK RECEBIDO:", data)

    if data.get("isGroup"):
        return {"status": "grupo ignorado"}

    numero = data.get("phone")

    mensagem = None

    # Detectar vários formatos possíveis da Z-API
    if isinstance(data.get("text"), dict):
        mensagem = data.get("text", {}).get("message") or data.get("text", {}).get("body")

    if not mensagem:
        mensagem = data.get("body")

    if not mensagem:
        mensagem = data.get("message")

    if not mensagem:
        print("⚠ Nenhuma mensagem detectada")
        return {"status": "sem mensagem"}

    print("📨 Mensagem:", mensagem)

    resposta = gerar_resposta(mensagem)

    background_tasks.add_task(enviar_whatsapp, numero, resposta)
    background_tasks.add_task(registrar_crm, numero, mensagem)

    return {"status": "ok"}


# ==========================================
# ENVIAR WHATSAPP
# ==========================================
def enviar_whatsapp(numero, mensagem):

    if not ZAPI_INSTANCE or not ZAPI_TOKEN:
        print("❌ ZAPI não configurada")
        return

    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"

    payload = {
        "phone": numero,
        "message": mensagem
    }

    try:
        requests.post(url, json=payload)
        print("✅ Mensagem enviada")
    except Exception as e:
        print("❌ Erro ao enviar WhatsApp:", e)


# ==========================================
# REGISTRAR NO CRM (Apps Script)
# ==========================================
def registrar_crm(numero, mensagem):

    if not CRM_WEBHOOK_URL:
        print("⚠ CRM não configurado")
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
        print("✅ Registrado no CRM")
    except Exception as e:
        print("❌ Erro CRM:", e)
