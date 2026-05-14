/**
 * Game Engine - 通用游戏引擎基类
 */
var GameEngine = function(config) {
    this.config = config || {};
    this.id = config.id || 'game';
    this.containerId = config.containerId || 'game-play-area';
    this.title = config.title || '游戏';
    this.state = 'idle'; // idle | running | paused | over
    this.score = 0;
    this.level = 1;
    this.lines = 0;
    this._timer = null;
    this._animFrame = null;
    this._stats = { startTime: 0, moves: 0, errors: 0 };
    this.saveKey = 'gn_save_' + this.id;
};

GameEngine.prototype = {
    // 初始化游戏界面
    init: function() {
        var area = document.getElementById(this.containerId);
        if (!area) return;
        area.innerHTML = '<div class="game-inner" id="game-' + this.id + '"></div>';
        this.el = document.getElementById('game-' + this.id);
        this.scoreEl = document.getElementById('game-play-score');
        this.titleEl = document.getElementById('game-play-title');
        this.titleEl.textContent = this.title;
        this.footerEl = document.getElementById('game-play-footer');
        this._bindControls();
    },

    // 绑定控制器
    _bindControls: function() {
        var self = this;
        var quitBtn = document.getElementById('game-quit-btn');
        var pauseBtn = document.getElementById('game-pause-btn');
        
        if (quitBtn) {
            quitBtn.onclick = function() {
                if (confirm('确定要退出游戏吗？')) self.quit();
            };
        }
        if (pauseBtn) {
            pauseBtn.onclick = function() { self.togglePause(); };
        }
    },

    // 开始
    start: function() {
        this.state = 'running';
        this._stats.startTime = Date.now();
        this.level = 1;
        this.score = 0;
        this.moves = 0;
        this._updateUI();
    },

    // 暂停/恢复
    togglePause: function() {
        if (this.state === 'running') {
            this.state = 'paused';
            this._stopLoop();
            this.showPauseScreen();
        } else if (this.state === 'paused') {
            this.state = 'running';
            this._startLoop();
            this.hidePauseScreen();
        }
    },

    showPauseScreen: function() {
        if (this.el) {
            this._pauseOverlay = document.createElement('div');
            this._pauseOverlay.style.cssText = 'position:absolute;inset:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:99;';
            this._pauseOverlay.innerHTML = '<div style="color:#fff;font-size:28px;font-weight:bold;text-align:center;">⏸️ 暂停中<br><span style="font-size:14px;opacity:0.7;">点击暂停继续</span></div>';
            this._pauseOverlay.onclick = function() { GameEngine._inst && GameEngine._inst.togglePause(); };
            this.el.style.position = 'relative';
            this.el.appendChild(this._pauseOverlay);
        }
    },

    hidePauseScreen: function() {
        if (this._pauseOverlay && this._pauseOverlay.parentNode) {
            this._pauseOverlay.parentNode.removeChild(this._pauseOverlay);
            this._pauseOverlay = null;
        }
    },

    // 停止游戏循环
    _stopLoop: function() {
        if (this._timer) { clearInterval(this._timer); this._timer = null; }
        if (this._animFrame) { cancelAnimationFrame(this._animFrame); this._animFrame = null; }
    },

    // 启动游戏循环（间隔模式）
    _startLoop: function(interval) {
        var self = this;
        this._stopLoop();
        this._timer = setInterval(function() { self.tick(); }, interval || this._getInterval());
    },

    _getInterval: function() {
        return Math.max(100, 800 - (this.level - 1) * 50);
    },

    // 每帧逻辑（子类重写）
    tick: function() { /* override */ },

    // 更新分数
    addScore: function(points) {
        this.score += points;
        this.moves++;
        this._updateUI();
    },

    // 等级计算
    _calcLevel: function() {
        return Math.floor(this.lines / 10) + 1;
    },

    // 提升一级
    levelUp: function() {
        this.level++;
        this._calcLevel();
        // 播放升级音效
        GameUtils.playSfx('levelUp');
    },


    // 更新UI
    _updateUI: function() {
        if (this.scoreEl) this.scoreEl.textContent = 'Score: ' + this.score;
    },

    // 保存
    save: function() {
        var data = {
            score: this.score,
            level: this.level,
            lines: this.lines,
            state: this.state,
            stats: this._stats,
            savedAt: Date.now()
        };
        GameUtils.save(this.saveKey, data);
    },

    // 加载
    load: function() {
        var data = GameUtils.load(this.saveKey);
        if (data) {
            this.score = data.score || 0;
            this.level = data.level || 1;
            this.lines = data.lines || 0;
            this._stats = data.stats || this._stats;
            return data;
        }
        return null;
    },

    // 清除存档
    clearSave: function() {
        GameUtils.clear(this.saveKey);
    },

    // 游戏结束
    gameOver: function() {
        this.state = 'over';
        this._stopLoop();
        var elapsed = Date.now() - this._stats.startTime;
        if (this.onGameOver) this.onGameOver(this.score, elapsed);
    },

    // 退出
    quit: function() {
        this._stopLoop();
        this.state = 'idle';
        GameHub.closeGame();
    },

    // 销毁
    destroy: function() {
        this._stopLoop();
        this.el = null;
    }
};