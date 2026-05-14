/**
 * ChessGame - 中国象棋
 * DOM实现简化版（已补全：checkWin + newGame）
 */
var ChessGame = function() {
    GameEngine.call(this, { id: 'chess', title: '♟️ 中国象棋' });
    this.board = [];
    this.selected = null;
    this.turn = 'red'; // red先手
    this.moveHistory = [];
};

ChessGame.prototype = Object.create(GameEngine.prototype);
ChessGame.prototype.constructor = ChessGame;

// 棋子定义
ChessGame.PIECES = {
    r: { name: '车', unicode: '俥', value: 200 },
    n: { name: '马', unicode: '傌', value: 80 },
    b: { name: '象', unicode: '相', value: 50 },
    a: { name: '士', unicode: '仕', value: 30 },
    k: { name: '将', unicode: '帅', value: 10000 },
    c: { name: '炮', unicode: '砲', value: 100 },
    p: { name: '兵', unicode: '兵', value: 30 }
};

ChessGame.prototype.init = function() {
    GameEngine.prototype.init.call(this);
    this._resetBoard();
    this._render();
    this._bindEvents();
        this._bindEvents();
        // 触摸支持
        this.initTouch();
        this.onTouchTap = this._onTouchTap.bind(this);
};

ChessGame.prototype.newGame = function() {
    this._resetBoard();
    this.moves = 0;
    this.score = 0;
    this.state = 'running';
    this._render();
};

ChessGame.prototype._resetBoard = function() {
    // 10x9, 0=空, 正数=红, 负数=黑
    this.board = [
        [-5,-4,-3,-2,-1,-3,-4,-5],
        [ 0, 0, 0, 0, 0, 0, 0, 0],
        [ 0, 0,-6, 0, 0, 0,-6, 0],
        [-7, 0,-7, 0,-7, 0,-7, 0],
        [ 0, 0, 0, 0, 0, 0, 0, 0],
        [ 0, 0, 0, 0, 0, 0, 0, 0],
        [ 7, 0, 7, 0, 7, 0, 7, 0],
        [ 0, 0, 6, 0, 0, 0, 6, 0],
        [ 0, 0, 0, 0, 0, 0, 0, 0],
        [ 5, 4, 3, 2, 1, 3, 4, 5]
    ];
    this.turn = 'red';
    this.selected = null;
    this.moveHistory = [];
};

ChessGame.prototype._render = function() {
    var self = this;
    var cellSize = Math.min(55, (window.innerWidth - 100) / 8);
    var w = cellSize * 8 + 20, h = cellSize * 10 + 20;
    var html = '<div style="display:flex;justify-content:center;">' +
        '<div style="position:relative;width:' + w + 'px;height:' + h + 'px;background:#dcb35c;border:3px solid #8b6914;border-radius:4px;">';

    for (var r = 0; r < 10; r++) {
        for (var c = 0; c < 8; c++) {
            var x = 10 + c * cellSize, y = 10 + r * cellSize;
            html += '<div style="position:absolute;left:' + x + 'px;top:' + y + 'px;width:' + cellSize + 'px;height:' + cellSize + 'px;' +
                'border:1px solid rgba(0,0,0,0.2);box-sizing:border-box;display:flex;align-items:center;justify-content:center;' +
                'font-size:' + (cellSize * 0.6) + 'px;cursor:pointer;user-select:none;" ' +
                'data-row="' + r + '" data-col="' + c + '">';
            var piece = this.board[r][c];
            if (piece !== 0) {
                var key = Object.keys(ChessGame.PIECES)[Math.abs(piece) - 1];
                var info = ChessGame.PIECES[key];
                var color = piece > 0 ? '#cc0000' : '#333';
                var bg = (this.selected && this.selected[0] === r && this.selected[1] === c) ?
                    'rgba(255,255,0,0.4)' : '';
                // 高亮可移动位置
                if (this.selected) {
                    var moves = this._getMoves(this.selected[0], this.selected[1]);
                    if (moves.some(function(m) { return m[0] === r && m[1] === c; })) {
                        bg = 'rgba(0,255,0,0.2)';
                    }
                }
                html += '<span style="color:' + color + ';text-shadow:1px 1px 1px rgba(0,0,0,0.5);' +
                    (bg ? 'background:' + bg + ';border-radius:50%;width:100%;height:100%;display:flex;align-items:center;justify-content:center;' : '') +
                    '">' + info.unicode + '</span>';
            }
            html += '</div>';
        }
    }
    // 楚河汉界
    html += '<div style="position:absolute;left:10px;top:' + (10 + cellSize * 4.5) + 'px;width:' + (cellSize * 8) + 'px;height:' + (cellSize) + 'px;' +
        'display:flex;align-items:center;justify-content:center;color:#8b6914;font-weight:bold;font-size:16px;border-top:2px solid #8b6914;border-bottom:2px solid #8b6914;\">楚河 汉界</div>';

    html += '</div></div>';
    html += '<div style="margin-top:12px;text-align:center;">' +
        '<span style="font-size:18px;">' + (this.turn === 'red' ? '🔴 红方' : '⚫ 黑方') + ' 执子</span>' +
        '<div style="margin-top:8px;">' +
        '<button class="game-btn" id="chess-new-game">🔄 新游戏</button>' +
        '<button class="game-btn" id="chess-undo">↩️ 悔棋</button>' +
        '<button class="game-btn game-btn-danger" id="chess-resign">🏳️ 认输</button>' +
        '</div></div>';

    this.el.innerHTML = html;
    this._bindEvents();
};

ChessGame.prototype._handleClick = function(r, c) {
    var piece = this.board[r][c];
    if (this.selected) {
        // 尝试移动
        var moves = this._getMoves(this.selected[0], this.selected[1]);
        if (moves.some(function(m) { return m[0] === r && m[1] === c; })) {
            this._move(this.selected[0], this.selected[1], r, c);
            return;
        }
    }
    // 选择棋子
    if (piece !== 0 && ((this.turn === 'red' && piece > 0) || (this.turn === 'black' && piece < 0))) {
        this.selected = [r, c];
        this._render();
    }
};

ChessGame.prototype._getMoves = function(r, c) {
    var piece = this.board[r][c];
    if (piece === 0) return [];
    var isRed = piece > 0;
    var type = Math.abs(piece);
    var moves = [];
    var self = this;

    function addMove(nr, nc) {
        if (nr < 0 || nr >= 10 || nc < 0 || nc >= 8) return;
        var target = self.board[nr][nc];
        if (target === 0 || (isRed && target < 0) || (!isRed && target > 0)) {
            moves.push([nr, nc]);
        }
    }

    switch (type) {
        case 1: // 车
            for (var i = r - 1; i >= 0; i--) { addMove(i, c); if (self.board[i][c] !== 0) break; }
            for (var i = r + 1; i < 10; i++) { addMove(i, c); if (self.board[i][c] !== 0) break; }
            for (var j = c - 1; j >= 0; j--) { addMove(r, j); if (self.board[r][j] !== 0) break; }
            for (var j = c + 1; j < 8; j++) { addMove(r, j); if (self.board[r][j] !== 0) break; }
            break;
        case 2: // 马
            var horse = [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]];
            horse.forEach(function(h) {
                var tr = r + h[0], tc = c + h[1];
                var br = r + (h[0] > 0 ? 1 : h[0] < 0 ? -1 : 0);
                var bc = c + (h[1] > 0 ? 1 : h[1] < 0 ? -1 : 0);
                if (self.board[br] && self.board[br][bc] === 0) addMove(tr, tc);
            });
            break;
        case 3: // 象
            var diag = [[-2,-2],[-2,2],[2,-2],[2,2]];
            diag.forEach(function(d) {
                var tr = r + d[0], tc = c + d[1];
                var mr = r + d[0] / 2, mc = c + d[1] / 2;
                if (tr >= 0 && tr < 10 && tc >= 0 && tc < 8 && self.board[mr] && self.board[mr][mc] === 0) {
                    if ((isRed && tr <= 4) || (!isRed && tr >= 5)) addMove(tr, tc);
                }
            });
            break;
        case 4: // 士
            var ang = [[-1,-1],[-1,1],[1,-1],[1,1]];
            ang.forEach(function(d) {
                var tr = r + d[0], tc = c + d[1];
                if ((isRed && tr >= 7 && tr <= 9 && tc >= 3 && tc <= 5) ||
                    (!isRed && tr >= 0 && tr <= 2 && tc >= 3 && tc <= 5)) addMove(tr, tc);
            });
            break;
        case 5: // 将
            var dirs = [[-1,0],[1,0],[0,-1],[0,1]];
            dirs.forEach(function(d) {
                var tr = r + d[0], tc = c + d[1];
                if ((isRed && tr >= 7 && tr <= 9 && tc >= 3 && tc <= 5) ||
                    (!isRed && tr >= 0 && tr <= 2 && tc >= 3 && tc <= 5)) addMove(tr, tc);
                // 飞将（对面将）- 简化：同列直线无子可吃将
                if (tr === r) {
                    var between = false;
                    var minc = Math.min(c, tc), maxc = Math.max(c, tc);
                    for (var cc = minc + 1; cc < maxc; cc++) {
                        if (self.board[r][cc] !== 0) { between = true; break; }
                    }
                    if (!between && self.board[tr][tc] === -piece) {
                        addMove(tr, tc);
                    }
                }
            });
            break;
        case 6: // 炮
            for (var i = r - 1; i >= 0; i--) {
                if (self.board[i][c] === 0) { addMove(i, c); }
                else {
                    for (var k = i - 1; k >= 0; k--) {
                        if (self.board[k][c] !== 0) { addMove(k, c); break; }
                    }
                    break;
                }
            }
            for (var i = r + 1; i < 10; i++) {
                if (self.board[i][c] === 0) { addMove(i, c); }
                else {
                    for (var k = i + 1; k < 10; k++) {
                        if (self.board[k][c] !== 0) { addMove(k, c); break; }
                    }
                    break;
                }
            }
            for (var j = c - 1; j >= 0; j--) {
                if (self.board[r][j] === 0) { addMove(r, j); }
                else {
                    for (var k = j - 1; k >= 0; k--) {
                        if (self.board[r][k] !== 0) { addMove(k, c); break; }
                    }
                    break;
                }
            }
            for (var j = c + 1; j < 8; j++) {
                if (self.board[r][j] === 0) { addMove(r, j); }
                else {
                    for (var k = j + 1; k < 8; k++) {
                        if (self.board[r][k] !== 0) { addMove(k, c); break; }
                    }
                    break;
                }
            }
            break;
        case 7: // 兵
            var dir = isRed ? -1 : 1;
            addMove(r + dir, c);
            if ((isRed && r <= 4) || (!isRed && r >= 5)) {
                addMove(r, c - 1);
                addMove(r, c + 1);
            }
            break;
    }
    return moves;
};

ChessGame.prototype._move = function(fr, fc, tr, tc) {
    this.moveHistory.push({
        board: JSON.parse(JSON.stringify(this.board)),
        turn: this.turn
    });

    var captured = this.board[tr][tc];
    this.board[tr][tc] = this.board[fr][fc];
    this.board[fr][fc] = 0;

    if (captured !== 0) {
        this.score += 100;
        GameUtils.playSound(300, 0.1, 'square');
    } else {
        GameUtils.playSound(500, 0.05, 'sine');
    }

    this.moves++;
    this.turn = this.turn === 'red' ? 'black' : 'red';
    this.selected = null;
    this._updateUI();
    this._render();
    this.save();

    // AI响应（简化）
    if (this.state === 'running') {
        this._aiMove();
    }
};

ChessGame.prototype._undo = function() {
    if (this.moveHistory.length === 0) { GameHub.showToast('没有可悔棋的步骤'); return; }
    var prev = this.moveHistory.pop();
    this.board = prev.board;
    this.turn = prev.turn;
    this.selected = null;
    this._render();
};

/** 胜利检测：检查是否将军或将死 */
ChessGame.prototype.checkWin = function() {
    // 检测将/帅是否被吃
    var redKing = false, blackKing = false;
    for (var r = 0; r < 10; r++) {
        for (var c = 0; c < 8; c++) {
            if (this.board[r][c] === 1) redKing = true;
            if (this.board[r][c] === -1) blackKing = true;
        }
    }
    if (!redKing) {
        this.gameOver();
        GameHub.showToast('🏆 黑方胜利！黑将吃掉了红帅！');
        return 'black';
    }
    if (!blackKing) {
        this.gameOver();
        GameHub.showToast('🏆 红方胜利！红帅吃掉了黑将！');
        return 'red';
    }

    // 检测是否被将军（无路可逃即为输，简化：检测将是否被攻击）
    var attacker = this._isKingInCheck(this.turn === 'red' ? 1 : -1);
    var defender = this._isKingInCheck(this.turn === 'black' ? -1 : 1);
    if (attacker && !defender) {
        GameHub.showToast('⚠️ ' + (this.turn === 'red' ? '红' : '黑') + '方被将军！');
        this.score += 50;
        this._updateUI();
    }

    return null;
};

/** 检查某一方是否被将军 */
ChessGame.prototype._isKingInCheck = function(kingPiece) {
    var kingPos = null;
    for (var r = 0; r < 10; r++) {
        for (var c = 0; c < 8; c++) {
            if (this.board[r][c] === kingPiece) kingPos = [r, c];
        }
    }
    if (!kingPos) return false;

    for (var i = 0; i < 10; i++) {
        for (var j = 0; j < 8; j++) {
            var p = this.board[i][j];
            if (p !== 0 && (kingPiece === 1 ? p < 0 : p > 0)) {
                var moves = this._getMoves(i, j);
                if (moves.some(function(m) { return m[0] === kingPos[0] && m[1] === kingPos[1]; })) {
                    return true;
                }
            }
        }
    }
    return false;
};

// AI走子（简单随机）
ChessGame.prototype._aiMove = function() {
    var self = this;
    var allMoves = [];
    var aiColor = this.turn;

    for (var r = 0; r < 10; r++) {
        for (var c = 0; c < 8; c++) {
            var p = this.board[r][c];
            if (p !== 0 && ((aiColor === 'black' && p < 0) || (aiColor === 'red' && p > 0))) {
                var moves = this._getMoves(r, c);
                moves.forEach(function(m) { allMoves.push([r, c, m[0], m[1]]); });
            }
        }
    }

    if (allMoves.length > 0) {
        var move = allMoves[GameUtils.rand(0, allMoves.length - 1)];
        setTimeout(function() { self._move(move[0], move[1], move[2], move[3]); }, 400);
    }
};

ChessGame.prototype.togglePause = function() {
    GameEngine.prototype.togglePause.call(this);
};

ChessGame.prototype.quit = function() {
    this.state = 'idle';
    this._stopLoop();
    GameHub.closeGame();
};


ChessGame.prototype.save = function() {
    var data = {
        board: this.board,
        turn: this.turn,
        captured: this.captured || { black:0, red:0 },
        moves: this.moves,
        score: this.score,
        state: this.state
    };
    GameUtils.save(this.saveKey, data);
};

ChessGame.prototype.load = function() {
    var data = GameUtils.load(this.saveKey);
    if (data) {
        this.board = data.board || this.board;
        this.turn = data.turn || 'red';
        this.captured = data.captured || { black:0, red:0 };
        this.moves = data.moves || 0;
        this.score = data.score || 0;
        this.state = data.state || 'running';
        return data;
    }
    return null;
};


// 触摸回调：将坐标转换为棋盘行列
ChessGame.prototype._onTouchTap = function(x, y) {
    var cellSize = Math.min(55, (window.innerWidth - 100) / 8);
    var col = Math.floor(x / cellSize);
    var row = Math.floor(y / cellSize);
    if (col >= 0 && col < 8 && row >= 0 && row < 10) {
        this._handleCellClick(row, col);
    }
};


window.ChessGame = ChessGame;