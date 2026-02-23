import os
from datetime import datetime
import pytz
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def saudacao_por_horario():
    fuso = pytz.timezone("America/Sao_Paulo")
    hora = datetime.now(fuso).hour

    if 5 <= hora <= 11:
        return "Bom dia"
    elif 12 <= hora <= 17:
        return "Boa tarde"
    else:
        return "Boa noite"


def classificar_mensagem(mensagem):
    msg = mensagem.lower()

    palavras_suporte = [
        "problema", "inversor", "erro", "manutenção",
        "segunda via", "reclamação", "suporte"
    ]

    palavras_prazo = [
        "prazo", "demora", "atraso", "quando vai instalar",
        "está demorando"
    ]

    palavras_orcamento = [
        "orçamento", "energia solar", "placa solar",
        "sistema", "valor", "simulação"
    ]

    if any(p in msg for p in palavras_prazo):
        return "PRAZO"

    if any(p in msg for p in palavras_suporte):
        return "SUPORTE"

    if any(p in msg for p in palavras_orcamento):
        return "ORCAMENTO"

    return "SAUDACAO"


def gerar_resposta(mensagem_usuario):

    categoria = classificar_mensagem(mensagem_usuario)

    # ===============================
    # PRAZO
    # ===============================
    if categoria == "PRAZO":
        return (
            "Eu entendo sua preocupação e agradeço por me avisar.\n\n"
            "Vou verificar internamente com o setor responsável e retorno para você com a posição correta, tudo bem?"
        )

    # ===============================
    # SUPORTE
    # ===============================
    if categoria == "SUPORTE":
        return (
            "Obrigada pelo seu contato!\n\n"
            "Essa parte quem cuida é a Lívia, do nosso setor administrativo.\n"
            "Vou encaminhar sua mensagem para ela e em breve você receberá o suporte necessário."
        )

    # ===============================
    # SAUDAÇÃO SIMPLES (OI)
    # ===============================
    if categoria == "SAUDACAO":
        saudacao = saudacao_por_horario()
        return (
            f"Olá, {saudacao}!\n"
            "Eu me chamo Raquel Paz e sou Consultora Comercial da SUNLUX ENERGIA ☀️\n"
            "Como posso te ajudar hoje?"
        )

    # ===============================
    # ORÇAMENTO
    # ===============================
    if categoria == "ORCAMENTO":

        prompt = f"""
Você é Raquel Paz, Consultora Comercial da SUNLUX ENERGIA.

Responda de forma profissional, clara e objetiva.
Nunca informe prazo.
Nunca invente valores.
Finalize sempre com pergunta.

Cliente disse:
"{mensagem_usuario}"

Peça:
1. Foto da fatura com kWh visível
2. Se é apenas uma unidade
3. Se terá novos aparelhos
4. Nome completo
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é especialista em vendas consultivas de energia solar."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        return response.choices[0].message.content
