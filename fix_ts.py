import os
import re

def fix_state_class(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the class State and the constructor
    class_start = -1
    constructor_start = -1
    for i, line in enumerate(lines):
        if line.strip() == 'class State {':
            class_start = i
        if class_start != -1 and line.strip().startswith('constructor()'):
            constructor_start = i
            break

    if class_start == -1 or constructor_start == -1:
        print("Could not find State class or constructor")
        return

    # Properties we want to ensure are declared
    state_properties = [
        ('_state', 'any'),
        ('_subscribers', 'any[]'),
        ('_cache', 'any'),
        ('_cacheReady', 'boolean'),
        ('_isNotifying', 'boolean'),
        ('tagAll', 'Map<string, number>'),
        ('tagSites', 'Map<string, string[]>'),
        ('activeTags', 'Set<string>'),
        ('_tagInitialized', 'boolean')
    ]

    # Check which properties are already declared in the class body (between class_start and constructor_start)
    declared = set()
    for i in range(class_start + 1, constructor_start):
        line = lines[i]
        for prop_name, prop_type in state_properties:
            if f'{prop_name}: {prop_type}' in line:
                declared.add(prop_name)

    # Insert missing properties just before the constructor
    insert_lines = []
    for prop_name, prop_type in state_properties:
        if prop_name not in declared:
            insert_lines.append(f'    {prop_name}: {prop_type};')

    if insert_lines:
        # Insert a blank line before the properties if the line before constructor is not blank
        if constructor_start > 0 and lines[constructor_start - 1].strip() != '':
            insert_lines.insert(0, '')
        # Insert the properties
        for i, line in enumerate(insert_lines):
            lines.insert(constructor_start + i, line + '\n')
        print(f"Added {len(insert_lines)} missing properties to State class in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def fix_datamanager_class(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the class DataManager and the constructor
    class_start = -1
    constructor_start = -1
    for i, line in enumerate(lines):
        if line.strip() == 'class DataManager {':
            class_start = i
        if class_start != -1 and line.strip().startswith('constructor()'):
            constructor_start = i
            break

    if class_start == -1 or constructor_start == -1:
        print("Could not find DataManager class or constructor")
        return

    # Properties we want to ensure are declared
    dm_properties = [
        ('raw', 'any'),
        ('sites', 'Map<string, any>'),
        ('categories', 'any'),
        ('mappings', 'Map<string, any>'),
        ('tagIndex', 'Map<string, any>'),
        ('tagCloud', 'Map<string, any>'),
        ('isLoaded', 'boolean'),
        ('version', 'any'),
        ('_loadError', 'any'),
        ('tagIndexSorted', 'any')  # we saw it used, but not sure of the type
    ]

    # Check which properties are already declared in the class body (between class_start and constructor_start)
    declared = set()
    for i in range(class_start + 1, constructor_start):
        line = lines[i]
        for prop_name, prop_type in dm_properties:
            if f'{prop_name}: {prop_type}' in line:
                declared.add(prop_name)

    # Insert missing properties just before the constructor
    insert_lines = []
    for prop_name, prop_type in dm_properties:
        if prop_name not in declared:
            insert_lines.append(f'    {prop_name}: {prop_type};')

    if insert_lines:
        # Insert a blank line before the properties if the line before constructor is not blank
        if constructor_start > 0 and lines[constructor_start - 1].strip() != '':
            insert_lines.insert(0, '')
        # Insert the properties
        for i, line in enumerate(insert_lines):
            lines.insert(constructor_start + i, line + '\n')
        print(f"Added {len(insert_lines)} missing properties to DataManager class in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def fix_common_errors_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We'll do a series of replacements for common patterns
    # We'll use regex to be more precise, but we'll do simple string replacements for now.

    # Patterns for EventTarget properties
    # We'll replace:
    #   e.target.value -> (e.target as HTMLInputElement).value
    #   event.target.value -> (event.target as HTMLInputElement).value
    content = re.sub(r'\be\.target\.value\b', '(e.target as HTMLInputElement).value', content)
    content = re.sub(r'\bevent\.target\.value\b', '(event.target as HTMLInputElement).value', content)

    #   e.target.closest( -> (e.target as Element).closest(
    #   event.target.closest( -> (event.target as Element).closest(
    content = re.sub(r'\be\.target\.closest\(', '(e.target as Element).closest(', content)
    content = re.sub(r'\bevent\.target\.closest\(', '(event.target as Element).closest(', content)

    #   e.target.style -> (e.target as HTMLElement).style
    #   event.target.style -> (event.target as HTMLElement).style
    content = re.sub(r'\be\.target\.style\b', '(e.target as HTMLElement).style', content)
    content = re.sub(r'\bevent\.target\.style\b', '(event.target as HTMLElement).style', content)

    #   e.target.tagName -> (e.target as Element).tagName
    #   event.target.tagName -> (event.target as Element).tagName
    content = re.sub(r'\be\.target\.tagName\b', '(e.target as Element).tagName', content)
    content = re.sub(r'\bevent\.target\.tagName\b', '(event.target as Element).tagName', content)

    #   e.target.src -> (e.target as HTMLImageElement).src
    #   event.target.src -> (event.target as HTMLImageElement).src
    content = re.sub(r'\be\.target\.src\b', '(e.target as HTMLImageElement).src', content)
    content = re.sub(r'\bevent\.target\.src\b', '(event.target as HTMLImageElement).src', content)

    #   e.target.dataset -> (e.target as Element).dataset
    #   event.target.dataset -> (event.target as Element).dataset
    content = re.sub(r'\be\.target\.dataset\b', '(e.target as Element).dataset', content)
    content = re.sub(r'\bevent\.target\.dataset\b', '(event.target as Element).dataset', content)

    # Patterns for Event properties
    #   e.key -> (e as KeyboardEvent).key
    #   event.key -> (event as KeyboardEvent).key
    content = re.sub(r'\be\.key\b', '(e as KeyboardEvent).key', content)
    content = re.sub(r'\bevent\.key\b', '(event as KeyboardEvent).key', content)

    # Fix toggleSidebar -> toggleSearch (we saw in app.ts)
    content = re.sub(r'\btoggleSidebar\b', 'toggleSearch', content)

    # Fix renderSites(false) -> renderSites(false, 'main-content') if not already fixed
    # We'll look for renderSites(false); and replace it, but only if it's not already followed by a second argument.
    # We'll do a more precise replacement: replace renderSites(false) with renderSites(false, 'main-content')
    # but only when it's not already renderSites(false, ...)
    # We'll use a regex that matches renderSites(false) not followed by a comma and then something.
    # We'll do: renderSites\(false\)(?!\s*,)
    content = re.sub(r'renderSites\(false\)(?!\s*,)', 'renderSites(false, \'main-content\')', content)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    root_dir = 'assets/js'
    # Fix State and DataManager classes
    fix_state_class(os.path.join(root_dir, 'state.ts'))
    fix_datamanager_class(os.path.join(root_dir, 'data.ts'))

    # Walk through all .ts files and fix common errors
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.ts'):
                filepath = os.path.join(dirpath, filename)
                fix_common_errors_in_file(filepath)
                print(f'Processed {filepath}')

if __name__ == '__main__':
    main()