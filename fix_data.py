import os
import re

def fix_datamanager(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # We'll look for the class DataManager and then insert property declarations after the class line and before the constructor.
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        stripped = line.strip()
        if stripped.startswith('class DataManager'):
            # We are at the class opening. Now we look for the constructor.
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('constructor()'):
                j += 1
            if j < len(lines):
                # Insert the property declarations at position j (before the constructor)
                # But we have already added the class line. We'll insert now.
                new_lines.append('    // Properties')
                new_lines.append('    raw: any;')
                new_lines.append('    sites: Map<string, any>;')
                new_lines.append('    categories: any;')
                new_lines.append('    mappings: Map<string, any>;')
                new_lines.append('    tagIndex: Map<string, any>;')
                new_lines.append('    tagCloud: Map<string, any>;')
                new_lines.append('    isLoaded: boolean;')
                new_lines.append('    version: any;')
                new_lines.append('    _loadError: any;')
                new_lines.append('')  # empty line for readability
                # Now we set i to j-1 because the loop will increment i and we want to process the constructor line next.
                i = j - 1
        i += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

if __name__ == '__main__':
    fix_datamanager('assets/js/data.ts')
    print('Added property declarations to data.ts')