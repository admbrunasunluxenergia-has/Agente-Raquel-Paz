import os
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto


def classificar_mensagem(mensagem):

    msg = normalizar(mensagem)

    suporte = [
        "problema", "inversor", "erro",
        "manutencao", "segunda via",
        "reclamacao", "suporte"
    ]

    prazo = [
        "prazo", "demora",
        "atraso", "quando vai instalar"
    ]

    orcamento = [
        "orcamento", "energia solar",
        "placa solar", "valor",
        "simulacao", "projeto solar"
    ]

    saudacoes = [
        "oi", "ola", "bom dia",
        "boa tarde", "boa noite"
    ]

    if any(p in msg for p in suporte):
        return "SUPORTE"

    if any(p in msg for p in prazo):
        return "PRAZO"

    if any(p in msg for p in orcamento):
        return "ORCAMENTO"

    if any(msg.startswith(s) for s in saudacoes):
        return "SAUDACAO"

    return "OUTRO"


def saudacao_por_horario():
    hora = datetime.now(ZoneInfo("America/Sao_Paulo")).hour

    if 5 <= hora < 12:
        return "Bom dia"
    elif 12 <= hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"


def gerar_resposta(mensagem_usuario, categoria, contexto_extra=""):

    try:

        if categoria == "PRAZO":
            return (
                "Eu entendo sua preocupação e agradeço por me avisar.\n\n"
                "Vou verificar internamente com o setor responsável e retorno para você com a posição correta, tudo bem?"
            )

        if categoria == "SUPORTE":
            return (
                "Obrigada pelo seu contato!\n\n"
                "Essa parte quem cuida é a Lívia, do nosso setor administrativo.\n"
                "Vou encaminhar sua mensagem para ela e em breve você receberá o suporte necessário."
            )

        if categoria == "SAUDACAO":
            saudacao = saudacao_por_horario()
            return (
                f"{saudacao}!\n"
                "Eu me chamo Raquel Paz e sou Consultora Comercial da SUNLUX ENERGIA ☀️\n"
                "Como posso te ajudar hoje?"
            )

        if categoria == "ORCAMENTO":

            prompt = f"""
Você é Raquel Paz, Consultora Comercial da SUNLUX ENERGIA.

Regras:
- Nunca informe prazo.
- Nunca invente valores.
- Seja objetiva.
- Use no máximo 1 emoji ☀️
- Finalize sempre com pergunta.

Cliente disse:
"{mensagem_usuario}"

{contexto_extra}

Peça:
1. Foto da fatura com kWh visível
2. Se é apenas uma unidade
3. Se terá novos aparelhos
4. Nome completo
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.3,
                messages=[
                    {"role": "system", "content": "Você é especialista em vendas consultivas de energia solar."},
                    {"role": "user", "content": prompt}
                ],
            )

            return response.choices[0].message.content

        return "Pode me explicar um pouco melhor para eu te ajudar da melhor forma?"

    except Exception:
        return "Tive uma instabilidade interna agora. Pode repetir sua mensagem por favor?"
