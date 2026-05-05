from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db.database import init_db
from api.routes import router
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="AI-powered research using LangGraph multi-agent orchestration",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,    # disable /docs in production
    redoc_url=None,   # disable /redoc in production
    openapi_url=None, # disable /openapi.json in production
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "multi-agent-research-api"}
