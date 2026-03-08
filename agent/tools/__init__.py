"""Aggregates all tool schemas and dispatch tables."""
from agent.tools import editor, shell, search, github, azure_search, blob_storage

SCHEMAS = (
    editor.SCHEMAS
    + shell.SCHEMAS
    + search.SCHEMAS
    + github.SCHEMAS
    + azure_search.SCHEMAS
    + blob_storage.SCHEMAS
)

DISPATCH: dict = {
    **editor.DISPATCH,
    **shell.DISPATCH,
    **search.DISPATCH,
    **github.DISPATCH,
    **azure_search.DISPATCH,
    **blob_storage.DISPATCH,
}
