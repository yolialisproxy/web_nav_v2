"use strict";
/// <reference path="./game-engine.ts" />
/// <reference path="../game-utils.ts" />
/// <reference path="../game-hub.ts" />
/// <reference path="../global.d.ts" />
/**
 * MahjongGame - 四川麻将（简约版）
 * 使用DOM tile实现（已补全: newGame、save/load持久化）
 */
class MahjongGame extends GameEngine {
    constructor() {
        super({ id: 'mahjong', title: '🀄 麻将' });
        this.tiles = [];
        this.selected = [];
        this.score = 0;
        this.matches = 0;
        this.totalPairs = 0;
        this._timer = null;
        this._gameTime = 0;
    }
    init() {
        GameEngine.prototype.init.call(this);
        this._generateTiles();
        this._render();
        this._startTimer();
    }
    /** 生成两副相同的牌 */
    _generateTiles() {
        this.tiles = [];
        const types = MahjongGame.TILE_TYPES.slice(0, 14);
        for (let i = 0; i < types.length; i++) {
            this.tiles.push(Object.assign(Object.assign({}, types[i]), { uid: i * 2, faceUp: false, cleared: false }));
            this.tiles.push(Object.assign(Object.assign({}, types[i]), { uid: i * 2 + 1, faceUp: false, cleared: false }));
        }
        this.tiles = GameUtils.shuffle(this.tiles);
        this.totalPairs = this.tiles.length / 2;
        this.matches = 0;
        this.selected = [];
        this._gameTime = 0;
        this.score = 0;
    }
    _startTimer() {
        const self = this;
        const timerStart = Date.now();
        this._timer = setInterval(function () {
            self._gameTime = Date.now() - timerStart;
            const timeEl = document.getElementById('maj-time');
            if (timeEl)
                timeEl.textContent = GameUtils.formatTime(self._gameTime);
        }, 500);
    }
    _render() {
        const self = this;
        const cols = 7;
        const cellSize = Math.min(50, (window.innerWidth - 100) / cols);
        this.el.innerHTML = `
<div style="text-align:center;">
  <div style="margin-bottom:12px;">
    <span style="font-size:14px;">得分: <strong id="maj-score">${this.score}</strong></span> &nbsp;
    <span style="font-size:14px;">配对: <strong>${this.matches}/${this.totalPairs}</strong></span> &nbsp;
    <span style="font-size:14px;">时间: <strong id="maj-time">${GameUtils.formatTime(this._gameTime)}</strong></span>
  </div>
  <div id="maj-board" style="display:grid;grid-template-columns:repeat(${cols},1fr);gap:4px;max-width:${cellSize * cols + 50}px;margin:0 auto;">
    ${this.tiles.map((tile, idx) => {
            if (tile.cleared) {
                return `<div style="width:${cellSize}px;height:${cellSize}px;"></div>`;
            }
            else if (tile.faceUp) {
                const selected = self.selected.some(s => s.uid === tile.uid);
                return `<div style="width:${cellSize}px;height:${cellSize}px;display:flex;align-items:center;justify-content:center;font-size:${cellSize * 0.55}px;background:${selected ? 'rgba(255,215,0,0.2)' : 'rgba(255,255,255,0.9)'};border:2px solid ${selected ? '#ffd700' : 'var(--color-border)'};border-radius:4px;cursor:pointer;transition:all .15s;" data-uid="${tile.uid}">${tile.char}</div>`;
            }
            else {
                return `<div style="width:${cellSize}px;height:${cellSize}px;background:linear-gradient(135deg,#2d3748,#4a5568);border:2px solid var(--color-border);border-radius:4px;cursor:pointer;font-size:${cellSize * 0.4}px;color:var(--color-text-dim);" data-uid="${tile.uid}">?</div>`;
            }
        }).join('')}
  </div>
  <div style="margin-top:12px;display:flex;gap:8px;justify-content:center;">
    <button class="game-btn" style="font-size:12px;padding:4px 12px;" id="maj-new">🔄 新游戏</button>
    <button class="game-btn" style="font-size:12px;padding:4px 12px;" id="maj-reveal">👁️ 提示(揭示)</button>
  </div>
</div>
`;
        this._bindEvents();
    }
    _bindEvents() {
        const self = this;
        const board = document.getElementById('maj-board');
        if (board) {
            board.addEventListener('click', function (e) {
                const tileEl = e.target.closest('[data-uid]');
                if (!tileEl)
                    return;
                const uid = parseInt(tileEl.dataset.uid);
                const tile = self.tiles.find(function (t) { return t.uid === uid; });
                if (!tile || tile.cleared || tile.faceUp)
                    return;
                tile.faceUp = true;
                self.selected.push(tile);
                GameUtils.playSfx('click');
                if (self.selected.length === 2) {
                    const a = self.selected[0], b = self.selected[1];
                    if (a.matchGroup === b.matchGroup) {
                        const cleared = self.tiles.filter(function (t) { return t.matchGroup === a.matchGroup; });
                        cleared.forEach(function (t) { t.cleared = true; t.faceUp = false; });
                        self.matches += 1;
                        self.score += 50 * self.matches; // 连击加分
                        GameUtils.playSound(600, 0.1, 'sine');
                    }
                    else {
                        a.faceUp = false;
                        b.faceUp = false;
                        self.score = Math.max(0, self.score - 5);
                        GameUtils.playSound(200, 0.1, 'square');
                    }
                    self.selected = [];
                    self._updateUI();
                    self._render();
                    if (self.matches === self.totalPairs) {
                        self._stopTimer();
                        self.gameOver();
                        GameHub.showToast('🎉 恭喜通关！得分: ' + self.score + ' 用时: ' + GameUtils.formatTime(self._gameTime));
                    }
                }
                self._render();
            });
        }
        document.getElementById('maj-new').addEventListener('click', function () { self.newGame(); });
        document.getElementById('maj-reveal').addEventListener('click', function () { self._hint(); });
    }
    _stopTimer() {
        if (this._timer) {
            clearInterval(this._timer);
            this._timer = null;
        }
    }
    /** 新游戏 */
    newGame() {
        this._generateTiles();
        this.matches = 0;
        this.score = 0;
        this.selected = [];
        this._gameTime = 0;
        this._stopTimer();
        this._startTimer();
        this._render();
        this.save();
    }
    /** 提示：翻开一对 */
    _hint() {
        const faceDown = this.tiles.filter(function (t) { return !t.cleared && !t.faceUp; });
        if (faceDown.length > 0) {
            const pair = faceDown.filter(function (t) { return t.matchGroup === faceDown[0].matchGroup; });
            if (pair.length >= 2) {
                pair[0].faceUp = true;
                pair[1].faceUp = true;
                this._render();
                const self = this;
                setTimeout(function () { pair.forEach(function (t) { t.faceUp = false; }); self._render(); }, 1500);
            }
        }
    }
    _updateUI() {
        const scoreEl = document.getElementById('maj-score');
        if (scoreEl)
            scoreEl.textContent = this.score;
        this.scoreEl && (this.scoreEl.textContent = 'Score: ' + this.score);
    }
    save() {
        const data = {
            tiles: this.tiles,
            score: this.score,
            matches: this.matches,
            totalPairs: this.totalPairs,
            _gameTime: this._gameTime,
            state: this.state
        };
        GameUtils.save(this.saveKey, data);
    }
    load() {
        const data = GameUtils.load(this.saveKey);
        if (data) {
            this.tiles = data.tiles || this.tiles;
            this.score = data.score || 0;
            this.matches = data.matches || 0;
            this.totalPairs = data.totalPairs || this.totalPairs;
            this._gameTime = data._gameTime || 0;
            return data;
        }
        return null;
    }
    togglePause() {
        GameEngine.prototype.togglePause.call(this);
        if (this._timer) {
            clearInterval(this._timer);
            this._timer = null;
        }
        if (this.state === 'running')
            this._startTimer();
    }
    quit() {
        this._stopTimer();
        this.state = 'idle';
        GameHub.closeGame();
    }
}
MahjongGame.TILE_TYPES = [
    { char: '🀇', name: '一筒', matchGroup: 0 },
    { char: '🀈', name: '二筒', matchGroup: 1 },
    { char: '🀉', name: '三筒', matchGroup: 2 },
    { char: '🀊', name: '四筒', matchGroup: 3 },
    { char: '🀋', name: '五筒', matchGroup: 4 },
    { char: '🀌', name: '六筒', matchGroup: 5 },
    { char: '🀍', name: '七筒', matchGroup: 6 },
    { char: '🀎', name: '八筒', matchGroup: 7 },
    { char: '🀏', name: '九筒', matchGroup: 8 },
    { char: '🀙', name: '一万', matchGroup: 9 },
    { char: '🀚', name: '二万', matchGroup: 10 },
    { char: '🀛', name: '三万', matchGroup: 11 },
    { char: '🀜', name: '四万', matchGroup: 12 },
    { char: '🀝', name: '五万', matchGroup: 13 }
];
window.MahjongGame = MahjongGame;
//# sourceMappingURL=mahjong.js.map