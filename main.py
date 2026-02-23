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
    mensagem_existe
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
def startup():
    criar_tabelas()


ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")
CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL")


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    if data.get("fromMe"):
        return {"status": "ignored_self"}

    if data.get("isGroup"):
        return {"status": "ignored_group"}

    numero = data.get("phone")
    mensagem_id = data.get("messageId") or data.get("id")
    mensagem = None

    if isinstance(data.get("text"), dict):
        mensagem = data.get("text", {}).get("message")
    elif isinstance(data.get("message"), str):
        mensagem = data.get("message")

    if not numero or not mensagem:
        return {"status": "invalid_payload"}

    if mensagem_existe(mensagem_id):
        return {"status": "duplicate_ignored"}

    categoria = classificar_mensagem(mensagem)

    historico = buscar_historico(numero)
    contato = buscar_contato(numero)

    contexto_extra = ""

    if contato:
        nome = contato[0]
        tipo = contato[1]
        contexto_extra += f"\nContato identificado: {nome} ({tipo})"

    if historico:
        contexto_extra += "\nHistórico recente:\n"
        for h in historico[-5:]:
            contexto_extra += f"Cliente: {h[0]}\nRaquel: {h[1]}\n"

    resposta = gerar_resposta(
        mensagem_usuario=mensagem,
        categoria=categoria,
        contexto_extra=contexto_extra
    )

    salvar_mensagem(numero, mensagem_id, mensagem, resposta, categoria)

    enviar_whatsapp(numero, resposta)

    registrar_crm(numero, mensagem)

    return {"status": "success"}


def salvar_mensagem(numero, mensagem_id, mensagem, resposta, categoria):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO mensagens (telefone, mensagem_id, mensagem, resposta, categoria)
        VALUES (%s, %s, %s, %s, %s)
    """, (numero, mensagem_id, mensagem, resposta, categoria))

    conn.commit()
    cursor.close()
    conn.close()


def enviar_whatsapp(numero, mensagem):

    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

    headers = {
        "Client-Token": ZAPI_CLIENT_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "phone": numero,
        "message": mensagem
    }

    requests.post(url, json=payload, headers=headers, timeout=10)


def registrar_crm(numero, mensagem):

    if not CRM_WEBHOOK_URL:
        return

    payload = {
        "telefone": numero,
        "status": "Novo Lead",
        "observacoes": mensagem
    }

    requests.post(CRM_WEBHOOK_URL, json=payload, timeout=5)
