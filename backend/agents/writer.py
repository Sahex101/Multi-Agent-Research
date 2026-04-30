from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm


async def writer_node(state: dict) -> dict:
    """Writes the final structured research report in Markdown."""
    llm = get_llm()

    all_sources = []
    for r in state.get("search_results", []):
        all_sources.extend(r.get("sources", []))
    unique_sources = list(dict.fromkeys(all_sources))  # deduplicate, preserve order

    sources_block = "\n".join(f"- {url}" for url in unique_sources)

    system = SystemMessage(content="""You are a professional research writer.
Write a comprehensive, well-structured research report in Markdown based on the analysis provided.

Use this structure:
# [Descriptive Report Title]

## Executive Summary
(2-3 sentence overview)

## Key Findings
(Bullet points of most important facts)

## Detailed Analysis
(Multiple subsections with depth)

## Conclusions
(What this means, actionable insights)

## Sources
(Leave a placeholder — sources will be appended)

Be informative, professional, and clear. Use headers, bullet points, and **bold** for emphasis.""")

    human = HumanMessage(
        content=f"Task: {state['task']}\n\nAnalysis:\n{state.get('analysis', '')}"
    )

    response = await llm.ainvoke([system, human])

    # Append sources section
    report = response.content
    if "## Sources" in report:
        report = report[: report.index("## Sources")]
    report = report.rstrip() + f"\n\n## Sources\n{sources_block}"

    events = state.get("events", []) + [
        {"agent": "writer", "status": "done", "message": "Final report written", "data": None}
    ]

    return {**state, "final_report": report, "events": events}
