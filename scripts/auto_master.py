#!/usr/bin/env python3
"""Master automation orchestrator"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def run_command(name, cmd, timeout=300):
    """Run a command and return results"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting {name}...")
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, 
                              text=True, timeout=timeout)
        elapsed = time.time() - start_time
        
        return {
            "name": name,
            "status": "success" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "elapsed_time": round(elapsed, 2),
            "stdout": result.stdout[-1000:] if result.stdout else "",
            "stderr": result.stderr[-1000:] if result.stderr else ""
        }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        return {
            "name": name,
            "status": "timeout",
            "elapsed_time": round(elapsed, 2),
            "message": f"Command timed out after {timeout} seconds"
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "name": name,
            "status": "error",
            "elapsed_time": round(elapsed, 2),
            "message": str(e)
        }

def main():
    """Run master automation sequence"""
    print("=== Starting Master Automation Sequence ===")
    start_time = time.time()
    
    results = {
        "start_time": datetime.now().isoformat(),
        "steps": []
    }
    
    # Step 1: Data update
    data_result = run_command(
        "Data Update", 
        "python scripts/auto_dev_system.py data-update",
        timeout=60
    )
    results["steps"].append(data_result)
    
    # Step 2: Tag generation
    tag_result = run_command(
        "Tag Generation",
        "python scripts/auto_dev_system.py tag-generation",
        timeout=30
    )
    results["steps"].append(tag_result)
    
    # Step 3: Data validation
    validation_result = run_command(
        "Data Validation",
        "python scripts/auto_dev_system.py data-validation",
        timeout=60
    )
    results["steps"].append(validation_result)
    
    # Step 4: Quality checks
    quality_result = run_command(
        "Quality Checks",
        "python scripts/auto_quality_check.py",
        timeout=120
    )
    results["steps"].append(quality_result)
    
    # Step 5: Deployment (only if quality checks pass)
    if quality_result["status"] == "success":
        deploy_result = run_command(
            "Deployment",
            "python scripts/auto_dev_system.py deploy",
            timeout=60
        )
        results["steps"].append(deploy_result)
    else:
        print("Skipping deployment due to quality check failures")
        results["steps"].append({
            "name": "Deployment",
            "status": "skipped",
            "message": "Skipped due to quality check failures"
        })
    
    # Calculate summary
    elapsed_time = time.time() - start_time
    successful_steps = sum(1 for step in results["steps"] 
                          if step.get("status") == "success")
    total_steps = len([s for s in results["steps"] if s.get("status") != "skipped"])
    
    results.update({
        "end_time": datetime.now().isoformat(),
        "total_elapsed_time": round(elapsed_time, 2),
        "successful_steps": successful_steps,
        "total_steps": total_steps,
        "overall_status": "success" if successful_steps == total_steps and total_steps > 0 else "failed"
    })
    
    print("\n=== Automation Sequence Complete ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    return results["overall_status"] == "success"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)