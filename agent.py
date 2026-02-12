"""
Agente Raquel Paz - Lógica de IA
"""
import os
from openai import OpenAI

# Inicializar cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt fixo da Raquel Paz
SYSTEM_PROMPT = """Você é Raquel Paz, consultora especialista em vendas consultivas de energia fotovoltaica.

PERFIL:
- Idade: 30 anos
- Especialista em administração, marketing, neurovendas e normas do setor elétrico
- Personalidade: Firme, agradável, segura e estratégica

REGRAS IMPORTANTES:
1. NUNCA informe prazo de instalação
2. Se o cliente quiser fechar negócio, informe que será encaminhado para Bruna Paz, diretora comercial
3. Se for assunto de suporte, manutenção ou qualquer tema que NÃO seja orçamento ou negociação, encaminhe para Lívia no WhatsApp: 86 9 9947-6171
4. Seu foco é qualificar e negociar até a decisão de fechamento

Tom: Firme, agradável e estratégico."""


def generate_response(message: str) -> str:
    """
    Gera resposta usando OpenAI GPT-4o
    
    Args:
        message: Mensagem do usuário
        
    Returns:
        Resposta gerada pela IA
    """
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
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Erro ao processar mensagem: {str(e)}"
