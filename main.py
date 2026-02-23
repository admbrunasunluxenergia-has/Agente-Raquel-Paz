import os
import logging
import requests
from fastapi import FastAPI, Request
from agent import gerar_resposta, classificar_mensagem
from database import (
    criar_tabelas,
    conectar,
    buscar_historico,
    buscar_contato,
    mensagem_existe  # 🔒 NOVO
)

# ==================================================
# CONFIGURAÇÃO LOG
# ==================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# ==================================================
# STARTUP
# ==================================================

@app.on_event("startup")
def startup():
    logger.info("🚀 Iniciando aplicação...")
    criar_tabelas()
    logger.info("✅ Banco pronto")


# ==================================================
# VARIÁVEIS DE AMBIENTE
# ==================================================

ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")
CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL")


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/")
def health():
    return {
        "status": "ok",
        "agent": "Raquel Paz",
        "version": "8.0-stable"
    }


# ==================================================
# WEBHOOK Z-API
# ==================================================

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    logger.info(f"🔥 Payload recebido: {data}")

    # 🔁 Ignorar mensagens do próprio agente
    if data.get("fromMe") is True:
        logger.info("🔁 Ignorado: mensagem enviada pelo agente")
        return {"status": "ignored_self"}

    # 👥 Ignorar grupos
    if data.get("isGroup") is True:
        logger.info("👥 Grupo ignorado")
        return {"status": "ignored_group"}

    numero = data.get("phone")
    mensagem = None
    mensagem_id = data.get("messageId") or data.get("id")

    if isinstance(data.get("text"), dict):
        mensagem = data.get("text", {}).get("message")
    elif isinstance(data.get("message"), str):
        mensagem = data.get("message")

    if not numero or not mensagem:
        logger.warning("⚠️ Payload inválido")
        return {"status": "invalid_payload"}

    # ==================================================
    # 🔒 ANTI DUPLICIDADE (ANTES DE TUDO)
    # ==================================================

    if mensagem_existe(mensagem_id):
        logger.info("🔁 Mensagem duplicada ignorada")
        return {"status": "duplicate_ignored"}

    logger.info(f"📞 Número: {numero}")
    logger.info(f"💬 Mensagem: {mensagem}")

    # ==================================================
    # CLASSIFICAÇÃO
    # ==================================================

    categoria = classificar_mensagem(mensagem)
    logger.info(f"📂 Categoria detectada: {categoria}")

    # ==================================================
    # CONTEXTO
    # ==================================================

    historico = buscar_historico(numero)
    contato = buscar_contato(numero)

    contexto_extra = ""

    if contato:
        nome, tipo, etapa = contato
        contexto_extra += f"\nContato identificado: {nome} ({tipo})"

    if historico:
        contexto_extra += "\nHistórico recente:\n"
        for h in historico[-5:]:
            contexto_extra += f"Cliente: {h[0]}\nRaquel: {h[1]}\n"

    # ==================================================
    # GERAR RESPOSTA
    # ==================================================

    try:
        resposta = gerar_resposta(
            mensagem_usuario=mensagem,
            categoria=categoria,
            contexto_extra=contexto_extra
        )
        logger.info("🤖 Resposta gerada com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro OpenAI: {e}")
        return {"status": "openai_error"}

    # ==================================================
    # SALVAR NO BANCO
    # ==================================================

    salvar_mensagem(numero, mensagem_id, mensagem, resposta, categoria)

    # ==================================================
    # ENVIAR WHATSAPP
    # ==================================================

    enviar_whatsapp(numero, resposta)

    # ==================================================
    # CRM
    # ==================================================

    registrar_crm(numero, mensagem)

    return {"status": "success"}


# ==================================================
# SALVAR MENSAGEM
# ==================================================

def salvar_mensagem(numero, mensagem_id, mensagem, resposta, categoria):
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO mensagens (telefone, mensagem_id, mensagem, resposta, categoria)
            VALUES (%s, %s, %s, %s, %s)
        """, (numero, mensagem_id, mensagem, resposta, categoria))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("💾 Mensagem salva no banco")

    except Exception as e:
        logger.error(f"❌ Erro ao salvar mensagem: {e}")


# ==================================================
# ENVIO Z-API
# ==================================================

def enviar_whatsapp(numero, mensagem):

    if not all([ZAPI_INSTANCE_ID, ZAPI_TOKEN, ZAPI_CLIENT_TOKEN]):
        logger.error("❌ Variáveis ZAPI ausentes")
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
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        logger.info(f"📤 ZAPI status: {response.status_code}")

    except Exception as e:
        logger.error(f"❌ Erro envio WhatsApp: {e}")


# ==================================================
# CRM
# ==================================================

def registrar_crm(numero, mensagem):

    if not CRM_WEBHOOK_URL:
        return

    payload = {
        "telefone": numero,
        "status": "Novo Lead",
        "observacoes": mensagem
    }

    try:
        requests.post(CRM_WEBHOOK_URL, json=payload, timeout=5)
        logger.info("📊 CRM registrado")

    except Exception as e:
        logger.error(f"❌ Erro CRM: {e}")
