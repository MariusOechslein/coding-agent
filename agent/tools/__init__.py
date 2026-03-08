"""Aggregates all tool schemas and dispatch tables."""
from agent.tools import editor, shell, search, github

SCHEMAS = (
    editor.SCHEMAS
    + shell.SCHEMAS
    + search.SCHEMAS
    + github.SCHEMAS
)

DISPATCH: dict = {
    **editor.DISPATCH,
    **shell.DISPATCH,
    **search.DISPATCH,
    **github.DISPATCH,
}
