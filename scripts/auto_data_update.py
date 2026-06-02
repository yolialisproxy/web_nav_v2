#!/usr/bin/env python3
"""Auto data update script for websites data"""

import json
import shutil
from datetime import datetime
from pathlib import Path

def update_websites_data():
    """Update websites.json from backup or generate if missing"""
    project_root = Path(__file__).parent.parent
    websites_path = project_root / 'data' / 'websites.json'
    backup_path = project_root / 'data' / 'websites.json.backup'
    
    # For now, ensure we have a valid websites.json
    if not websites_path.exists() or websites_path.stat().st_size < 1000:
        # Create minimal valid structure if missing/corrupted
        websites_path.parent.mkdir(parents=True, exist_ok=True)
        with open(websites_path, 'w') as f:
            json.dump([{
                "name": "Example Site",
                "url": "https://example.com",
                "description": "An example site",
                "tags": ["example", "demo"]
            }], f, indent=2)
        return {"status": "created_minimal", "sites": 1}
    
    # Validate existing file
    try:
        with open(websites_path, 'r') as f:
            data = json.load(f)
        return {"status": "valid", "sites": len(data)}
    except json.JSONDecodeError:
        # Restore from backup if exists
        if backup_path.exists():
            shutil.copy(backup_path, websites_path)
            with open(websites_path, 'r') as f:
                data = json.load(f)
            return {"status": "restored_from_backup", "sites": len(data)}
        else:
            # Create minimal as fallback
            with open(websites_path, 'w') as f:
                json.dump([{
                    "name": "Fallback Site",
                    "url": "https://fallback.com",
                    "description": "Fallback site",
                    "tags": ["fallback"]
                }], f, indent=2)
            return {"status": "created_fallback", "sites": 1}

if __name__ == "__main__":
    result = update_websites_data()
    print(json.dumps(result, indent=2))