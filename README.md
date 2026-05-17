# Loopr 🔁

> A recursive AI-powered testing agent that finds bugs, suggests fixes, applies them, and loops until your codebase is clean.

Built with **IBM Bob**. Powered by **IBM watsonx.ai**.

---

## The Problem

Writing tests is slow. Fixing bugs is slower. And doing both repeatedly until everything passes? Nobody has time for that.

Existing tools generate tests once and stop. They don't fix failures. They don't learn from your codebase. They don't remember what they already tried.

**Loopr does.**

---

## How It Works

Loopr enters a recursive loop:

1. **Reads** all Python files in your target repository
2. **Generates** pytest test functions using IBM watsonx.ai (Granite model)
3. **Runs** the tests and collects pass/fail results
4. **Suggests** targeted fixes for failing tests — one fix per file
5. **Shows** a colored diff of proposed changes and asks for your approval
6. **Applies** the fix to the actual file if approved
7. **Repeats** until all tests pass or max iterations reached

Every bug found and every fix applied is stored in a local **context bank** (`.agent-context.json`) — so Loopr never repeats the same mistake and gets smarter about your codebase over time.

---

## Demo

```
🔄 ITERATION 1/3
📝 Generating tests...    Generated 4 tests
🧪 Running tests...       ✅ 3 passed  ❌ 1 failed

🔍 FIX SUGGESTION 1/2
📁 File: calculator.py
💡 subtract() was returning a+b instead of a-b

📋 Proposed changes:
--- original/calculator.py
+++ fixed/calculator.py
-    return a + b  # BUG
+    return a - b  # FIX

❓ Apply this fix? (y/n/skip): y
✅ Fix applied to sample-repo/calculator.py

🔄 ITERATION 2/3
🧪 Running tests...       ✅ 6 passed  ❌ 0 failed
🎉 All tests passing! Exiting loop.
```

---

## Installation

**Prerequisites:**
- Python 3.10+
- IBM watsonx.ai credentials (API key + Project ID)

**Install:**
```bash
git clone https://github.com/moosakhan2/loopr
cd loopr
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

**Configure credentials:**

Create a `.env` file in the root:
```
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

---

## Usage

```bash
loopr ./path/to/your/repo
```

Loopr will automatically:
- Discover all Python files in the directory
- Generate tests, run them, suggest and apply fixes
- Ask before applying any change
- Remember what it fixed for smarter future runs

**Options** (coming soon):
```bash
loopr run --coverage 85    # Target coverage threshold
loopr run --max-iter 5     # Max iterations (default: 3)
loopr run --auto-approve   # Apply all fixes without prompting
```

---

## Architecture

```
agent/
  cli.py             # Entry point — parses args, calls loop
  loop.py            # Recursive orchestration loop
  generator.py       # Generates pytest functions via watsonx.ai
  runner.py          # Runs pytest, parses results
  fixer.py           # Suggests fixes via watsonx.ai (one call per file)
  context_bank.py    # Reads/writes .agent-context.json
  watsonx_client.py  # IBM watsonx.ai API wrapper with IAM auth
.agent-context.json  # Persistent memory across runs
sample-repo/         # Example buggy codebase for demo
```

**The memory loop:**

```
Run 1: 0 bug fixes known → generates basic tests → finds bugs → fixes applied
Run 2: 2 bug fixes known → generates smarter tests → finds fewer bugs
Run 3: all tests pass → exits
```

---

## Built With IBM Bob

Loopr was designed and built using **IBM Bob** as the AI development partner throughout the entire process. Bob's full repository context awareness was used to architect, implement, and refine every module.

All Bob task session reports are in the `/bob_sessions` folder.

**Powered at runtime by IBM watsonx.ai** — the Granite model (`ibm/granite-3-8b-instruct`) handles test generation, failure analysis, and fix suggestion at every iteration.

---

## Example: Running Against the Sample Repo

```bash
# Reset the sample repo to its buggy state
cd loopr

# Run Loopr
loopr ./sample-repo

# Watch it find and fix bugs in calculator.py and string_utils.py
# across multiple iterations, getting smarter each time
```

---

## License

MIT
