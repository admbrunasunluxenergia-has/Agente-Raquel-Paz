# Agente Raquel Paz

Agente de IA para vendas consultivas de energia fotovoltaica.

## Estrutura

```
agente-raquel-paz/
├── main.py              # API FastAPI
├── agent.py             # Lógica do agente
├── requirements.txt     # Dependências
├── Procfile             # Comando Railway
├── runtime.txt          # Versão Python
└── .env.example         # Exemplo de variáveis
```

## Instalação Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis
cp .env.example .env
# Editar .env com suas credenciais

# Executar
uvicorn main:app --reload
```

## Deploy no Railway

1. Criar projeto no Railway
2. Conectar repositório GitHub
3. Adicionar variáveis de ambiente:
   - `OPENAI_API_KEY`
   - `PORT=8000`
4. Deploy automático

## Endpoints

- `GET /` - Health check
- `POST /webhook` - Receber mensagens

## Variáveis de Ambiente

```
OPENAI_API_KEY=sk-proj-...
PORT=8000
```
