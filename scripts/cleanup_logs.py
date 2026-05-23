#!/usr/bin/env python3
"""
清理日志文件，只保留最近的 N 个审计段落。
段落以时间戳行开头：[YYYY-MM-DD HH:MM:SS]
"""
import sys
import os

def main():
    if len(sys.argv) < 5 or sys.argv[1] != '--log' or sys.argv[3] != '--keep':
        print("Usage: python cleanup_logs.py --log <log_file> --keep <N>")
        sys.exit(1)
    
    log_file = sys.argv[2]
    try:
        keep = int(sys.argv[4])
    except ValueError:
        print("Keep argument must be an integer")
        sys.exit(1)
    
    if not os.path.exists(log_file):
        print(f"Log file {log_file} does not exist.")
        sys.exit(0)
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find indices of lines that start with timestamp pattern
    import re
    timestamp_pattern = re.compile(r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]')
    section_starts = [i for i, line in enumerate(lines) if timestamp_pattern.match(line)]
    
    if not section_starts:
        # No sections found, nothing to keep
        print("No timestamp sections found in log.")
        # Optionally clear the file? We'll keep it as is.
        return
    
    # Determine which sections to keep: the last `keep` sections
    if len(section_starts) <= keep:
        # Already have <= keep sections, nothing to remove
        print(f"Found {len(section_starts)} sections, keeping all (<= {keep}).")
        return
    
    # Sections to remove: all except the last `keep`
    # We'll keep lines from the start of the (len(section_starts) - keep)-th section to the end.
    start_index = section_starts[-keep]
    # Keep lines from start_index to end
    kept_lines = lines[start_index:]
    
    # Write back
    with open(log_file, 'w', encoding='utf-8') as f:
        f.writelines(kept_lines)
    
    removed_sections = len(section_starts) - keep
    print(f"Removed {removed_sections} old sections, kept {keep} sections.")

if __name__ == '__main__':
    main()