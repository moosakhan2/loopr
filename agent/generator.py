"""
generator.py

Generates pytest test functions using watsonx.ai.
Incorporates bug fix history from the context bank to avoid repeating past mistakes.
"""

import re
from typing import List
from . import watsonx_client


def generate_tests(code: str, context: dict) -> list[str]:
    """
    Given the source code of a file and the current context bank,
    return a list of pytest test functions as source code strings.
    Each string is one complete test function, ready to write to a .py file.
    """
    
    # Build the prompt for watsonx.ai
    prompt = _build_prompt(code, context)
    
    # Get the response from watsonx.ai
    response = watsonx_client.complete(prompt)
    
    # Parse the response into individual test functions
    tests = _parse_tests(response)
    
    return tests


def _build_prompt(code: str, context: dict) -> str:
    """
    Construct a detailed prompt for watsonx.ai that includes:
    - The task description
    - The source code to test
    - Bug fix history to avoid repeating mistakes
    - Output format requirements
    """
    
    prompt_parts = [
        "You are an expert Python test engineer. Your task is to generate pytest test functions for the following code.",
        "",
        "# CODE TO TEST:",
        "```python",
        code,
        "```",
        ""
    ]
    
    # Include bug fix history if available
    bug_history = context.get("bug_fix_history", [])
    if bug_history:
        prompt_parts.extend([
            "# IMPORTANT - PAST BUGS TO AVOID:",
            "The following bugs have been found and fixed in previous iterations.",
            "Generate tests that would have caught these bugs, and avoid similar mistakes:",
            ""
        ])
        
        for i, bug_entry in enumerate(bug_history[-5:], 1):  # Last 5 bugs
            bug_desc = bug_entry.get("bug", "Unknown bug")
            fix_desc = bug_entry.get("fix", "Unknown fix")
            file_name = bug_entry.get("file", "Unknown file")
            prompt_parts.append(f"{i}. Bug in {file_name}: {bug_desc}")
            prompt_parts.append(f"   Fix applied: {fix_desc}")
        
        prompt_parts.append("")
    
    # Add requirements
    prompt_parts.extend([
    "# CRITICAL OUTPUT RULES — VIOLATIONS WILL BREAK THE TEST SUITE:",
    "1. Output ONLY raw Python function definitions. Nothing else.",
    "2. NEVER use 'self' as a parameter — these are NOT class methods.",
    "3. NEVER use 'import unittest' or 'class Test'.",
    "4. NEVER indent a def inside another def.",
    "5. NEVER add prose, numbered lists, or commentary outside functions.",
    "6. Every function starts at column 0 with 'def test_'.",
    "7. Every function body is indented exactly 4 spaces.",
    "8. Every function name is unique.",
    "9. Use only plain 'assert' statements — no self.assertEqual.",
    "10. Write maximum 4 functions.",
    "",
    "CORRECT EXAMPLE:",
    "def test_add_positive():",
    "    assert add(2, 3) == 5",
    "",
    "def test_subtract_returns_difference():",
    "    assert subtract(5, 3) == 2",
    "",
    "WRONG EXAMPLE (NEVER DO THIS):",
    "def test_add(self):",
    "    self.assertEqual(add(2,3), 5)",
    "",
    "Now write exactly 4 pytest functions following the CORRECT EXAMPLE format:"
])
    
    return "\n".join(prompt_parts)


def _parse_tests(response: str) -> list[str]:
    """
    Parse the watsonx.ai response to extract individual test functions.
    Returns a list of strings, each containing one complete test function.
    """
    
    # Remove markdown code blocks if present
    response = re.sub(r'```python\s*', '', response)
    response = re.sub(r'```\s*', '', response)
    
    # Split by test function definitions
    # Look for lines that start with "def test_"
    test_pattern = r'(def test_\w+\([^)]*\):.*?)(?=\ndef test_|\Z)'
    matches = re.findall(test_pattern, response, re.DOTALL)
    
    if not matches:
        # Fallback: try to find any function definitions
        test_pattern = r'(def test_.*?)(?=\ndef |\Z)'
        matches = re.findall(test_pattern, response, re.DOTALL)
    
    # Clean up each test function
    tests = []
    seen_names = set()
    for match in matches:
        # Clean up whitespace
        test_func = match.strip()
        
        # Ensure proper indentation (4 spaces for function body)
        lines = test_func.split('\n')
        cleaned_lines = [lines[0]]  # Keep the def line as-is
        
        for line in lines[1:]:
            if line.strip():  # Non-empty line
                # Ensure it has at least 4 spaces of indentation
                if not line.startswith('    '):
                    cleaned_lines.append('    ' + line.lstrip())
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append('')  # Preserve empty lines
        
        test_func = '\n'.join(cleaned_lines)
        
        # Only include if it looks like a valid test function
        if test_func.startswith('def test_') and 'assert' in test_func:
            func_name = test_func.split('(')[0]
            if func_name not in seen_names:
                seen_names.add(func_name)
                tests.append(test_func)
    
    # If we didn't find any tests, raise an error
    if not tests:
        raise RuntimeError(
            f"Failed to parse test functions from watsonx.ai response. "
            f"Response was: {response[:200]}..."
        )
    
    return tests


if __name__ == "__main__":
    # Hardcoded sample for standalone testing
    print("Testing generator.py...")
    print("=" * 70)
    
    # Sample code to generate tests for
    sample_code = '''
def calculate_discount(price, discount_percent):
    """Calculate the final price after applying a discount."""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount

def divide_numbers(a, b):
    """Divide two numbers."""
    return a / b
'''
    
    # Sample context with bug history
    sample_context = {
        "requirements": ["Functions should handle edge cases"],
        "architecture_notes": ["Simple utility functions"],
        "bug_fix_history": [
            {
                "iteration": 1,
                "bug": "divide_numbers crashes with ZeroDivisionError when b=0",
                "fix": "Added check for zero divisor",
                "file": "utils.py"
            },
            {
                "iteration": 2,
                "bug": "calculate_discount allows negative prices",
                "fix": "Added validation for price >= 0",
                "file": "utils.py"
            }
        ]
    }
    
    print("Sample code:")
    print("-" * 70)
    print(sample_code)
    print("-" * 70)
    print()
    
    print("Sample context (bug history):")
    print("-" * 70)
    for bug in sample_context["bug_fix_history"]:
        print(f"  • {bug['bug']}")
    print("-" * 70)
    print()
    
    try:
        print("Generating tests...")
        tests = generate_tests(sample_code, sample_context)
        
        print(f"\n✓ Generated {len(tests)} test functions:\n")
        print("=" * 70)
        
        for i, test in enumerate(tests, 1):
            print(f"\n# Test {i}:")
            print(test)
            print()
        
        print("=" * 70)
        print(f"✓ generator.py is working correctly! Generated {len(tests)} tests.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("  1. You have a .env file with watsonx.ai credentials")
        print("  2. The watsonx_client.py module is working")
        print("  3. You have internet connectivity")

# Made with Bob
