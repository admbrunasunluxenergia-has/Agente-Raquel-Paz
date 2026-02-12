import os
import requests
from openai import OpenAI

# Configuração OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuração Z-API
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_BASE_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}"

# System prompt da Raquel Paz
SYSTEM_PROMPT = """Você é Raquel Paz, consultora especialista em vendas consultivas de energia fotovoltaica da SUNLUX ENERGIA.

PERFIL:
- Idade: 30 anos
- Estilo: Firme, agradável e estratégico
- Especialidade: Vendas consultivas de energia solar fotovoltaica

REGRAS IMPORTANTES:
1. NUNCA informar prazo de instalação
2. Se cliente quiser fechar negócio: encaminhar para Bruna Paz (diretora comercial)
3. Se for suporte/manutenção: encaminhar para Lívia no WhatsApp 86 9 9947-6171
4. Manter tom profissional, consultivo e estratégico
5. Focar em entender a necessidade do cliente antes de oferecer soluções
6. Fazer perguntas qualificadoras para entender o perfil do cliente

ABORDAGEM:
- Seja consultiva, não apenas vendedora
- Entenda a dor do cliente antes de apresentar solução
- Qualifique o lead com perguntas estratégicas
- Demonstre expertise técnica quando necessário
- Mantenha conversas objetivas mas agradáveis"""

async def process_message(phone: str, message: str) -> dict:
    """Processa mensagem e envia resposta via Z-API"""
    try:
        # Gerar resposta com OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        print(f"Resposta gerada: {ai_response}")
        
        # Enviar resposta via Z-API
        send_result = send_zapi_response(phone, ai_response)
        
        return {
            "phone": phone,
            "message_received": message,
            "response_sent": ai_response,
            "zapi_status": send_result
        }
        
    except Exception as e:
        print(f"Erro ao processar mensagem: {str(e)}")
        # Tentar enviar mensagem de erro amigável
        error_message = "Desculpe, tive um problema técnico. Por favor, tente novamente em instantes."
        send_zapi_response(phone, error_message)
        raise

def send_zapi_response(phone: str, message: str) -> dict:
    """Envia mensagem via Z-API"""
    try:
        url = f"{ZAPI_BASE_URL}/send-text"
        payload = {
            "phone": phone,
            "message": message
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        print(f"Mensagem enviada com sucesso para {phone}")
        return {"status": "sent", "response": response.json()}
        
    except Exception as e:
        print(f"Erro ao enviar mensagem via Z-API: {str(e)}")
        return {"status": "error", "error": str(e)}
