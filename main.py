import os
import requests
from fastapi import FastAPI, Request
from agent import gerar_resposta
from database import criar_tabelas, conectar

app = FastAPI()

# =============================
# INICIALIZAÇÃO BANCO
# =============================

criar_tabelas()

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
        "version": "5.0"
    }

# =============================
# WEBHOOK RECEBIMENTO
# =============================
from database import buscar_historico, buscar_contato

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    if data.get("fromMe"):
        return {"status": "ignored own message"}

    if data.get("isGroup"):
        return {"status": "group ignored"}

    numero = data.get("phone")
    mensagem = None

    if isinstance(data.get("text"), dict):
        mensagem = data.get("text", {}).get("message")
    elif isinstance(data.get("message"), str):
        mensagem = data.get("message")

    if not numero or not mensagem:
        return {"status": "no message"}

    # 🔎 Buscar histórico
    historico = buscar_historico(numero)

    # 🔎 Buscar contato (interno ou cliente)
    contato = buscar_contato(numero)

    contexto_extra = ""

    if contato:
        nome, tipo = contato
        contexto_extra += f"\nContato identificado: {nome} ({tipo})"

    if historico:
        contexto_extra += "\nHistórico recente:\n"
        for h in historico:
            contexto_extra += f"Cliente: {h[0]}\nRaquel: {h[1]}\n"

    # 👇 envia mensagem + contexto para o agente
    resposta = gerar_resposta(mensagem + contexto_extra)

    salvar_mensagem(numero, mensagem, resposta)

    enviar_whatsapp(numero, resposta)

    registrar_crm(numero, mensagem)

    return {"status": "success"}
# =============================
# SALVAR NO POSTGRES
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
