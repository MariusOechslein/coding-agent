"""Web search tool using Brave Search API."""
import os
import httpx


API_URL = "https://api.search.brave.com/res/v1/web/search"


def web_search(query: str, num_results: int = 5) -> str:
    """Search the web and return formatted results."""
    api_key = os.environ.get("SEARCH_API_KEY")
    if not api_key:
        return "Error: SEARCH_API_KEY not set in environment."

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {"q": query, "count": num_results}

    try:
        response = httpx.get(API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as e:
        return f"Search API error: {e.response.status_code} {e.response.text}"
    except Exception as e:
        return f"Search failed: {e}"

    results = data.get("web", {}).get("results", [])
    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r.get('title', '')}")
        lines.append(f"   URL: {r.get('url', '')}")
        lines.append(f"   {r.get('description', '')}")
        lines.append("")

    return "\n".join(lines)


SCHEMAS = [
    {
        "name": "web_search",
        "description": "Search the web for information. Use this to look up documentation, find libraries, research error messages, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results to return (default 5)"},
            },
            "required": ["query"],
        },
    },
]

DISPATCH = {
    "web_search": web_search,
}
