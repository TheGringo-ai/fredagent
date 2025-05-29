# 🧠 FredAgent: AI-Ops Automation Engine

**FredAgent** is a high-performance, API-driven AI-Ops automation system built with FastAPI, GPT-based planning, memory querying, and intelligent logging. Designed to power industrial-grade workflows with audit-ready logs and actionable plans.

---

## 🚀 Features

- ✨ **Natural Language Planning** (`/generate-plan`)
- 🧠 **Memory Search + Log Querying** (`/log/query`)
- 📊 **Admin Tools** (`/memory/system`, `/memory/logs`)
- 🔐 Filter by IP, timestamp, event, keyword
- 📝 Streaming summaries powered by LLMs

---

## 📦 Tech Stack

- **FastAPI** – lightning-fast web API
- **LangChain / OpenAI** – LLM-driven planning + summarization
- **SentenceTransformers** – memory vectorization
- **GitHub + Uvicorn** – dev + deploy

---

## 📁 Project Structure

```
fredagent/
├── web/
│   ├── routes/         # FastAPI endpoints (planner, logs, memory)
│   ├── memory/         # Planner, memory manager, logger, agents
│   └── main.py         # Entrypoint
├── requirements.txt    # Dependencies
├── .gitignore
└── README.md
```

---

## 🔧 Setup

```bash
# Create and activate virtual env
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn web.main:app --reload
```

---

## 🔐 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/generate-plan` | Generates multi-step plans from a natural prompt |
| GET  | `/memory/system` | System health check |
| GET  | `/memory/logs` | View last N memory logs |
| GET  | `/log/query` | Summarize logs with filters and LLM |

---

## 🧠 Sample Query

```bash
curl -X POST http://localhost:8000/generate-plan \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Automate my book release workflow"}'
```

---

## 👤 Maintainer

**Fred Taylor**  
📧 yoyofred@gringosgambit.com  
🔗 https://github.com/TheGringo-ai

---

---

## 📄 License

MIT – Do whatever you want, just don't be shady.

---

## 🚀 Deployment

To deploy this app to Render or Railway:

1. Clone the repo  
2. Set your environment variables:
   - `OPENAI_API_KEY`
   - `GOOGLE_API_KEY`
   - `USE_GEMINI=true` or `false`
3. Add a `Procfile` containing:
   ```txt
   web: uvicorn web.main:app --host=0.0.0.0 --port=${PORT:-8000}
   ```
4. Add a `requirements.txt` with all dependencies
5. On Render:
   - Create a new Web Service
   - Select this repo
   - Use the Procfile or command above

🔐 Optional: Set up IP whitelisting or token-based auth in production.
