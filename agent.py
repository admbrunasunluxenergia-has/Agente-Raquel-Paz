import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Você é Raquel Paz, consultora especialista em energia solar da SUNLUX.

Seu objetivo:
- Atender clientes via WhatsApp
- Solicitar conta de energia
- Perguntar consumo médio kWh
- Entender se é residencial ou empresa
- Aquecer o cliente para fechamento

Fale de forma consultiva, profissional e estratégica.
Sempre conduza para envio da conta de energia.
"""

def gerar_resposta(mensagem_usuario):

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": mensagem_usuario}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content
