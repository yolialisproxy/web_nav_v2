/**
 * Tetris - 经典俄罗斯方块
 * Canvas实现
 */
var Tetris = function() {
    GameEngine.call(this, { id: 'tetris', title: '🟩 俄罗斯方块' });
    this.board = [];
    this.current = null;
    this.next = null;
    this.level = 1;
    this.lines = 0;
    this.combo = 0;
    this.canvas = null;
    this.ctx = null;
    this._interval = null;
    this._dropSpeed = 800;
};

Tetris.prototype = Object.create(GameEngine.prototype);
Tetris.prototype.constructor = Tetris;

Tetris.BLOCKS = {
    I: { shape: [[1,1,1,1]], color: '#00f0f0', pivot: 1 },
    O: { shape: [[1,1],[1,1]], color: '#f0f000', pivot: 0 },
    T: { shape: [[0,1,0],[1,1,1]], color: '#a000f0', pivot: 1 },
    S: { shape: [[0,1,1],[1,1,0]], color: '#00f000', pivot: 1 },
    Z: { shape: [[1,1,0],[0,1,1]], color: '#f00000', pivot: 1 },
    J: { shape: [[1,0,0],[1,1,1]], color: '#0000f0', pivot: 1 },
    L: { shape: [[0,0,1],[1,1,1]], color: '#f0a000', pivot: 1 }
};

Tetris.prototype.init = function() {
    GameEngine.prototype.init.call(this);
    var inner = this.el;
    inner.style.cssText = 'display:flex;gap:10px;justify-content:center;align-items:flex-start;flex-wrap:wrap;';
    var html = '<canvas id="tetris-canvas" width="300" height="600"></canvas>' +
        '<div style="display:flex;flex-direction:column;align-items:center;gap:10px;">' +
        '<div style="color:var(--color-text);font-size:14px;">下一个</div>' +
        '<canvas id="tetris-next" width="100" height="80"></canvas>' +
        '<div style="color:var(--color-text);font-size:12px;" id="tetris-stats">' +
        '分数: <span id="tet-score">0</span><br>' +
        '行数: <span id="tet-lines">0</span><br>' +
        '等级: <span id="tet-level">1</span>' +
        '</div></div>';
    inner.innerHTML = html;

    this.canvas = document.getElementById('tetris-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.nextCanvas = document.getElementById('tetris-next');
    this.nextCtx = this.nextCanvas.getContext('2d');

    this._cols = 10;
    this._rows = 20;
    this._blockSize = this.canvas.width / this._cols;
    this._resetBoard();
    this._startGame();
    this._bindKeys();
};

Tetris.prototype._resetBoard = function() {
    this.board = [];
    for (var r = 0; r < this._rows; r++) {
        this.board[r] = [];
        for (var c = 0; c < this._cols; c++) {
            this.board[r][c] = 0;
        }
    }
};

Tetris.prototype._startGame = function() {
    var self = this;
    this.state = 'running';
    this.score = 0;
    this.lines = 0;
    this.level = 1;
    this.combo = 0;
    this._dropSpeed = 800;
    this._resetBoard();
    this.current = this._newPiece();
    this.next = this._newPiece();
    this._startDrop();
    this._render();
};

Tetris.prototype._newPiece = function() {
    var keys = Object.keys(Tetris.BLOCKS);
    var key = keys[GameUtils.rand(0, keys.length - 1)];
    var def = GameUtils.clone(Tetris.BLOCKS[key]);
    return { key: key, shape: def.shape, color: def.color, x: Math.floor((this._cols - def.shape[0].length) / 2), y: 0 };
};

Tetris.prototype._startDrop = function() {
    var self = this;
    this._stopDrop();
    this._interval = setInterval(function() { self._moveDown(); }, this._dropSpeed);
};

Tetris.prototype._stopDrop = function() {
    if (this._interval) { clearInterval(this._interval); this._interval = null; }
};

Tetris.prototype._moveDown = function() {
    if (this.state !== 'running') return;
    if (this._canMove(this.current, this.current.x, this.current.y + 1)) {
        this.current.y++;
        this._render();
    } else {
        this._lockPiece();
        this._clearLines();
        this.current = this.next;
        this.next = this._newPiece();
        if (!this._canMove(this.current, this.current.x, this.current.y)) {
            this._gameOver();
        }
        this._render();
    }
};

Tetris.prototype._canMove = function(piece, newX, newY) {
    for (var r = 0; r < piece.shape.length; r++) {
        for (var c = 0; c < piece.shape[r].length; c++) {
            if (!piece.shape[r][c]) continue;
            var nr = newY + r, nc = newX + c;
            if (nc < 0 || nc >= this._cols || nr >= this._rows) return false;
            if (nr >= 0 && this.board[nr][nc]) return false;
        }
    }
    return true;
};

Tetris.prototype._lockPiece = function() {
    for (var r = 0; r < this.current.shape.length; r++) {
        for (var c = 0; c < this.current.shape[r].length; c++) {
            if (!this.current.shape[r][c]) continue;
            var nr = this.current.y + r, nc = this.current.x + c;
            if (nr >= 0 && nr < this._rows && nc >= 0 && nc < this._cols) {
                this.board[nr][nc] = this.current.color;
            }
        }
    }
};

Tetris.prototype._clearLines = function() {
    var cleared = 0;
    for (var r = this._rows - 1; r >= 0; r--) {
        if (this.board[r].every(function(cell) { return cell !== 0; })) {
            this.board.splice(r, 1);
            this.board.unshift([]);
            for (var c = 0; c < this._cols; c++) this.board[0][c] = 0;
            cleared++;
            r++; // 重新检查当前行
        }
    }
    if (cleared > 0) {
        this.combo++;
        var points = [0, 100, 300, 500, 800][cleared] * this.level + this.combo * 50;
        this.score += points;
        this.lines += cleared;
        this.level = Math.floor(this.lines / 10) + 1;
        this._dropSpeed = Math.max(100, 800 - (this.level - 1) * 60);
        if (this._interval) this._startDrop();
    } else {
        this.combo = 0;
    }
};

Tetris.prototype._rotate = function() {
    var shape = this.current.shape;
    var newShape = [];
    for (var c = 0; c < shape[0].length; c++) {
        newShape[c] = [];
        for (var r = shape.length - 1; r >= 0; r--) {
            newShape[c][shape.length - 1 - r] = shape[r][c];
        }
    }
    var newPiece = GameUtils.clone(this.current);
    newPiece.shape = newShape;
    if (this._canMove(newPiece, newPiece.x, newPiece.y)) {
        this.current = newPiece;
        this._render();
    } else {
        // wall kick
        for (var offset of [-1, 1, -2, 2]) {
            if (this._canMove(newPiece, newPiece.x + offset, newPiece.y)) {
                this.current = newPiece;
                this.current.x += offset;
                this._render();
                return;
            }
        }
    }
};

Tetris.prototype._moveLeft = function() {
    if (this._canMove(this.current, this.current.x - 1, this.current.y)) {
        this.current.x--; this._render();
    }
};

Tetris.prototype._moveRight = function() {
    if (this._canMove(this.current, this.current.x + 1, this.current.y)) {
        this.current.x++; this._render();
    }
};

Tetris.prototype._hardDrop = function() {
    while (this._canMove(this.current, this.current.x, this.current.y + 1)) {
        this.current.y++;
    }
    this._lockPiece();
    this._clearLines();
    this.score += 2;
    this.current = this.next;
    this.next = this._newPiece();
    if (!this._canMove(this.current, this.current.x, this.current.y)) {
        this._gameOver();
    }
    this._render();
};

Tetris.prototype._render = function() {
    var ctx = this.ctx;
    var bs = this._blockSize;
    // 清空
    ctx.fillStyle = '#0a0a1a';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    // 网格
    ctx.strokeStyle = 'rgba(255,255,255,0.03)';
    for (var r = 0; r <= this._rows; r++) {
        ctx.beginPath(); ctx.moveTo(0, r * bs); ctx.lineTo(this.canvas.width, r * bs); ctx.stroke();
    }
    for (var c = 0; c <= this._cols; c++) {
        ctx.beginPath(); ctx.moveTo(c * bs, 0); ctx.lineTo(c * bs, this.canvas.height); ctx.stroke();
    }
    // 已锁定方块
    for (var r = 0; r < this._rows; r++) {
        for (var c = 0; c < this._cols; c++) {
            if (this.board[r][c]) {
                ctx.fillStyle = this.board[r][c];
                ctx.fillRect(c * bs + 1, r * bs + 1, bs - 2, bs - 2);
                ctx.fillStyle = 'rgba(255,255,255,0.2)';
                ctx.fillRect(c * bs + 1, r * bs + 1, bs - 2, bs / 3);
            }
        }
    }
    // 当前方块（ghost）
    if (this.current) {
        var ghostY = this.current.y;
        while (this._canMove({ shape: this.current.shape, x: this.current.x, y: ghostY + 1 }, this.current.x, ghostY + 1)) ghostY++;
        ctx.globalAlpha = 0.2;
        this._drawPiece(ctx, this.current.shape, this.current.x, ghostY, '#555');
        ctx.globalAlpha = 1;
        // 当前方块
        this._drawPiece(ctx, this.current.shape, this.current.x, this.current.y, this.current.color);
    }
    // 更新分数
    document.getElementById('tet-score').textContent = this.score;
    document.getElementById('tet-lines').textContent = this.lines;
    document.getElementById('tet-level').textContent = this.level;
};

Tetris.prototype._drawPiece = function(ctx, shape, x, y, color) {
    var bs = this._blockSize;
    for (var r = 0; r < shape.length; r++) {
        for (var c = 0; c < shape[r].length; c++) {
            if (shape[r][c]) {
                var px = (x + c) * bs, py = (y + r) * bs;
                ctx.fillStyle = color;
                ctx.fillRect(px + 1, py + 1, bs - 2, bs - 2);
                ctx.fillStyle = 'rgba(255,255,255,0.3)';
                ctx.fillRect(px + 1, py + 1, bs - 2, bs / 3);
            }
        }
    }
};

// 渲染下一个方块
Tetris.prototype._renderNext = function() {
    var ctx = this.nextCtx;
    var bs = this.nextCanvas.width / 4;
    ctx.fillStyle = 'rgba(10,10,26,1)';
    ctx.fillRect(0, 0, this.nextCanvas.width, this.nextCanvas.height);
    if (this.next) {
        var shape = this.next.shape;
        var ox = Math.floor((4 - shape[0].length) / 2);
        var oy = Math.floor((3 - shape.length) / 2);
        for (var r = 0; r < shape.length; r++) {
            for (var c = 0; c < shape[r].length; c++) {
                if (shape[r][c]) {
                    ctx.fillStyle = this.next.color;
                    ctx.fillRect((ox + c) * bs + 1, (oy + r) * bs + 1, bs - 2, bs - 2);
                }
            }
        }
    }
};

Tetris.prototype._bindKeys = function() {
    var self = this;
    this._keyHandler = function(e) {
        if (GameHub.currentGame !== 'tetris') return;
        if (self.state !== 'running') return;
        switch (e.key) {
            case 'ArrowLeft': e.preventDefault(); self._moveLeft(); break;
            case 'ArrowRight': e.preventDefault(); self._moveRight(); break;
            case 'ArrowDown': e.preventDefault(); self._moveDown(); self.addScore(1); break;
            case 'ArrowUp': e.preventDefault(); self._rotate(); break;
            case ' ': e.preventDefault(); self._hardDrop(); self.addScore(2); break;
        }
    };
    document.addEventListener('keydown', this._keyHandler);
};

Tetris.prototype._gameOver = function() {
    this.state = 'over';
    this._stopDrop();
    document.removeEventListener('keydown', this._keyHandler);
    if (this.onGameOver) this.onGameOver(this.score, Date.now() - this._stats.startTime);
    GameHub.showToast('💀 游戏结束！最终得分: ' + this.score);
};

Tetris.prototype.togglePause = function() {
    GameEngine.prototype.togglePause.call(this);
    if (this.state === 'paused') this._stopDrop();
    if (this.state === 'running') this._startDrop();
};

Tetris.prototype.tick = function() {};

Tetris.prototype.quit = function() {
    this._stopDrop();
    if (this._keyHandler) document.removeEventListener('keydown', this._keyHandler);
    this.state = 'idle';
    GameHub.closeGame();
};


Tetris.prototype.save = function() {
    var data = {
        grid: this.grid,
        score: this.score,
        level: this.level,
        lines: this.lines,
        piece: this.piece,
        nextPiece: this.nextPiece,
        dropInterval: this.dropInterval,
        lastTime: this.lastTime,
        state: this.state
    };
    GameUtils.save(this.saveKey, data);
};

Tetris.prototype.load = function() {
    var data = GameUtils.load(this.saveKey);
    if (data) {
        this.grid = data.grid || this.grid;
        this.score = data.score || 0;
        this.level = data.level || 1;
        this.lines = data.lines || 0;
        this.piece = data.piece || null;
        this.nextPiece = data.nextPiece || null;
        this.dropInterval = data.dropInterval || 1000;
        this.lastTime = data.lastTime || 0;
        this.state = data.state || 'running';
        return true;
    }
    return false;
};

window.Tetris = Tetris;