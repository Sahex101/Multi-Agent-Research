from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResearchRequest(BaseModel):
    task: str
    max_search_queries: int = 3


class AgentEvent(BaseModel):
    agent: str
    status: str  # "running" | "done" | "error"
    message: str
    data: Optional[dict] = None


class ResearchSession(BaseModel):
    id: str
    task: str
    status: str
    final_report: Optional[str] = None
    created_at: datetime
    updated_at: datetime
