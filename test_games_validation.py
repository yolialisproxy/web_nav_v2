#!/usr/bin/env python3
"""
游戏版块快速验证脚本
使用方法: python3 test_games.py
"""

import os, re, json

ROOT = '/home/yoli/GitHub/web_nav_v2'

def check_file(path, desc):
    exists = os.path.exists(path)
    print(f'{"✅" if exists else "❌"} {desc}: {path.split("/")[-1]}')
    return exists

print('=== 游戏版块验证 ===\n')

# 1. 检查游戏文件
print('【1】游戏文件检查:')
games = [
    ('assets/js/games/game-engine.js', 'GameEngine 基类'),
    ('assets/js/games/solitaire.js',  '纸牌接龙'),
    ('assets/js/games/tetris.js',     '俄罗斯方块'),
    ('assets/js/games/go.js',         '围棋'),
    ('assets/js/games/chess.js',      '象棋'),
    ('assets/js/games/mahjong.js',    '麻将'),
    ('assets/js/games/wuxia.js',      '武侠世界'),
    ('assets/js/games/dating.js',     '恋爱大富翁'),
    ('assets/js/games/2048.js',       '2048'),
    ('assets/js/games/gomoku.js',     '五子棋'),
]
all_exist = all(check_file(os.path.join(ROOT, p), d) for p,d in games)
print()

# 2. 检查 HTML 注册
print('【2】HTML 脚本引入检查:')
with open(os.path.join(ROOT, 'index.html')) as f:
    html = f.read()
game_scripts = re.findall(r'src=["\']([^"\']*games/[^"\']+\.js)["\']', html)
print(f'✅ 找到 {len(game_scripts)} 个游戏脚本')
for s in game_scripts:
    print(f'   - {s}')
print()

# 3. 检查分类按钮
print('【3】游戏大厅分类按钮:')
cats = re.findall(r'data-cat=["\']([^"\']+)["\']', html)
print(f'   ✅ 分类: {", ".join(set(cats))}')
print()

# 4. 检查 game-hub 注册
print('【4】game-hub.js 游戏注册表:')
with open(os.path.join(ROOT, 'assets/js/game-hub.js')) as f:
    hub = f.read()
registered = re.findall(r'(\w+):\s*\{[^}]*cat:\s*["\'](\w+)', hub)
print(f'   共注册 {len(registered)} 个游戏:')
for name, cat in registered:
    print(f'   ✅ {name:15s} → {cat}')
print()

# 5. 结构验证
print('【5】接口方法验证:')
required = ['init', 'save', 'load', 'quit']
issues = []
for path, desc in games[1:]:  # skip engine
    fpath = os.path.join(ROOT, path)
    ctor = desc.replace('纸牌','Solitaire').replace('俄罗斯','Tetris').replace('围棋','GoGame')\
               .replace('象棋','ChessGame').replace('麻将','MahjongGame')\
               .replace('武侠','WuxiaGame').replace('恋爱','DatingGame')\
               .replace('2048','Game2048').replace('五子棋','Gomoku')
    with open(fpath) as f:
        content = f.read()
    missing = [m for m in required if not re.search(r'\.prototype\.' + m + r'\s*=', content)]
    if missing:
        issues.append((desc, missing))
        print(f'❌ {desc}: 缺 {", ".join(missing)}')
    else:
        print(f'✅ {desc}: {", ".join(required)} 全')

print()
if issues:
    print(f'❌ 发现 {len(issues)} 个游戏有问题')
else:
    print('✅ 全部9个游戏接口完整！')

print('\n=== 验证完成 ===')
print('建议: 启动 python3 -m http.server 8000 手动浏览器测试')
