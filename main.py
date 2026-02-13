import os
import requests
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from agent import generate_ai_response

app = FastAPI()

ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("CLIENTE_TOKEN")
CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL")

ULTIMAS_MENSAGENS = set()

def saudacao_por_horario():
    hora = datetime.now().hour
    if hora < 12:
        return "Bom dia"
    elif hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def enviar_mensagem(phone, message):
    try:
        url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
        headers = {
            "Client-Token": ZAPI_CLIENT_TOKEN
        }
        payload = {
            "phone": phone,
            "message": message
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Mensagem enviada para {phone}")
    except Exception as e:
        print("Erro ao enviar mensagem:", str(e))

def salvar_no_crm(phone, mensagem):
    try:
        requests.post(
            CRM_WEBHOOK_URL,
            json={
                "name": "",
                "telefone": phone,
                "cidade": "",
                "status": "Novo Lead",
                "observacoes": mensagem
            },
            timeout=5
        )
        print("Lead salvo no CRM.")
    except Exception as e:
        print("Erro CRM:", str(e))

@app.get("/")
async def health():
    return {"status": "online", "agent": "Raquel Paz"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()
        print("Payload recebido:", payload)

        if payload.get("isGroup"):
            return JSONResponse({"status": "ignored_group"}, status_code=200)

        message_id = payload.get("messageId")

        if message_id in ULTIMAS_MENSAGENS:
            print("Mensagem duplicada ignorada")
            return JSONResponse({"status": "duplicate"}, status_code=200)

        ULTIMAS_MENSAGENS.add(message_id)

        phone = payload.get("phone")
        message = payload.get("text", {}).get("message")

        if not phone or not message:
            return JSONResponse({"status": "invalid"}, status_code=200)

        texto_lower = message.lower()

        # 🔁 Direcionamento automático pós-venda
        palavras_pos_venda = [
            "geração", "fatura", "revisão", "manutenção",
            "contestação", "suporte", "não estou entendendo"
        ]

        if any(p in texto_lower for p in palavras_pos_venda):
            resposta = (
                f"{saudacao_por_horario()}! Vou encaminhar você para nosso setor administrativo.\n\n"
                "Nossa consultora Lívia dará continuidade ao seu atendimento:\n"
                "📲 86 9 9947-6171"
            )
            enviar_mensagem(phone, resposta)
            return JSONResponse({"status": "forwarded"}, status_code=200)

        # 📝 Registrar no CRM
        salvar_no_crm(phone, message)

        # 🤖 Gerar resposta IA
        resposta_ai = generate_ai_response(message)

        enviar_mensagem(phone, resposta_ai)

        return JSONResponse({"status": "ok"}, status_code=200)

    except Exception as e:
        print("Erro webhook:", str(e))
        return JSONResponse({"status": "error"}, status_code=200)
