"""Shell execution tool — runs commands inside the podman sandbox."""
from agent.sandbox import runner


def run_command(command: str, timeout: int = 30) -> str:
    """Run a shell command in the sandbox and return formatted output."""
    result = runner.execute(command, timeout=timeout)
    parts = []
    if result["stdout"]:
        parts.append(f"stdout:\n{result['stdout']}")
    if result["stderr"]:
        parts.append(f"stderr:\n{result['stderr']}")
    parts.append(f"exit code: {result['returncode']}")
    return "\n".join(parts)


SCHEMAS = [
    {
        "name": "run_command",
        "description": (
            "Execute a shell command inside the secure sandbox container. "
            "The working directory is /workspace. "
            "Use this to run Python scripts, install packages with uv, run tests, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"},
                "timeout": {"type": "integer", "description": "Timeout in seconds (default 30)"},
            },
            "required": ["command"],
        },
    },
]

DISPATCH = {
    "run_command": run_command,
}
