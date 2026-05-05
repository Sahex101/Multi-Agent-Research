import uuid
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone

from models.schemas import ResearchRequest
from graph.research_graph import research_graph
from db.database import get_db, ResearchSessionModel
from config import mark_azure_failed, settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["research"])


async def _check_rate_limit(db: AsyncSession):
    """Raises 429 if daily or monthly session limits are exceeded."""
    now = datetime.now(timezone.utc)

    # Count today's sessions
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    daily_count = await db.scalar(
        select(func.count()).where(ResearchSessionModel.created_at >= day_start)
    )
    if daily_count >= settings.max_sessions_per_day:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit reached ({settings.max_sessions_per_day} sessions/day). Please try again tomorrow.",
        )

    # Count this month's sessions
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_count = await db.scalar(
        select(func.count()).where(ResearchSessionModel.created_at >= month_start)
    )
    if monthly_count >= settings.max_sessions_per_month:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly limit reached ({settings.max_sessions_per_month} sessions/month). Please try again next month.",
        )

# Maps node names to the next agent's start message
_NEXT_AGENT_START = {
    "planner": ("researcher", "Searching the web for {n} sub-questions..."),
    "researcher": ("analyst", "Analyzing and synthesizing all findings..."),
    "analyst": ("writer", "Writing the final research report..."),
}


def _sse(event_type: str, data: dict) -> str:
    return f"data: {json.dumps({'type': event_type, **data})}\n\n"


async def run_research_stream(task: str, max_search_queries: int, session_id: str, db: AsyncSession):
    """Generator that streams SSE events as each agent completes work."""

    yield _sse("agent_start", {"agent": "planner", "message": "Analyzing task and planning research..."})

    initial_state = {
        "task": task,
        "max_search_queries": max_search_queries,
        "sub_questions": [],
        "search_results": [],
        "analysis": "",
        "final_report": "",
        "events": [],
    }

    # Track how many events we've already streamed
    events_sent = 0
    final_state = None

    try:
        async for state_update in research_graph.astream(initial_state):
            for node_name, node_state in state_update.items():
                # Stream any new agent events produced by this node
                all_events = node_state.get("events", [])
                for event in all_events[events_sent:]:
                    yield _sse("agent_update", event)
                events_sent = len(all_events)

                # Signal what's coming next
                if node_name in _NEXT_AGENT_START:
                    next_agent, msg_template = _NEXT_AGENT_START[node_name]
                    n = len(node_state.get("sub_questions", []))
                    msg = msg_template.format(n=n) if "{n}" in msg_template else msg_template
                    yield _sse("agent_start", {"agent": next_agent, "message": msg})

                final_state = node_state

        if final_state:
            report = final_state.get("final_report", "")
            session_obj = await db.get(ResearchSessionModel, session_id)
            if session_obj:
                session_obj.status = "done"
                session_obj.final_report = report
                session_obj.updated_at = datetime.now(timezone.utc)
                await db.commit()
            yield _sse("complete", {"report": report, "session_id": session_id})

    except Exception as e:
        err_msg = str(e)
        # If Azure deployment doesn't exist yet, flip to OpenRouter and retry once
        if "DeploymentNotFound" in err_msg:
            mark_azure_failed()
            yield _sse("agent_update", {
                "agent": "system",
                "message": "Azure deployment not found — retrying with OpenRouter fallback...",
            })
            # Retry the whole graph with OpenRouter now active
            async for state_update in research_graph.astream(initial_state):
                for node_name, node_state in state_update.items():
                    all_events = node_state.get("events", [])
                    for event in all_events[events_sent:]:
                        yield _sse("agent_update", event)
                    events_sent = len(all_events)
                    if node_name in _NEXT_AGENT_START:
                        next_agent, msg_template = _NEXT_AGENT_START[node_name]
                        n = len(node_state.get("sub_questions", []))
                        msg = msg_template.format(n=n) if "{n}" in msg_template else msg_template
                        yield _sse("agent_start", {"agent": next_agent, "message": msg})
                    final_state = node_state
            if final_state:
                report = final_state.get("final_report", "")
                session_obj = await db.get(ResearchSessionModel, session_id)
                if session_obj:
                    session_obj.status = "done"
                    session_obj.final_report = report
                    session_obj.updated_at = datetime.now(timezone.utc)
                    await db.commit()
                yield _sse("complete", {"report": report, "session_id": session_id})
            return
        # Log full error internally, send only a generic message to the client
        logger.error("Research stream error (session=%s): %s", session_id, err_msg)
        yield _sse("error", {"message": "An error occurred while processing your request. Please try again."})
        session_obj = await db.get(ResearchSessionModel, session_id)
        if session_obj:
            session_obj.status = "error"
            await db.commit()

@router.post("/research/stream")
async def research_stream(request: ResearchRequest, db: AsyncSession = Depends(get_db)):
    """Start a research session and stream agent events via SSE."""
    await _check_rate_limit(db)

    session_id = str(uuid.uuid4())

    session = ResearchSessionModel(
        id=session_id,
        task=request.task,
        status="running",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.commit()

    return StreamingResponse(
        run_research_stream(request.task, request.max_search_queries, session_id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/usage")
async def get_usage(db: AsyncSession = Depends(get_db)):
    """Returns current daily and monthly session usage vs. limits."""
    now = datetime.now(timezone.utc)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    daily = await db.scalar(select(func.count()).where(ResearchSessionModel.created_at >= day_start))
    monthly = await db.scalar(select(func.count()).where(ResearchSessionModel.created_at >= month_start))

    return {
        "daily":   {"used": daily,   "limit": settings.max_sessions_per_day},
        "monthly": {"used": monthly, "limit": settings.max_sessions_per_month},
    }


@router.get("/sessions")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ResearchSessionModel).order_by(ResearchSessionModel.created_at.desc()).limit(20)
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "task": s.task,
            "status": s.status,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    session = await db.get(ResearchSessionModel, session_id)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": session.id,
        "task": session.task,
        "status": session.status,
        "final_report": session.final_report,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }
