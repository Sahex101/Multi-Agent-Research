from langgraph.graph import StateGraph, END, START
from typing import TypedDict
from agents.planner import planner_node
from agents.researcher import researcher_node
from agents.analyst import analyst_node
from agents.writer import writer_node


class ResearchState(TypedDict):
    task: str
    max_search_queries: int
    sub_questions: list[str]
    search_results: list[dict]
    analysis: str
    final_report: str
    events: list[dict]


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("writer", writer_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "writer")
    graph.add_edge("writer", END)

    return graph.compile()


research_graph = build_graph()
