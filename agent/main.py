"""Entry point for the coding agent."""
import sys
import os
from dotenv import load_dotenv
from agent.sandbox import runner
from agent import agent


def main():
    load_dotenv()

    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        print("Coding Agent — powered by Claude")
        print("Enter your task (or 'quit' to exit):\n")
        task = input("> ").strip()
        if task.lower() in ("quit", "exit", "q"):
            return

    if not task:
        print("No task provided.")
        return

    print("[sandbox] Starting podman container...")
    try:
        runner.start()
        print("[sandbox] Ready.\n")
    except Exception as e:
        print(f"[sandbox] Warning: could not start sandbox: {e}")
        print("[sandbox] run_command tool will not work without podman.\n")

    try:
        agent.run(task)
    finally:
        # Leave container running for the session; user can call runner.stop() manually
        pass


if __name__ == "__main__":
    main()
