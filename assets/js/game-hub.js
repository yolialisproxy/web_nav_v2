/**
 * GameHub - 游戏大厅管理与路由（已完整：9游戏）
 */
var GameHub = {
    games: {
        solitaire: { name: '🃏 纸牌接龙', icon: '🃏', desc: '经典Klondike单人纸牌', cat: 'classic', constructor: null },
        tetris:    { name: '🟩 俄罗斯方块', icon: '🟩', desc: '永不过时的方块消除', cat: 'classic', constructor: null },
        go:        { name: '⚫ 围棋',      icon: '⚫', desc: '黑白纵横，千年智慧',   cat: 'strategy', constructor: null },
        chess:     { name: '♟️ 象棋',      icon: '♟️', desc: '中国象棋在线对战AI',   cat: 'strategy', constructor: null },
        mahjong:   { name: '🀄 麻将',      icon: '🀄', desc: '四川麻将简约版',       cat: 'classic', constructor: null },
        wuxia:     { name: '⚔️ 武侠世界',   icon: '⚔️', desc: '武侠剧情杀怪升级',     cat: 'rpg', constructor: null },
        dating:    { name: '💕 恋爱大富翁', icon: '💕', desc: '恋爱养成+大富翁',     cat: 'rpg', constructor: null },
        game2048:  { name: '🔢 2048',       icon: '🔢', desc: '数字滑动合体挑战',     cat: 'puzzle', constructor: null },
        gomoku:    { name: '⚫ 五子棋',     icon: '⚫', desc: '15路棋盘双人对弈',     cat: 'strategy', constructor: null }
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
        var grid = document.getElementById('game-grid');
        if (!grid) return;
        grid.innerHTML = '';
        var self = this;
        Object.keys(this.games).forEach(function(key) {
            var game = self.games[key];
            if (game.hidden) return; // 支持隐藏标记
            if (category !== 'all' && game.cat !== category) return;
            var card = document.createElement('div');
            card.className = 'game-card';
            var saveData = GameUtils.load('gn_save_' + key);
            if (saveData) card.classList.add('has-save');

            // 新游戏标签
            var badge = saveData ? '<span class="game-card-badge">💾 继续</span>' : '';

            card.innerHTML = '<span class="game-card-icon">' + game.icon + '</span>' +
                '<div class="game-card-name">' + game.name + '</div>' +
                '<div class="game-card-desc">' + game.desc + '</div>' + badge;
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

    formatTime: GameUtils ? GameUtils.formatTime : function(ms) {
        var s = Math.floor(ms / 1000), m = Math.floor(s / 60);
        s = s % 60;
        return (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
    }
};

document.addEventListener('DOMContentLoaded', function() {
    GameHub.init();
});