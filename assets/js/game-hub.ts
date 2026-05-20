/**
 * GameHub - 游戏大厅管理与路由（已完整：9游戏）
 */
var GameHub = {
    games: {
        solitaire: { name: '🃏 纸牌接龙', icon: '🃏', desc: '经典Klondike单人纸牌', cat: 'classic', rating: 5, constructor: null },
        tetris:    { name: '🟩 俄罗斯方块', icon: '🟩', desc: '永不过时的方块消除',   cat: 'classic', rating: 5, constructor: null },
        go:        { name: '⚫ 围棋',      icon: '⚫', desc: '黑白纵横，千年智慧',   cat: 'strategy', rating: 4, constructor: null },
        chess:     { name: '♟️ 象棋',      icon: '♟️', desc: '中国象棋在线对战AI',   cat: 'strategy', rating: 5, constructor: null },
        mahjong:   { name: '🀄 麻将',      icon: '🀄', desc: '四川麻将简约版',       cat: 'classic', rating: 4, constructor: null },
        wuxia:     { name: '⚔️ 武侠世界',   icon: '⚔️', desc: '武侠剧情杀怪升级',     cat: 'rpg', rating: 4, constructor: null },
        dating:    { name: '💕 恋爱大富翁', icon: '💕', desc: '恋爱养成+大富翁',     cat: 'rpg', rating: 3, constructor: null },
        game2048:  { name: '🔢 2048',       icon: '🔢', desc: '数字滑动合体挑战',     cat: 'puzzle', rating: 5, constructor: null },
        gomoku:    { name: '⚫ 五子棋',     icon: '⚫', desc: '15路棋盘双人对弈',     cat: 'strategy', rating: 4, constructor: null }
    },
    currentGame: null,
    currentEngine: null,

    init: function() {
        // 注册打开/关闭事件
        var toggle = document.getElementById('game-menu-toggle');
        var close = document.getElementById('game-hub-close');
        var overlay = document.getElementById('game-hub-overlay');

        if (toggle) toggle.addEventListener('click', function() { GameHub.openHub(); });
        if (close) close.addEventListener('click', function() { GameHub.closeHub(); });
        if (overlay) overlay.addEventListener('click', function(e) {
            if (e.target === overlay) GameHub.closeHub();
        });

        // 分类按钮（all, classic, strategy, rpg, puzzle 等）
        document.querySelectorAll('.game-cat-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.game-cat-btn').forEach(function(b) { b.classList.remove('active'); });
                this.classList.add('active');
                GameHub._filterCategory(this.dataset.cat);
            }.bind(btn));
        });

        // 音效开关
        var soundBtn = document.getElementById('game-sound-toggle');
        if (soundBtn) {
            soundBtn.addEventListener('click', function() {
                GameUtils.toggleSound();
                soundBtn.textContent = GameUtils.soundEnabled ? '🔊' : '🔇';
                soundBtn.title = GameUtils.soundEnabled ? '音效开' : '音效关';
            });
        }

        // 退出游戏
        var quitBtn = document.getElementById('game-quit-btn');
        if (quitBtn) quitBtn.addEventListener('click', function() { GameHub.closeGame(); });

        // 渲染游戏网格
        this.renderGrid('all');
    },

    renderGrid: function(category) {
        this.currentCat = category; // 保存当前分类，便于后续重渲染
        var grid = document.getElementById('game-grid');
        if (!grid) return;
        grid.innerHTML = '';
        var self = this;
        Object.keys(this.games).forEach(function(key) {
            var game = self.games[key];
            if (game.hidden) return; // 支持隐藏标记
            if (category !== 'all') {
                if (category === 'recent') {
                    if (!self._isRecent(key)) return;
                } else {
                    if (game.cat !== category) return;
                }
            }
            var card = document.createElement('div');
            card.className = 'game-card';
            var saveData = GameUtils.load('gn_save_' + key);
            if (saveData) card.classList.add('has-save');

            // 新游戏标签
            var badge = saveData ? '<span class="game-card-badge">💾 继续</span>' : '';

            // 评分星星
            var stars = '<div class="game-card-stars" aria-label="评分 ' + (game.rating || 0) + ' 星">' +
                '★'.repeat(game.rating || 0) +
                '</div>';

            // 收藏按钮（复用 favorite 系统）
            var isFav = window.favoriteManager && window.favoriteManager.isFavorite(game.name);
            var favHeart = isFav ? '♥' : '♡';
            var favClass = isFav ? 'favorite-btn favorited' : 'favorite-btn';
            var favBtn = '<button class="' + favClass + '" data-game-key="' + key + '" onclick="event.stopPropagation();GameHub.toggleGameFav(\'' + key + '\');" aria-label="收藏游戏">' + favHeart + '</button>';

            card.innerHTML = '<span class="game-card-icon">' + game.icon + '</span>' +
                '<div class="game-card-name">' + game.name + '</div>' +
                '<div class="game-card-desc">' + game.desc + '</div>' +
                stars + badge + favBtn;
            card.addEventListener('click', function() { self.startGame(key); });
            grid.appendChild(card);
        });
    },

    _filterCategory: function(cat) { this.renderGrid(cat); },

    openHub: function() {
        this.renderGrid('all');
        document.getElementById('game-hub-overlay').classList.add('active');
        // 重置分类按钮
        document.querySelectorAll('.game-cat-btn').forEach(function(b) {
            b.classList.toggle('active', b.dataset.cat === 'all');
        });
    },

    closeHub: function() {
        document.getElementById('game-hub-overlay').classList.remove('active');
    },


    renderContainer: function() {
        // 如果容器已存在，跳过
        if (document.getElementById('game-play-overlay')) return;

        var container = document.createElement('div');
        container.id = 'game-play-overlay';
        container.className = 'game-play-overlay';
        container.innerHTML = 
            '<div class="game-wrapper">' +
                '<header class="game-header">' +
                    '<span id="game-play-title" class="game-title">游戏</span>' +
                    '<div class="game-header-controls">' +
                        '<button id="game-sound-toggle" class="game-sound-toggle" title="音效" aria-label="切换音效">🔊</button>' +
                        '<span id="game-play-level" class="game-level-display" title="当前等级">Lv.1</span>' +
                        '<button id="game-close-btn" class="game-close" aria-label="关闭游戏">&times;</button>' +
                    '</div>' +
                '</header>' +
                '<div id="game-canvas-container">' +
                    '<canvas id="game-canvas" class="game-canvas"></canvas>' +
                    '<div id="game-play-area" style="display:none;"></div>' +
                '</div>' +
                '<footer class="game-footer">' +
                    '<span id="game-play-score">Score: 0</span>' +
                    '<span id="game-play-time">Time: 00:00</span>' +
                '</footer>' +
            '</div>';
        document.body.appendChild(container);
    },

    startGame: function(gameKey) {
        var self = this;
        this.closeHub();
        this.currentGame = gameKey;
        this._gameStartTime = Date.now(); // 记录游戏启动时间

        // 统计：游戏启动事件
        if (typeof window.trackSiteClick === 'function') {
            window.trackSiteClick('game: ' + this.games[gameKey].name);
        }

        // 重置游戏状态 UI
        var scoreEl = document.getElementById('game-play-score');
        var levelEl = document.getElementById('game-play-level');
        if (scoreEl) scoreEl.textContent = 'Score: 0';
        if (levelEl) levelEl.textContent = 'Lv.1';
        // 恢复音效按钮状态
        var soundBtn = document.getElementById('game-sound-toggle');
        if (soundBtn) {
            soundBtn.textContent = GameUtils.soundEnabled ? '🔊' : '🔇';
            soundBtn.title = GameUtils.soundEnabled ? '音效开' : '音效关';
        }


        // 动态加载游戏模块映射（9个游戏）
        var gameMap = {
            solitaire: 'Solitaire',
            tetris:    'Tetris',
            go:        'GoGame',
            chess:     'ChessGame',
            mahjong:   'MahjongGame',
            wuxia:     'WuxiaGame',
            dating:    'DatingGame',
            game2048:  'Game2048',
            gomoku:    'Gomoku'
        };
        var ctorName = gameMap[gameKey];
        var ctor = window[ctorName];

        if (!ctor) {
            GameHub.showToast('游戏模块 "' + gameKey + '" 尚未加载完成，请稍后再试');
            document.getElementById('game-play-title').textContent = this.games[gameKey].name;
            document.getElementById('game-play-area').innerHTML =
                '<div style="text-align:center;padding:60px;color:var(--color-text-dim)">' +
                '<div style="font-size:48px;margin-bottom:16px">🛠️</div>' +
                '<div>游戏 "' + gameKey + '" 正在全力开发中</div>' +
                '<div style="margin-top:12px;font-size:12px">敬请期待！</div></div>';
            document.getElementById('game-play-overlay').classList.add('active');
            return;
        }

        this.currentEngine = new ctor();

        this.currentEngine.onGameOver = function(score, elapsed) {
            GameHub.showToast('🎮 游戏结束！得分: ' + score + ' | 用时: ' + GameUtils.formatTime(elapsed));
        };

        // 记录最近游戏
        this.pushRecent(gameKey);

        // 显示游戏界面
        var playOverlay = document.getElementById('game-play-overlay');
        document.getElementById('game-play-title').textContent = this.currentEngine.title;
        document.getElementById('game-play-score').textContent = 'Score: ' + this.currentEngine.score;
        playOverlay.classList.add('active');

        this.currentEngine.init();
    },

    closeGame: function() {
        if (this.currentEngine) {
            if (this.currentEngine.save) this.currentEngine.save();
            if (this.currentEngine.destroy) this.currentEngine.destroy();
            this.currentEngine = null;
        }
        // 记录游戏时长统计（本次 session）
        if (this.currentGame && this._gameStartTime) {
            var elapsed = Date.now() - this._gameStartTime;
            var statsKey = 'gn_stats_' + this.currentGame;
            try {
                var raw = localStorage.getItem(statsKey);
                var entry = raw ? JSON.parse(raw) : { totalSeconds: 0, sessions: 0 };
                entry.lastDuration = elapsed;
                entry.totalSeconds += Math.floor(elapsed / 1000);
                entry.sessions += 1;
                entry.lastPlayed = new Date().toISOString();
                localStorage.setItem(statsKey, JSON.stringify(entry));
            } catch(e) {}
        }
        if (this.currentGame) this._gameStartTime = null;
        this.currentGame = null;
        document.getElementById('game-play-overlay').classList.remove('active');
    },

    showToast: function(msg, duration) {
        var t = document.getElementById('toast-container');
        if (t && typeof toast === 'function') {
            toast(msg, duration || 3000);
        } else {
            var el = document.createElement('div');
            el.style.cssText = 'position:fixed;bottom:30px;left:50%;transform:translateX(-50%);' +
                'background:var(--color-bg-alt, #1a1a2e);color:var(--color-text,#e2e8f0);' +
                'padding:12px 24px;border-radius:8px;border:1px solid var(--color-border,#333);' +
                'z-index:9999;transition:opacity .3s;font-size:14px;';
            el.textContent = msg;
            document.body.appendChild(el);
            setTimeout(function() { el.style.opacity = '0'; }, (duration || 3000) - 400);
            setTimeout(function() { if (el.parentNode) el.parentNode.removeChild(el); }, duration || 3000);
        }
    },

    // 切换游戏收藏状态（复用 favorite 系统）
    toggleGameFav: function(key) {
        if (!this.games[key]) return;
        var game = this.games[key];
        var favManager = window.favoriteManager;
        if (!favManager) return;

        var isFav = favManager.isFavorite(game.name);
        var result;
        if (isFav) {
            result = favManager.remove(game.name);
        } else {
            result = favManager.add({
                name: game.name,
                url: '#game/' + key,
                category: '游戏',
                icon: game.icon,
                description: game.desc
            });
        }
        if (result && result.success) {
            // 重新渲染当前分类网格（更新所有按钮状态）
            if (this.currentCat) this.renderGrid(this.currentCat);
        }
    },

    formatTime: GameUtils ? GameUtils.formatTime : function(ms) {
        var s = Math.floor(ms / 1000), m = Math.floor(s / 60);
        s = s % 60;
        return (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
    },

    // === 最近游戏 ===
    _RECENT_MAX: 5,
    _RECENT_KEY: 'gn_recent_games_v1',

    // 格式化时间并写入最近游戏
    pushRecent: function(key) {
        var list = GameHub._loadRecent();
        // 去重并移到开头
        list = list.filter(function(k) { return k !== key; });
        list.unshift(key);
        if (list.length > GameHub._RECENT_MAX) list.length = GameHub._RECENT_MAX;
        try { localStorage.setItem(GameHub._RECENT_KEY, JSON.stringify(list)); } catch(e) {}
    },

    _loadRecent: function() {
        try {
            var raw = localStorage.getItem(GameHub._RECENT_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch(e) { return []; }
    },

    _isRecent: function(key) {
        return GameHub._loadRecent().indexOf(key) !== -1;
    }
};

document.addEventListener('DOMContentLoaded', function() {
    GameHub.init();
});