<div align="center">

# 🤖 AI Customer Support Agent

**An intelligent, RAG-powered customer support chatbot with multi-language support and smart ticket categorisation.**

[![CI](https://github.com/DeepWebRSGT/ai-customer-support-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/DeepWebRSGT/ai-customer-support-agent/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-V3-8A2BE2)](https://deepseek.com)

<br>

**Built by [Rami A.](https://github.com/DeepWebRSGT) — AI Agent Developer**  
🇳🇱 Netherlands · 🇹🇷 Turkish · 🇸🇾 Arabic · 🇬🇧 English · 🇳🇱 Dutch

</div>

---

## ✨ Overview

Instead of expensive offshore support teams or rigid chatbot platforms, this agent gives you:

- **🧠 AI-Powered Responses** — Understands natural language across **Turkish, English, and Dutch**
- **📚 RAG (Retrieval-Augmented Generation)** — Queries a knowledge base before answering, so replies are accurate and fact-based
- **🏷️ Smart Categorisation** — Automatically classifies every inquiry by urgency (`urgent → high → normal → low`) and topic (`shipping`, `returns`, `payment`, `account`, `technical`)
- **🔌 API-Ready Architecture** — Modular classes make it trivial to swap in any vector store (Chroma, Pinecone, Qdrant), LLM provider (OpenAI, Claude, Gemini), or messaging platform (Slack, Telegram, WhatsApp)
- **📊 Full Session Logging** — Every conversation is saved to JSON for analysis, training, or compliance
- **💸 Zero Recurring Costs** — Categorisation runs 100% locally; the LLM API is optional (graceful fallback to templates)

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/DeepWebRSGT/ai-customer-support-agent.git
cd ai-customer-support-agent

# 2. Install dependencies
python -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows

pip install -r requirements.txt

# 3. Set your DeepSeek API key (optional — works without it too)
#    Copy .env.example to .env and fill in your key
cp .env.example .env              # Linux / macOS
# copy .env.example .env          # Windows
# Edit .env: DEEPSEEK_API_KEY=sk-...

# 4. Run
python main.py
```

### Docker

```bash
docker build -t ai-support-agent .
docker run -it --rm -e DEEPSEEK_API_KEY=sk-... ai-support-agent
```

---

## 🧪 Example Usage

```
╭─ [URGENT] Shipping ─────────────────────────────╮
│                                                  │
│   Siparişinizin gecikmesi için üzgünüz.          │
│   Lütfen sipariş numaranızı bizimle paylaşın,    │
│   kargo durumunuzu kontrol edelim.               │
│                                                  │
╰──────────────────────────────────────────────────╯
Session: session_20260524_165113

> Şifremi unuttum, nasıl sıfırlayabilirim?

╭─ [NORMAL] Account ──────────────────────────────╮
│                                                  │
│   Giriş sayfasındaki 'Şifremi Unuttum' linkine  │
│   tıklayarak sıfırlama bağlantısı alabilirsiniz. │
│                                                  │
╰──────────────────────────────────────────────────╯

> What are your working hours?

╭─ [LOW] General ─────────────────────────────────╮
│                                                  │
│   Weekdays 09:00–18:00, Saturdays 10:00–15:00.  │
│   Closed Sundays.                                │
│                                                  │
╰──────────────────────────────────────────────────╯
```

---

## 📁 Project Structure

```
ai-customer-support-agent/
├── main.py               # Entry point — CLI interface with /commands
├── agent.py              # Core AI agent (DeepSeek + RAG pipeline)
├── knowledge_base.py     # In-memory document store with keyword search
├── categorizer.py        # Real-time ticket classifier (zero API cost)
├── storage.py            # JSON-based session logging
├── sessions.json         # Demo conversation data
│
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Build config & metadata
├── Dockerfile            # Containerised deployment
│
├── .env.example          # Environment variable template
├── .gitignore            # Files to exclude from version control
├── LICENSE               # MIT license
└── README.md             # This file
```

---

## 🧠 Architecture

```
 Customer Message
       │
       ▼
┌──────────────┐     ┌──────────────────┐
│  Categorizer  │────▶│  Knowledge Base  │
│  (local, no   │     │  (keyword search)│
│   API cost)   │     └────────┬─────────┘
└──────┬───────┘              │
       │ urgency + topic      │ context
       ▼                      ▼
┌──────────────────────────────────────┐
│           Agent (LLM)                │
│  DeepSeek / OpenAI / Claude / etc.   │
│  System prompt + KB context + query  │
└────────────────┬─────────────────────┘
                 │ response
                 ▼
┌──────────────────────────────────────┐
│           Storage (JSON)             │
│  Logs every exchange for analysis    │
└──────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Why |
|----------|-----|
| **Keyword categorisation** (not LLM) | Zero cost, instant, works offline |
| **In-memory KB** | Swap to Chroma/Qdrant when you scale |
| **JSON storage** | Easy to inspect, migrate, or plug into a DB |
| **Graceful fallback** | Templates when API is down = never silent |
| **DeepSeek default** | Best price/quality for support (prompt caching = ultra low cost) |

---

## 🔌 Extending

### Add a new language

Edit `_detect_language()` in `agent.py` and add a system prompt in `_build_system_prompt()`. That's it.

### Connect to a real vector store

Replace `KnowledgeBase.search()` with a call to your vector DB. The interface is `search(query, top_k) → list[dict]`.

### Connect to Slack / Telegram / WhatsApp

The `handle()` method returns a clean `{reply, classification, sources, session_id}` dict. Wrap it in your webhook handler of choice.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| LLM | DeepSeek-V3 (OpenAI-compatible API) |
| CLI | Rich (beautiful terminal output) |
| Storage | JSON (swap to SQLite / Postgres) |
| Container | Docker (multi-stage build) |
| CI | GitHub Actions (lint + test) |
| License | MIT |

---

## 📄 License

MIT — use it, modify it, share it. No strings attached.

---

<div align="center">

**Questions? [Open an issue](https://github.com/DeepWebRSGT/ai-customer-support-agent/issues)**  
**Built with ❤️ by Rami — AI Agent Developer**

</div>
