# CONTRACTS.md

This file defines the shared agreements for the loopr project.
Every AI editor session and every team member codes to these contracts.
Do not change an interface without telling the whole team first.

---

## Project structure

```
agent/
  cli.py             # entry point (Person A)
  loop.py            # orchestrates the iteration (Person A)
  generator.py       # generates tests (Person B)
  runner.py          # runs tests (Person C)
  fixer.py           # suggests fixes (Person B)
  context_bank.py    # reads/writes JSON (Person A)
  watsonx_client.py  # wrapper around watsonx.ai (Person B)

.agent-context.json  # the persistent context bank (auto-created)
sample-repo/         # the codebase under test (Person C)
```

---

## Context bank schema

The file `.agent-context.json` always has this exact shape.
`context_bank.py` is the only module that reads or writes it.

```json
{
  "requirements": [],
  "architecture_notes": [],
  "bug_fix_history": [
    {"iteration": 1, "bug": "...", "fix": "...", "file": "..."}
  ]
}
```

---

## Module interfaces

These are the exact function signatures every module must implement.
Use these as the source of truth — not whatever the AI generates by default.

```python
# watsonx_client.py
def complete(prompt: str) -> str:
    """Send a prompt to watsonx.ai and return the raw text response."""

# generator.py
def generate_tests(code: str, context: dict) -> list[str]:
    """
    Given the source code of a file and the current context bank,
    return a list of pytest test functions as source code strings.
    Each string is one complete test function, ready to write to a .py file.
    """

# runner.py
def run_tests(tests: list[str], target_path: str) -> list[dict]:
    """
    Write each test string to a temp file, run pytest, parse results.
    Returns a list of dicts, one per test:
      {"name": str, "passed": bool, "error": str | None}
    """

# fixer.py
def suggest_fix(failures: list[dict], code: str, context: dict) -> dict:
    """
    Given a list of failing test results, the source code, and context,
    return a suggested fix:
      {"file": str, "patch": str, "explanation": str}
    """

# context_bank.py
def load() -> dict: ...
def save(data: dict) -> None: ...
def append_history(bug: str, fix: str, file: str, iteration: int) -> None: ...
```

---

## Environment variables

All credentials live in `.env` at the repo root. This file is gitignored — never commit it.

```
WATSONX_API_KEY=your_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

---

## Rules

- One module per Bob/AI prompt. Never ask it to build the whole agent at once.
- Always ask for a small test alongside the code.
- If a function signature here conflicts with what the AI generated, fix the AI output — not this file.
- Paste this entire file into Bob's context before starting any task.