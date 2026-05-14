/**
 * MahjongGame - 四川麻将（简约版）
 * 使用DOM tile实现
 */
var MahjongGame = function() {
    GameEngine.call(this, { id: 'mahjong', title: '🀄 麻将' });
    this.tiles = [];
    this.selected = [];
    this.score = 0;
    this.matches = 0;
    this.totalPairs = 0;
    this._timer = null;
    this._gameTime = 0;
};

MahjongGame.prototype = Object.create(GameEngine.prototype);
MahjongGame.prototype.constructor = MahjongGame;

// 麻将符号定义
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
    { char: '🀝', name: '五万', matchGroup: 13 },
    { char: '🀞', name: '六万', matchGroup: 14 },
    { char: '🀟', name: '七万', matchGroup: 15 },
    { char: '🀠', name: '东风', matchGroup: 16 },
    { char: '🀡', name: '南风', matchGroup: 17 },
    { char: '🀢', name: '西风', matchGroup: 18 },
    { char: '🀣', name: '北风', matchGroup: 19 },
];

MahjongGame.prototype.init = function() {
    GameEngine.prototype.init.call(this);
    this._generateTiles();
    this._render();
    this._startTimer();
};

MahjongGame.prototype._generateTiles = function() {
    this.tiles = [];
    var types = MahjongGame.TILE_TYPES.slice(0, 14); // 使用14种牌
    for (var i = 0; i < types.length; i++) {
        this.tiles.push({ ...types[i], uid: i * 2, faceUp: false, cleared: false });
        this.tiles.push({ ...types[i], uid: i * 2 + 1, faceUp: false, cleared: false });
    }
    // Fisher-Yates 洗牌
    this.tiles = GameUtils.shuffle(this.tiles);
    this.totalPairs = this.tiles.length / 2;
    this.matches = 0;
    this.selected = [];
};

MahjongGame.prototype._startTimer = function() {
    var self = this;
    var timerStart = Date.now();
    this._timer = setInterval(function() {
        self._gameTime = Date.now() - timerStart;
        document.getElementById('maj-time').textContent = GameUtils.formatTime(self._gameTime);
    }, 500);
};

MahjongGame.prototype._render = function() {
    var self = this;
    var cols = 7;
    var cellSize = Math.min(50, (window.innerWidth - 100) / cols);
    var html = '<div style="text-align:center;">' +
        '<div style="margin-bottom:12px;">' +
        '<span style="font-size:14px;">得分: <strong id="maj-score">' + this.score + '</strong></span> &nbsp;' +
        '<span style="font-size:14px;">配对: <strong>' + this.matches + '/' + this.totalPairs + '</strong></span> &nbsp;' +
        '<span style="font-size:14px;">时间: <strong id="maj-time">' + GameUtils.formatTime(this._gameTime) + '</strong></span>' +
        '</div>' +
        '<div id="maj-board" style="display:grid;grid-template-columns:repeat(' + cols + ',1fr);gap:4px;max-width:' + (cellSize * cols + 50) + 'px;margin:0 auto;">';

    this.tiles.forEach(function(tile, idx) {
        if (tile.cleared) {
            html += '<div style="width:' + cellSize + 'px;height:' + cellSize + 'px;"></div>';
        } else if (tile.faceUp) {
            var selected = self.selected.some(function(s) { return s.uid === tile.uid; });
            html += '<div style="width:' + cellSize + 'px;height:' + cellSize + 'px;' +
                'display:flex;align-items:center;justify-content:center;' +
                'font-size:' + (cellSize * 0.55) + 'px;' +
                'background:' + (selected ? 'rgba(255,215,0,0.2)' : 'rgba(255,255,255,0.9)') + ';' +
                'border:2px solid ' + (selected ? '#ffd700' : 'var(--color-border)') + ';' +
                'border-radius:4px;cursor:pointer;transition:all .15s;" ' +
                'data-uid="' + tile.uid + '">' + tile.char + '</div>';
        } else {
            html += '<div style="width:' + cellSize + 'px;height:' + cellSize + 'px;' +
                'background:linear-gradient(135deg,#2d3748,#4a5568);' +
                'border:2px solid var(--color-border);border-radius:4px;cursor:pointer;' +
                'font-size:' + (cellSize * 0.4) + 'px;color:var(--color-text-dim);" ' +
                'data-uid="' + tile.uid + '">?</div>';
        }
    });

    html += '</div>' +
        '<div style="margin-top:12px;display:flex;gap:8px;justify-content:center;">' +
        '<button class="game-btn" style="font-size:12px;padding:4px 12px;" id="maj-new">' +
        '🔄 新游戏</button>' +
        '<button class="game-btn" style="font-size:12px;padding:4px 12px;" id="maj-reveal">' +
        '👁️ 提示</button></div></div>';

    this.el.innerHTML = html;
    this._bindEvents();
};

MahjongGame.prototype._bindEvents = function() {
    var self = this;
    var board = document.getElementById('maj-board');
    if (board) {
        board.addEventListener('click', function(e) {
            var tileEl = e.target.closest('[data-uid]');
            if (!tileEl) return;
            var uid = parseInt(tileEl.dataset.uid);
            var tile = self.tiles.find(function(t) { return t.uid === uid; });
            if (!tile || tile.cleared || tile.faceUp) return;

            tile.faceUp = true;
            self.selected.push(tile);

            if (self.selected.length === 2) {
                var a = self.selected[0], b = self.selected[1];
                if (a.matchGroup === b.matchGroup) {
                    // 匹配成功
                    var cleared = self.tiles.filter(function(t) { return t.matchGroup === a.matchGroup; });
                    cleared.forEach(function(t) { t.cleared = true; t.faceUp = false; });
                    self.matches += 1;
                    self.score += 50 * self.matches; // 连击加分
                    GameUtils.playSound(600, 0.1, 'sine');
                } else {
                    // 匹配失败
                    a.faceUp = false;
                    b.faceUp = false;
                    self.score = Math.max(0, self.score - 5);
                    GameUtils.playSound(200, 0.1, 'square');
                }
                self.selected = [];
                self._updateUI();
                self._render();

                // 检查胜利
                if (self.matches === self.totalPairs) {
                    self._stopTimer();
                    self.gameOver();
                    GameHub.showToast('🎉 恭喜通关！得分: ' + self.score + ' 用时: ' + GameUtils.formatTime(self._gameTime));
                }
            }
            self._render();
        });
    }

    document.getElementById('maj-new').addEventListener('click', function() {
        self.score = 0; self.matches = 0; self._gameTime = 0;
        self._stopTimer(); self._generateTiles(); self._startTimer(); self._render();
    });

    document.getElementById('maj-reveal').addEventListener('click', function() {
        var faceDown = self.tiles.filter(function(t) { return !t.cleared && !t.faceUp; });
        if (faceDown.length > 0) {
            var idx = GameUtils.rand(0, faceDown.length - 1);
            faceDown[idx].faceUp = true;
            self._render();
            setTimeout(function() {
                faceDown[idx].faceUp = false;
                self._render();
            }, 2000);
        }
    });
};

MahjongGame.prototype._stopTimer = function() {
    if (this._timer) { clearInterval(this._timer); this._timer = null; }
};

MahjongGame.prototype._updateUI = function() {
    if (document.getElementById('maj-score')) {
        document.getElementById('maj-score').textContent = this.score;
    }
    this.scoreEl && (this.scoreEl.textContent = 'Score: ' + this.score);
};

MahjongGame.prototype.togglePause = function() {
    GameEngine.prototype.togglePause.call(this);
    if (this._timer) { clearInterval(this._timer); this._timer = null; }
    if (this.state === 'running') this._startTimer();
};

MahjongGame.prototype.quit = function() {
    this._stopTimer();
    this.state = 'idle';
    GameHub.closeGame();
};

window.MahjongGame = MahjongGame;