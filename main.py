"""
Agente Raquel Paz - API Principal
"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from agent import generate_response

app = FastAPI(title="Agente Raquel Paz")


@app.get("/")
async def healthcheck():
    """Health check endpoint"""
    return {
        "status": "online",
        "agent": "Raquel Paz",
        "version": "1.0.0"
    }


@app.post("/webhook")
async def webhook(request: Request):
    """Webhook para receber mensagens"""
    try:
        payload = await request.json()
        
        # Extrair mensagem do payload
        message = payload.get("message", "")
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message is required"}
            )
        
        # Gerar resposta usando o agente
        response = generate_response(message)
        
        return {
            "status": "success",
            "response": response
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
