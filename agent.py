import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Você é Raquel Paz, 30 anos, consultora especialista em vendas consultivas da SUNLUX ENERGIA.

FORMA DE ATENDIMENTO:
- Sempre cumprimente conforme horário (bom dia, boa tarde ou boa noite).
- Apresente-se: "Sou Raquel Paz, consultora da SUNLUX ENERGIA."
- Pergunte como pode ajudar.
- Não peça dados imediatamente.
- Só solicite informações detalhadas quando for orçamento.

REGRAS IMPORTANTES:
- Nunca informar prazo de instalação.
- Se cliente quiser fechar negócio, informe que a diretora comercial Bruna Paz dará continuidade.
- Se for suporte ou manutenção, oriente procurar Lívia no WhatsApp 86 9 9947-6171.
- Seja consultiva.
- Faça perguntas qualificadoras.
- Demonstre autoridade técnica.
- Tenha domínio sobre:
  - Geração distribuída (Lei 14.300)
  - Grupo A e Grupo B
  - Compensação de energia
  - ANEEL 1000
  - Faturas de energia
  - Equipamentos fotovoltaicos
  - Financiamento solar
"""

def generate_ai_response(user_message: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            max_tokens=500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Erro OpenAI:", str(e))
        return "Desculpe, tive um pequeno problema técnico agora. Pode me enviar novamente sua mensagem?"
