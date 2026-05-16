"""
Context bank module for managing persistent agent memory.

Reads and writes the .agent-context.json file that stores:
- requirements
- architecture_notes
- bug_fix_history
"""

import json
import os
from pathlib import Path
from typing import Any


CONTEXT_FILE = ".agent-context.json"


def _get_context_path() -> Path:
    """Get the path to the context file in the current working directory."""
    return Path.cwd() / CONTEXT_FILE


def _get_empty_schema() -> dict[str, Any]:
    """Return the empty context schema."""
    return {
        "requirements": [],
        "architecture_notes": [],
        "bug_fix_history": []
    }


def load() -> dict[str, Any]:
    """
    Load the context bank from .agent-context.json.
    
    If the file doesn't exist, creates it with the empty schema.
    
    Returns:
        dict: The context data with keys: requirements, architecture_notes, bug_fix_history
    """
    context_path = _get_context_path()
    
    if not context_path.exists():
        # Create the file with empty schema
        empty_context = _get_empty_schema()
        save(empty_context)
        return empty_context
    
    try:
        with open(context_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Ensure all required keys exist
        schema = _get_empty_schema()
        for key in schema:
            if key not in data:
                data[key] = schema[key]
                
        return data
    except json.JSONDecodeError:
        # If file is corrupted, reset to empty schema
        empty_context = _get_empty_schema()
        save(empty_context)
        return empty_context


def save(data: dict[str, Any]) -> None:
    """
    Save the context data to .agent-context.json.
    
    Args:
        data: The context dictionary to save
    """
    context_path = _get_context_path()
    
    with open(context_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def append_history(bug: str, fix: str, file: str, iteration: int) -> None:
    """
    Append a bug fix entry to the history in the context bank.
    
    Args:
        bug: Description of the bug found
        fix: Description of the fix applied
        file: File path where the bug was found
        iteration: Iteration number when the bug was found
    """
    context = load()
    
    entry = {
        "iteration": iteration,
        "bug": bug,
        "fix": fix,
        "file": file
    }
    
    context["bug_fix_history"].append(entry)
    save(context)


if __name__ == "__main__":
    # Demo usage
    print("Context Bank Demo")
    print("=" * 50)
    
    # Load (will create if doesn't exist)
    ctx = load()
    print(f"\nLoaded context: {json.dumps(ctx, indent=2)}")
    
    # Add some sample data
    ctx["requirements"].append("Function must handle edge cases")
    ctx["architecture_notes"].append("Using pytest for testing")
    save(ctx)
    print("\nAdded requirements and notes")
    
    # Append history
    append_history(
        bug="Division by zero not handled",
        fix="Added zero check before division",
        file="calculator.py",
        iteration=1
    )
    print("\nAppended bug fix history")
    
    # Load again to verify
    ctx = load()
    print(f"\nFinal context: {json.dumps(ctx, indent=2)}")

# Made with Bob
