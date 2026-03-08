"""File editor tools — all paths are relative to workspace/."""
import os

WORKSPACE = "/Users/mariusoechslein/Desktop/coding-agent/workspace"


def _abs(path: str) -> str:
    # Strip leading slash/dot to keep everything inside workspace
    clean = path.lstrip("/").lstrip("./")
    return os.path.join(WORKSPACE, clean)


def read_file(path: str) -> str:
    """Read a file from the workspace."""
    try:
        with open(_abs(path)) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file in the workspace (creates directories as needed)."""
    abs_path = _abs(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w") as f:
        f.write(content)
    return f"Written {len(content)} bytes to {path}"


def edit_file(path: str, old_string: str, new_string: str) -> str:
    """Replace old_string with new_string in a file."""
    abs_path = _abs(path)
    try:
        with open(abs_path) as f:
            content = f.read()
    except FileNotFoundError:
        return f"Error: file not found: {path}"

    if old_string not in content:
        return f"Error: string not found in {path}"

    new_content = content.replace(old_string, new_string, 1)
    with open(abs_path, "w") as f:
        f.write(new_content)
    return f"Edited {path}"


def list_files(path: str = ".") -> str:
    """List files and directories in a workspace path."""
    abs_path = _abs(path)
    try:
        entries = []
        for root, dirs, files in os.walk(abs_path):
            # Make root relative to workspace
            rel_root = os.path.relpath(root, WORKSPACE)
            for d in sorted(dirs):
                entries.append(f"{rel_root}/{d}/")
            for f in sorted(files):
                entries.append(f"{rel_root}/{f}")
        return "\n".join(entries) if entries else "(empty)"
    except FileNotFoundError:
        return f"Error: path not found: {path}"


SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path relative to workspace root"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file in the workspace. Creates the file and any parent directories if they don't exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path relative to workspace root"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace an exact string in a file. Use this for targeted edits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path relative to workspace root"},
                    "old_string": {"type": "string", "description": "The exact string to replace"},
                    "new_string": {"type": "string", "description": "The replacement string"},
                },
                "required": ["path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files and directories in the workspace (or a subdirectory).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path relative to workspace root (default: '.')"},
                },
            },
        },
    },
]

DISPATCH = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "list_files": list_files,
}
