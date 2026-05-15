/**
 * Gomoku - 五子棋 (15x15)
 * Canvas实现，支持双人对战
 */
var Gomoku = function() {
    GameEngine.call(this, { id: 'gomoku', title: '⚫ 五子棋' });
    this.board = [];      // 15x15, 0=空, 1=黑, 2=白
    this.currentPlayer = 1;
    this.captured = { 1: 0, 2: 0 };
    this._history = [];
    this.boardSize = 15;
};

Gomoku.prototype = Object.create(GameEngine.prototype);
Gomoku.prototype.constructor = Gomoku;

Gomoku.prototype.init = function() {
        // 触摸落子音效反馈
    GameEngine.prototype.init.call(this);
    this.canvas = document.createElement('canvas');
    this.canvas.width = Math.min(450, window.innerWidth - 80);
    this.canvas.height = this.canvas.width;
    this.canvas.id = 'gomoku-canvas';
    this.el.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');

    // 右侧信息
    var info = document.createElement('div');
    info.style.cssText = 'min-width:140px;text-align:center;padding:10px;';
    info.innerHTML = '<div style="margin-bottom:16px;">' +
        '<div style="color:var(--color-text);font-size:14px;margin-bottom:8px;">执子: <span id="gom-turn" style="font-size:18px;">⚫</span></div>' +
        '<div style="margin-top:12px;font-size:12px;">' + Gomoku.prototype.formatTime(0) + '</div>' +
        '</div>' +
        '<button class="game-btn" id="gom-undo" style="margin-bottom:6px;width:100%">↩️ 悔棋</button>' +
        '<button class="game-btn game-btn-danger" id="gom-resign" style="width:100%">🏳️ 认输</button>';
    this.el.appendChild(info);

    this._boardCanvas = document.createElement('canvas');
    this._boardCanvas.width = this.canvas.width;
    this._boardCanvas.height = this.canvas.height;
    this._boardCtx = this._boardCanvas.getContext('2d');

    this._cellSize = this.canvas.width / (this.boardSize + 1);
    this._offset = this._cellSize;
    this._initBoard();
    this._drawBoardStatic();
    this._render();
    this._bindEvents();
    this._startTimer();
};

Gomoku.prototype._initBoard = function() {
    this.board = [];
    for (var r = 0; r < this.boardSize; r++) {
        this.board[r] = [];
        for (var c = 0; c < this.boardSize; c++) {
            this.board[r][c] = 0;
        }
    }
    this.currentPlayer = 1;
    this._history = [];
    this.captured = {1:0, 2:0};
};

Gomoku.prototype._startTimer = function() {
    var self = this;
    this._timerStart = Date.now();
    this._timerInterval = setInterval(function() {
        var elapsed = Date.now() - self._timerStart;
        var disp = document.querySelector('#gomoku-canvas + div > div > div:last-child');
        if (disp) disp.textContent = Gomoku.prototype.formatTime(elapsed);
    }, 500);
};

Gomoku.prototype._drawBoardStatic = function() {
    var ctx = this._boardCtx;
    var cs = this._cellSize;
    var off = this._offset;
    var sz = this.boardSize;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // 木色背景
    ctx.fillStyle = '#dcb35c';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // 网格线
    ctx.strokeStyle = '#3a2a0a';
    ctx.lineWidth = 1;
    for (var i = 0; i < sz; i++) {
        ctx.beginPath();
        ctx.moveTo(off, off + i * cs);
        ctx.lineTo(off + (sz - 1) * cs, off + i * cs);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(off + i * cs, off);
        ctx.lineTo(off + i * cs, off + (sz - 1) * cs);
        ctx.stroke();
    }

    // 天元和星位 (15x15的标准星位)
    var stars = [[3,3],[3,7],[3,11],[7,3],[7,7],[7,11],[11,3],[11,7],[11,11]];
    ctx.fillStyle = '#3a2a0a';
    stars.forEach(function(p) {
        ctx.beginPath();
        ctx.arc(off + p[0] * cs, off + p[1] * cs, 4, 0, Math.PI * 2);
        ctx.fill();
    });
};

Gomoku.prototype._render = function() {
    var ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.drawImage(this._boardCanvas, 0, 0);

    var cs = this._cellSize;
    var off = this._offset;

    // 画棋子
    for (var r = 0; r < this.boardSize; r++) {
        for (var c = 0; c < this.boardSize; c++) {
            if (this.board[r][c] !== 0) {
                var px = off + c * cs, py = off + r * cs;
                ctx.beginPath();
                ctx.arc(px, py, cs * 0.45, 0, Math.PI * 2);
                if (this.board[r][c] === 1) {
                    ctx.fillStyle = '#1a1a1a';
                    ctx.fill();
                    ctx.strokeStyle = '#555';
                    ctx.lineWidth = 1;
                    ctx.stroke();
                } else {
                    ctx.fillStyle = '#f5f5f5';
                    ctx.fill();
                    ctx.strokeStyle = '#333';
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        }
    }

    document.getElementById('gom-turn').textContent = this.currentPlayer === 1 ? '⚫' : '⚪';
};

Gomoku.prototype._handleClick = function(e) {
    if (this.state !== 'running') return;
    var rect = this.canvas.getBoundingClientRect();
    var x = e.clientX - rect.left;
    var y = e.clientY - rect.top;
    var cs = this._cellSize;
    var off = this._offset;
    var c = Math.round((x - off) / cs);
    var r = Math.round((y - off) / cs);
    if (r >= 0 && r < this.boardSize && c >= 0 && c < this.boardSize && this.board[r][c] === 0) {
        this._placeStone(r, c);
    }
};

Gomoku.prototype._placeStone = function(r, c) {
    this._history.push(JSON.parse(JSON.stringify(this.board)));
    this.board[r][c] = this.currentPlayer;
    this.moves++;
    this.score = this._countStones(this.currentPlayer);
    this._updateUI();
    GameUtils.playSound(440, 0.05, 'sine');

    // 检查胜利
    if (this._checkWin(r, c)) {
        this.gameOver();
        GameHub.showToast('🎉 ' + (this.currentPlayer === 1 ? '黑棋' : '白棋') + '获胜！');
        return;
    }

    this.currentPlayer = this.currentPlayer === 1 ? 2 : 1;
    this._render();
    this.save();
};

Gomoku.prototype._checkWin = function(r, c) {
    var player = this.board[r][c];
    var dirs = [[1,0],[0,1],[1,1],[1,-1]];
    for (var d = 0; d < dirs.length; d++) {
        var dr = dirs[d][0], dc = dirs[d][1];
        var count = 1;
        // 正方向
        for (var i = 1; i < 5; i++) {
            var nr = r + dr * i, nc = c + dc * i;
            if (nr < 0 || nr >= this.boardSize || nc < 0 || nc >= this.boardSize) break;
            if (this.board[nr][nc] !== player) break;
            count++;
        }
        // 反方向
        for (var i = 1; i < 5; i++) {
            var nr = r - dr * i, nc = c - dc * i;
            if (nr < 0 || nr >= this.boardSize || nc < 0 || nc >= this.boardSize) break;
            if (this.board[nr][nc] !== player) break;
            count++;
        }
        if (count >= 5) return true;
    }
    return false;
};

Gomoku.prototype._countStones = function(player) {
    var count = 0;
    for (var r = 0; r < this.boardSize; r++) {
        for (var c = 0; c < this.boardSize; c++) {
            if (this.board[r][c] === player) count++;
        }
    }
    return count;
};

Gomoku.prototype._undo = function() {
    if (this._history.length === 0) {
        GameHub.showToast('没有可悔棋的步骤');
        return;
    }
    this.currentPlayer = this.currentPlayer === 1 ? 2 : 1;
    this.board = this._history.pop();
    GameUtils.playSfx('click');
    this._render();
};

Gomoku.prototype._bindEvents = function() {
    var self = this;
    this.canvas.addEventListener('click', function(e) { self._handleClick(e); });
    document.getElementById('gom-undo').addEventListener('click', function() { self._undo(); });
    document.getElementById('gom-resign').addEventListener('click', function() {
        var winner = self.currentPlayer === 1 ? '白棋' : '黑棋';
        self.gameOver();
        GameHub.showToast('🏳️ ' + winner + '获胜！');
    });
};

Gomoku.prototype.togglePause = function() {
    GameEngine.prototype.togglePause.call(this);
    if (this._timerInterval) { clearInterval(this._timerInterval); this._timerInterval = null; }
    if (this.state === 'running') this._startTimer();
};

Gomoku.prototype.quit = function() {
    if (this._timerInterval) clearInterval(this._timerInterval);
    this.state = 'idle';
    GameHub.closeGame();
};


Gomoku.prototype.save = function() {
    var data = {
        board: this.board,
        currentPlayer: this.currentPlayer,
        captured: this.captured,
        history: this._history,
        moves: this.moves,
        score: this.score,
        state: this.state
    };
    GameUtils.save(this.saveKey, data);
};

Gomoku.prototype.load = function() {
    var data = GameUtils.load(this.saveKey);
    if (data) {
        this.board = data.board || this.board;
        this.currentPlayer = data.currentPlayer || 1;
        this.captured = data.captured || {1:0, 2:0};
        this._history = data.history || [];
        this.moves = data.moves || 0;
        this.score = data.score || 0;
        this.state = data.state || 'running';
        return data;
    }
    return null;
};

window.Gomoku = Gomoku;