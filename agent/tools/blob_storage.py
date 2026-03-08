"""Azure Blob Storage tool — fetches and extracts text from documents."""
import io
import os

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient


def fetch_document(path: str, max_chars: int = 10000) -> str:
    """Download a blob by its relative path and return extracted text."""
    try:
        account_url = os.environ["AZURE_STORAGE_ACCOUNT_URL"]
        container = os.environ["AZURE_STORAGE_CONTAINER_NAME"]
    except KeyError as e:
        return f"Error: missing environment variable {e}"

    if not path.endswith(".pdf"):
        ext = path.rsplit(".", 1)[-1] if "." in path else "unknown"
        return f"Unsupported file type '.{ext}'. Only PDF is currently supported."

    try:
        client = BlobClient(
            account_url=account_url,
            container_name=container,
            blob_name=path,
            credential=DefaultAzureCredential(),
        )
        data = client.download_blob().readall()
    except Exception as e:
        return f"Error downloading blob '{path}': {e}"

    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages).strip()
    except Exception as e:
        return f"Error extracting PDF text from '{path}': {e}"

    if not text:
        return f"No extractable text found in '{path}' (may be a scanned/image PDF)."

    if len(text) > max_chars:
        text = text[:max_chars] + f"\n\n... [truncated — {len(text)} total chars]"

    return text


SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_document",
            "description": (
                "Download and read the full text of a document from Azure Blob Storage. "
                "Use this when a search result snippet is not sufficient and you need the "
                "complete document content. The path comes from the search index result."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path of the file within the storage container, as returned by the search index",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum characters to return (default 10000)",
                    },
                },
                "required": ["path"],
            },
        },
    },
]

DISPATCH = {
    "fetch_document": fetch_document,
}
