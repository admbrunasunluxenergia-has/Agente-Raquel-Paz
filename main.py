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
# ROTA DE SAÚDE (TESTE)
# =============================

@app.get("/")
def health():
    return {
        "status": "ok",
        "agent": "Raquel Paz",
        "version": "2.2"
    }

# =============================
# WEBHOOK Z-API
# =============================

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("📩 PAYLOAD RECEBIDO:")
    print(data)

    # Ignora grupos
    if data.get("isGroup"):
        print("⚠️ Mensagem de grupo ignorada")
        return {"status": "group ignored"}

    # Captura número
    numero = data.get("phone")

    # Captura mensagem (estrutura padrão Z-API)
    mensagem = None

    if isinstance(data.get("text"), dict):
        mensagem = data.get("text", {}).get("message")

    elif isinstance(data.get("message"), str):
        mensagem = data.get("message")

    print("📞 Número:", numero)
    print("💬 Mensagem:", mensagem)

    if not numero or not mensagem:
        print("⚠️ Dados insuficientes")
        return {"status": "no message"}

    # =============================
    # GERA RESPOSTA COM OPENAI
    # =============================

    try:
        resposta = gerar_resposta(mensagem)
        print("🤖 Resposta gerada:")
        print(resposta)
    except Exception as e:
        print("❌ ERRO OPENAI:", e)
        return {"status": "openai error"}

    # =============================
    # ENVIA PARA Z-API
    # =============================

    enviar_whatsapp(numero, resposta)

    # =============================
    # REGISTRA NO CRM
    # =============================

    registrar_crm(numero, mensagem)

    return {"status": "success"}


# =============================
# ENVIO WHATSAPP
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

        print("📤 Status envio:", response.status_code)
        print("📤 Resposta ZAPI:", response.text)

    except Exception as e:
        print("❌ ERRO ENVIO ZAPI:", e)


# =============================
# REGISTRO CRM
# =============================

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
        print("❌ ERRO CRM:", e)
