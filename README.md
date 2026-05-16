# Agentic Testing Framework

An AI-powered testing framework that uses watsonx.ai to automatically generate, run, and fix tests for your Python code.

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure watsonx.ai credentials:**

Create a `.env` file in the project root (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit `.env` and add your watsonx.ai credentials:
```
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
```

## Usage

### Test the watsonx client

```bash
python -m agent.watsonx_client
```

This will test the connection to watsonx.ai and generate a simple completion.

### Generate tests for sample code

```bash
python -m agent.generator
```

This will:
1. Use a hardcoded sample function (`calculate_discount`)
2. Generate 3-5 pytest test functions using watsonx.ai
3. Print the generated tests to the console

### Use in your code

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

## Project Structure

```
agent/
  __init__.py          # Package initialization
  watsonx_client.py    # watsonx.ai API wrapper
  generator.py         # Test generation logic
  cli.py               # CLI entry point (TODO)
  loop.py              # Orchestration loop (TODO)
  runner.py            # Test execution (TODO)
  fixer.py             # Fix suggestions (TODO)
  context_bank.py      # JSON context storage (TODO)

.env                   # Your credentials (not in git)
.env.example           # Template for credentials
requirements.txt       # Python dependencies
README.md              # This file
```

## Modules

### watsonx_client.py

Wrapper around watsonx.ai API:
- Reads credentials from `.env`
- Exposes `complete(prompt: str) -> str` function
- Handles API client initialization and error handling

### generator.py

Test generation module:
- Implements `generate_tests(code: str, context: dict) -> List[str]`
- Builds prompts that ask watsonx for 3-5 pytest functions
- Parses LLM response to extract individual test functions
- Returns list of test function strings

## Next Steps

The following modules are planned but not yet implemented:
- `runner.py` - Execute generated tests and collect results
- `fixer.py` - Suggest fixes for failing tests
- `context_bank.py` - Manage context storage in `.agent-context.json`
- `loop.py` - Orchestrate the test-fix iteration cycle
- `cli.py` - Command-line interface for the framework

## License

MIT