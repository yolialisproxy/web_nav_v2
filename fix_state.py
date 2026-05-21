import os
import re

def add_state_properties(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # We'll look for the class State and then insert property declarations after the class line or before the constructor.
    new_lines = []
    in_class = False
    class_started = False
    for i, line in enumerate(lines):
        new_lines.append(line)
        stripped = line.strip()
        if stripped.startswith('class State'):
            in_class = True
            class_started = True
        # When we are in the class and we see the constructor, we can insert the properties before it.
        if in_class and stripped.startswith('constructor()') and class_started:
            # Insert the property declarations before the constructor
            # We'll insert them at the beginning of the class, right after the class line.
            # But we have already added the class line. We need to go back and insert after the class line.
            # Instead, let's do a different approach: we'll build the class body separately.
            pass

    # Let's do a simpler approach: we know the structure of the State class from the file.
    # We'll replace the entire class with a fixed version? That might be too risky.
    # Instead, we'll insert the property declarations after the class line and before the constructor.

    # We'll do a two-pass: first, find the class and constructor lines.
    # Then, insert the property declarations in between.

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match the class State and its constructor
    # We'll look for: class State { ... constructor() { ... }
    # We want to insert after the opening brace of the class and before the constructor.

    # We'll split the content into lines and process.
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        if line.strip() == 'class State {':
            # We are at the class opening. Now we look for the constructor.
            # We'll insert the property declarations after the class line and before the constructor.
            # But note: there might be other class fields or comments.
            # We'll just insert after the class line and then continue.
            # However, we must not insert if we are already past the constructor.
            # Let's look ahead for the constructor.
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('constructor()'):
                j += 1
            if j < len(lines):
                # Insert the property declarations at position j (before the constructor)
                # But we have already added the class line. We'll insert now.
                new_lines.append('    // Tag system properties')
                new_lines.append('    tagAll: Map<string, number>;')
                new_lines.append('    tagSites: Map<string, string[]>;')
                new_lines.append('    activeTags: Set<string>;')
                new_lines.append('    _tagInitialized: boolean;')
                new_lines.append('')  # empty line for readability
                # Now we set i to j-1 because the loop will increment i and we want to process the constructor line next.
                i = j - 1
        i += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

if __name__ == '__main__':
    add_state_properties('assets/js/state.ts')
    print('Added property declarations to state.ts')