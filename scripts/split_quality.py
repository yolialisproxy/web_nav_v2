#!/usr/bin/env python3
"""三层数据分离器"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_json_io import safe_read_json, safe_write_json

def classify(s):
    if not isinstance(s, dict): return None
    t = bool(s.get(title) and str(s.get(title)).strip())
    d = bool(s.get(description) and str(s.get(description)).strip())
    if t and d: return ads
    elif t or d: return dwd
    return ods

def main():
    data = safe_read_json(data/websites.json)
    ads, dwd, ods = [], [], []
    def traverse(obj):
        if isinstance(obj, list):
            for x in obj:
                if isinstance(x, dict):
                    if url in x:
                        l = classify(x)
                        if l == ads: ads.append(x)
                        elif l == dwd: dwd.append(x)
                        else: ods.append(x)
                    else: traverse(x)
        elif isinstance(obj, dict):
            for v in obj.values(): traverse(v)
    traverse(data)
    print(f"ADS={len(ads)}, DWD={len(dwd)}, ODS={len(ods)}")
    safe_write_json(data/websites.json, ads)
    safe_write_json(data/dwd_processing.json, dwd)
    safe_write_json(data/ods_raw_buffer.json, ods)
    print("✅ 分离完成，主数据只含完全增强站点")

if __name__ == "__main__": main()
