# Multi-Agent Research Assistant

> AI-powered research using LangGraph multi-agent orchestration — **100% free** via OpenRouter + Vercel + Railway.

**[Live Demo](https://your-vercel-url.vercel.app)** · **[Backend API](https://your-railway-url.railway.app/docs)**

---

## Architecture

```
User Task
   │
   ▼
┌──────────┐     ┌────────────┐     ┌─────────┐     ┌────────┐
│  Planner │────▶│ Researcher │────▶│ Analyst │────▶│ Writer │
│          │     │            │     │         │     │        │
│ Breaks   │     │ DuckDuckGo │     │Synthesis│     │ Final  │
│ task into│     │ web search │     │& themes │     │ Report │
│ sub-Qs   │     │ + summarize│     │         │     │   .md  │
└──────────┘     └────────────┘     └─────────┘     └────────┘
```

**Real-time streaming:** Each agent streams its progress via Server-Sent Events (SSE) to the frontend — you see every step as it happens.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) |
| **LLMs** | OpenRouter free models (Llama 3.1, Gemma 3) |
| **Web Search** | DuckDuckGo Search (no API key needed) |
| **Backend** | FastAPI + async Python |
| **Database** | SQLite (local) / upgradeable to Supabase |
| **Frontend** | React + Vite + TypeScript + Tailwind CSS |
| **Streaming** | Server-Sent Events (SSE) |
| **Backend Hosting** | Railway (free tier) |
| **Frontend Hosting** | Vercel (free tier) |

---

## Free Setup — $0 Cost

1. **OpenRouter API key** → [openrouter.ai](https://openrouter.ai) — free tier includes Llama 3.1 8B and Gemma 3
2. **Railway** → [railway.app](https://railway.app) — free $5/month credits (more than enough)
3. **Vercel** → [vercel.com](https://vercel.com) — free hobby tier

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- OpenRouter API key

### Backend

```bash
cd backend
cp .env.example .env
# Add your OPENROUTER_API_KEY to .env

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### Docker (full stack)

```bash
cp backend/.env.example backend/.env
# Add OPENROUTER_API_KEY to backend/.env

docker compose up --build
```

---

## Agents

### 🧠 Planner
Breaks the research task into 2–4 focused sub-questions using `google/gemma-3-4b-it:free`.

### 🌐 Researcher
For each sub-question: searches DuckDuckGo (no API key), extracts top results, and summarizes key findings using `meta-llama/llama-3.1-8b-instruct:free`.

### 📊 Analyst
Synthesizes all research summaries, identifies themes, contradictions, and gaps using `meta-llama/llama-3.1-8b-instruct:free`.

### ✍️ Writer
Produces a professional, structured Markdown report with Executive Summary, Key Findings, Detailed Analysis, Conclusions, and Sources using `google/gemma-3-12b-it:free`.

---

## API

| Endpoint | Method | Description |
|---|---|---|
| `POST /api/research/stream` | POST | Start research + stream SSE events |
| `GET /api/sessions` | GET | List recent sessions |
| `GET /api/sessions/{id}` | GET | Get session + report |
| `GET /health` | GET | Health check |
| `GET /docs` | GET | Interactive API docs |

### Request
```json
POST /api/research/stream
{
  "task": "What are the best practices for production RAG systems?",
  "max_search_queries": 3
}
```

---

## Deploy

### GitHub Actions (automatic)
Push to `main` → auto-deploys backend to Railway + frontend to Vercel.

**Required secrets** (Settings → Secrets):
```
RAILWAY_TOKEN          # From railway.app dashboard
RAILWAY_BACKEND_URL    # Your Railway deployment URL
VERCEL_TOKEN           # From vercel.com dashboard
VERCEL_ORG_ID          # From Vercel project settings
VERCEL_PROJECT_ID      # From Vercel project settings
```

---

## Extending

- **Add agents:** Create a new file in `backend/agents/`, add a node to `backend/graph/research_graph.py`
- **Swap models:** Change `WRITER_MODEL` etc. in `.env` — any OpenRouter model works
- **Add Supabase:** Replace `sqlite+aiosqlite` with `postgresql+asyncpg` in `db/database.py`
- **Add auth:** Add Supabase Auth or a simple JWT middleware to FastAPI

---

*Built by [Sahel Ahmadzai](https://ahmadzai.tech) · BSc AI @ JKU Linz*
