"""
fixer.py

Suggests fixes for failing tests using watsonx.ai.
Incorporates bug fix history from the context bank to avoid repeating past mistakes.
"""

import re
from . import watsonx_client


def suggest_fix(failures: list[dict], code: str, context: dict) -> list[dict]:
    """
    Given a list of failing test results, the source code, and context,
    return a list of suggested fixes, one per file:
      [{"file": str, "patch": str, "explanation": str}, ...]
    """
    
    # Build the prompt for watsonx.ai
    prompt = _build_prompt(failures, code, context)
    
    # Get the response from watsonx.ai
    response = watsonx_client.complete(prompt)
    
    # Parse the response into the required format
    fixes = _parse_fix(response, context)
    
    return fixes


def _build_prompt(failures: list[dict], code: str, context: dict) -> str:
    """
    Construct a detailed prompt for watsonx.ai that includes:
    - The failing test results
    - The original source code
    - Bug fix history to avoid repeating mistakes
    - Output format requirements
    """
    
    prompt_parts = [
        "You are an expert Python debugger. Your task is to fix the code that is causing tests to fail.",
        "",
        "# FAILING TESTS:",
    ]
    
    # Add each failing test with its error
    for failure in failures:
        test_name = failure.get("name", "unknown_test")
        error = failure.get("error", "No error message provided")
        prompt_parts.append(f"- {test_name}:")
        prompt_parts.append(f"  Error: {error}")
    
    prompt_parts.extend([
        "",
        "# ORIGINAL CODE:",
        "```python",
        code,
        "```",
        ""
    ])
    
    # Include bug fix history if available
    bug_history = context.get("bug_fix_history", [])
    if bug_history:
        prompt_parts.extend([
            "# IMPORTANT - PAST FIXES TO AVOID:",
            "The following fixes have already been tried in previous iterations.",
            "DO NOT suggest these same fixes again. Try a different approach:",
            ""
        ])
        
        for i, bug_entry in enumerate(bug_history[-5:], 1):  # Last 5 fixes
            bug_desc = bug_entry.get("bug", "Unknown bug")
            fix_desc = bug_entry.get("fix", "Unknown fix")
            file_name = bug_entry.get("file", "Unknown file")
            prompt_parts.append(f"{i}. In {file_name}:")
            prompt_parts.append(f"   Bug: {bug_desc}")
            prompt_parts.append(f"   Fix attempted: {fix_desc}")
        
        prompt_parts.append("")
    
    # Add requirements
    prompt_parts.extend([
        "# REQUIREMENTS:",
        "1. Analyze the failing tests and identify which file(s) need fixing",
        "2. For EACH file that needs changes, provide the COMPLETE corrected code",
        "3. The corrected code should be ready to replace the original file entirely",
        "4. Include all functions and classes from the original, with fixes applied",
        "5. Explain clearly what was wrong and how you fixed it",
        "6. If past fixes were attempted, try a different approach",
        "",
        "# OUTPUT FORMAT:",
        "Provide your response in this EXACT format for each file that needs fixing:",
        "",
        "FILE: calculator.py",
        "EXPLANATION:",
        "[Your explanation of what was wrong in this file and how you fixed it]",
        "CORRECTED_CODE:",
        "```python",
        "[The complete corrected code for calculator.py here]",
        "```",
        "END_FILE",
        "",
        "FILE: string_utils.py",
        "EXPLANATION:",
        "[Your explanation of what was wrong in this file and how you fixed it]",
        "CORRECTED_CODE:",
        "```python",
        "[The complete corrected code for string_utils.py here]",
        "```",
        "END_FILE",
        "",
        "Now provide the fixes:"
    ])
    
    return "\n".join(prompt_parts)


def _parse_fix(response: str, context: dict) -> list[dict]:
    """
    Parse the watsonx.ai response to extract fix information for multiple files.
    Returns a list of dicts: [{"file": str, "patch": str, "explanation": str}, ...]
    """
    
    fixes = []
    
    # Split response by FILE blocks
    # Pattern: FILE: filename ... EXPLANATION: ... CORRECTED_CODE: ... END_FILE
    file_pattern = r'FILE:\s*(\S+)\s*\n.*?EXPLANATION:\s*\n(.*?)CORRECTED_CODE:\s*\n```python\s*\n(.*?)\n```.*?END_FILE'
    matches = re.findall(file_pattern, response, re.DOTALL | re.IGNORECASE)
    
    if matches:
        # Successfully parsed structured format
        for file_name, explanation, code in matches:
            fixes.append({
                "file": file_name.strip(),
                "patch": code.strip(),
                "explanation": explanation.strip()
            })
    else:
        # Fallback: try to parse single-file format (backward compatibility)
        # Extract file name
        file_match = re.search(r'FILE:\s*(\S+)', response, re.IGNORECASE)
        file_name = file_match.group(1).strip() if file_match else "unknown.py"
        
        # Extract explanation
        explanation_match = re.search(
            r'EXPLANATION:\s*\n(.*?)(?=CORRECTED_CODE:|```python|FILE:|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        explanation = explanation_match.group(1).strip() if explanation_match else "Fix applied based on test failures"
        
        # Extract corrected code
        code_match = re.search(r'```python\s*\n(.*?)\n```', response, re.DOTALL)
        
        if code_match:
            corrected_code = code_match.group(1).strip()
        else:
            # Try without markdown
            code_match = re.search(
                r'CORRECTED_CODE:\s*\n(.*?)(?=END_FILE|FILE:|$)',
                response,
                re.DOTALL | re.IGNORECASE
            )
            if code_match:
                corrected_code = code_match.group(1).strip()
            else:
                # Last resort: extract function definitions
                func_pattern = r'(def \w+.*?)(?=\ndef |\Z)'
                functions = re.findall(func_pattern, response, re.DOTALL)
                if functions:
                    corrected_code = '\n\n'.join(functions).strip()
                else:
                    raise RuntimeError(
                        f"Failed to extract corrected code from watsonx.ai response. "
                        f"Response was: {response[:300]}..."
                    )
        
        # Try to infer filename from code if not found
        if file_name == "unknown.py":
            if "calculator" in corrected_code.lower():
                file_name = "calculator.py"
            elif "utils" in corrected_code.lower():
                file_name = "utils.py"
            else:
                # Check bug history
                bug_history = context.get("bug_fix_history", [])
                if bug_history:
                    file_name = bug_history[-1].get("file", "unknown.py")
        
        fixes.append({
            "file": file_name,
            "patch": corrected_code,
            "explanation": explanation
        })
    
    if not fixes:
        raise RuntimeError(
            f"Failed to parse any fixes from watsonx.ai response. "
            f"Response was: {response[:300]}..."
        )
    
    return fixes


if __name__ == "__main__":
    # Hardcoded sample for standalone testing
    print("Testing fixer.py...")
    print("=" * 70)
    
    # Sample failing tests
    sample_failures = [
        {
            "name": "test_divide_by_zero",
            "passed": False,
            "error": "ZeroDivisionError: division by zero at line 8 in divide_numbers(10, 0)"
        },
        {
            "name": "test_negative_discount",
            "passed": False,
            "error": "AssertionError: Expected ValueError for negative discount, but function returned -50.0"
        }
    ]
    
    # Sample buggy code
    sample_code = '''
def calculate_discount(price, discount_percent):
    """Calculate the final price after applying a discount."""
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
                "bug": "Function allows invalid inputs without validation",
                "fix": "Added basic input validation",
                "file": "calculator.py"
            }
        ]
    }
    
    print("Sample failing tests:")
    print("-" * 70)
    for failure in sample_failures:
        print(f"  • {failure['name']}: {failure['error']}")
    print("-" * 70)
    print()
    
    print("Sample buggy code:")
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
        print("Generating fix suggestions...")
        fixes = suggest_fix(sample_failures, sample_code, sample_context)
        
        print(f"\n✓ Generated {len(fixes)} fix suggestion(s)!\n")
        print("=" * 70)
        
        for i, fix in enumerate(fixes, 1):
            print(f"\n# Fix {i}:")
            print(f"File: {fix['file']}")
            print(f"\nExplanation:\n{fix['explanation']}")
            print(f"\nCorrected Code:\n{fix['patch']}")
            print("\n" + "-" * 70)
        
        print("=" * 70)
        print(f"✓ fixer.py is working correctly! Generated {len(fixes)} fix(es).")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("  1. You have a .env file with watsonx.ai credentials")
        print("  2. The watsonx_client.py module is working")
        print("  3. You have internet connectivity")

# Made with Bob