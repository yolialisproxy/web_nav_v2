#!/usr/bin/env python3
"""Health check script for automation system"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def check_file_freshness(file_path, max_age_hours=24):
    """Check if file is fresh enough"""
    try:
        if not os.path.exists(file_path):
            return {"status": "missing", "age_hours": None}
        
        file_mtime = os.path.getmtime(file_path)
        age_seconds = datetime.now().timestamp() - file_mtime
        age_hours = age_seconds / 3600
        
        return {
            "status": "fresh" if age_hours <= max_age_hours else "stale",
            "age_hours": round(age_hours, 2),
            "max_age_hours": max_age_hours
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_git_status():
    """Check git repository status"""
    try:
        # Check if we're in a git repo
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      check=True, capture_output=True)
        
        # Check for uncommitted changes
        result = subprocess.run(['git', 'diff-index', '--quiet', 'HEAD', '--'],
                              capture_output=True)
        has_changes = result.returncode != 0
        
        # Get last commit info
        log_result = subprocess.run(['git', 'log', '-1', '--pretty=format:%H %s (%cr)'],
                                  capture_output=True, text=True)
        last_commit = log_result.stdout.strip() if log_result.returncode == 0 else "unknown"
        
        return {
            "status": "healthy",
            "has_uncommitted_changes": has_changes,
            "last_commit": last_commit
        }
    except subprocess.CalledProcessError:
        return {"status": "not_git_repo"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_essential_files():
    """Check that essential automation files exist"""
    project_root = Path(__file__).parent.parent
    essential_files = [
        'scripts/auto_dev_system.py',
        'scripts/auto_data_update.py',
        'scripts/auto_tag_generation.py',
        'scripts/auto_data_validation.py',
        'scripts/auto_quality_check.py',
        'scripts/auto_deploy.py',
        'scripts/auto_master.py'
    ]
    
    results = {}
    for file_path in essential_files:
        full_path = project_root / file_path
        results[file_path] = {
            "exists": full_path.exists(),
            "size": full_path.stat().st_size if full_path.exists() else 0,
            "executable": os.access(full_path, os.X_OK) if full_path.exists() else False
        }
    
    all_exist = all(info["exists"] for info in results.values())
    return {
        "status": "complete" if all_exist else "incomplete",
        "files": results
    }

def main():
    """Run all health checks"""
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "git_status": check_git_status(),
            "essential_files": check_essential_files(),
            "data_files": {
                "websites_json": check_file_freshness('data/websites.json', max_age_hours=6),
                "tag_index_json": check_file_freshness('data/tag_index.json', max_age_hours=6),
                "sites_with_tags_json": check_file_freshness('data/sites_with_tags.json', max_age_hours=24)
            },
            "reports": {
                "last_performance_report": check_file_freshness('performance_reports/', max_age_hours=24) if os.path.exists('performance_reports/') else {"status": "no_reports_dir"},
                "last_health_check": check_file_freshness('logs/auto_dev_system.log', max_age_hours=2)
            }
        }
    }
    
    # Determine overall health
    git_ok = health_data["checks"]["git_status"].get("status") == "healthy"
    files_ok = health_data["checks"]["essential_files"].get("status") == "complete"
    data_fresh = all(check.get("status") == "fresh" for check in 
                    health_data["checks"]["data_files"].values()
                    if check.get("status") in ["fresh", "stale"])  # Skip missing/error
    
    health_data["overall_status"] = "healthy" if (git_ok and files_ok and data_fresh) else "unhealthy"
    
    print(json.dumps(health_data, indent=2, ensure_ascii=False))
    
    # Also write to status file for easy monitoring
    status_file = Path(__file__).parent.parent / 'docs' / 'AUTOMATION_STATUS.md'
    status_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(status_file, 'w') as f:
        f.write(f"""# Automation Status

Last updated: {health_data['timestamp']}

## Overall Status: {health_data['overall_status']}

### Checks Summary
- Git Status: {health_data['checks']['git_status'].get('status', 'unknown')}
- Essential Files: {health_data['checks']['essential_files'].get('status', 'unknown')}
- Data Freshness: {'OK' if data_fresh else 'Issues detected'}

### Detailed Results
```json
{json.dumps(health_data, indent=2)}
```
""")
    
    return health_data["overall_status"] == "healthy"

if __name__ == "__main__":
    healthy = main()
    sys.exit(0 if healthy else 1)