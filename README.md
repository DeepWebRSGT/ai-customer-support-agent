# AI Customer Support Agent Demo

A smart AI-powered customer support agent that understands inquiries, searches a knowledge base, and provides accurate responses with automatic ticket categorization.

> 🇹🇷 Türkçe açıklama: Müşteri destek taleplerini anlayan, bilgi tabanında arama yapan ve otomatik olarak kategorize eden yapay zeka destekli bir müşteri hizmetleri asistanı.

---

## ✨ Features

- **🤖 AI-Powered Conversations** — Understands natural language questions
- **📚 Knowledge Base Integration** — Automatically searches relevant information
- **🏷️ Smart Ticket Categorization** — Classifies inquiries as Urgent, Normal, or Low
- **🌍 Multi-language Support** — Turkish + English (easily extendable)
- **🔧 Modular Design** — Easy to customize and extend
- **📊 Session Logging** — Tracks all conversations for analysis

## 🛠️ Tech Stack

- **Python 3.10+**
- **LangChain** — Agent framework
- **OpenAI / Anthropic API** — LLM backend
- **SQLite** — Session storage

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/ramicode/ai-customer-support-agent
cd ai-customer-support-agent

# 2. Install
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set your API key
#   Windows: set OPENAI_API_KEY=sk-...
#   Mac/Linux: export OPENAI_API_KEY=sk-...

# 4. Run
python main.py
```

## 📁 Project Structure

```
ai-customer-support-agent/
├── main.py              # Entry point — run this
├── agent.py             # Core AI agent logic
├── knowledge_base.py    # Document search & retrieval
├── categorizer.py       # Ticket category classifier
├── storage.py           # Session & conversation storage
├── requirements.txt     # Dependencies
└── README.md            # This file
```

## 🧪 Example Usage

```
User: "Siparişim 3 gündür gelmedi, ne oluyor?"
Agent: [URGENT] 📦 I see this is an order delivery issue.
Let me check the shipping policy...

User: "Ürün iadesi nasıl yapılıyor?"
Agent: [NORMAL] 🔄 Here's our return process step by step...

User: "Çalışma saatleriniz nedir?"
Agent: [LOW] ⏰ Our working hours are 09:00 - 18:00 on weekdays.
```

## 🔌 API Integration Ready

This agent can be extended to connect with:
- **Zendesk / Freshdesk** — Ticket systems
- **Slack / Discord** — Team notifications
- **Twilio** — SMS/Call automation
- **WhatsApp API** — Customer messaging
- **Hermes Agent** — Advanced agent orchestration

## 📄 License

MIT — Free to use, modify, and share.

---

*Built by [Rami](https://github.com/ramicode) — AI Agent Developer 
🇳🇱 Netherlands | 🇹🇷 Turkish / 🇸🇾 Arabic / 🇬🇧 English*
