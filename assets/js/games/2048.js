/**
 * Game2048 - 经典2048数字益智游戏
 * Canvas + DOM 实现
 */
var Game2048 = function() {
    GameEngine.call(this, { id: 'game2048', title: '🔢 2048' });
    this.grid = [];       // 4x4 网格
    this.score = 0;
    this.best = 0;
    this.size = 4;
};

Game2048.prototype = Object.create(GameEngine.prototype);
Game2048.prototype.constructor = Game2048;

Game2048.prototype.init = function() {
    GameEngine.prototype.init.call(this);
    this._loadBest();
    this._reset();
    this._render();
    this._bindEvents();
};

Game2048.prototype._reset = function() {
    this.grid = [];
    for (var i = 0; i < this.size; i++) {
        this.grid[i] = [];
        for (var j = 0; j < this.size; j++) {
            this.grid[i][j] = 0;
        }
    }
    this.score = 0;
    this._spawnTile();
    this._spawnTile();
    this._updateUI();
};

Game2048.prototype._spawnTile = function() {
    var empty = [];
    for (var r = 0; r < this.size; r++) {
        for (var c = 0; c < this.size; c++) {
            if (this.grid[r][c] === 0) empty.push([r, c]);
        }
    }
    if (empty.length > 0) {
        var pos = empty[GameUtils.rand(0, empty.length - 1)];
        this.grid[pos[0]][pos[1]] = Math.random() < 0.9 ? 2 : 4; // 90%出2，10%出4
    }
};

Game2048.prototype._render = function() {
    var self = this;
    var cellSize = Math.min(80, (window.innerWidth - 100) / 5);
    var gap = 8;

    var html = '<div style="display:grid;grid-template-columns:repeat(' + this.size + ',1fr);gap:' + gap + 'px;max-width:' + (cellSize * this.size + gap * (this.size - 1)) + 'px;margin:0 auto;">';

    for (var r = 0; r < this.size; r++) {
        for (var c = 0; c < this.size; c++) {
            var val = this.grid[r][c];
            var bg = val === 0 ? 'rgba(255,255,255,0.05)' : this._tileColor(val);
            var fontSize = val < 100 ? cellSize * 0.4 : cellSize * 0.3;
            html += '<div style="width:' + cellSize + 'px;height:' + cellSize + 'px;display:flex;align-items:center;justify-content:center;' +
                'background:' + bg + ';border-radius:8px;font-size:' + fontSize + 'px;font-weight:bold;color:' + this._textColor(val) + ';">' +
                (val || '') + '</div>';
        }
    }
    html += '</div>';

    html += '<div style="margin-top:12px;text-align:center;">' +
        '<div style="font-size:14px;color:var(--color-text-dim);">得分: <strong style="font-size:18px;color:var(--color-primary-light)">' + this.score + '</strong>' +
        '&nbsp;&nbsp;&nbsp;最高: <strong style="font-size:18px;color:#ffd700">' + this.best + '</strong></div>' +
        '<div style="margin-top:8px;">' +
        '<button class="game-btn" id="2048-new">🔄 新游戏</button>' +
        '<button class="game-btn" id="2048-undo">↩️ 撤销</button>' +
        '</div></div>';

    this.el.innerHTML = html;
    this._bindEvents();
};

Game2048.prototype._tileColor = function(val) {
    var colors = {
        2:    'rgba(238,228,218,0.4)',
        4:    'rgba(238,225,201,0.4)',
        8:    'rgba(243,178,122,0.5)',
        16:   'rgba(246,124,95,0.5)',
        32:   'rgba(246,94,59,0.5)',
        64:   'rgba(237,207,114,0.5)',
        128:  'rgba(237,204,97,0.5)',
        256:  'rgba(237,200,80,0.5)',
        512:  'rgba(237,197,63,0.5)',
        1024: 'rgba(237,194,46,0.6)',
        2048: 'rgba(237,194,46,0.7)'
    };
    return colors[val] || 'rgba(61,43,31,0.4)';
};

Game2048.prototype._textColor = function(val) {
    return val <= 4 ? '#776e65' : '#f9f6f2';
};

Game2048.prototype._bindEvents = function() {
    var self = this;
    document.getElementById('2048-new').addEventListener('click', function() { self.newGame(); });
    document.getElementById('2048-undo').addEventListener('click', function() { self._undo(); });
    this._keyHandler = function(e) {
        if (GameHub.currentGame !== 'game2048' || self.state !== 'running') return;
        var moved = false;
        switch (e.key) {
            case 'ArrowLeft':  e.preventDefault(); moved = self._move('left');  break;
            case 'ArrowRight': e.preventDefault(); moved = self._move('right'); break;
            case 'ArrowUp':    e.preventDefault(); moved = self._move('up');    break;
            case 'ArrowDown':  e.preventDefault(); moved = self._move('down');  break;
        }
        if (moved) {
            self._spawnTile();
            self._updateUI();
            self._render();
            self._checkWin();
        }
    };
    document.addEventListener('keydown', this._keyHandler);
    // 触摸滑动支持
    var startX, startY;
    this.el.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    }, {passive: true});
    this.el.addEventListener('touchend', function(e) {
        if (self.state !== 'running') return;
        var dx = e.changedTouches[0].clientX - startX;
        var dy = e.changedTouches[0].clientY - startY;
        if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 30) {
            var moved = self._move(dx > 0 ? 'right' : 'left');
            if (moved) { self._spawnTile(); self._updateUI(); self._render(); self._checkWin(); }
        } else if (Math.abs(dy) > 30) {
            var moved = self._move(dy > 0 ? 'down' : 'up');
            if (moved) { self._spawnTile(); self._updateUI(); self._render(); self._checkWin(); }
        }
    }, {passive: true});
};

Game2048.prototype._move = function(direction) {
    // 保存历史
    this._saveState();

    var moved = false;
    var merged = Array(this.size).fill().map(() => Array(this.size).fill(false));

    // 遍历顺序
    var rowOrder = direction === 'down' ? [3,2,1,0] : [0,1,2,3];
    var colOrder = direction === 'right' ? [3,2,1,0] : [0,1,2,3];

    for (var i = 0; i < this.size; i++) {
        for (var j = 0; j < this.size; j++) {
            var r = direction === 'up' || direction === 'down' ? (direction === 'down' ? 3 - i : i) : j;
            var c = direction === 'left' || direction === 'right' ? (direction === 'right' ? 3 - i : i) : j;

            if (this.grid[r][c] === 0) continue;

            // 计算目标位置
            var nr = r, nc = c;
            if (direction === 'up')    nr = this._findFarthest(r, c, -1, 0);
            if (direction === 'down')  nr = this._findFarthest(r, c, 1, 0);
            if (direction === 'left')  nc = this._findFarthest(r, c, 0, -1);
            if (direction === 'right') nc = this._findFarthest(r, c, 0, 1);

            // 合并检查
            if (this._inBounds(nr, nc) && this.grid[nr][nc] === this.grid[r][c] && !merged[nr][nc]) {
                this.grid[nr][nc] *= 2;
                this.grid[r][c] = 0;
                this.score += this.grid[nr][nc];
                merged[nr][nc] = true;
                moved = true;
            } else {
                // 移到最远空位
                if (direction === 'up' && nr !== r) { this.grid[nr][c] = this.grid[r][c]; this.grid[r][c] = 0; moved = true; }
                if (direction === 'down' && nr !== r) { this.grid[nr][c] = this.grid[r][c]; this.grid[r][c] = 0; moved = true; }
                if (direction === 'left' && nc !== c) { this.grid[r][nc] = this.grid[r][c]; this.grid[r][c] = 0; moved = true; }
                if (direction === 'right' && nc !== c) { this.grid[r][nc] = this.grid[r][c]; this.grid[r][c] = 0; moved = true; }
            }
        }
    }
    return moved;
};

Game2048.prototype._findFarthest = function(r, c, dr, dc) {
    var nr = r, nc = c;
    while (this._inBounds(nr + dr, nc + dc) && this.grid[nr + dr][nc + dc] === 0) {
        nr += dr; nc += dc;
    }
    return {r: nr, c: nc};
};

Game2048.prototype._inBounds = function(r, c) {
    return r >= 0 && r < this.size && c >= 0 && c < this.size;
};

Game2048.prototype._saveState = function() {
    var snapshot = {
        grid: JSON.parse(JSON.stringify(this.grid)),
        score: this.score
    };
    if (!this._history) this._history = [];
    this._history.push(snapshot);
    if (this._history.length > 50) this._history.shift();
};

Game2048.prototype._undo = function() {
    if (!this._history || this._history.length === 0) {
        GameHub.showToast('没有可撤销的步骤');
        return;
    }
    var snapshot = this._history.pop();
    this.grid = snapshot.grid;
    this.score = snapshot.score;
    this._updateUI();
    this._render();
};

Game2048.prototype._updateUI = function() {
    if (this.scoreEl) this.scoreEl.textContent = 'Score: ' + this.score;
    if (this.score > this.best) {
        this.best = this.score;
        this._saveBest();
    }
};

Game2048.prototype._loadBest = function() {
    try {
        var data = localStorage ? localStorage.getItem('gn_save_game2048_best') : null;
        if (data) this.best = parseInt(data, 10);
    } catch (e) { this.best = 0; }
};

Game2048.prototype._saveBest = function() {
    try {
        if (localStorage) localStorage.setItem('gn_save_game2048_best', this.best.toString());
    } catch (e) {}
};

Game2048.prototype._checkWin = function() {
    for (var r = 0; r < this.size; r++) {
        for (var c = 0; c < this.size; c++) {
            if (this.grid[r][c] === 2048) {
                this.gameOver();
                GameHub.showToast('🎉 恭喜达成2048！继续挑战更高分。');
                return;
            }
        }
    }
    // 检查是否无路可走
    if (this._isFull() && !this._canMove()) {
        this.gameOver();
        GameHub.showToast('💀 游戏结束！最终得分: ' + this.score);
    }
};

Game2048.prototype._isFull = function() {
    for (var r = 0; r < this.size; r++) {
        for (var c = 0; c < this.size; c++) {
            if (this.grid[r][c] === 0) return false;
        }
    }
    return true;
};

Game2048.prototype._canMove = function() {
    for (var r = 0; r < this.size; r++) {
        for (var c = 0; c < this.size; c++) {
            var val = this.grid[r][c];
            if (val === 0) return true;
            [[-1,0],[1,0],[0,-1],[0,1]].forEach(function(dir) {
                var nr = r + dir[0], nc = c + dir[1];
                if (nr >= 0 && nr < this.size && nc >= 0 && nc < this.size) {
                    if (this.grid[nr][nc] === val || this.grid[nr][nc] === 0) return true;
                }
            }, this);
        }
    }
    return false;
};

Game2048.prototype.newGame = function() {
    this._history = [];
    this._reset();
    this.state = 'running';
    this._render();
    this.save();
};

GameEngine.prototype.save.call(this);
GameEngine.prototype.load.call(this);

Game2048.prototype.togglePause = function() {
    GameEngine.prototype.togglePause.call(this);
};

Game2048.prototype.quit = function() {
    this._stopLoop();
    this.state = 'idle';
    document.removeEventListener('keydown', this._keyHandler);
    GameHub.closeGame();
};


Game2048.prototype.save = function() {
    var data = {
        grid: this.grid,
        score: this.score,
        best: this.best,
        moves: this.moves || 0,
        state: this.state
    };
    GameUtils.save(this.saveKey, data);
    // best 单独 localStorage
    try { if (localStorage) localStorage.setItem('gn_save_game2048_best', String(this.best)); } catch(e){}
};

Game2048.prototype.load = function() {
    var data = GameUtils.load(this.saveKey);
    if (data) {
        this.grid = data.grid || this.grid;
        this.score = data.score || 0;
        this.best = data.best || 0;
        this.moves = data.moves || 0;
        this.state = data.state || 'running';
        return data;
    }
    // 恢复 best
    try {
        var best = localStorage ? localStorage.getItem('gn_save_game2048_best') : null;
        if (best) this.best = parseInt(best, 10) || 0;
    } catch(e){}
    return null;
};

window.Game2048 = Game2048;