# 🔁 Loopr

> A recursive AI-powered testing agent that finds bugs, suggests fixes, and loops until your codebase is clean.

Built with IBM Bob. Powered by watsonx.ai. Works with any language.

---

## The Problem

Writing tests is slow. Fixing bugs is slower. And doing both repeatedly until you hit a coverage threshold? Nobody has time for that.

Existing tools generate tests once and stop. They don't fix failures. They don't learn from your codebase. They don't remember what they already tried.

**Loopr does.**

---

## How It Works

Loopr enters a recursive loop:

1. **Reads** your codebase and understands intent — not just syntax
2. **Generates** tests (unit, black box, white box) based on your code and requirements
3. **Runs** your test suite and collects pass/fail results
4. **Suggests** targeted fixes for failing tests
5. **Waits for your approval** before applying any patch
6. **Repeats** until your coverage threshold is met

Every bug found, every fix applied, and every decision made is stored in a local **context bank** — so Loopr never repeats the same mistake and gets smarter about your codebase over time.

```
🔍 Reading codebase...
📝 Generating tests... (12 new tests)
🧪 Running tests... 6 passed, 6 failed
🔧 Suggested fix for auth.py line 42:
   - if user.token == None
   + if user.token is None

   Apply fix? (y/n/skip): y

🔄 Re-running tests... 10 passed, 2 failed
🔧 Fixing remaining 2...
✅ All tests passing — coverage at 87%
🎉 Loopr satisfied. Done in 4 cycles.
```

---

## Installation

```bash
pip install loopr
```

---

## Quick Start

**1. Initialize Loopr in your project:**
```bash
loopr init
```
This creates a `loopr.json` context bank in your project root. Fill in your project description, requirements, and test command. Loopr uses this to understand what your code is *supposed* to do.

**2. Run the recursive loop:**
```bash
loopr run --coverage 85
```

**3. Review a summary report:**
```bash
loopr report
```

---

## CLI Options

```bash
loopr run [options]

Options:
  --coverage INT      Target coverage threshold (default: 85)
  --strict            Sets coverage target to 90%
  --dry-run           Suggest fixes without applying them
  --auto-approve      Apply all fixes without prompting
  --lang TEXT         Hint the primary language (e.g. python, javascript)
  --test-cmd TEXT     Override the test command (e.g. "npm test", "pytest")
```

---

## Context Bank

Loopr stores a `loopr.json` file in your project:

```json
{
  "project": "My API",
  "description": "A REST API for user authentication",
  "requirements": [
    "Users must be able to log in with email and password",
    "Tokens expire after 24 hours"
  ],
  "test_command": "pytest",
  "bugs_found": [],
  "fixes_applied": [],
  "patterns": []
}
```

This file persists across sessions — Loopr remembers what it already tried so it doesn't repeat the same fixes.

---

## Supported Test Runners

Loopr works with any test runner out of the box:

| Language | Test Runner |
|----------|-------------|
| Python | `pytest`, `unittest` |
| JavaScript | `jest`, `mocha`, `vitest` |
| TypeScript | `jest`, `vitest` |
| Java | `JUnit`, `mvn test` |
| Go | `go test` |
| Ruby | `rspec` |
| Any | Custom command via `--test-cmd` |

---

## Built With IBM Bob

Loopr was built using **IBM Bob** as the AI development partner throughout the entire development process. Bob's full repository context awareness was used to architect, implement, and refine the recursive loop logic, context bank design, and watsonx.ai integration.

All Bob task session reports are available in the `/bob_sessions` folder.

**Powered at runtime by IBM watsonx.ai** — the Granite model handles test generation, failure analysis, and fix suggestion at every step of the loop.

---

## Example: Testing a Node.js Project

```bash
cd my-express-app
loopr init
# fill in loopr.json with your project details
loopr run --coverage 85 --test-cmd "npm test"
```

## Example: Testing a Python Project

```bash
cd my-fastapi-app
loopr init
loopr run --coverage 90 --strict
```

---

## License

MIT
