"""
Loop controller module - orchestrates the recursive testing loop.

This module coordinates the flow: generator → runner → fixer.
Integrates real implementations with error handling.
"""

import os
import difflib
from pathlib import Path
from typing import Any, Dict, List

from agent.context_bank import load, save, append_history
from agent.generator import generate_tests
from agent.runner import run_tests
from agent.fixer import suggest_fix


def _read_target_code(target_path: str) -> str:
    """
    Read the main Python file from the target directory.
    For now, reads the first .py file found (excluding __init__.py and test files).
    
    Args:
        target_path: Path to the target repository
        
    Returns:
        Source code as a string
    """
    target_dir = Path(target_path)
    
    # Find Python files (excluding __init__.py and test files)
    py_files = [
        f for f in target_dir.glob("*.py")
        if f.name != "__init__.py" and not f.name.startswith("test_")
    ]
    
    if not py_files:
        raise RuntimeError(f"No Python files found in {target_path}")
    
    # Read the first file found
    target_file = py_files[0]
    with open(target_file, 'r', encoding='utf-8') as f:
        return f.read()


def _apply_fix(target_path: str, fix_suggestion: dict, original_code: str) -> bool:
    """Show a colored diff and ask user approval before applying the fix."""
    try:
        target_dir = Path(target_path)
        file_name = fix_suggestion.get("file", "")
        patch = fix_suggestion.get("patch", "")
        
        if not file_name or not patch:
            return False
        
        # Show colored diff
        original_lines = original_code.splitlines(keepends=True)
        patched_lines = patch.splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            original_lines, patched_lines,
            fromfile=f"original/{file_name}",
            tofile=f"fixed/{file_name}"
        ))
        
        if diff:
            print("\n📋 Proposed changes:")
            print("-" * 70)
            for line in diff:
                if line.startswith('+') and not line.startswith('+++'):
                    print(f"\033[92m{line}\033[0m", end='')  # green
                elif line.startswith('-') and not line.startswith('---'):
                    print(f"\033[91m{line}\033[0m", end='')  # red
                else:
                    print(line, end='')
            print("\n" + "-" * 70)
        
        # Ask for approval
        answer = input("\n❓ Apply this fix? (y/n/skip): ").strip().lower()
        if answer == 'y':
            target_file = target_dir / file_name
            if not target_file.exists():
                matches = list(target_dir.glob(f"**/{file_name}"))
                if not matches:
                    print(f"   ⚠️  File {file_name} not found")
                    return False
                target_file = matches[0]
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(patch)
            print(f"   ✅ Fix applied to {target_file}")
            return True
        else:
            print("   ⏭️  Fix skipped.")
            return False
    except Exception as e:
        print(f"   ⚠️  Could not apply fix: {e}")
        return False


def run(path: str) -> Dict[str, Any]:
    """
    Run one iteration of the testing loop.
    
    This is the main entry point for the loop controller.
    Performs a single iteration: generate → run → fix.
    
    Args:
        path: Path to the target repository to test
        
    Returns:
        Dictionary with summary of the run
    """
    print(f"🔍 Starting loop for repository: {path}")
    
    # Load context bank
    print("📖 Loading context bank...")
    try:
        context = load()
        print(f"   Found {len(context['bug_fix_history'])} previous bug fixes")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not load context bank: {e}")
        context = {
            "requirements": [],
            "architecture_notes": [],
            "bug_fix_history": []
        }
    
    # Read code from target path
    print(f"📄 Reading code from {path}...")
    try:
        code = _read_target_code(path)
        print(f"   Read {len(code)} characters of code")
    except Exception as e:
        print(f"   ❌ Error reading code: {e}")
        return {
            "path": path,
            "error": f"Failed to read code: {str(e)}",
            "tests_generated": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "fix_suggested": False
        }
    
    # Step 1: Generate tests
    print("\n📝 Generating tests...")
    try:
        tests = generate_tests(code, context)
        print(f"   Generated {len(tests)} tests")
    except Exception as e:
        print(f"   ❌ Error generating tests: {e}")
        print(f"   This usually means watsonx.ai returned unexpected output.")
        print(f"   Check your .env credentials and try again.")
        return {
            "path": path,
            "error": f"Failed to generate tests: {str(e)}",
            "tests_generated": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "fix_suggested": False
        }
    
    # Step 2: Run tests
    print("\n🧪 Running tests...")
    try:
        results = run_tests(tests, path)
        passed = [r for r in results if r["passed"]]
        failed = [r for r in results if not r["passed"]]
        print(f"   ✅ {len(passed)} passed")
        print(f"   ❌ {len(failed)} failed")
    except Exception as e:
        print(f"   ❌ Error running tests: {e}")
        return {
            "path": path,
            "error": f"Failed to run tests: {str(e)}",
            "tests_generated": len(tests),
            "tests_passed": 0,
            "tests_failed": 0,
            "fix_suggested": False
        }
    
    # Step 3: If there are failures, suggest fixes
    fix_suggestion = None
    if failed:
        print("\n🔧 Analyzing failures and suggesting fixes...")
        try:
            fix_suggestion = suggest_fix(failed, code, context)
            
            # Display the fix suggestion
            print("\n" + "=" * 70)
            print("🔍 FIX SUGGESTION")
            print("=" * 70)
            print(f"📁 File: {fix_suggestion['file']}")
            print(f"💡 Explanation: {fix_suggestion['explanation']}")
            print(f"\n📝 Patch:")
            print(fix_suggestion['patch'])
            print("=" * 70)
            
            # Save fix to context bank
            append_history(
                bug=fix_suggestion['explanation'],
                fix=fix_suggestion['patch'],
                file=fix_suggestion['file'],
                iteration=len(context['bug_fix_history']) + 1
            )
            
            # Show diff and ask for approval
            print("\n🔨 Reviewing fix...")
            _apply_fix(path, fix_suggestion, code)
            
        except Exception as e:
            print(f"   ⚠️  Warning: Could not generate fix suggestion: {e}")
            print(f"   This usually means watsonx.ai returned unexpected output.")
            fix_suggestion = {
                "file": "unknown",
                "patch": "",
                "explanation": f"Error: {str(e)}"
            }
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
