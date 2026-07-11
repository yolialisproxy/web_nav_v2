#!/usr/bin/env python3
"""Automated deployment script"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_quality_checks():
    """Run quality checks before deployment"""
    try:
        result = subprocess.run([sys.executable, 'scripts/auto_quality_check.py'],
                              capture_output=True, text=True, timeout=120)
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def git_commit_and_push(message=None):
    """Commit changes and push to remote"""
    if message is None:
        message = f"Auto-deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Check if there are changes to commit
        diff_result = subprocess.run(['git', 'diff', '--cached', '--quiet'],
                                   capture_output=True)
        if diff_result.returncode == 0:
            return {"status": "no_changes", "message": "No changes to commit"}
        
        # Commit
        subprocess.run(['git', 'commit', '-m', message], check=True)
        
        # Push
        subprocess.run(['git', 'push'], check=True)
        
        return {"status": "success", "message": "Changes committed and pushed"}
    except subprocess.CalledProcessError as e:
        return {"status": "failed", "message": f"Git command failed: {e}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    """Main deployment function"""
    print("Starting automated deployment process...")
    
    # Step 1: Run quality checks
    print("Running quality checks...")
    quality_result = run_quality_checks()
    print(json.dumps(quality_result, indent=2))
    
    if quality_result["status"] != "success":
        print("Quality checks failed. Aborting deployment.")
        return quality_result
    
    # Step 2: Commit and push
    print("Committing and pushing changes...")
    deploy_result = git_commit_and_push()
    print(json.dumps(deploy_result, indent=2))
    
    return deploy_result

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("status") in ("success", "no_changes") else 1)