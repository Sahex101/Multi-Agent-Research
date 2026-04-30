from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm


async def analyst_node(state: dict) -> dict:
    """Synthesizes all research findings into a coherent analysis."""
    llm = get_llm()

    findings = "\n\n---\n\n".join(
        f"Sub-question: {r['question']}\nFindings: {r['summary']}"
        for r in state.get("search_results", [])
    )

    system = SystemMessage(content="""You are a senior research analyst.
Synthesize the provided research findings into a coherent analysis.
Identify key themes, contradictions, gaps, and insights.
Structure your analysis clearly with sections.
Be objective, critical, and thorough.""")

    human = HumanMessage(
        content=f"Original task: {state['task']}\n\nResearch findings:\n{findings}"
    )

    response = await llm.ainvoke([system, human])

    events = state.get("events", []) + [
        {"agent": "analyst", "status": "done", "message": "Synthesized all findings into analysis", "data": None}
    ]

    return {**state, "analysis": response.content, "events": events}
