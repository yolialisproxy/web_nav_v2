"use strict";
/**
 * Game Engine - 通用游戏引擎基类
 */
var GameEngine = function (config) {
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
    init: function () {
        var area = document.getElementById(this.containerId);
        if (!area)
            return;
        area.innerHTML = '<div class="game-inner" id="game-' + this.id + '"></div>';
        this.el = document.getElementById('game-' + this.id);
        this.scoreEl = document.getElementById('game-play-score');
        this.titleEl = document.getElementById('game-play-title');
        this.titleEl.textContent = this.title;
        this.footerEl = document.getElementById('game-play-footer');
        this._bindControls();
    },
    // 绑定控制器
    _bindControls: function () {
        var self = this;
        var quitBtn = document.getElementById('game-quit-btn');
        var pauseBtn = document.getElementById('game-pause-btn');
        if (quitBtn) {
            quitBtn.onclick = function () {
                if (confirm('确定要退出游戏吗？'))
                    self.quit();
            };
        }
        if (pauseBtn) {
            pauseBtn.onclick = function () { self.togglePause(); };
        }
    },
    // 开始
    start: function () {
        this.state = 'running';
        this._stats.startTime = Date.now();
        this.level = 1;
        this.score = 0;
        this.moves = 0;
        this._updateUI();
    },
    // 暂停/恢复
    togglePause: function () {
        if (this.state === 'running') {
            this.state = 'paused';
            this._stopLoop();
            this.showPauseScreen();
        }
        else if (this.state === 'paused') {
            this.state = 'running';
            this._startLoop();
            this.hidePauseScreen();
        }
    },
showPauseScreen: function () {
	if (this.el) {
		this._pauseOverlay = document.createElement('div');
		this._pauseOverlay.style.cssText = 'position:absolute;inset:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:99;';
		this._pauseOverlay.innerHTML = '<div style="color:#fff;font-size:28px;font-weight:bold;text-align:center;">⏸️ 暂停中<br><span style="font-size:14px;opacity:0.7;">点击暂停继续</span></div>';
		var self = this;
		this._pauseOverlay.onclick = function () { self.togglePause(); };
		this.el.style.position = 'relative';\n		this.el.appendChild(this._pauseOverlay);
	}
	},
