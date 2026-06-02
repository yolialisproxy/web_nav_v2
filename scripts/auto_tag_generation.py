#!/usr/bin/env python3
"""Automatic tag index generation from websites data"""

import json
from collections import Counter
from pathlib import Path

def generate_tag_index():
    """Generate tag index from websites data"""
    project_root = Path(__file__).parent.parent
    websites_path = project_root / 'data' / 'websites.json'
    tag_index_path = project_root / 'data' / 'tag_index.json'
    
    try:
        with open(websites_path, 'r') as f:
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