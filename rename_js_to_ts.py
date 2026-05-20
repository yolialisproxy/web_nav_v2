import os
import re
import sys

def rename_and_fix_imports(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.js'):
                js_path = os.path.join(dirpath, filename)
                ts_path = os.path.join(dirpath, filename[:-3] + '.ts')
                print(f'Renaming {js_path} -> {ts_path}')
                os.rename(js_path, ts_path)
                
                # Now fix imports in the .ts file
                with open(ts_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Pattern to match import/require with .js extension
                # Matches: from 'file.js', from "file.js", require('file.js'), require("file.js")
                # Also accounts for optional spaces and different quote styles
                def replace_js_extension(match):
                    # match groups: 
                    #   group1: 'from' or 'require'
                    #   group2: quote character (either ' or ")
                    #   group3: the path inside (without .js)
                    #   group4: the same quote character as group2 (because we used \2 for the closing quote)
                    # Actually, we designed the pattern to have:
                    #   (from|require)\s*([\'"])([^\'"]*)\.js\2
                    # So group1: from/require, group2: quote, group3: path, group4: quote (same as group2)
                    # We want to keep the quote and remove the .js, so we return group1 + group2 + group3 + group2
                    return f'{match.group(1)}{match.group(2)}{match.group(3)}{match.group(2)}'
                
                pattern = r'(from|require)\s*([\'"])([^\'"]*)\.js\2'
                new_content = re.sub(pattern, replace_js_extension, content)
                
                if new_content != content:
                    print(f'  Fixed imports in {ts_path}')
                    with open(ts_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == '__main__':
    root_dir = os.path.join(os.getcwd(), 'assets/js')
    if not os.path.exists(root_dir):
        print(f'Error: {root_dir} does not exist')
        sys.exit(1)
    rename_and_fix_imports(root_dir)
    print('Done renaming and fixing imports.')