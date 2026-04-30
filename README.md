# Multi-Agent Research Assistant

> AI-powered research using LangGraph multi-agent orchestration — runs locally with Azure OpenAI or OpenRouter (free tier).

**Built by [Sahel Ahmadzai](https://ahmadzai.tech) · BSc AI @ JKU Linz · AI & Automation Engineer**

---

## Architecture

```
User Task
   │
   ▼
┌──────────┐     ┌────────────┐     ┌─────────┐     ┌────────┐
│  Planner │────▶│ Researcher │────▶│ Analyst │────▶│ Writer │
│          │     │            │     │         │     │        │
│ Breaks   │     │ Web search │     │Synthesis│     │ Final  │
│ task into│     │ + summarize│     │& themes │     │ Report │
│ sub-Qs   │     │            │     │         │     │   .md  │
└──────────┘     └────────────┘     └─────────┘     └────────┘
```

**Real-time streaming:** Each agent streams its progress via Server-Sent Events (SSE) — you see every step live.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) |
| **LLMs** | Azure OpenAI (primary) · OpenRouter free tier (fallback) |
| **Web Search** | Tavily (recommended) · DuckDuckGo · Wikipedia (guaranteed fallback) |
| **Backend** | FastAPI + async Python |
| **Database** | SQLite (async via SQLAlchemy) |
| **Frontend** | React + Vite + TypeScript + Tailwind CSS |
| **Streaming** | Server-Sent Events (SSE) |

---

## Quick Start

### Windows (one command)
```powershell
.\start.ps1
```

Opens both backend (port 8000) and frontend (port 5173) in one click.

### Manual Setup

**Backend:**
```bash
cd backend
cp .env.example .env
# Fill in your API keys in .env

python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173 · API docs: http://localhost:8000/docs

### Docker
```bash
cp backend/.env.example backend/.env
docker compose up --build
```

---

## Configuration (`backend/.env`)

```env
# ── LLM: Azure OpenAI (GitHub Education / Azure for Students) ──────────
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-4o-mini   # name of your deployed model

# ── LLM: OpenRouter fallback (free, auto-used if Azure not configured) ──
OPENROUTER_API_KEY=your-key         # free at openrouter.ai

# ── Web Search: Tavily (1000 free searches/month) ───────────────────────
TAVILY_API_KEY=tvly-...             # free at app.tavily.com
# If not set: falls back to DuckDuckGo → Wikipedia (always works)
```

**Provider priority:**
- LLM: Azure → OpenRouter (auto-fallback if deployment not found)
- Search: Tavily → DuckDuckGo → Wikipedia (always has results)

---

## Agents

### 🧠 Planner
Breaks the research task into focused sub-questions.

### 🌐 Researcher
For each sub-question: searches the web (Tavily/DDG/Wikipedia), extracts results, summarizes key findings with source citations.

### 📊 Analyst
Synthesizes all research summaries, identifies themes, contradictions, and knowledge gaps.

### ✍️ Writer
Produces a professional Markdown report with Executive Summary, Key Findings, Analysis, Conclusions, and Sources.

---

## API

| Endpoint | Method | Description |
|---|---|---|
| `POST /api/research/stream` | POST | Start research + stream SSE events |
| `GET /api/sessions` | GET | List recent sessions |
| `GET /api/sessions/{id}` | GET | Get session + full report |
| `GET /health` | GET | Health check |

### Example Request
```json
POST /api/research/stream
{
  "task": "What are the best practices for production RAG systems?",
  "max_search_queries": 3
}
```

---

## Deploy to Cloud

### GitHub Actions (automatic)
Push to `main` → auto-deploys backend to Railway + frontend to Vercel.

**Required GitHub Secrets:**
```
RAILWAY_TOKEN
RAILWAY_BACKEND_URL
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
```

---

## Extending

- **Add agents:** Create a file in `backend/agents/`, add a node in `backend/graph/research_graph.py`
- **Swap LLMs:** Change `AZURE_DEPLOYMENT_NAME` or `openrouter_model` in `config.py`
- **Add auth:** Add JWT middleware to FastAPI
- **Production DB:** Replace `sqlite+aiosqlite` with `postgresql+asyncpg`

