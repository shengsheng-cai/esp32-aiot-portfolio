import os
import re
import json
import sys
import subprocess
from pathlib import Path
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are an AI agent. Respond with JSON only.

TOOLS:
1. bash(command)   - execute shell command
2. read(file)      - read file content
3. write(file,content) - write content to file
4. finish(answer)  - return final answer and stop

JSON format:
{
  "thought": "your reasoning",
  "action": "bash|read|write|finish",
  "input": "tool input"
}"""

MAX_STEPS = 10


def run_tool(action: str, inp: str) -> str:
    if action == "bash":
        r = subprocess.run(inp, shell=True, capture_output=True, text=True, timeout=10)
        return (r.stdout + r.stderr).strip()
    if action == "read":
        try:
            return Path(inp).read_text()
        except Exception as e:
            return str(e)
    if action == "write":
        parts = inp.split(",", 1)
        if len(parts) == 2:
            Path(parts[0].strip()).write_text(parts[1].strip())
            return "written"
        return "error: expected 'filename,content'"
    return f"unknown action: {action}"


def parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*?\}", text, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise ValueError("cannot parse JSON from response")


def run(goal: str):
    history = [f"System: {SYSTEM_PROMPT}", f"User Goal: {goal}"]

    for step in range(1, MAX_STEPS + 1):
        response = _client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents="\n\n".join(history),
        )
        raw = response.text.strip()

        print(f"\n── Step {step} ──────────────────────")
        try:
            parsed = parse_json(raw)
        except ValueError:
            print(f"JSON parse error:\n{raw}")
            break

        thought = parsed.get("thought", "")
        action = parsed.get("action", "")
        inp = parsed.get("input", "")

        print(f"Thought : {thought}")
        print(f"Action  : {action}({inp})")

        if action == "finish":
            print(f"\nAnswer  : {inp}")
            return

        result = run_tool(action, inp)
        print(f"Result  : {result}")

        history.append(f"Agent: {raw}")
        history.append(f"Observation: {result}")

    print("\n[達到最大步數，停止]")


if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Goal: ")
    run(goal)
