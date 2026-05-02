import asyncio
import logging
from duckduckgo_search import DDGS
from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm, settings

logger = logging.getLogger(__name__)


def _tavily_search(query: str, max_results: int = 4) -> list[dict]:
    """Search using Tavily API — reliable, purpose-built for AI agents."""
    from tavily import TavilyClient
    client = TavilyClient(api_key=settings.tavily_api_key)
    resp = client.search(query, max_results=max_results)
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")}
        for r in resp.get("results", [])
    ]


def _ddg_search(query: str, max_results: int = 4) -> list[dict]:
    """DuckDuckGo search — may be rate-limited."""
    try:
        with DDGS() as ddgs:
            return [
                {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
                for r in ddgs.text(query, max_results=max_results)
            ]
    except Exception as e:
        logger.warning(f"DuckDuckGo failed: {e}")
        return []


def _wikipedia_search(query: str, max_results: int = 4) -> list[dict]:
    """Wikipedia full-text search — always free, no key, never rate-limited."""
    import wikipediaapi
    import urllib.request
    import json
    import urllib.parse
    import re

    wiki = wikipediaapi.Wikipedia("MultiAgentResearch/1.0", "en")

    # Strip question words and common filler to extract search keywords
    stopwords = {"what", "is", "are", "how", "does", "why", "when", "where",
                 "which", "who", "and", "or", "the", "a", "an", "in", "of",
                 "for", "to", "do", "use", "used", "explain", "describe",
                 "tell", "me", "about", "specific", "problems", "compared"}
    keywords = " ".join(w for w in query.split() if w.lower() not in stopwords)
    # Remove HTML-looking fragments and limit length
    search_q = re.sub(r"[^\w\s\-]", " ", keywords).strip()[:100] or query[:80]

    results = []
    seen_titles: set[str] = set()

    try:
        url = (
            "https://en.wikipedia.org/w/api.php?"
            + urllib.parse.urlencode({
                "action": "query",
                "list": "search",
                "srsearch": search_q,
                "srlimit": max_results + 2,
                "format": "json",
                "utf8": 1,
            })
        )
        req = urllib.request.Request(url, headers={"User-Agent": "MultiAgentResearch/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        titles = [r["title"] for r in data.get("query", {}).get("search", [])]
    except Exception as e:
        logger.warning(f"Wikipedia search failed: {e}")
        titles = []

    for title in titles:
        if len(results) >= max_results or title in seen_titles:
            continue
        seen_titles.add(title)
        page = wiki.page(title)
        if page.exists():
            results.append({
                "title": page.title,
                "url": page.fullurl,
                "snippet": page.summary[:700],
            })

    return results


def web_search(query: str, max_results: int = 4) -> list[dict]:
    """3-tier search: Tavily (best) → DuckDuckGo → Wikipedia (guaranteed)."""
    # Tier 1: Tavily
    if settings.tavily_api_key:
        try:
            results = _tavily_search(query, max_results)
            if results:
                logger.info(f"Tavily: {len(results)} results for '{query[:50]}'")
                return results
        except Exception as e:
            logger.warning(f"Tavily failed: {e}")

    # Tier 2: DuckDuckGo
    results = _ddg_search(query, max_results)
    if results:
        logger.info(f"DuckDuckGo: {len(results)} results for '{query[:50]}'")
        return results

    # Tier 3: Wikipedia (always works)
    logger.info(f"Falling back to Wikipedia for '{query[:50]}'")
    return _wikipedia_search(query, max_results)


async def researcher_node(state: dict) -> dict:
    """Searches the web for each sub-question and summarizes findings."""
    llm = get_llm()
    search_results = []
    events = list(state.get("events", []))
    sub_questions = state.get("sub_questions", [])
    loop = asyncio.get_event_loop()

    for question in sub_questions:
        raw = await loop.run_in_executor(None, web_search, question)

        if not raw:
            events.append({
                "agent": "researcher",
                "status": "warning",
                "message": f'No results found for: "{question}"',
                "data": {"sources_found": 0, "sources": []},
            })
            continue

        context = "\n\n".join(
            f"Source: {r['url']}\nTitle: {r['title']}\n{r['snippet']}" for r in raw
        )
        system = SystemMessage(content="""You are a research analyst. 
Given a question and web search results, extract and summarize the most relevant factual information.
Be concise but thorough. Include key facts, numbers, and insights. Cite sources by URL.""")
        human = HumanMessage(content=f"Question: {question}\n\nSearch results:\n{context}")
        response = await llm.ainvoke([system, human])

        result = {
            "question": question,
            "summary": response.content,
            "sources": [r["url"] for r in raw],
        }
        search_results.append(result)
        events.append({
            "agent": "researcher",
            "status": "done",
            "message": f'Researched: "{question}"',
            "data": {"sources_found": len(raw), "sources": result["sources"]},
        })

    return {**state, "search_results": search_results, "events": events}
