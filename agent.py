# agent.py

import os
import requests
from openai import OpenAI

# --- CONFIGURAÇÃO INICIAL ---
# Carrega as variáveis de ambiente para uso no agente
try:
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    ZAPI_INSTANCE_ID = os.environ['ZAPI_INSTANCE_ID']
    ZAPI_TOKEN = os.environ['ZAPI_TOKEN']
    ZAPI_CLIENT_TOKEN = os.environ['ZAPI_CLIENT_TOKEN']
    CRM_WEBHOOK_URL = os.environ['CRM_WEBHOOK_URL']
except KeyError as e:
    print(f"ERRO CRÍTICO: Variável de ambiente não encontrada: {e}")
    # Em um ambiente de produção, isso deveria parar a aplicação ou alertar.
    # Por enquanto, vamos definir valores padrão para evitar que o programa quebre na inicialização.
    OPENAI_API_KEY = ZAPI_INSTANCE_ID = ZAPI_TOKEN = ZAPI_CLIENT_TOKEN = CRM_WEBHOOK_URL = ""


# Inicializa o cliente da OpenAI (padrão 2026)
client = OpenAI(api_key=OPENAI_API_KEY)

# --- MEMÓRIA SIMPLES DO AGENTE ---
# Um dicionário para armazenar o histórico de conversas de cada usuário (telefone)
conversation_history = {}

# --- PROMPT DO SISTEMA (A PERSONALIDADE DA RAQUEL) ---
SYSTEM_PROMPT = """
Você é Raquel Paz, uma consultora especialista em energia fotovoltaica da SUNLUX ENERGIA.
Sua comunicação deve ser profissional, clara e consultiva.

REGRAS PRINCIPAIS:
1.  **Apresentação**: Sempre se apresente como "Raquel Paz, consultora da SUNLUX ENERGIA".
2.  **Objetivo**: Seu objetivo principal é qualificar o cliente para um orçamento. Para isso, você precisa saber o consumo de energia dele (em kWh ou o valor em R$ da fatura).
3.  **Não peça dados de imediato**: Inicie a conversa de forma natural. Só peça o consumo quando o cliente demonstrar interesse em um orçamento.
4.  **Direcionamento de Suporte**: Se a mensagem contiver palavras como 'manutenção', 'revisão', 'suporte', 'fatura', 'geração', 'não estou entendendo', responda de forma educada e direcione para a Lívia, informando o contato: (86) 99947-6171. Não tente resolver o problema.
5.  **Direcionamento de Fechamento**: Para fechar negócio ou assinar contrato, encaminhe para a diretora Bruna Paz.
6.  **Domínio Técnico**: Demonstre conhecimento sobre a Lei 14.300, ANEEL 1000, Grupo A/B, e o sistema de compensação de energia, mas de forma simples e didática, sem sobrecarregar o cliente.
7.  **Proibido**: Nunca informe ou prometa prazos de instalação.
"""

def process_message(message_data: dict) -> None:
    """
    Função principal que processa a mensagem recebida, gera uma resposta e a envia.
    """
    try:
        phone = message_data.get('phone')
        message_text = message_data.get('text', {}).get('message', '')
        is_group = message_data.get('isGroup')

        # 1. Ignorar mensagens de grupo ou sem texto
        if is_group or not message_text:
            print(f"Mensagem de grupo ou vazia ignorada. Remetente: {phone}")
            return

        print(f"Processando mensagem de {phone}: '{message_text}'")

        # 2. Salvar lead no CRM (com tratamento de erro)
        save_lead_to_crm(phone, message_data.get('senderName', 'Não informado'))

        # 3. Gerar resposta com a IA
        # Adiciona a mensagem atual ao histórico
        history = conversation_history.get(phone, [])
        history.append({"role": "user", "content": message_text})
        
        # Gera a resposta da IA
        ai_response = get_ai_response(history)

        # Adiciona a resposta da IA ao histórico
        history.append({"role": "assistant", "content": ai_response})
        
        # Limita o histórico para não ficar muito grande (últimas 10 trocas)
        conversation_history[phone] = history[-10:]

        # 4. Enviar resposta via Z-API
        send_message_zapi(phone, ai_response)

    except Exception as e:
        print(f"ERRO no processamento da mensagem: {e}")


def save_lead_to_crm(phone: str, name: str) -> None:
    """
    Envia os dados do lead para o webhook do CRM.
    """
    if not CRM_WEBHOOK_URL:
        print("AVISO: URL do CRM não configurada. Lead não foi salvo.")
        return
        
    payload = {
        "phone": phone,
        "name": name,
        "source": "WhatsApp - Agente Raquel"
    }
    try:
        response = requests.post(CRM_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()  # Lança um erro para respostas HTTP 4xx/5xx
        print(f"Lead salvo no CRM com sucesso para o número: {phone}")
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao salvar lead no CRM: {e}")


def get_ai_response(history: list) -> str:
    """
    Chama a API da OpenAI para gerar uma resposta baseada no histórico.
    """
    if not OPENAI_API_KEY:
        print("AVISO: Chave da OpenAI não configurada. Usando resposta padrão.")
        return "Olá! Sou a Raquel da SUNLUX. Em que posso ajudar? (Erro: IA não configurada)"

    try:
        messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}] + history
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages_for_api,
            temperature=0.7,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"ERRO ao chamar a API da OpenAI: {e}")
        return "Peço desculpas, estou com uma instabilidade em meu sistema. Poderia repetir sua pergunta em alguns instantes?"


def send_message_zapi(phone: str, message: str) -> None:
    """
    Envia a mensagem de resposta usando a API da Z-API.
    Esta é a função crítica que precisa ser validada.
    """
    if not all([ZAPI_INSTANCE_ID, ZAPI_TOKEN, ZAPI_CLIENT_TOKEN]):
        print("AVISO: Credenciais da Z-API não configuradas. Mensagem não enviada.")
        return

    # Montagem da URL CORRETA
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
    
    headers = {
        "Client-Token": ZAPI_CLIENT_TOKEN,
        "Content-Type": "application/json"
    }
    
    payload = {
        "phone": phone,
        "message": message
    }
    
    print(f"Enviando para Z-API. URL: {url}, Payload: {payload}" )

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        # Verificação detalhada da resposta
        if response.status_code == 200 or response.status_code == 201:
            print(f"Mensagem enviada com sucesso para {phone}. Response: {response.json()}")
        else:
            # Log do erro detalhado retornado pela Z-API
            print(f"ERRO ao enviar mensagem via Z-API. Status: {response.status_code}, Resposta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"ERRO DE CONEXÃO ao enviar mensagem para a Z-API: {e}")

