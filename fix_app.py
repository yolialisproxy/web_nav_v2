import os
import sys

def fix_app_ts(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # We'll process line by line
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Fix renderSites(false) -> renderSites(false, 'main-content')
        if line.strip() == 'renderSites(false);':
            new_lines.append("        renderSites(false, 'main-content');\n")
            i += 1
            continue
        # Fix Property 'value' does not exist on type 'EventTarget'
        # Typically: e.target.value -> (e.target as HTMLInputElement).value
        # We'll look for patterns like .value where the left side is EventTarget
        # This is heuristic; we'll do simple replacements for common patterns
        if '.value' in line and ('e.target' in line or 'event.target' in line):
            line = line.replace('e.target.value', '(e.target as HTMLInputElement).value')
            line = line.replace('event.target.value', '(event.target as HTMLInputElement).value')
        # Fix Property 'closest' does not exist on type 'EventTarget'
        if '.closest(' in line and ('e.target' in line or 'event.target' in line):
            line = line.replace('e.target.closest(', '(e.target as Element).closest(')
            line = line.replace('event.target.closest(', '(event.target as Element).closest(')
        # Fix Property 'style' does not exist on type 'Element' - actually Element has style, so maybe it's not Element?
        # If it's something like `element.style` where element is EventTarget, we need to cast
        if '.style' in line and ('e.target' in line or 'event.target' in line):
            line = line.replace('e.target.style', '(e.target as HTMLElement).style')
            line = line.replace('event.target.style', '(event.target as HTMLElement).style')
        # Fix Property 'tagName' does not exist on type 'EventTarget'
        if '.tagName' in line and ('e.target' in line or 'event.target' in line):
            line = line.replace('e.target.tagName', '(e.target as Element).tagName')
            line = line.replace('event.target.tagName', '(event.target as Element).tagName')
        # Fix Property 'src' does not exist on type 'EventTarget'
        if '.src' in line and ('e.target' in line or 'event.target' in line):
            line = line.replace('e.target.src', '(e.target as HTMLImageElement).src')
            line = line.replace('event.target.src', '(event.target as HTMLImageElement).src')
        # Fix Cannot find name 'toggleSidebar'
        if 'toggleSidebar()' in line:
            line = line.replace('toggleSidebar()', 'toggleSearch()')  # based on the suggestion
        # Fix Property 'stop' does not exist on type { games: ... }
        # This is likely: game.stop() where game is from the games object
        # We'll need to see context; for now, we'll leave it and maybe fix later
        # Fix Property 'visitKey' does not exist on type 'FavoriteManager' etc. - those are in favorite.ts
        
        new_lines.append(line)
        i += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    fix_app_ts('assets/js/app.ts')
    print('Fixed app.ts')