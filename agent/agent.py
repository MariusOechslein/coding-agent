"""Core agent loop: plan → act → observe → repeat."""
import json
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from agent import tools

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


def _make_client() -> AzureOpenAI:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return AzureOpenAI(
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
        api_version=api_version,
    )


def run(task: str) -> None:
    """Run the agent on a task, streaming output to stdout."""
    client = _make_client()
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    print(f"\n[agent] Starting task: {task}\n")

    for iteration in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=deployment,
            max_tokens=8096,
            tools=tools.SCHEMAS,
            messages=messages,
        )

        choice = response.choices[0]
        message = choice.message

        # Append assistant message to history
        messages.append(message.to_dict())

        # Print any text content
        if message.content and message.content.strip():
            print(message.content)

        # Check stop reason
        if choice.finish_reason == "stop":
            print("\n[agent] Done.")
            break

        if choice.finish_reason != "tool_calls":
            print(f"\n[agent] Unexpected finish reason: {choice.finish_reason}")
            break

        # Execute all tool calls
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)

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

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_text,
            })

    else:
        print(f"\n[agent] Reached max iterations ({MAX_ITERATIONS}).")


def _fmt_input(inp: dict) -> str:
    """Format tool input for display, truncating long values."""
    parts = []
    for k, v in inp.items():
        s = str(v)
        parts.append(f"{k}={s[:80] + '...' if len(s) > 80 else s!r}")
    return ", ".join(parts)
