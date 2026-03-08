# Coding Agent

A CLI coding agent powered by Claude that plans, writes, and verifies code inside a secure sandbox.

## How it works

The agent follows a loop:
1. **Plan** — thinks through the task step by step
2. **Act** — uses tools to implement the plan (write files, run commands, search the web, etc.)
3. **Verify** — runs the code and fixes errors
4. **Report** — summarizes what was built

Code execution happens inside a [Podman](https://podman.io/) container for isolation.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)
- [Podman](https://podman.io/) (for sandboxed code execution)
- Anthropic API key

## Setup

```bash
# Install dependencies
uv sync

# Copy and fill in your credentials
cp .env.example .env
```

Edit `.env` and add your API key:
```
ANTHROPIC_API_KEY=your_key_here
```

## Usage

```bash
# Interactive mode
uv run coding-agent

# Pass a task directly
uv run coding-agent "write a Python script that sorts a CSV file by the second column"
```

## Tools available to the agent

| Tool | Description |
|------|-------------|
| `run_command` | Execute shell commands in the sandbox |
| `read_file` / `write_file` | Read and write files in `/workspace` |
| `search` | Web search |
| `github` | Interact with GitHub |
