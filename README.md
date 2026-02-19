# 🚀 Agente Raquel Paz

Agente de IA para atendimento e vendas consultivas de energia fotovoltaica (SUNLUX).

Integrações:
- WhatsApp (Z-API)
- OpenAI
- Google Sheets (CRM via Apps Script)
- Railway (Deploy)

---

# 📁 Estrutura do Projeto

agente-raquel-paz/
├── main.py              # API FastAPI (webhook e health check)
├── agent.py             # Lógica da IA e regras comerciais
├── requirements.txt     # Dependências
├── Procfile             # Comando de inicialização Railway
├── runtime.txt          # Versão do Python
└── .env.example         # Modelo de variáveis de ambiente

---

# 🧠 Funcionalidades Atuais

✅ Recebe mensagens do WhatsApp via webhook  
✅ Processa texto com OpenAI  
✅ Responde automaticamente  
✅ Envia dados para CRM (Google Sheets)  
✅ Health Check ativo  
✅ Deploy automático via Railway  

---

# ⚙️ Variáveis de Ambiente

Configurar no Railway:
