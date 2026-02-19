import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_resposta(mensagem_usuario):

    try:

        prompt = f"""
Você é Raquel Paz, consultora especializada em energia solar da SUNLUX.

Objetivo:
- Qualificar o lead
- Pedir consumo médio da conta de energia
- Solicitar envio da fatura
- Conduzir para orçamento

Seja profissional, clara e consultiva.

Cliente disse:
{mensagem_usuario}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é uma especialista em vendas consultivas de energia solar."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        print("❌ ERRO OPENAI:", e)
        return "Olá! No momento estou instável, mas já vou te atender 😊"
