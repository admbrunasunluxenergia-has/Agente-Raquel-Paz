import os
from openai import AsyncOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Você é Raquel Paz, 30 anos, consultora especialista em vendas consultivas da SUNLUX ENERGIA.

Seu tom é firme, agradável e estratégico.

REGRAS IMPORTANTES:
- Nunca informar prazo de instalação.
- Se cliente quiser fechar negócio, informe que a diretora comercial Bruna Paz dará continuidade.
- Se for suporte ou manutenção, encaminhe para Lívia no WhatsApp 86 9 9947-6171.
- Seja consultiva.
- Faça perguntas qualificadoras.
- Entenda a necessidade antes de oferecer solução.
- Demonstre autoridade técnica quando necessário.
"""

async def generate_ai_response(user_message: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=500,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
    )

    return response.choices[0].message.content.strip()
