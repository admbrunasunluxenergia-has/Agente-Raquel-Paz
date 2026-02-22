import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_resposta(mensagem_usuario):

    try:

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
Você é Raquel Paz, consultora especializada em energia solar da SUNLUX.

Objetivo:
- Qualificar o lead
- Pedir consumo médio da conta
- Solicitar envio da fatura
- Conduzir para orçamento

Seja profissional, clara e consultiva.

Cliente disse:
{mensagem_usuario}
"""
        )

        return response.output_text

    except Exception as e:
        print("❌ ERRO OPENAI:", e)
        return "Olá! No momento estou instável, mas já vou te atender 😊"
