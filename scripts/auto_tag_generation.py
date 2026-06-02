#!/usr/bin/env python3
"""Automatic tag index generation from websites data"""

import json
from collections import Counter
from pathlib import Path

def generate_tag_index():
    """Generate tag index from websites data"""
    project_root = Path(__file__).parent.parent
    # Try sites_with_tags.json first (has enriched tags), fallback to websites.json
    sites_with_tags_path = project_root / 'data' / 'sites_with_tags.json'
    websites_path = project_root / 'data' / 'websites.json'
    tag_index_path = project_root / 'data' / 'tag_index.json'
    
    # Prefer sites_with_tags.json if it has real data
    if sites_with_tags_path.exists() and sites_with_tags_path.stat().st_size > 1000:
        source_path = sites_with_tags_path
    else:
        source_path = websites_path
    
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            sites = json.load(f)
        
        # Count tags across all sites
        tag_counter = Counter()
        for site in sites:
            tags = site.get('tags', [])
            if isinstance(tags, list):
                tag_counter.update(tags)
        
        # Generate tag index
        tag_index = [{"tag": tag, "count": count} 
                     for tag, count in tag_counter.most_common()]
        
        # Save tag index
        tag_index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(tag_index_path, 'w') as f:
            json.dump(tag_index, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "unique_tags": len(tag_index),
            "total_tag_occurrences": sum(tag_counter.values())
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    result = generate_tag_index()
    print(json.dumps(result, indent=2))