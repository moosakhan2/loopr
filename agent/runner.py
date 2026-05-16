"""
Test runner module that executes pytest tests and returns structured results.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any


def run_tests(tests: List[str], target_path: str) -> List[Dict[str, Any]]:
    """
    Runs a list of pytest test functions against a target codebase.
    
    Args:
        tests: List of test function source code strings
        target_path: Path to the codebase under test
    
    Returns:
        List of test results with format:
        [{"name": str, "passed": bool, "error": str | None}, ...]
    """
    target_path_obj = Path(target_path).resolve()
    tests_dir = target_path_obj / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    # Write each test to a temporary file
    test_file = tests_dir / "test_generated.py"
    
    # Combine all test strings into a single test file
    test_content = "\n\n".join(tests)
    
    with open(test_file, "w") as f:
        f.write(test_content)
    
    # Run pytest with JSON report
    json_report_path = tests_dir / ".report.json"
    
    try:
        # Run pytest with json-report plugin
        result = subprocess.run(
            [
                "pytest",
                str(test_file),
                "--json-report",
                f"--json-report-file={json_report_path}",
                "--tb=short",
                "-v"
            ],
            cwd=str(target_path_obj),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse the JSON report
        if json_report_path.exists():
            with open(json_report_path, "r") as f:
                report = json.load(f)
            
            # Convert to contract format
            results = []
            for test in report.get("tests", []):
                results.append({
                    "name": test.get("nodeid", "unknown"),
                    "passed": test.get("outcome") == "passed",
                    "error": test.get("call", {}).get("longrepr") if test.get("outcome") != "passed" else None
                })
            
            return results
        else:
            # Fallback if JSON report wasn't generated
            return [{
                "name": "pytest_execution",
                "passed": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None
            }]
    
    except subprocess.TimeoutExpired:
        return [{
            "name": "pytest_execution",
            "passed": False,
            "error": "Test execution timed out after 30 seconds"
        }]
    except Exception as e:
        return [{
            "name": "pytest_execution",
            "passed": False,
            "error": f"Error running tests: {str(e)}"
        }]
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if json_report_path.exists():
            json_report_path.unlink()


if __name__ == "__main__":
    # Test the runner with a hardcoded test string
    print("Testing runner.py standalone...")
    
    # Sample test that should pass
    test_code = """
import sys
sys.path.insert(0, '.')

from calculator import add, subtract

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_subtract_bug():
    # This will fail due to the bug in subtract
    assert subtract(5, 3) == 2
"""
    
    # Run against sample-repo
    results = run_tests([test_code], "sample-repo")
    
    print("\nTest Results:")
    print(json.dumps(results, indent=2))
    
    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    
    if any(not r["passed"] for r in results):
        print("\nFailures detected (expected due to bugs in calculator.py):")
        for r in results:
            if not r["passed"]:
                print(f"  - {r['name']}")
                if r["error"]:
                    print(f"    Error: {r['error'][:200]}...")

# Made with Bob
