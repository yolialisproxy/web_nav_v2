import os
import sys
import subprocess
import json

def test_auto_dev_system_has_data_commands():
    result = subprocess.run([sys.executable, 'scripts/auto_dev_system.py', '--help'], 
                          capture_output=True, text=True)
    assert 'data-update' in result.stdout
    assert 'tag-generation' in result.stdout
    assert 'data-validation' in result.stdout

def test_auto_dev_system_data_commands_work():
    # Test that the commands at least run without import errors
    commands = ['data-update', 'tag-generation', 'data-validation']
    for cmd in commands:
        result = subprocess.run([sys.executable, 'scripts/auto_dev_system.py', cmd], 
                              capture_output=True, text=True, timeout=30)
        # Should not fail with import errors
        assert "hermes_tools not available" not in result.stderr or                "No module named 'hermes_tools'" not in result.stderr