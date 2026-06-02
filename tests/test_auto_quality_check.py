import os
import sys
import subprocess
import json

def test_auto_quality_check_exists():
    assert os.path.exists('scripts/auto_quality_check.py')

def test_auto_quality_check_runs():
    # Test that script runs without immediate import errors
    result = subprocess.run([sys.executable, 'scripts/auto_quality_check.py'], 
                          capture_output=True, text=True, timeout=30)
    # Should not fail with import errors
    assert "hermes_tools not available" not in result.stderr or            "No module named 'hermes_tools'" not in result.stderr