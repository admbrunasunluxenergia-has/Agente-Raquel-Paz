import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from agent import generate_ai_response

app = FastAPI()

ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")


@app.get("/")
async def health_check():
    return {
        "status": "online",
        "agent": "Raquel Paz",
        "version": "2.0.0"
    }


@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()
        print(f"Payload recebido: {payload}")

        phone = payload.get("phone")
        text_data = payload.get("text", {})
        message = text_data.get("message")
        is_group = payload.get("isGroup", False)

        # 🔒 Proteção anti-spam (ignorar grupos)
        if is_group:
            print(f"Mensagem de grupo ignorada: {phone}")
            return JSONResponse(
                status_code=200,
                content={"status": "ignored", "reason": "group_message"}
            )

        # 🔍 Validação
        if not phone or not message:
            print(f"Dados inválidos - phone: {phone}, message: {message}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid payload"}
            )

        print(f"Processando mensagem de {phone}: {message}")

        # 🤖 Gerar resposta da IA
        try:
            ai_response = await generate_ai_response(message)
            print(f"Resposta gerada: {ai_response}")
        except Exception as e:
            print(f"Erro ao gerar resposta da IA: {str(e)}")
            ai_response = "Desculpe, tive um problema técnico. Por favor, tente novamente em instantes."

        # 📤 Enviar resposta via Z-API
        send_url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

        print("URL usada:", send_url)
        print("Número enviado:", phone)

        try:
            response = requests.post(
                send_url,
                headers={
                    "Content-Type": "application/json",
                    "Client-Token": ZAPI_CLIENT_TOKEN
                },
                json={
                    "phone": phone,
                    "message": ai_response
                },
                timeout=10
            )

            print("STATUS Z-API:", response.status_code)
            print("RESPOSTA Z-API:", response.text)

            response.raise_for_status()
            print(f"Mensagem enviada com sucesso para {phone}")

        except Exception as e:
            print(f"Erro ao enviar mensagem via Z-API: {str(e)}")

        return JSONResponse(status_code=200, content={"status": "success"})

    except Exception as e:
        print(f"Erro no webhook: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"}
        )
