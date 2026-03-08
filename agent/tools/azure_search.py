"""Azure AI Search tool — queries a search index using DefaultAzureCredential."""
import os
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential


def _make_client() -> SearchClient:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    index = os.environ["AZURE_SEARCH_INDEX_NAME"]
    # Prefer API key if set (useful for local dev), otherwise use DefaultAzureCredential
    api_key = os.environ.get("AZURE_SEARCH_API_KEY")
    credential = AzureKeyCredential(api_key) if api_key else DefaultAzureCredential()
    return SearchClient(endpoint=endpoint, index_name=index, credential=credential)


def search_documents(query: str, num_results: int = 5) -> str:
    """Search the Azure AI Search index and return formatted results."""
    try:
        client = _make_client()
    except KeyError as e:
        return f"Error: missing environment variable {e}"

    try:
        results = client.search(search_text=query, top=num_results)
    except Exception as e:
        return f"Search error: {e}"

    lines = []
    for i, doc in enumerate(results, 1):
        # Extract common field names; fall back gracefully if index schema differs
        title = doc.get("title") or doc.get("name") or doc.get("id", f"Document {i}")
        content = doc.get("content") or doc.get("chunk") or doc.get("text") or ""
        source = doc.get("source") or doc.get("url") or doc.get("filepath") or ""
        score = doc.get("@search.score", "")

        lines.append(f"[{i}] {title}" + (f" (score: {score:.3f})" if score else ""))
        if source:
            lines.append(f"    Source: {source}")
        if content:
            snippet = content[:500].replace("\n", " ")
            lines.append(f"    {snippet}{'...' if len(content) > 500 else ''}")
        lines.append("")

    return "\n".join(lines) if lines else "No results found."


SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": (
                "Search the knowledge base for documents relevant to a query. "
                "Use this to find information, background context, or source material "
                "before answering questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default 5)",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

DISPATCH = {
    "search_documents": search_documents,
}
