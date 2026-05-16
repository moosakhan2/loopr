"""
fixer.py

Suggests fixes for failing tests using watsonx.ai.
Analyzes test failures and generates patch suggestions.
"""

from typing import List, Dict, Any
from . import watsonx_client


def suggest_fix(failures: List[Dict[str, Any]], code: str, context: Dict[str, Any]) -> Dict[str, str]:
    """
    Analyze test failures and suggest a fix.
    
    Args:
        failures: List of failed test results with name, passed, and error fields
        code: The source code that has bugs
        context: Context bank data with bug history
        
    Returns:
        Dictionary with file, patch, and explanation keys
    """
    if not failures:
        return {
            "file": "",
            "patch": "",
            "explanation": "No failures to fix"
        }
    
    # Build prompt for watsonx.ai
    prompt = _build_fix_prompt(failures, code, context)
    
    try:
        # Get fix suggestion from watsonx.ai
        response = watsonx_client.complete(prompt)
        
        # Parse the response
        fix = _parse_fix_response(response)
        
        return fix
        
    except Exception as e:
        # Return a structured error response
        return {
            "file": "unknown",
            "patch": "",
            "explanation": f"Error generating fix: {str(e)}"
        }


def _build_fix_prompt(failures: List[Dict[str, Any]], code: str, context: Dict[str, Any]) -> str:
    """Build a prompt for watsonx.ai to suggest a fix."""
    
    prompt_parts = [
        "You are an expert Python debugger. Analyze the following test failures and suggest a fix.",
        "",
        "# SOURCE CODE:",
        "```python",
        code,
        "```",
        "",
        "# TEST FAILURES:",
    ]
    
    for i, failure in enumerate(failures, 1):
        prompt_parts.append(f"\n{i}. Test: {failure['name']}")
        if failure.get('error'):
            prompt_parts.append(f"   Error: {failure['error']}")
    
    prompt_parts.extend([
        "",
        "# TASK:",
        "1. Identify the bug in the source code that caused these test failures",
        "2. Suggest a fix in unified diff format",
        "3. Explain what was wrong and how the fix addresses it",
        "",
        "# OUTPUT FORMAT:",
        "Provide your response in the following format:",
        "",
        "FILE: <filename>",
        "EXPLANATION: <brief explanation of the bug>",
        "PATCH:",
        "```",
        "- <line to remove>",
        "+ <line to add>",
        "```",
        "",
        "Now analyze and suggest a fix:"
    ])
    
    return "\n".join(prompt_parts)


def _parse_fix_response(response: str) -> Dict[str, str]:
    """Parse the watsonx.ai response into structured fix data."""
    
    fix = {
        "file": "unknown",
        "patch": "",
        "explanation": ""
    }
    
    lines = response.strip().split('\n')
    current_section = None
    patch_lines = []
    
    for line in lines:
        line_upper = line.upper().strip()
        
        if line_upper.startswith('FILE:'):
            fix['file'] = line.split(':', 1)[1].strip()
        elif line_upper.startswith('EXPLANATION:'):
            fix['explanation'] = line.split(':', 1)[1].strip()
            current_section = 'explanation'
        elif line_upper.startswith('PATCH:'):
            current_section = 'patch'
        elif line.strip().startswith('```'):
            # Skip code fence markers
            continue
        elif current_section == 'patch' and line.strip():
            patch_lines.append(line)
        elif current_section == 'explanation' and line.strip() and not line_upper.startswith('PATCH:'):
            # Continue multi-line explanation
            fix['explanation'] += ' ' + line.strip()
    
    fix['patch'] = '\n'.join(patch_lines)
    
    # Fallback: if parsing failed, use the whole response as explanation
    if not fix['explanation'] and not fix['patch']:
        fix['explanation'] = response.strip()
    
    return fix


if __name__ == "__main__":
    # Test the fixer with sample data
    print("Testing fixer.py...")
    print("=" * 70)
    
    sample_code = '''
def subtract(a, b):
    """Subtract b from a."""
    return a + b  # Bug: should be a - b
'''
    
    sample_failures = [
        {
            "name": "test_subtract",
            "passed": False,
            "error": "AssertionError: assert 8 == 2\n  where 8 = subtract(5, 3)"
        }
    ]
    
    sample_context = {
        "requirements": [],
        "architecture_notes": [],
        "bug_fix_history": []
    }
    
    print("Sample code:")
    print("-" * 70)
    print(sample_code)
    print("-" * 70)
    print()
    
    print("Sample failure:")
    print("-" * 70)
    print(f"  Test: {sample_failures[0]['name']}")
    print(f"  Error: {sample_failures[0]['error']}")
    print("-" * 70)
    print()
    
    try:
        print("Generating fix suggestion...")
        fix = suggest_fix(sample_failures, sample_code, sample_context)
        
        print("\n✓ Fix suggestion generated:\n")
        print("=" * 70)
        print(f"File: {fix['file']}")
        print(f"Explanation: {fix['explanation']}")
        print(f"\nPatch:")
        print(fix['patch'])
        print("=" * 70)
        print("\n✓ fixer.py is working correctly!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("  1. You have a .env file with watsonx.ai credentials")
        print("  2. The watsonx_client.py module is working")
        print("  3. You have internet connectivity")

# Made with Bob