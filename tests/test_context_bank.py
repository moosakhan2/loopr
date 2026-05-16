"""
Tests for the context_bank module.
"""

import json
import os
import pytest
from pathlib import Path
from agent.context_bank import load, save, append_history, CONTEXT_FILE


@pytest.fixture
def temp_context_file(tmp_path, monkeypatch):
    """Create a temporary context file for testing."""
    # Change to temp directory for tests
    monkeypatch.chdir(tmp_path)
    yield tmp_path / CONTEXT_FILE
    # Cleanup happens automatically with tmp_path


def test_load_creates_file_if_not_exists(temp_context_file):
    """Test that load() creates the context file with empty schema if it doesn't exist."""
    assert not temp_context_file.exists()
    
    context = load()
    
    assert temp_context_file.exists()
    assert "requirements" in context
    assert "architecture_notes" in context
    assert "bug_fix_history" in context
    assert context["requirements"] == []
    assert context["architecture_notes"] == []
    assert context["bug_fix_history"] == []


def test_save_and_load_roundtrip(temp_context_file):
    """Test that data saved can be loaded back correctly."""
    test_data = {
        "requirements": ["req1", "req2"],
        "architecture_notes": ["note1"],
        "bug_fix_history": [
            {"iteration": 1, "bug": "test bug", "fix": "test fix", "file": "test.py"}
        ]
    }
    
    save(test_data)
    loaded_data = load()
    
    assert loaded_data == test_data


def test_load_handles_corrupted_json(temp_context_file):
    """Test that load() handles corrupted JSON by resetting to empty schema."""
    # Write invalid JSON
    with open(temp_context_file, 'w') as f:
        f.write("{ invalid json }")
    
    context = load()
    
    # Should return empty schema
    assert context["requirements"] == []
    assert context["architecture_notes"] == []
    assert context["bug_fix_history"] == []


def test_load_adds_missing_keys(temp_context_file):
    """Test that load() adds missing keys from schema."""
    # Write partial data
    partial_data = {"requirements": ["req1"]}
    with open(temp_context_file, 'w') as f:
        json.dump(partial_data, f)
    
    context = load()
    
    # Should have all keys
    assert "requirements" in context
    assert "architecture_notes" in context
    assert "bug_fix_history" in context
    assert context["requirements"] == ["req1"]


def test_append_history(temp_context_file):
    """Test that append_history adds entries correctly."""
    # Start with empty context
    load()
    
    # Append first entry
    append_history(
        bug="Bug 1",
        fix="Fix 1",
        file="file1.py",
        iteration=1
    )
    
    context = load()
    assert len(context["bug_fix_history"]) == 1
    assert context["bug_fix_history"][0]["bug"] == "Bug 1"
    assert context["bug_fix_history"][0]["fix"] == "Fix 1"
    assert context["bug_fix_history"][0]["file"] == "file1.py"
    assert context["bug_fix_history"][0]["iteration"] == 1
    
    # Append second entry
    append_history(
        bug="Bug 2",
        fix="Fix 2",
        file="file2.py",
        iteration=2
    )
    
    context = load()
    assert len(context["bug_fix_history"]) == 2
    assert context["bug_fix_history"][1]["bug"] == "Bug 2"


def test_save_preserves_formatting(temp_context_file):
    """Test that saved JSON is properly formatted."""
    test_data = {
        "requirements": ["req1"],
        "architecture_notes": [],
        "bug_fix_history": []
    }
    
    save(test_data)
    
    # Read raw file content
    with open(temp_context_file, 'r') as f:
        content = f.read()
    
    # Should be indented (not minified)
    assert '\n' in content
    assert '  ' in content  # 2-space indent

# Made with Bob
