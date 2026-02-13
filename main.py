import os
import requests
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("CLIENTE_TOKEN")
CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL")

# MEMÓRIA SIMPLES EM RAM
memoria_clientes = {}

def saudacao_por_horario():
    hora = datetime.now().hour
    if hora < 12:
        return "Bom dia"
    elif hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def enviar_mensagem(phone, mensagem):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    payload = {"phone": phone, "message": mensagem}
    requests.post(url, json=payload, headers=headers)

def salvar_no_crm(nome, telefone, observacoes):
    try:
        requests.post(
            CRM_WEBHOOK_URL,
            json={
                "name": nome,
                "telefone": telefone,
                "cidade": "",
                "status": "Novo Lead",
                "observacoes": observacoes
            },
            timeout=5
        )
    except:
        pass

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # 🔒 FILTRO ANTI LOOP
    if data.get("isStatusReply"):
        return JSONResponse({"status": "ignored status"})

    if data.get("fromMe"):
        return JSONResponse({"status": "ignored self message"})

    message = data.get("text", {}).get("message", "")
    phone = data.get("phone")

    if not message or not phone:
        return JSONResponse({"status": "no message"})

    message_lower = message.lower()

    # Criar memória se não existir
    if phone not in memoria_clientes:
        memoria_clientes[phone] = {"etapa": "inicio"}

    etapa = memoria_clientes[phone]["etapa"]

    # INÍCIO
    if etapa == "inicio":
        saudacao = saudacao_por_horario()
        resposta = f"{saudacao}, sou Raquel Paz, consultora da SUNLUX ENERGIA. Como posso te ajudar?"
        enviar_mensagem(phone, resposta)
        memoria_clientes[phone]["etapa"] = "aguardando_intencao"
        return JSONResponse({"status": "ok"})

    # ORÇAMENTO
    if "orçamento" in message_lower or "orcamento" in message_lower:
        resposta = (
            "Perfeito 😊 Para elaborar sua proposta preciso das seguintes informações:\n\n"
            "• Nome completo\n"
            "• Endereço da instalação\n"
            "• Média de consumo em kWh\n"
            "• Haverá acréscimo de equipamentos?\n"
            "• Outras unidades vinculadas?\n\n"
            "Se desejar simulação de financiamento, envie também:\n"
            "• Nome completo\n"
            "• Telefone\n"
            "• Data de nascimento\n"
            "• CPF"
        )
        enviar_mensagem(phone, resposta)
        salvar_no_crm("Lead WhatsApp", phone, message)
        memoria_clientes[phone]["etapa"] = "orçamento_em_andamento"
        return JSONResponse({"status": "ok"})

    # PÓS VENDA
    if any(p in message_lower for p in ["fatura", "geração", "conta", "análise"]):
        enviar_mensagem(phone, "Vou encaminhar você para nosso setor administrativo 😊")
        numero_lidia = "5586999999999"
        enviar_mensagem(numero_lidia, f"Cliente precisa de pós-venda: {phone}")
        memoria_clientes[phone]["etapa"] = "encaminhado_pos_venda"
        return JSONResponse({"status": "ok"})

    return JSONResponse({"status": "no action"})
