/**
 * GoGame - 围棋
 * Canvas实现，完整规则
 */
var GoGame = function() {
    GameEngine.call(this, { id: 'go', title: '⚫ 围棋' });
    this.board = []; // 19x19, 0=空, 1=黑, 2=白
    this.currentPlayer = 1; // 1=黑, 2=白
    this.captured = { 1: 0, 2: 0 };
    this.history = [];
    this.boardSize = 19;
};

GoGame.prototype = Object.create(GameEngine.prototype);
GoGame.prototype.constructor = GoGame;

GoGame.prototype.init = function() {
    GameEngine.prototype.init.call(this);
    this.canvas = document.createElement('canvas');
    this.canvas.width = Math.min(570, window.innerWidth - 80);
    this.canvas.height = this.canvas.width;
    this.canvas.id = 'go-canvas';
    this.el.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    this.boardEl = this.el;

    // 右侧信息面板
    var info = document.createElement('div');
    info.style.cssText = 'min-width:140px;text-align:center;padding:10px;';
    info.innerHTML = '<div style="margin-bottom:16px;">' +
        '<div style="color:var(--color-text);font-size:14px;margin-bottom:8px;">执子: <span id="go-turn" style="font-size:18px;">⚫</span></div>' +
        '<div style="font-size:12px;color:var(--color-text-dim);">黑: <span id="go-black-captured">0</span> 目</div>' +
        '<div style="font-size:12px;color:var(--color-text-dim);">白: <span id="go-white-captured">0</span> 目</div>' +
        '<div style="margin-top:12px;font-size:12px;">' + GameUtils.formatTime(0) + '</div>' +
        '</div>' +
        '<button class="game-btn" id="go-undo" style="margin-bottom:6px;width:100%">↩️ 悔棋</button>' +
        '<button class="game-btn" id="go-pass" style="margin-bottom:6px;width:100%">▶ 虚着</button>' +
        '<button class="game-btn game-btn-danger" id="go-resign" style="width:100%">🏳️ 认输</button>';
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

GoGame.prototype._initBoard = function() {
    this.board = [];
    for (var r = 0; r < this.boardSize; r++) {
        this.board[r] = [];
        for (var c = 0; c < this.boardSize; c++) {
            this.board[r][c] = 0;
        }
    }
    this.currentPlayer = 1;
    this.captured = { 1: 0, 2: 0 };
    this.history = [];
};

GoGame.prototype._startTimer = function() {
    var self = this;
    this._timerStart = Date.now();
    this._timerInterval = setInterval(function() {
        var elapsed = Date.now() - self._timerStart;
        var disp = document.querySelector('#go-canvas + div > div > div:last-child');
        if (disp) disp.textContent = GoGame.prototype.formatTime(elapsed);
    }, 500);
};

GoGame.prototype._drawBoardStatic = function() {
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

    // 星位
    var stars = [[3,3],[3,9],[3,15],[9,3],[9,9],[9,15],[15,3],[15,9],[15,15]];
    ctx.fillStyle = '#3a2a0a';
    stars.forEach(function(p) {
        ctx.beginPath();
        ctx.arc(off + p[0] * cs, off + p[1] * cs, 4, 0, Math.PI * 2);
        ctx.fill();
    });
};

GoGame.prototype._render = function() {
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

    // 更新信息
    document.getElementById('go-turn').textContent = this.currentPlayer === 1 ? '⚫' : '⚪';
    document.getElementById('go-black-captured').textContent = this.captured[1];
    document.getElementById('go-white-captured').textContent = this.captured[2];
};

GoGame.prototype._handleClick = function(e) {
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

GoGame.prototype._placeStone = function(r, c) {
    // 保存历史
    this.history.push({
        board: GameUtils.clone(this.board),
        captured: GameUtils.clone(this.captured),
        player: this.currentPlayer
    });

    this.board[r][c] = this.currentPlayer;
    var opponent = this.currentPlayer === 1 ? 2 : 1;

    // 检查提子
    var directions = [[-1,0],[1,0],[0,-1],[0,1]];
    var captured = 0;
    directions.forEach(function(dir) {
        var nr = r + dir[0], nc = c + dir[1];
        if (nr >= 0 && nr < this.boardSize && nc >= 0 && nc < this.boardSize && this.board[nr][nc] === opponent) {
            var group = this._getGroup(nr, nc);
            if (this._getLiberties(group) === 0) {
                group.forEach(function(p) {
                    this.board[p[0]][p[1]] = 0;
                    captured++;
                }, this);
                this.captured[this.currentPlayer] += captured;
            }
        }
    }, this);

    // 检查自杀规则
    var selfGroup = this._getGroup2(r, c);
    if (this._getLiberties2(selfGroup) === 0 && captured === 0) {
        // 还原
        var prev = this.history.pop();
        this.board = prev.board;
        this.captured = prev.captured;
        return; // 非法着法
    }

    GameUtils.playSound(440, 0.05, 'sine');

    this.moves++;
    this.score = this.captured[1] + this.captured[2];
    this._updateUI();

    // 切换玩家
    this.currentPlayer = opponent;
    this._render();
    this.save();
};

GoGame.prototype._getGroup = function(r, c) {
    var color = this.board[r][c];
    if (!color) return [];
    var visited = {};
    var group = [];
    var queue = [[r, c]];
    while (queue.length > 0) {
        var p = queue.shift();
        var key = p[0] + ',' + p[1];
        if (visited[key]) continue;
        visited[key] = true;
        if (this.board[p[0]] && this.board[p[0]][p[1]] === color) {
            group.push(p);
            [[-1,0],[1,0],[0,-1],[0,1]].forEach(function(dir) {
                var nr = p[0] + dir[0], nc = p[1] + dir[1];
                if (nr >= 0 && nr < this.boardSize && nc >= 0 && nc < this.boardSize) {
                    queue.push([nr, nc]);
                }
            }, this);
        }
    }
    return group;
};

GoGame.prototype._getLiberties = function(group) {
    var liberties = {};
    group.forEach(function(p) {
        [[-1,0],[1,0],[0,-1],[0,1]].forEach(function(dir) {
            var nr = p[0] + dir[0], nc = p[1] + dir[1];
            if (nr >= 0 && nr < this.boardSize && nc >= 0 && nc < this.boardSize) {
                if (this.board[nr][nc] === 0) liberties[nr + ',' + nc] = true;
            }
        }, this);
    }, this);
    return Object.keys(liberties).length;
};

GoGame.prototype._getGroup2 = function(r, c) {
    var color = this.board[r][c];
    var visited = {};
    var group = [];
    var queue = [[r, c]];
    while (queue.length > 0) {
        var p = queue.shift();
        var key = p[0] + ',' + p[1];
        if (visited[key]) continue;
        visited[key] = true;
        if (this.board[p[0]] && this.board[p[0]][p[1]] === color) {
            group.push(p);
            [[-1,0],[1,0],[0,-1],[0,1]].forEach(function(dir) {
                var nr = p[0] + dir[0], nc = p[1] + dir[1];
                if (nr >= 0 && nr < this.boardSize && nc >= 0 && nc < this.boardSize) {
                    queue.push([nr, nc]);
                }
            }, this);
        }
    }
    return group;
};

GoGame.prototype._getLiberties2 = function(group) {
    var liberties = {};
    group.forEach(function(p) {
        [[-1,0],[1,0],[0,-1],[0,1]].forEach(function(dir) {
            var nr = p[0] + dir[0], nc = p[1] + dir[1];
            if (nr >= 0 && nr < this.boardSize && nc >= 0 && nc < this.boardSize) {
                if (this.board[nr][nc] === 0) liberties[nr + ',' + nc] = true;
            }
        }, this);
    }, this);
    return Object.keys(liberties).length;
};

GoGame.prototype._bindEvents = function() {
    var self = this;
    this.canvas.addEventListener('click', function(e) { self._handleClick(e); });
    document.getElementById('go-undo').addEventListener('click', function() { self._undo(); });
    document.getElementById('go-pass').addEventListener('click', function() {
        self.currentPlayer = self.currentPlayer === 1 ? 2 : 1;
        GameHub.showToast('虚着');
        self._render();
    });
    document.getElementById('go-resign').addEventListener('click', function() {
        var winner = self.currentPlayer === 1 ? '白棋' : '黑棋';
        self.gameOver();
        GameHub.showToast('🏳️ ' + winner + '获胜！');
    });
};

GoGame.prototype._undo = function() {
    if (this.history.length === 0) { GameHub.showToast('没有可悔棋的步骤'); return; }
    var prev = this.history.pop();
    this.board = prev.board;
    this.captured = prev.captured;
    this.currentPlayer = prev.player;
    this._render();
};

GoGame.prototype.togglePause = function() {
    GameEngine.prototype.togglePause.call(this);
    if (this._timerInterval) { clearInterval(this._timerInterval); this._timerInterval = null; }
    if (this.state === 'running') this._startTimer();
};

GoGame.prototype.quit = function() {
    if (this._timerInterval) clearInterval(this._timerInterval);
    this.state = 'idle';
    GameHub.closeGame();
};

window.GoGame = GoGame;