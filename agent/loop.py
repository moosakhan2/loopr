"""
Loop controller module - orchestrates the recursive testing loop.

This module coordinates the flow: generator → runner → fixer.
For Sprint 1, uses mock functions. Real implementations will be integrated in Sprint 2.
"""

from typing import Any
from agent.context_bank import load, save


def _mock_generate_tests(code: str, context: dict[str, Any]) -> list[str]:
    """
    Mock test generator for Sprint 1.
    
    Args:
        code: Source code to generate tests for
        context: Context bank data
        
    Returns:
        List of test function strings
    """
    return [
        "def test_addition():\n    assert 2 + 2 == 4",
        "def test_subtraction():\n    assert 5 - 3 == 2",
        "def test_multiplication():\n    assert 3 * 4 == 12"
    ]


def _mock_run_tests(tests: list[str], target_path: str) -> list[dict[str, Any]]:
    """
    Mock test runner for Sprint 1.
    
    Args:
        tests: List of test function strings
        target_path: Path to the target repository
        
    Returns:
        List of test results with name, passed, and error fields
    """
    return [
        {"name": "test_addition", "passed": True, "error": None},
        {"name": "test_subtraction", "passed": False, "error": "AssertionError: assert 2 == 3"},
        {"name": "test_multiplication", "passed": True, "error": None}
    ]


def _mock_suggest_fix(failures: list[dict[str, Any]], code: str, context: dict[str, Any]) -> dict[str, str]:
    """
    Mock fix suggester for Sprint 1.
    
    Args:
        failures: List of failed test results
        code: Original source code
        context: Context bank data
        
    Returns:
        Dictionary with file, patch, and explanation
    """
    return {
        "file": "calculator.py",
        "patch": "- result = a - b\n+ result = a + b",
        "explanation": "The subtraction function was using addition operator instead of subtraction"
    }


def run(path: str) -> dict[str, Any]:
    """
    Run one iteration of the testing loop.
    
    This is the main entry point for the loop controller.
    For Sprint 1, performs a single iteration with mock functions.
    
    Args:
        path: Path to the target repository to test
        
    Returns:
        Dictionary with summary of the run
    """
    print(f"🔍 Starting loop for repository: {path}")
    
    # Load context bank
    print("📖 Loading context bank...")
    context = load()
    print(f"   Found {len(context['bug_fix_history'])} previous bug fixes")
    
    # Mock: Read code from target path
    # In real implementation, this would read actual files
    mock_code = "def subtract(a, b):\n    return a + b  # Bug: should be a - b"
    print(f"📄 Read code from {path}")
    
    # Step 1: Generate tests
    print("\n📝 Generating tests...")
    tests = _mock_generate_tests(mock_code, context)
    print(f"   Generated {len(tests)} tests")
    
    # Step 2: Run tests
    print("\n🧪 Running tests...")
    results = _mock_run_tests(tests, path)
    passed = [r for r in results if r["passed"]]
    failed = [r for r in results if not r["passed"]]
    print(f"   ✅ {len(passed)} passed")
    print(f"   ❌ {len(failed)} failed")
    
    # Step 3: If there are failures, suggest fixes
    fix_suggestion = None
    if failed:
        print("\n🔧 Analyzing failures and suggesting fixes...")
        fix_suggestion = _mock_suggest_fix(failed, mock_code, context)
        print(f"   File: {fix_suggestion['file']}")
        print(f"   Explanation: {fix_suggestion['explanation']}")
        print(f"   Patch:\n{fix_suggestion['patch']}")
    else:
        print("\n✅ All tests passed!")
    
    # Prepare summary
    summary = {
        "path": path,
        "tests_generated": len(tests),
        "tests_passed": len(passed),
        "tests_failed": len(failed),
        "fix_suggested": fix_suggestion is not None,
        "fix_details": fix_suggestion
    }
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"   Repository: {summary['path']}")
    print(f"   Tests generated: {summary['tests_generated']}")
    print(f"   Tests passed: {summary['tests_passed']}")
    print(f"   Tests failed: {summary['tests_failed']}")
    if summary['fix_suggested']:
        print(f"   Fix suggested: Yes")
    print("=" * 60)
    
    return summary


if __name__ == "__main__":
    # Demo usage
    print("Loop Controller Demo")
    print("=" * 60)
    
    result = run("./sample-repo")
    
    print("\n\nReturned summary:")
    import json
    print(json.dumps(result, indent=2))

# Made with Bob
