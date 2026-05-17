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
    
    # Parse the concatenated code to extract individual files
    files = _parse_code_files(code)
    
    if not files:
        # Fallback: treat entire code as single file
        files = [{"name": "unknown.py", "content": code}]
    
    fixes = []
    
    # Process each file individually
    for file_info in files:
        file_name = file_info["name"]
        file_code = file_info["content"]
        
        # Build focused prompt for this file
        prompt = _build_prompt(failures, file_code, file_name, context)
        
        # Get response from watsonx.ai
        try:
            response = watsonx_client.complete(prompt)
            
            # Parse the response
            corrected_code, explanation = _parse_fix(response, file_name)
            
            fixes.append({
                "file": file_name,
                "patch": corrected_code,
                "explanation": explanation
            })
        except Exception as e:
            # If this file fails, continue with others
            print(f"   ⚠️  Could not generate fix for {file_name}: {e}")
            continue
    
    if not fixes:
        raise RuntimeError("Failed to generate any fixes from watsonx.ai")
    
    return fixes


def _parse_code_files(code: str) -> list[dict]:
    """
    Parse concatenated code with file headers into individual files.
    Headers look like: # ===== FILE: filename.py =====
    Returns: [{"name": str, "content": str}, ...]
    """
    files = []
    
    # Split by file headers
    file_pattern = r'#\s*={3,}\s*FILE:\s*(\S+)\s*={3,}\s*\n(.*?)(?=#\s*={3,}\s*FILE:|$)'
    matches = re.findall(file_pattern, code, re.DOTALL)
    
    if matches:
        for file_name, file_content in matches:
            files.append({
                "name": file_name.strip(),
                "content": file_content.strip()
            })
    
    return files


def _build_prompt(failures: list[dict], file_code: str, file_name: str, context: dict) -> str:
    """
    Construct a focused prompt for a single file.
    """
    
    prompt_parts = [
        f"You are an expert Python debugger. Fix the code in {file_name} that is causing tests to fail.",
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
        f"# ORIGINAL CODE FOR {file_name}:",
        "```python",
        file_code,
        "```",
        ""
    ])
    
    # Include bug fix history if available
    bug_history = context.get("bug_fix_history", [])
    if bug_history:
        # Filter history for this file
        file_history = [h for h in bug_history if h.get("file") == file_name]
        if file_history:
            prompt_parts.extend([
                f"# PAST FIXES FOR {file_name} TO AVOID:",
                "DO NOT repeat these fixes. Try a different approach:",
                ""
            ])
            
            for i, bug_entry in enumerate(file_history[-3:], 1):  # Last 3 fixes for this file
                bug_desc = bug_entry.get("bug", "Unknown bug")
                fix_desc = bug_entry.get("fix", "Unknown fix")
                prompt_parts.append(f"{i}. Bug: {bug_desc}")
                prompt_parts.append(f"   Fix attempted: {fix_desc}")
            
            prompt_parts.append("")
    
    # Add requirements
    prompt_parts.extend([
        "# REQUIREMENTS:",
        f"1. Analyze the failing tests and fix the bugs in {file_name}",
        "2. Provide the COMPLETE corrected code for this file",
        "3. Include all functions and classes from the original, with fixes applied",
        "4. If past fixes were attempted, try a different approach",
        "",
        f"Return ONLY the complete corrected Python code for {file_name}.",
        "No explanations. No markdown. No file headers. Just raw Python code starting with the first line of the file."
    ])
    
    return "\n".join(prompt_parts)


def _parse_fix(response: str, file_name: str) -> tuple[str, str]:
    """
    Parse the watsonx.ai response for a single file.
    Returns: (corrected_code, explanation)
    """
    
    # Strip markdown code blocks if present
    code_match = re.search(r'```python\s*\n(.*?)\n```', response, re.DOTALL)
    
    if code_match:
        corrected_code = code_match.group(1).strip()
    else:
        # Try without markdown - just take the whole response as code
        corrected_code = response.strip()
        
        # Remove any common non-code prefixes
        for prefix in ["Here is the corrected code:", "Corrected code:", "Fixed code:"]:
            if corrected_code.startswith(prefix):
                corrected_code = corrected_code[len(prefix):].strip()
    
    # Generate a simple explanation
    explanation = f"Fixed bugs in {file_name} based on test failures"
    
    if not corrected_code:
        raise RuntimeError(
            f"Failed to extract corrected code from watsonx.ai response for {file_name}. "
            f"Response was: {response[:300]}..."
        )
    
    return corrected_code, explanation


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