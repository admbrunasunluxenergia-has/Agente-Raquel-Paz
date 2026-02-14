# main.py

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
import uvicorn
import os
from agent import process_message

# Inicializa a aplicação FastAPI
app = FastAPI()

@app.get("/")
def health_check():
    """Endpoint para verificação de saúde da API."""
    return {"status": "ok", "agent": "Raquel Paz", "version": "1.0.0"}

@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint que recebe os webhooks da Z-API.
    """
    try:
        # Pega o corpo da requisição em JSON
        data = await request.json()
        print("Webhook recebido:", data)
        
        # Adiciona o processamento da mensagem a uma tarefa em segundo plano
        # Isso faz com que a API responda imediatamente com 200 OK para a Z-API,
        # evitando timeouts enquanto a IA processa a resposta.
        background_tasks.add_task(process_message, data)
        
        return {"status": "received"}

    except Exception as e:
        # Se o corpo da requisição não for um JSON válido ou outro erro ocorrer
        print(f"Erro no endpoint /webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid request format")

if __name__ == "__main__":
    # Pega a porta da variável de ambiente, com 8000 como padrão
    port = int(os.environ.get("PORT", 8000))
    # Executa o servidor Uvicorn. O host 0.0.0.0 é essencial para o Railway.
    uvicorn.run(app, host="0.0.0.0", port=port)

