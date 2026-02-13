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


def saudacao_por_horario():
    hora = datetime.now().hour
    if hora < 12:
        return "Bom dia"
    elif hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"


@app.get("/")
async def health_check():
    return {
        "status": "online",
        "agent": "Raquel Paz",
        "version": "3.0.0"
    }


@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()
        print(f"Payload recebido: {payload}")

        phone = payload.get("phone")
        text_data = payload.get("text", {})
        message = text_data.get("message", "").lower()
        is_group = payload.get("isGroup", False)
        from_me = payload.get("fromMe", False)

        # 🔒 Ignorar grupo
        if is_group:
            return JSONResponse(status_code=200, content={"status": "ignored_group"})

        # 🔒 Ignorar mensagens enviadas pelo próprio agente (ANTI-LOOP)
        if from_me:
            return JSONResponse(status_code=200, content={"status": "ignored_from_me"})

        if not phone or not message:
            return JSONResponse(status_code=400, content={"error": "Invalid payload"})

        print(f"Processando mensagem de {phone}: {message}")

        # 🎯 DIRECIONAMENTO AUTOMÁTICO - PÓS VENDA
        palavras_pos_venda = [
            "fatura", "geração", "usina", "contestação",
            "não estou entendendo", "analisar conta"
        ]

        if any(p in message for p in palavras_pos_venda):
            resposta = (
                "Entendi 😊 Vou encaminhar você para o nosso setor de pós-venda. "
                "A consultora Lívia dará continuidade no seu atendimento.\n\n"
                "👉 WhatsApp: 86 9 9947-6171"
            )
        else:
            # 🤖 IA
            resposta = await generate_ai_response(message)

        # 📤 Envio via Z-API
        send_url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

        response = requests.post(
            send_url,
            headers={
                "Content-Type": "application/json",
                "Client-Token": ZAPI_CLIENT_TOKEN
            },
            json={
                "phone": phone,
                "message": resposta
            },
            timeout=10
        )

        print("STATUS Z-API:", response.status_code)
        print("RESPOSTA Z-API:", response.text)

        return JSONResponse(status_code=200, content={"status": "success"})

    except Exception as e:
        print("Erro no webhook:", str(e))
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
