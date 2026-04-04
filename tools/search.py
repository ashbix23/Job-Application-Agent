"""
search.py — Web search tool powered by Brave Search API.

Used by the agent to research:
  - Company background, mission, recent news
  - Engineering culture, tech stack
  - The specific role / team context
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"

_MAX_RESULTS = 5
_MAX_SNIPPET_LEN = 400  # chars per result, keeps context tight


def web_search(query: str, num_results: int = _MAX_RESULTS) -> dict:
    """
    Run a web search and return summarised results.

    Returns:
        {"success": True,  "results": [...], "query": query}
      | {"success": False, "error": "...",   "query": query}

    Each result:
        {"title": str, "url": str, "snippet": str}
    """
    if not BRAVE_API_KEY:
        return {
            "success": False,
            "error": "BRAVE_API_KEY not set. Add it to your .env file.",
            "query": query,
        }

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY,
    }
    params = {
        "q": query,
        "count": min(num_results, 10),
        "text_decorations": False,
        "search_lang": "en",
    }

    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(BRAVE_ENDPOINT, headers=headers, params=params)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"Brave API HTTP {e.response.status_code}", "query": query}
    except httpx.RequestError as e:
        return {"success": False, "error": f"Network error: {e}", "query": query}

    data = response.json()
    raw_results = data.get("web", {}).get("results", [])

    results = []
    for item in raw_results:
        snippet = item.get("description", "").strip()
        if len(snippet) > _MAX_SNIPPET_LEN:
            snippet = snippet[:_MAX_SNIPPET_LEN] + "..."
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": snippet,
        })

    return {"success": True, "results": results, "query": query}
