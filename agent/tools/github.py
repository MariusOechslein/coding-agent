"""GitHub tools using the GitHub REST API."""
import os
import httpx

BASE_URL = "https://api.github.com"


def _headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def github_search_code(query: str, num_results: int = 5) -> str:
    """Search GitHub for code."""
    try:
        response = httpx.get(
            f"{BASE_URL}/search/code",
            headers=_headers(),
            params={"q": query, "per_page": num_results},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as e:
        return f"GitHub API error: {e.response.status_code} {e.response.text}"
    except Exception as e:
        return f"GitHub search failed: {e}"

    items = data.get("items", [])
    if not items:
        return "No code results found."

    lines = []
    for item in items:
        lines.append(f"- {item['repository']['full_name']}: {item['path']}")
        lines.append(f"  {item['html_url']}")
    return "\n".join(lines)


def github_get_file(repo: str, path: str, ref: str = "HEAD") -> str:
    """Get the raw content of a file from a GitHub repository."""
    try:
        response = httpx.get(
            f"{BASE_URL}/repos/{repo}/contents/{path}",
            headers=_headers(),
            params={"ref": ref},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as e:
        return f"GitHub API error: {e.response.status_code} {e.response.text}"
    except Exception as e:
        return f"Failed to get file: {e}"

    import base64
    content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
    return content


SCHEMAS = [
    {
        "name": "github_search_code",
        "description": "Search GitHub for code examples, libraries, or implementations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "GitHub code search query (e.g. 'async retry python')"},
                "num_results": {"type": "integer", "description": "Number of results (default 5)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "github_get_file",
        "description": "Read the contents of a file from a public GitHub repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository in owner/name format (e.g. 'psf/requests')"},
                "path": {"type": "string", "description": "File path within the repo"},
                "ref": {"type": "string", "description": "Branch, tag, or commit SHA (default: HEAD)"},
            },
            "required": ["repo", "path"],
        },
    },
]

DISPATCH = {
    "github_search_code": github_search_code,
    "github_get_file": github_get_file,
}
