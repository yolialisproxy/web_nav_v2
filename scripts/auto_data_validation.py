#!/usr/bin/env python3
"""Data validation and cleaning script for websites data"""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

def validate_and_clean_websites_data():
    """Validate and clean websites data"""
    project_root = Path(__file__).parent.parent
    websites_path = project_root / 'data' / 'websites.json'
    backup_path = project_root / 'data' / 'websites.json.validation_backup'
    
    # Backup original
    if websites_path.exists():
        import shutil
        shutil.copy(websites_path, backup_path)
    
    try:
        with open(websites_path, 'r', encoding='utf-8') as f:
            sites = json.load(f)
        
        if not isinstance(sites, list):
            sites = []
        
        original_count = len(sites)
        cleaned_sites = []
        seen_urls = set()
        
        for site in sites:
            if not isinstance(site, dict):
                continue
            
            # Ensure required fields
            site.setdefault('name', 'Unknown Site')
            site.setdefault('url', '')
            site.setdefault('description', '')
            site.setdefault('tags', [])
            
            # Clean and validate URL
            url = site['url'].strip()
            if not url:
                continue
                
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                site['url'] = url
            
            # Validate URL format
            try:
                parsed = urlparse(url)
                if not parsed.netloc:
                    continue
            except Exception:
                continue
            
            # Deduplicate by URL
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Clean name and description
            site['name'] = site['name'].strip()[:200]  # Limit length
            site['description'] = site['description'].strip()[:500]
            
            # Ensure tags is a list and clean tags
            if not isinstance(site['tags'], list):
                site['tags'] = []
            site['tags'] = [tag.strip().lower() for tag in site['tags'] 
                           if isinstance(tag, str) and tag.strip()]
            site['tags'] = list(set(site['tags']))  # Remove duplicates
            
            cleaned_sites.append(site)
        
        # Save cleaned data
        websites_path.parent.mkdir(parents=True, exist_ok=True)
        with open(websites_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_sites, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "original_count": original_count,
            "cleaned_count": len(cleaned_sites),
            "removed_duplicates": original_count - len(seen_urls),
            "invalid_removed": original_count - len(cleaned_sites) - (original_count - len(seen_urls))
        }
        
    except Exception as e:
        # Restore from backup on error
        if backup_path.exists():
            import shutil
            shutil.copy(backup_path, websites_path)
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    result = validate_and_clean_websites_data()
    print(json.dumps(result, indent=2))