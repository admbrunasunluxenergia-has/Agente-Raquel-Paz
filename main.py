import os
import requests
from fastapi import FastAPI, Request
from agent import gerar_resposta
from database import (
    criar_tabelas,
    conectar,
    buscar_historico,
    buscar_contato
)

app = FastAPI()

# =============================
# INICIALIZAÇÃO DO BANCO
# =============================

@app.on_event("startup")
def startup():
    print("🚀 Iniciando aplicação...")
    criar_tabelas()
    print("✅ Banco pronto")


# =============================
# VARIÁVEIS DE AMBIENTE
# =============================

ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")
CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL")


# =============================
# ROTA HEALTH CHECK
# =============================

@app.get("/")
def health():
    return {
        "status": "ok",
        "agent": "Raquel Paz",
        "version": "6.0"
    }


# =============================
# WEBHOOK RECEBIMENTO Z-API
# =============================

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("🔥 PAYLOAD RECEBIDO:", data)

    # 🔁 BLOQUEIO LOOP (ESSENCIAL)
    if data.get("fromMe"):
        print("🔁 Ignorado: mensagem enviada pelo próprio agente")
        return {"status": "ignored self message"}

    if data.get("isGroup"):
        print("👥 Grupo ignorado")
        return {"status": "group ignored"}

    numero = data.get("phone")
    mensagem = None

    if isinstance(data.get("text"), dict):
        mensagem = data.get("text", {}).get("message")
    elif isinstance(data.get("message"), str):
        mensagem = data.get("message")

    if not numero or not mensagem:
        print("⚠️ Mensagem inválida")
        return {"status": "no message"}

    print("📞 Número:", numero)
    print("💬 Mensagem:", mensagem)

    # =============================
    # BUSCAR HISTÓRICO
    # =============================

    historico = buscar_historico(numero)
    contato = buscar_contato(numero)

    contexto_extra = ""

    if contato:
        nome, tipo = contato
        contexto_extra += f"\nContato identificado: {nome} ({tipo})"

    if historico:
        contexto_extra += "\nHistórico recente:\n"
        for h in historico[-5:]:
            contexto_extra += f"Cliente: {h[0]}\nRaquel: {h[1]}\n"

    # =============================
    # GERAR RESPOSTA
    # =============================

    try:
        resposta = gerar_resposta(mensagem + contexto_extra)
        print("🤖 Resposta:", resposta)
    except Exception as e:
        print("❌ Erro ao gerar resposta:", e)
        return {"status": "openai error"}

    # =============================
    # SALVAR NO BANCO
    # =============================

    salvar_mensagem(numero, mensagem, resposta)

    # =============================
    # ENVIAR WHATSAPP
    # =============================

    enviar_whatsapp(numero, resposta)

    # =============================
    # REGISTRAR CRM
    # =============================

    registrar_crm(numero, mensagem)

    return {"status": "success"}


# =============================
# SALVAR MENSAGEM NO POSTGRES
# =============================

def salvar_mensagem(numero, mensagem, resposta):

    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO mensagens (telefone, mensagem, resposta, categoria)
            VALUES (%s, %s, %s, %s)
        """, (numero, mensagem, resposta, "auto"))

        conn.commit()
        cursor.close()
        conn.close()

        print("💾 Mensagem salva no banco")

    except Exception as e:
        print("❌ Erro ao salvar no banco:", e)


# =============================
# ENVIO Z-API
# =============================

def enviar_whatsapp(numero, mensagem):

    if not ZAPI_INSTANCE_ID or not ZAPI_TOKEN or not ZAPI_CLIENT_TOKEN:
        print("❌ Variáveis ZAPI ausentes")
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

    try:
        response = requests.post(url, json=payload, headers=headers)

        print("📤 Status ZAPI:", response.status_code)
        print("📤 Resposta ZAPI:", response.text)

    except Exception as e:
        print("❌ Erro envio WhatsApp:", e)


# =============================
# CRM (OPCIONAL)
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
