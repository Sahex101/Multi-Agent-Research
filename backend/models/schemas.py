from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ResearchRequest(BaseModel):
    task: str = Field(..., min_length=10, max_length=2000)
    max_search_queries: int = Field(default=3, ge=1, le=10)

    @field_validator("task")
    @classmethod
    def task_no_injection(cls, v: str) -> str:
        # Strip null bytes and control characters that have no place in a task
        cleaned = v.replace("\x00", "").strip()
        if not cleaned:
            raise ValueError("Task must not be empty after stripping whitespace.")
        return cleaned


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
