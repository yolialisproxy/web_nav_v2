/**
 * Solitaire - 经典纸牌接龙 (Klondike)
 * 使用DOM实现，支持拖拽操作
 */
var Solitaire = function() {
    GameEngine.call(this, { id: 'solitaire', title: '🃏 纸牌接龙' });
    this.tableau = [];       // 7列牌堆
    this.stock = [];         // 牌库
    this.waste = [];         // 废牌堆
    this.foundation = [[], [], [], []]; // 4个基础堆
    this.dragInfo = null;
    this._history = [];      // 撤销历史
};

Solitaire.prototype = Object.create(GameEngine.prototype);
Solitaire.prototype.constructor = Solitaire;

Solitaire.CARDS = [];
(function() {
    var suits = ['♠', '♥', '♦', '♣'];
    var colors = { '♠': 'black', '♥': 'red', '♦': 'red', '♣': 'black' };
    for (var s = 0; s < suits.length; s++) {
        for (var v = 1; v <= 13; v++) {
            Solitaire.CARDS.push({ suit: suits[s], value: v, color: colors[suits[s]],
                display: (function(v, s) {
                    var names = ['A','2','3','4','5','6','7','8','9','10','J','Q','K'];
                    return names[v-1] + s;
                })(v, suits[s])
            });
        }
    }
})();

Solitaire.prototype.init = function() {
        // 移动端触摸拖拽支持
        this._initTouchDrag();
    GameEngine.prototype.init.call(this);
    this.render();
};

/** 保存当前状态到历史 */
Solitaire.prototype._saveState = function() {
    var state = {
        tableau: JSON.parse(JSON.stringify(this.tableau)),
        stock: JSON.parse(JSON.stringify(this.stock)),
        waste: JSON.parse(JSON.stringify(this.waste)),
        foundation: JSON.parse(JSON.stringify(this.foundation)),
        score: this.score,
        moves: this.moves
    };
    this._history.push(state);
    // 限制历史记录长度
    if (this._history.length > 100) this._history.shift();
};

/** 撤销 */
Solitaire.prototype._undo = function() {
    if (this._history.length === 0) {
        GameHub.showToast('没有可撤销的步骤');
        return;
    }
    var state = this._history.pop();
    this.tableau = state.tableau;
    this.stock = state.stock;
    this.waste = state.waste;
    this.foundation = state.foundation;
    this.score = state.score;
    this.moves = state.moves;
    GameUtils.playSound(300, 0.1, 'sine');
    this.render();
};

/** 新游戏 */
Solitaire.prototype.newGame = function() {
    this._history = [];
    this._deal();
};

/** 移动牌：从source到target（自动尝试移到基础堆或列） */
Solitaire.prototype.move = function(fromCol, toCol) {
    if (fromCol < 0 || fromCol >= 7 || toCol < 0 || toCol >= 7) return false;
    var fromColCards = this.tableau[fromCol];
    if (fromColCards.length === 0) return false;

    // 只允许移动最上面的翻开牌及其上面的所有翻开牌
    var firstFaceUp = -1;
    for (var i = 0; i < fromColCards.length; i++) {
        if (fromColCards[i].faceUp) { firstFaceUp = i; break; }
    }
    if (firstFaceUp === -1) return false;

    var movingCards = fromColCards.slice(firstFaceUp);

    // 尝试移到目标列
    var targetCol = this.tableau[toCol];
    if (targetCol.length === 0) {
        // 空列只能放K
        if (movingCards[0].value !== 13) return false;
        // 移动
        this._saveState();
        for (var j = firstFaceUp; j < fromColCards.length; j++) {
            targetCol.push(fromColCards.pop());
        }
        // 翻开原列顶牌
        if (this.tableau[fromCol].length > 0) {
            this.tableau[fromCol][this.tableau[fromCol].length - 1].faceUp = true;
        }
        this.moves++;
        this.addScore(0);
        this._checkWin();
        this.save();
        this.render();
        return true;
    }

    var topCard = targetCol[targetCol.length - 1];
    if (!topCard.faceUp) return false;

    // 检查颜色交替、数值递减
    if (topCard.color === movingCards[0].color) return false;
    if (topCard.value !== movingCards[0].value + 1) return false;

    // 合法移动
    this._saveState();
    for (var j = firstFaceUp; j < fromColCards.length; j++) {
        targetCol.push(fromColCards.pop());
    }
    // 翻开原列顶牌
    if (this.tableau[fromCol].length > 0) {
        this.tableau[fromCol][this.tableau[fromCol].length - 1].faceUp = true;
    }
    this.moves++;
    this.addScore(0);
    this._checkWin();
    this.save();
    this.render();
    return true;
};

Solitaire.prototype.render = function() {
    var self = this;
    var h = '';
    // 顶行：牌库、废牌、4个基础堆
    h += '<div class=\"sol-top-row\">'
    h += '<div class=\"sol-pile sol-stock\" id=\"sol-stock\" data-pile=\"stock\">' +
        (this.stock.length > 0 ? '<div class=\"sol-card back\"></div>' : '<div class=\"sol-placeholder\">📦</div>') +
        '</div>';
    h += '<div class=\"sol-pile sol-waste\" id=\"sol-waste\" data-pile=\"waste\">';
    for (var i = Math.max(0, this.waste.length - 3); i < this.waste.length; i++) {
        h += this._renderCard(this.waste[i], true);
    }
    h += '</div>';
    // 基础堆
    for (var f = 0; f < 4; f++) {
        h += '<div class=\"sol-pile sol-foundation\" id=\"sol-foundation-' + f + '\" data-pile=\"foundation-' + f + '\">';
        if (this.foundation[f].length > 0) {
            h += this._renderCard(this.foundation[f][this.foundation[f].length - 1], true);
        } else {
            h += '<div class=\"sol-placeholder\">🏆</div>';
        }
        h += '</div>';
    }
    h += '</div>';
    // 7列牌桌
    h += '<div class=\"sol-tableau\" id=\"sol-tableau\">';
    for (var c = 0; c < 7; c++) {
        h += '<div class=\"sol-col\" id=\"sol-col-' + c + '\" data-col=\"' + c + '\">';
        for (var r = 0; r < this.tableau[c].length; r++) {
            var card = this.tableau[c][r];
            var isLast = (r === this.tableau[c].length - 1);
            h += '<div class=\"sol-card-tableau\" data-col=\"' + c + '\" data-row=\"' + r + '\" style=\"margin-top:' + (isLast ? '0' : r * 22) + 'px\">';
            if (card.faceUp) {
                h += this._renderCard(card, true);
            } else {
                h += '<div class=\"sol-card back\" style=\"position:absolute;top:' + (r * 22) + 'px\">' +
                    '<div class=\"card-inner\">?</div></div>';
            }
            h += '</div>';
        }
        h += '</div>';
    }
    h += '</div>';
    // 按钮
    h += '<div class=\"game-actions-bar\"><button class=\"game-btn\" id=\"sol-new-game\">🔄 新游戏</button>' +
        '<button class=\"game-btn\" id=\"sol-hint\">💡 提示</button>' +
        '<button class=\"game-btn\" id=\"sol-undo\">↩️ 撤销(' + this._history.length + ')</button></div>';
    h += '<div style=\"clear:both\"></div>';

    var cardW = window.innerWidth < 600 ? 38 : 56;
    var cardH = cardW * 1.4;
    var gap = window.innerWidth < 600 ? 2 : 4;

    // 动态生成CSS
    h += '<style>' +
        '.sol-top-row{display:flex;gap:' + gap + 'px;padding:10px;' + (window.innerWidth < 600 ? 'flex-wrap:wrap;' : 'justify-content:center;') + '}' +
        '.sol-pile{width:' + cardW + 'px;height:' + cardH + 'px;position:relative;}' +
        '.sol-placeholder{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:20px;border:2px dashed var(--color-border);border-radius:6px;color:var(--color-text-dim)}' +
        '.sol-card{width:100%;height:100%;position:absolute;top:0;left:0;}' +
        '.sol-card-tableau{width:100%;position:absolute;top:0;left:0;}' +
        '.sol-col{position:relative;width:' + cardW + 'px;min-height:' + (cardH + 50) + 'px;}' +
        '.sol-tableau{display:flex;gap:' + gap + 'px;padding:15px;' + (window.innerWidth < 600 ? 'overflow-x:auto;justify-content:flex-start;' : 'justify-content:center;') + '}' +
        '.sol-pile{cursor:pointer;}' +
        '.sol-pile:hover{transform:translateY(-2px);}' +
        '.sol-col{cursor:pointer;}' +
        '.sol-col:hover .sol-card-tableau:last-child{transform:translateY(-2px);}' +
        '@media(max-width:600px){.sol-card{font-size:11px}.sol-pile{width:38px;height:53px}}' +
        '</style>';

    this.el.innerHTML = h;
    this._bindEvents();
    if (this.moves === 0) this._deal();
};

Solitaire.prototype._deal = function() {
    var deck = GameUtils.shuffle(Solitaire.CARDS);
    this.tableau = [[], [], [], [], [], [], []];
    for (var i = 0; i < 7; i++) {
        for (var j = 0; j <= i; j++) {
            var card = deck.pop();
            card.faceUp = (j === i);
            this.tableau[i].push(card);
        }
    }
    this.stock = deck;
    this.waste = [];
    this.foundation = [[], [], [], []];
    this._history = [];
    this.score = 0;
    this.moves = 0;
    this.lines = 0;
    this.save();
    this.render();
};

Solitaire.prototype._renderCard = function(card, faceUp) {
    var s = card.suit, v = card.value, c = card.color;
    var names = {1:'A',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'10',11:'J',12:'Q',13:'K'};
    var bg = c === 'red' ? 'rgba(255,80,80,0.15)' : 'rgba(255,255,255,0.08)';
    var txt = c === 'red' ? '#ff6b6b' : '#e2e8f0';
    return '<div class=\"sol-card-face\" style=\"width:100%;height:100%;background:' + bg +
        ';border:1px solid var(--color-border);border-radius:6px;display:flex;flex-direction:column;' +
        'align-items:center;justify-content:center;color:' + txt + ';font-size:14px;font-weight:bold;\">' +
        '<div>' + s + '</div><div style=\"font-size:12px;opacity:0.7\">' + names[v] + '</div></div>';
};

Solitaire.prototype._bindEvents = function() {
    var self = this;
    // 牌库点击
    var stock = document.getElementById('sol-stock');
    if (stock) {
        stock.addEventListener('click', function() {
            if (self.state !== 'running') return;
            self._saveState();
            if (self.stock.length > 0) {
                var card = self.stock.pop();
                card.faceUp = true;
                self.waste.push(card);
                self.moves++;
                self.addScore(0);
                self.save();
                self.render();
            } else if (self.waste.length > 0) {
                while (self.waste.length > 0) {
                    var c = self.waste.pop();
                    c.faceUp = false;
                    self.stock.push(c);
                }
                self.moves++;
                self.save();
                self.render();
            }
        });
    }
    // 废牌双击移到基础堆
    var waste = document.getElementById('sol-waste');
    if (waste) {
        waste.addEventListener('dblclick', function() {
            if (self.waste.length > 0) self._autoToFoundation(self.waste[self.waste.length - 1]);
        });
    }
    // 新游戏
    var newBtn = document.getElementById('sol-new-game');
    if (newBtn) newBtn.addEventListener('click', function() { self.newGame(); });
    // 撤销
    var undoBtn = document.getElementById('sol-undo');
    if (undoBtn) undoBtn.addEventListener('click', function() { self._undo(); });
    // 列点击：尝试顶牌移到基础堆
    for (var c = 0; c < 7; c++) {
        (function(col) {
            var colEl = document.getElementById('sol-col-' + col);
            if (colEl) {
                colEl.addEventListener('dblclick', function() {
                    if (self.state !== 'running') return;
                    var cards = self.tableau[col];
                    if (cards.length === 0) return;
                    var topCard = cards[cards.length - 1];
                    if (!topCard.faceUp) return;
                    self._autoToFoundation(topCard);
                });
            }
        })(c);
    }
};

/** 自动将牌移到合适的基础堆 */
Solitaire.prototype._autoToFoundation = function(card) {
    var suitIdx = ['♠','♥','♦','♣'].indexOf(card.suit);
    if (suitIdx === -1) return false;
    var f = this.foundation[suitIdx];
    var expected = (f.length === 0) ? 1 : f[f.length - 1].value + 1;
    if (card.value === expected) {
        f.push(card);
        // 从牌堆中移除
        this._removeCardFromTableau(card);
        this.score += 10;
        this.moves++;
        this.lines = f.reduce(function(s, arr) { return s + arr.length; }, 0);
        this._checkWin();
        this.save();
        this.render();
        return true;
    }
    return false;
};

/** 从tableau中移除指定的牌 */
Solitaire.prototype._removeCardFromTableau = function(card) {
    for (var c = 0; c < 7; c++) {
        var col = this.tableau[c];
        for (var r = col.length - 1; r >= 0; r--) {
            if (col[r] === card) {
                col.splice(r, 1);
                // 翻开移除后最上面的牌
                if (col.length > 0) col[col.length - 1].faceUp = true;
                return true;
            }
        }
    }
    // 检查废牌
    for (var i = this.waste.length - 1; i >= 0; i--) {
        if (this.waste[i] === card) {
            this.waste.splice(i, 1);
            return true;
        }
    }
    return false;
};

Solitaire.prototype._checkWin = function() {
    if (this.foundation.every(function(f) { return f.length === 13; })) {
        this.gameOver();
        GameHub.showToast('🎉 恭喜完成纸牌接龙！最终得分: ' + this.score);
    }
};

Solitaire.prototype.addScore = function(points) {
    this.score += points;
};

Solitaire.prototype.save = function() {
    var data = {
        tableau: this.tableau,
        stock: this.stock,
        waste: this.waste,
        foundation: this.foundation,
        score: this.score,
        moves: this.moves,
        state: this.state
    };
    GameUtils.save(this.saveKey, data);
};

Solitaire.prototype.load = function() {
    var data = GameUtils.load(this.saveKey);
    if (data) {
        this.tableau = data.tableau || this.tableau;
        this.stock = data.stock || this.stock;
        this.waste = data.waste || this.waste;
        this.foundation = data.foundation || this.foundation;
        this.score = data.score || 0;
        this.moves = data.moves || 0;
        this.state = data.state || 'running';
        return true;
    }
    return false;
};

Solitaire.prototype.tick = function() {}; // pass回合制


Solitaire.prototype.quit = function() {
    this.state = 'idle';
    GameHub.closeGame();
};


// Solitaire 触摸拖拽支持
Solitaire.prototype._initTouchDrag = function() {
    var cards = this.el.querySelectorAll('[data-card]');
    var self = this;
    cards.forEach(function(card) {
        card.addEventListener('touchstart', function(e) {
            e.preventDefault();
            var touch = e.touches[0];
            card._touchStartX = touch.clientX;
            card._touchStartY = touch.clientY;
            card._touchMoved = false;
            card._origTransform = card.style.transform || '';
        }, { passive: false });

        card.addEventListener('touchmove', function(e) {
            e.preventDefault();
            var touch = e.touches[0];
            var dx = touch.clientX - card._touchStartX;
            var dy = touch.clientY - card._touchStartY;
            if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
                card._touchMoved = true;
                card.style.transform = 'translate(' + dx + 'px, ' + dy + 'px)';
                card.style.zIndex = 1000;
            }
        }, { passive: false });

        card.addEventListener('touchend', function(e) {
            if (card._touchMoved) {
                card.style.transform = card._origTransform;
                card.style.zIndex = '';
                var endEvent = new CustomEvent('cardtouchend', {
                    detail: {
                        card: card,
                        clientX: e.changedTouches[0].clientX,
                        clientY: e.changedTouches[0].clientY
                    }
                });
                card.dispatchEvent(endEvent);
            } else {
                card.click();
            }
        }, { passive: false });
    });
};

window.Solitaire = Solitaire;