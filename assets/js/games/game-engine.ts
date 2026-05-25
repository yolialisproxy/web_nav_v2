"use strict";
/**
 * Game Engine - 通用游戏引擎基类
 */
class GameEngine {
    config: any;
    id: string;
    containerId: string;
    title: string;
    state: 'idle' | 'running' | 'paused' | 'over';
    score: number;
    level: number;
    lines: number;
    moves: number;
    protected _timer: any;
    private _animFrame: any;
    _stats: { startTime: number; moves: number; errors: number };
    saveKey: string;
    el: any;
    scoreEl: any;
    titleEl: any;
    footerEl: any;
    _pauseOverlay: any;

    constructor(config: any) {
        this.config = config || {};
        this.id = config.id || 'game';
        this.containerId = config.containerId || 'game-play-area';
        this.title = config.title || '游戏';
        this.state = 'idle';
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.moves = 0;
        this._timer = null;
        this._animFrame = null;
        this._stats = { startTime: 0, moves: 0, errors: 0 };
        this.saveKey = 'gn_save_' + this.id;
    }

    init(): void {
        const area = document.getElementById(this.containerId);
        if (!area) return;
        area.innerHTML = `<div class="game-inner" id="game-${this.id}"></div>`;
        this.el = document.getElementById(`game-${this.id}`);
        this.scoreEl = document.getElementById('game-play-score');
        this.titleEl = document.getElementById('game-play-title');
        this.titleEl.textContent = this.title;
        this.footerEl = document.getElementById('game-play-footer');
        this._bindControls();
    }

    private _bindControls(): void {
        const self = this;
        const quitBtn = document.getElementById('game-quit-btn');
        const pauseBtn = document.getElementById('game-pause-btn');
        if (quitBtn) {
            quitBtn.onclick = () => {
                if (confirm('确定要退出游戏吗？')) {
                    self.quit();
                }
            };
        }
        if (pauseBtn) {
            pauseBtn.onclick = () => self.togglePause();
        }
    }

    start(): void {
        this.state = 'running';
        this._stats.startTime = Date.now();
        this.level = 1;
        this.score = 0;
        this.moves = 0;
        this._updateUI();
    }

    togglePause(): void {
        if (this.state === 'running') {
            this.state = 'paused';
            this._stopLoop();
            this.showPauseScreen();
        } else if (this.state === 'paused') {
            this.state = 'running';
            this._startLoop();
            this.hidePauseScreen();
        }
    }

    showPauseScreen(): void {
        if (this.el) {
            this._pauseOverlay = document.createElement('div');
            this._pauseOverlay.style.cssText = 'position:absolute;inset:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:99';
            this._pauseOverlay.innerHTML = `<div style="color:#fff;font-size:28px;font-weight:bold;text-align:center;">⏸️ 暂停中<br><span style="font-size:14px;opacity:0.7;">点击暂停继续</span></div>`;
            const self = this;
            this._pauseOverlay.onclick = () => self.togglePause();
            this.el.style.position = 'relative';
            this.el.appendChild(this._pauseOverlay);
        }
    }

    hidePauseScreen(): void {
        if (this._pauseOverlay) {
            this._pauseOverlay.parentNode.removeChild(this._pauseOverlay);
            this._pauseOverlay = null;
        }
    }

    private _startLoop(): void {
        const self = this;
        const loop = () => {
            self._update();
            self._animFrame = requestAnimationFrame(loop);
        };
        this._animFrame = requestAnimationFrame(loop);
    }

    private _stopLoop(): void {
        if (this._animFrame) {
            cancelAnimationFrame(this._animFrame);
            this._animFrame = null;
        }
    }

    protected _updateUI(): void {
        if (this.scoreEl) this.scoreEl.textContent = this.score.toString();
        if (this.titleEl) this.titleEl.textContent = this.title;
    }

    _update(): void {
        // 由子类实现
    }

    quit(): void {
        this.state = 'over';
        this._stopLoop();
        this.save();
    }

    save(): void {
        try {
            const state = {
                id: this.id,
                score: this.score,
                level: this.level,
                lines: this.lines,
                state: this.state,
                stats: this._stats
            };
            localStorage.setItem(this.saveKey, JSON.stringify(state));
        } catch (e) {
            console.warn('保存游戏状态失败:', e);
        }
    }

    load(): void {
        try {
            const state = localStorage.getItem(this.saveKey);
            if (state) {
                const data = JSON.parse(state);
                this.id = data.id || this.id;
                this.score = data.score || 0;
                this.level = data.level || 1;
                this.lines = data.lines || 0;
                this.state = data.state || 'idle';
                this._stats = data._stats || { startTime: 0, moves: 0, errors: 0 };
            }
        } catch (e) {
            console.warn('加载游戏状态失败:', e);
        }
    }

    reset(): void {
        this.state = 'idle';
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.moves = 0;
        this._stats = { startTime: 0, moves: 0, errors: 0 };
        this._updateUI();
    }
    gameOver(): void {        this.quit();    }}