#!/usr/bin/env python3
"""Comprehensive quality check script"""

import json
import subprocess
import sys
from pathlib import Path

def find_project_root(start_path):
    """Find the project root by looking for package.json and data directory."""
    # First, try upward search from start_path
    current = Path(start_path).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "package.json").is_file() and (parent / "data").is_dir():
            return parent
    # If not found, try some known locations
    home = Path.home()
    candidates = [
        home / "GitHub" / "web_nav_v2",
        home / "web_nav_v2",
        home,
    ]
    for candidate in candidates:
        if candidate.is_dir():
            if (candidate / "package.json").is_file() and (candidate / "data").is_dir():
                return candidate
    return None

def run_npm_tests(project_root):
    """Run npm test suite"""
    try:
        result = subprocess.run(['npm', 'test'], 
                              cwd=project_root,
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

def run_typecheck(project_root):
    """Run TypeScript type checking"""
    try:
        result = subprocess.run(['npm', 'run', 'typecheck'], 
                              cwd=project_root,
                              capture_output=True, text=True, timeout=30)
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "stdout": result.stdout[-500:],
            "stderr": result.stderr[-500:] if result.stderr else "",
            "returncode": result.returncode
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def validate_data_files(project_root):
    """Validate critical data files exist and are valid JSON"""
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
    # Find project root
    script_path = Path(__file__).resolve()
    project_root = find_project_root(script_path)
    if project_root is None:
        # Fallback to parent.parent (original behavior)
        project_root = script_path.parent.parent
        print(f"Warning: Could not find project root via marker, using fallback: {project_root}", file=sys.stderr)
    else:
        print(f"Info: Found project root at: {project_root}", file=sys.stderr)
    
    results = {
        "timestamp": subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip(),
        "project_root": str(project_root),
        "npm_tests": run_npm_tests(project_root),
        "typecheck": run_typecheck(project_root),
        "data_validation": validate_data_files(project_root)
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