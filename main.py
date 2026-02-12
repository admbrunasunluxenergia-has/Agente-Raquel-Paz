"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
from agent import process_message

app = FastAPI()

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "online",
        "agent": "Raquel Paz",
        "version": "2.0.0"
    }

@app.post("/webhook")
async def webhook(request: Request):
    """Webhook para receber mensagens da Z-API"""
    try:
        # Receber payload da Z-API
        payload = await request.json()
        print(f"Payload recebido: {payload}")
        
        # Extrair dados do payload Z-API
        phone = payload.get("phone")
        text_data = payload.get("text", {})
        message = text_data.get("message", "")
        is_group = payload.get("isGroup", False)
        
        # Ignorar mensagens de grupo (proteção crítica)
        if is_group:
            print(f"Mensagem de grupo ignorada: {phone}")
            return JSONResponse(
                status_code=200,
                content={"status": "ignored", "reason": "group_message"}
            )
        
        # Validar dados obrigatórios
        if not phone or not message:
            print(f"Dados inválidos - phone: {phone}, message: {message}")
            return JSONResponse(
                status_code=400,
                content={"error": "Missing phone or message"}
            )
        
        # Processar mensagem e enviar resposta
        print(f"Processando mensagem de {phone}: {message}")
        result = await process_message(phone, message)
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "result": result}
        )
        
    except Exception as e:
        print(f"Erro no webhook: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
