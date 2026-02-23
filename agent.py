import os
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def saudacao_por_horario():
    hora = datetime.now().hour

    if 5 <= hora <= 11:
        return "Bom dia"
    elif 12 <= hora <= 17:
        return "Boa tarde"
    else:
        return "Boa noite"


def classificar_mensagem(mensagem):
    msg = mensagem.lower()

    # CATEGORIA C – PRAZO / CLIENTE IRRITADO
    palavras_prazo = [
        "qual o prazo", "quando vai instalar", "está demorando",
        "ja faz muito tempo", "ninguém me responde", "demora",
        "atraso", "instalação"
    ]

    if any(p in msg for p in palavras_prazo):
        return "PRAZO"

    # CATEGORIA B – SUPORTE
    palavras_suporte = [
        "problema no inversor", "sistema desligado", "erro aplicativo",
        "internet desconectada", "manutenção", "suporte",
        "fatura não chegou", "segunda via", "reclamação",
        "acompanhamento de instalação"
    ]

    if any(p in msg for p in palavras_suporte):
        return "SUPORTE"

    # CATEGORIA A – ORÇAMENTO
    palavras_orcamento = [
        "orçamento", "energia solar", "placa solar",
        "usina solar", "projeto solar", "sistema fotovoltaico",
        "reduzir conta", "instalar energia solar",
        "valor do sistema", "simulação"
    ]

    if any(p in msg for p in palavras_orcamento):
        return "ORCAMENTO"

    return "GERAL"


def gerar_resposta(mensagem_usuario):

    try:
        categoria = classificar_mensagem(mensagem_usuario)
        saudacao = saudacao_por_horario()

        # ================================
        # CATEGORIA PRAZO (REGRA CRÍTICA)
        # ================================
        if categoria == "PRAZO":
            return (
                "Eu entendo sua preocupação e agradeço por me avisar.\n\n"
                "Vou verificar internamente com o setor responsável e retorno para você com a posição correta, tudo bem?"
            )

        # ================================
        # CATEGORIA SUPORTE
        # ================================
        if categoria == "SUPORTE":
            return (
                "Obrigada pelo seu contato!\n\n"
                "Essa parte quem cuida é a Lívia, do nosso setor administrativo.\n"
                "Vou encaminhar sua mensagem para ela e em breve você receberá o suporte necessário."
            )

        # ================================
        # PRIMEIRA MENSAGEM (ORÇAMENTO)
        # ================================
        if categoria in ["ORCAMENTO", "GERAL"]:

            prompt = f"""
Você é Raquel Paz, Consultora Comercial da SUNLUX ENERGIA.

REGRAS OBRIGATÓRIAS:
- Linguagem profissional, humana e objetiva.
- Nunca linguagem robótica.
- Máximo 1 emoji ☀️.
- Nunca informar prazo.
- Nunca inventar valores.
- Sempre finalizar com pergunta quando for fluxo comercial.

Cliente escreveu:
"{mensagem_usuario}"

Se for início de conversa, use este modelo:

"Olá, {saudacao}!
Eu me chamo Raquel Paz e sou Consultora Comercial da SUNLUX ENERGIA ☀️
Como posso te ajudar hoje?"

Se for interesse em orçamento, siga este fluxo:

1️⃣ Solicitar foto nítida da fatura (kWh visível)
2️⃣ Perguntar se é apenas uma unidade consumidora
3️⃣ Perguntar sobre novos aparelhos (ar-condicionado, freezer, etc.)
4️⃣ Solicitar nome completo

Sempre conduzir de forma consultiva.
Sempre finalizar com pergunta.
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é especialista em vendas consultivas de energia solar."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )

            return response.choices[0].message.content

    except Exception as e:
        print("ERRO AGENTE:", e)
        return "No momento estou finalizando um atendimento, mas já retorno para você."
