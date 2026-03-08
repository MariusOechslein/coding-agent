"""Podman-based sandbox for safe code execution."""
import subprocess
import threading


IMAGE = "python:3.12-slim"
CONTAINER_NAME = "coding-agent-sandbox"
WORKSPACE_HOST = "/Users/mariusoechslein/Desktop/coding-agent/workspace"
WORKSPACE_CONTAINER = "/workspace"
DEFAULT_TIMEOUT = 30  # seconds


def _run(cmd: list[str], timeout: int = 10) -> tuple[str, str, int]:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout, result.stderr, result.returncode


def start():
    """Start the sandbox container if not already running."""
    # Check if already running
    stdout, _, rc = _run(["podman", "inspect", "--format", "{{.State.Status}}", CONTAINER_NAME])
    if rc == 0 and stdout.strip() == "running":
        return

    # Remove stale container if it exists
    subprocess.run(["podman", "rm", "-f", CONTAINER_NAME], capture_output=True)

    # Start fresh container
    _, stderr, rc = _run([
        "podman", "run", "-d",
        "--name", CONTAINER_NAME,
        "-v", f"{WORKSPACE_HOST}:{WORKSPACE_CONTAINER}",
        "-w", WORKSPACE_CONTAINER,
        "--memory", "512m",
        "--cpus", "1",
        IMAGE,
        "sleep", "infinity",
    ], timeout=60)

    if rc != 0:
        raise RuntimeError(f"Failed to start sandbox: {stderr}")

    # Install uv inside container
    _run(["podman", "exec", CONTAINER_NAME,
          "sh", "-c", "pip install uv -q"], timeout=60)


def stop():
    """Stop and remove the sandbox container."""
    subprocess.run(["podman", "rm", "-f", CONTAINER_NAME], capture_output=True)


def execute(command: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Run a shell command inside the sandbox container.
    Returns {"stdout": ..., "stderr": ..., "returncode": ...}
    """
    try:
        result = subprocess.run(
            ["podman", "exec", CONTAINER_NAME, "sh", "-c", command],
            capture_output=True,
            text=True,
            timeout=timeout + 5,  # outer timeout slightly longer
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "returncode": 124,
        }
