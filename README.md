# 🔁 Loopr - Recursive Testing Agent

An AI-powered testing framework that uses watsonx.ai to automatically generate, run, and fix tests for your Python code. Loopr iteratively finds bugs, suggests fixes, and loops until your codebase is clean.

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd loopr
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

Required packages:
- `pytest` - Test framework
- `pytest-json-report` - JSON output for test results
- `python-dotenv` - Environment variable management
- `requests` - HTTP client for watsonx.ai API

3. **Configure watsonx.ai credentials:**

Create a `.env` file in the project root (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit `.env` and add your watsonx.ai credentials:
```env
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### Run End-to-End

Run the complete testing loop on your codebase:

```bash
python -m agent.cli ./path/to/your/project
```

Example with the included sample repository:
```bash
python -m agent.cli ./sample-repo
```

**CLI Options:**
```bash
python -m agent.cli ./sample-repo --coverage 85 --max-iterations 3 --verbose
```

- `--coverage` - Target coverage threshold (default: 85)
- `--max-iterations` - Maximum number of iterations (default: 3)
- `--dry-run` - Suggest fixes without applying them
- `--auto-approve` - Apply all fixes without prompting
- `--verbose` / `-v` - Enable verbose output

## 📖 Usage Examples

### Test Individual Modules

**Test the watsonx.ai client:**
```bash
python -m agent.watsonx_client
```

**Test the test generator:**
```bash
python -m agent.generator
```

**Test the test runner:**
```bash
python -m agent.runner
```

**Test the context bank:**
```bash
python -m agent.context_bank
```

**Test the orchestration loop:**
```bash
python -m agent.loop
```

### Use as a Library

```python
from agent import generate_tests

# Your code to test
code = '''
def add(a, b):
    return a + b
'''

# Context (optional)
context = {
    "requirements": ["Function should handle integers and floats"],
    "architecture_notes": [],
    "bug_fix_history": []
}

# Generate tests
tests = generate_tests(code, context)

# Print generated tests
for i, test in enumerate(tests, 1):
    print(f"Test {i}:")
    print(test)
    print()
```

## 📁 Project Structure

```
loopr/
├── agent/
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # CLI entry point ✅
│   ├── loop.py              # Orchestration loop ✅
│   ├── generator.py         # Test generation ✅
│   ├── runner.py            # Test execution ✅
│   ├── fixer.py             # Fix suggestions (TODO)
│   ├── context_bank.py      # JSON context storage ✅
│   └── watsonx_client.py    # watsonx.ai API wrapper ✅
├── sample-repo/
│   ├── calculator.py        # Sample code with bugs
│   └── tests/               # Generated tests go here
├── .agent-context.json      # Context bank (auto-generated)
├── .env                     # Your credentials (not in git)
├── .env.example             # Template for credentials
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## 🔧 Module Details

### cli.py
Command-line interface that:
- Parses arguments (path, coverage, max-iterations, etc.)
- Validates target path
- Calls the orchestration loop
- Handles errors and user interrupts

### loop.py
Orchestrates the testing cycle:
- Loads context bank
- Generates tests using watsonx.ai
- Runs tests with pytest
- Suggests fixes for failures
- Updates context bank with bug history

### generator.py
Test generation using watsonx.ai:
- Implements `generate_tests(code: str, context: dict) -> List[str]`
- Builds prompts with bug history context
- Parses LLM response into individual test functions
- Returns list of pytest test function strings

### runner.py
Test execution engine:
- Implements `run_tests(tests: List[str], target_path: str) -> List[dict]`
- Writes tests to temporary files in `target_path/tests/`
- Runs pytest with `--json-report` flag
- Parses results into structured format: `{"name": str, "passed": bool, "error": str | None}`
- Handles timeouts and execution errors

### context_bank.py
Persistent memory management:
- Implements `load()`, `save()`, and `append_history()` functions
- Manages `.agent-context.json` file
- Stores requirements, architecture notes, and bug fix history
- Auto-creates file with empty schema if missing

### watsonx_client.py
watsonx.ai API wrapper:
- Implements `complete(prompt: str) -> str`
- Handles IBM Cloud IAM authentication
- Uses `ibm/granite-3-8b-instruct` model
- Manages API errors and timeouts

### fixer.py (TODO)
Fix suggestion engine:
- Will implement `suggest_fix(failures: List[dict], code: str, context: dict) -> dict`
- Will analyze test failures and suggest code fixes
- Will return patch format with explanation

## 🧪 Sample Repository

The `sample-repo/` directory contains a sample calculator module with intentional bugs for testing:

**calculator.py** - 5 functions with 3 bugs:
1. `subtract(a, b)` - Returns `a + b` instead of `a - b`
2. `divide(a, b)` - Doesn't handle division by zero
3. `power(a, b)` - Uses `*` instead of `**`

Run the agent on it:
```bash
python -m agent.cli ./sample-repo
```

## 📊 Context Bank Schema

The `.agent-context.json` file stores:

```json
{
  "requirements": [],
  "architecture_notes": [],
  "bug_fix_history": [
    {
      "iteration": 1,
      "bug": "Description of the bug",
      "fix": "Description of the fix",
      "file": "path/to/file.py"
    }
  ]
}
```

This context is used to:
- Inform test generation (avoid past mistakes)
- Track bug patterns over iterations
- Improve fix suggestions

## 🐛 Troubleshooting

**"WATSONX_API_KEY not found in .env file"**
- Make sure you created a `.env` file with your credentials
- Check that the file is in the project root directory

**"Failed to get IAM token"**
- Verify your API key is correct
- Check your internet connection
- Ensure you have access to IBM Cloud

**"pytest: command not found"**
- Install pytest: `pip install pytest pytest-json-report`

**Tests not running**
- Ensure your target directory has Python files
- Check that the path is correct
- Try running with `--verbose` flag for more details

## 📝 Development Status

### ✅ Completed
- CLI entry point with argument parsing
- Context bank (JSON storage)
- Test runner with pytest integration
- Test generator with watsonx.ai
- Orchestration loop (using mocks for Sprint 1)
- watsonx.ai client wrapper
- Sample repository with intentional bugs

### 🚧 In Progress
- Integration of real runner.py into loop.py
- Integration of real generator.py into loop.py

### 📋 TODO
- Fix suggester module (fixer.py)
- Multi-iteration loop with fix application
- Coverage tracking
- Interactive fix approval

## 🤝 Contributing

This project was built with IBM watsonx.ai and follows the agentic testing pattern.

## 📄 License

MIT

---

**Made with Bob** 🤖