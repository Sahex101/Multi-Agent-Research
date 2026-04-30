from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm
import json
import re


async def planner_node(state: dict) -> dict:
    """Breaks the research task into focused sub-questions."""
    llm = get_llm()

    system = SystemMessage(content="""You are a research planning expert.
Given a research task, generate 2-4 focused sub-questions that together cover the topic thoroughly.
Return ONLY a JSON array of strings. Example: ["What is X?", "How does Y work?", "What are the implications of Z?"]
No explanation, no markdown — just the raw JSON array.""")

    human = HumanMessage(content=f"Research task: {state['task']}")

    response = await llm.ainvoke([system, human])
    content = response.content.strip()

    # Extract JSON array from response
    match = re.search(r"\[.*?\]", content, re.DOTALL)
    if match:
        try:
            sub_questions = json.loads(match.group())
        except json.JSONDecodeError:
            sub_questions = [state["task"]]
    else:
        sub_questions = [state["task"]]

    # Clamp to max_search_queries
    sub_questions = sub_questions[: state.get("max_search_queries", 3)]

    return {**state, "sub_questions": sub_questions, "events": state.get("events", []) + [
        {"agent": "planner", "status": "done", "message": f"Broke task into {len(sub_questions)} sub-questions", "data": {"sub_questions": sub_questions}}
    ]}
