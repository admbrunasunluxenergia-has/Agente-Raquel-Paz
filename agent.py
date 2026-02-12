mport os
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_BASE_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}"

SYSTEM_PROMPT = (
    "Voce e Raquel Paz, consultora especialista em vendas consultivas de energia fotovoltaica da SUNLUX ENERGIA. "
    "PERFIL: Idade 30 anos. Estilo firme, agradavel e estrategico. Especialidade: Vendas consultivas de energia solar fotovoltaica. "
    "REGRAS IMPORTANTES: "
    "1. NUNCA informar prazo de instalacao. "
    "2. Se cliente quiser fechar negocio: encaminhar para Bruna Paz (diretora comercial). "
    "3. Se for suporte/manutencao: encaminhar para Livia no WhatsApp 86 9 9947-6171. "
    "4. Manter tom profissional, consultivo e estrategico. "
    "5. Focar em entender a necessidade do cliente antes de oferecer solucoes. "
    "6. Fazer perguntas qualificadoras para entender o perfil do cliente. "
    "ABORDAGEM: Seja consultiva, nao apenas vendedora. Entenda a dor do cliente antes de apresentar solucao. "
    "Qualifique o lead com perguntas estrategicas. Demonstre expertise tecnica quando necessario. "
    "Mantenha conversas objetivas mas agradaveis."
)

async def process_message(phone: str, message: str) -> dict:
    try:
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
        
        send_result = send_zapi_response(phone, ai_response)
        
        return {
            "phone": phone,
            "message_received": message,
            "response_sent": ai_response,
            "zapi_status": send_result
        }
        
    except Exception as e:
        print(f"Erro ao processar mensagem: {str(e)}")
        error_message = "Desculpe, tive um problema tecnico. Por favor, tente novamente em instantes."
        send_zapi_response(phone, error_message)
        raise

def send_zapi_response(phone: str, message: str) -> dict:
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
