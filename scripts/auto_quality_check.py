#!/usr/bin/env python3
"""Comprehensive quality check script"""

import json
import subprocess
import sys
from pathlib import Path

def run_npm_tests():
    """Run npm test suite"""
    try:
        result = subprocess.run(['npm', 'test'], 
                              capture_output=True, text=True, timeout=60)
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "stdout": result.stdout[-500:],  # Last 500 chars
            "stderr": result.stderr[-500:] if result.stderr else "",
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "message": "Tests timed out"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_typecheck():
    """Run TypeScript type checking"""
    try:
        result = subprocess.run(['npm', 'run', 'typecheck'], 
                              capture_output=True, text=True, timeout=30)
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "stdout": result.stdout[-500:],
            "stderr": result.stderr[-500:] if result.stderr else "",
            "returncode": result.returncode
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def validate_data_files():
    """Validate critical data files exist and are valid JSON"""
    project_root = Path(__file__).parent.parent
    required_files = [
        'data/websites.json',
        'data/tag_index.json',
        'data/sites_with_tags.json'
    ]
    
    results = {}
    for file_path in required_files:
        full_path = project_root / file_path
        try:
            if full_path.exists():
                with open(full_path, 'r') as f:
                    json.load(f)
                results[file_path] = {"status": "valid", "size": full_path.stat().st_size}
            else:
                results[file_path] = {"status": "missing", "size": 0}
        except json.JSONDecodeError as e:
            results[file_path] = {"status": "invalid_json", "error": str(e)}
        except Exception as e:
            results[file_path] = {"status": "error", "error": str(e)}
    
    return results

def main():
    """Run all quality checks"""
    results = {
        "timestamp": subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip(),
        "npm_tests": run_npm_tests(),
        "typecheck": run_typecheck(),
        "data_validation": validate_data_files()
    }
    
    # Determine overall status
    npm_ok = results["npm_tests"]["status"] == "success"
    typecheck_ok = results["typecheck"]["status"] == "success"
    data_ok = all(v.get("status") == "valid" for v in results["data_validation"].values())
    
    results["overall_status"] = "success" if (npm_ok and typecheck_ok and data_ok) else "failed"
    
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return results["overall_status"] == "success"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)