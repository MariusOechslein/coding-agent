"""Core agent loop: plan → act → observe → repeat."""
import json
import anthropic
from agent import tools

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 50

SYSTEM_PROMPT = """\
You are an expert coding agent. When given a task:

1. PLAN first: think through what needs to be done step by step before writing any code.
2. ACT: use the available tools to implement the plan.
3. VERIFY: run the code to confirm it works. Fix any errors.
4. REPORT: summarize what you built and how to use it.

Available workspace: all files you create go into /workspace (accessible as relative paths).
Code execution runs inside a secure sandbox. Use `uv` to manage Python dependencies.

Be thorough but efficient. Prefer simple, working solutions.
"""


def run(task: str) -> None:
    """Run the agent on a task, streaming output to stdout."""
    client = anthropic.Anthropic()
    messages: list[dict] = [{"role": "user", "content": task}]

    print(f"\n[agent] Starting task: {task}\n")

    for iteration in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=8096,
            system=SYSTEM_PROMPT,
            tools=tools.SCHEMAS,
            messages=messages,
        )

        # Append assistant response to history
        messages.append({"role": "assistant", "content": response.content})

        # Print any text blocks
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(block.text)

        # Check stop reason
        if response.stop_reason == "end_turn":
            print("\n[agent] Done.")
            break

        if response.stop_reason != "tool_use":
            print(f"\n[agent] Unexpected stop reason: {response.stop_reason}")
            break

        # Execute all tool calls
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input
            print(f"\n[tool] {tool_name}({_fmt_input(tool_input)})")

            handler = tools.DISPATCH.get(tool_name)
            if handler is None:
                result_text = f"Error: unknown tool '{tool_name}'"
            else:
                try:
                    result_text = handler(**tool_input)
                except Exception as e:
                    result_text = f"Error executing {tool_name}: {e}"

            # Truncate very long outputs to avoid blowing the context window
            if len(result_text) > 8000:
                result_text = result_text[:8000] + "\n... [truncated]"

            print(f"[result] {result_text[:200]}{'...' if len(result_text) > 200 else ''}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result_text,
            })

        messages.append({"role": "user", "content": tool_results})

    else:
        print(f"\n[agent] Reached max iterations ({MAX_ITERATIONS}).")


def _fmt_input(inp: dict) -> str:
    """Format tool input for display, truncating long values."""
    parts = []
    for k, v in inp.items():
        s = str(v)
        parts.append(f"{k}={s[:80] + '...' if len(s) > 80 else s!r}")
    return ", ".join(parts)
