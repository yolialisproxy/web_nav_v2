/**
 * DatingGame - 恋爱大富翁（恋爱养成 + 大富翁模式）
 * 支持：一男追多女、一女追多男、一男多女模式
 */
var DatingGame = function() {
    GameEngine.call(this, { id: 'dating', title: '💕 恋爱大富翁' });
    this.mode = 'male'; // male/female/multi
    this.player = null;
    this.targets = [];
    this.board = [];
    this.position = 0;
    this.turns = 0;
    this.affection = {};
    this.events = [];
    this.day = 1;
};

DatingGame.prototype = Object.create(GameEngine.prototype);
DatingGame.prototype.constructor = DatingGame;

// 格子类型
DatingGame.CELL_TYPES = {
    NORMAL: 0, EVENT: 1, GIFT: 2, DATE: 3, RIVAL: 4, HEART: 5
};

DatingGame.CHARACTERS = [
    { name: '林雨桐', icon: '🌸', color: '#ff69b4', desc: '温柔可人的文学社社长' },
    { name: '苏婉儿', icon: '🌺', color: '#ff1493', desc: '高冷的学霸千金' },
    { name: '唐小蝶', icon: '🦋', color: '#ff6347', desc: '活泼开朗的邻家女孩' },
    { name: '慕容雪', icon: '❄️', color: '#87ceeb', desc: '冰雪聪明的转校生' }
];

DatingGame.EVENTS = [
    { type: 'gift', text: '💝 随机礼物！好感+10', affectionDelta: 10, goldCost: -20 },
    { type: 'date', text: '💕 浪漫约会！好感+20', affectionDelta: 20, goldCost: -50 },
    { type: 'rival', text: '😡 情敌出现！好感-8', affectionDelta: -8 },
    { type: 'lucky', text: '🍀 幸运日！获得50两', goldDelta: 50 },
    { type: 'trap', text: '💀 踩到陷阱！失去30两', goldDelta: -30 },
    { type: 'charm', text: '✨ 魅力提升！好感+5', affectionDelta: 5 }
];

DatingGame.prototype.init = function() {
    GameEngine.prototype.init.call(this);
    // 尝试读取存档
    if (!this.load()) {
        this._selectMode();
    } else {
        this.state = 'running';
        this._startGame(); // 初始化玩家数据
    }
};

DatingGame.prototype._selectMode = function() {
    var self = this;
    var modes = [
        { key: 'male', icon: '👨', label: '一男追多女' },
        { key: 'female', icon: '👩', label: '一女追多男' },
        { key: 'multi', icon: '👫', label: '一男多女模式' }
    ];
    var html = '<div style="text-align:center;padding:30px;">' +
        '<div style="font-size:24px;margin-bottom:20px;">💕 恋爱大富翁</div>' +
        '<div style="font-size:13px;color:var(--color-text-dim);margin-bottom:20px;">选择你的游戏模式</div>';
    modes.forEach(function(m) {
        html += '<button class="game-btn" data-mode="' + m.key + '" style="padding:12px 30px;font-size:15px;margin:6px;width:auto;">' +
            m.icon + ' ' + m.label + '</button>';
    });
    html += '</div>';
    this.el.innerHTML = html;
    this.el.querySelectorAll('[data-mode]').forEach(function(btn) {
        btn.addEventListener('click', function() {
            self.mode = this.dataset.mode;
            self.newGame();
        });
    });
};

DatingGame.prototype.newGame = function() {
    this._reset();
    this.state = 'running';
    this.render();
    this.save();
};

DatingGame.prototype._reset = function() {
    this.d = {};
    this.turns = 0;
    this.day = 1;
    this.gold = 100;
    this.score = 0;
    this.affection = {};
    this.player = { name: this.mode === 'female' ? '苏雨晴' : '李逍遥', gold: 100 };
    this.clearSave();
    this._startGame();
};

DatingGame.prototype._startGame = function() {
    this.targets = DatingGame.CHARACTERS.map(function(c, i) {
        return { ...c, affection: 30 + Math.floor(Math.random() * 20), uid: i, gifts: 0 };
    });
    this.targets.forEach(function(t) { this.affection[t.name] = t.affection; }, this);
    this._generateBoard();
    this.position = 0;
    this.state = 'running';
    this.render();
};

DatingGame.prototype._generateBoard = function() {
    this.board = [];
    var size = 24;
    for (var i = 0; i < size; i++) {
        var type = DatingGame.CELL_TYPES.NORMAL;
        var event = null;
        if (i === 0) { type = DatingGame.CELL_TYPES.HEART; }
        else if (i % 6 === 0 && i > 0) { type = DatingGame.CELL_TYPES.DATE; }
        else if (i % 4 === 0) { type = DatingGame.CELL_TYPES.EVENT; }
        else if (i % 7 === 0) { type = DatingGame.CELL_TYPES.GIFT; }
        else if (i % 8 === 0) { type = DatingGame.CELL_TYPES.RIVAL; }
        else {
            var evIdx = i % DatingGame.EVENTS.length;
            type = DatingGame.CELL_TYPES.EVENT;
            event = DatingGame.EVENTS[evIdx];
        }
        this.board.push({ type: type, event: event, index: i });
    }
};

DatingGame.prototype.render = function() {
    var self = this;
    if (!this.el) return;
    if (!this.targets || this.targets.length === 0) {
        this._selectMode();
        return;
    }
    if (this.state === 'idle') return;

    var html = '';
    // 状态栏
    html += '<div style="display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap;justify-content:center;font-size:13px;">' +
        '<span>📅 第' + this.day + '天</span>' +
        '<span>💰 ' + this.player.gold + '两</span>' +
        '<span>🎯 步数: ' + this.turns + '</span>' +
        '</div>';

    // 棋盘
    html += '<div style="overflow-x:auto;padding:10px 0;margin-bottom:16px;">';
    html += '<div style="display:flex;gap:4px;min-width:max-content;">';
    this.board.forEach(function(cell, i) {
        var isCurrent = i === self.position;
        var bg = isCurrent ? 'rgba(255,215,0,0.3)' : i % 2 === 0 ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.1)';
        var symbols = ['🏠', '💕', '🎁', '🌸', '😡', '✨'];
        var icon = cell.type <= 5 ? symbols[cell.type] : '📍';
        html += '<div style="width:44px;height:44px;display:flex;align-items:center;justify-content:center;' +
            'border-radius:6px;background:' + bg + ';border:2px solid ' +
            (isCurrent ? '#ffd700' : 'var(--color-border)') + ';font-size:20px;flex-shrink:0;">' +
            icon + '</div>';
    });
    html += '</div></div>';

    // 当前格子
    var cell = this.board[this.position];
    html += '<div style="text-align:center;margin-bottom:12px;">';
    html += '<div style="font-size:12px;color:var(--color-text-dim);">当前格子</div>';
    html += '<div style="font-size:18px;">' + (cell.type <= 5 ? ['🏠 起点', '💕 约会', '🎁 礼物', '🌸 事件', '😡 情敌', '✨ 心意'][cell.type] : '📍 普通') + '</div>';
    html += '</div>';

    // 好感度
    html += '<div style="margin-bottom:12px;">';
    this.targets.forEach(function(t) {
        var a = self.affection[t.name] || 0;
        var color = a > 80 ? '#ff6b6b' : a > 50 ? '#ffd700' : a > 20 ? '#87ceeb' : '#ff6347';
        html += '<div style="margin-bottom:4px;">' + t.icon + ' ' + t.name +
            ' <span style="color:' + color + ';">' + a + '</span>/100 ' +
            '<span style="font-size:10px;color:var(--color-text-dim);">' + '💕'.repeat(Math.floor(a / 25)) + '</span></div>';
    });
    html += '</div>';

    // 操作按钮
    if (this.state === 'running') {
        html += '<div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">' +
            '<button class="game-btn" id="dating-roll">🎲 掷骰子</button>' +
            '<button class="game-btn" id="dating-invest">💰 投资(股市)</button>' +
            '<button class="game-btn" id="dating-gift">🎁 送礼(-20两)</button>' +
            '<button class="game-btn" id="dating-endday">🌙 结束当天</button>' +
            '</div>';
    }

    // 日志
    if (this.events.length > 0) {
        html += '<div style="margin-top:12px;text-align:left;font-size:12px;color:var(--color-text-dim);max-height:100px;overflow-y:auto;">';
        this.events.slice(-6).forEach(function(ev) { html += '<div>' + ev + '</div>'; });
        html += '</div>';
    }

    this.el.innerHTML = html;
    this._bindEvents();
};

DatingGame.prototype._bindEvents = function() {
    var self = this;
    var rollBtn = document.getElementById('dating-roll');
    if (rollBtn) rollBtn.addEventListener('click', function() { self._rollDice(); });
    var investBtn = document.getElementById('dating-invest');
    if (investBtn) investBtn.addEventListener('click', function() { self._invest(); });
    var giftBtn = document.getElementById('dating-gift');
    if (giftBtn) giftBtn.addEventListener('click', function() { self._giveGift(); });
    var endBtn = document.getElementById('dating-endday');
    if (endBtn) endBtn.addEventListener('click', function() { self._endDay(); });
};

DatingGame.prototype._rollDice = function() {
    var steps = GameUtils.rand(1, 6);
    this.turns++;
    this.position = (this.position + steps) % this.board.length;
    var cell = this.board[this.position];
    this.events.push('第' + this.day + '天 第' + this.turns + '步: 掷出' + steps + '，到达' + this.position + '号格');
    this._processCell(cell);
    this._checkWinLose();
    this.save();
    this.render();
};

DatingGame.prototype._processCell = function(cell) {
    var self = this;
    var targetIdx = GameUtils.rand(0, this.targets.length - 1);
    var target = this.targets[targetIdx];

    switch (cell.type) {
        case DatingGame.CELL_TYPES.HEART:
            this.events.push('🏠 回到起点，获得20两');
            this.player.gold += 20;
            break;
        case DatingGame.CELL_TYPES.DATE:
            if (this.player.gold >= 30) {
                this.player.gold -= 30;
                var delta = GameUtils.rand(5, 15);
                this.affection[target.name] = Math.min(100, (this.affection[target.name] || 0) + delta);
                target.gifts++;
                this.events.push('💕 和' + target.name + '约会，好感+' + delta);
                GameUtils.playSound(660, 0.1, 'sine');
            } else {
                this.events.push('💕 想约会但钱不够...');
            }
            break;
        case DatingGame.CELL_TYPES.GIFT:
            if (this.player.gold >= 15) {
                this.player.gold -= 15;
                var d = GameUtils.rand(3, 12);
                this.affection[target.name] = Math.min(100, (this.affection[target.name] || 0) + d);
                this.events.push('🎁 送给' + target.name + '礼物，好感+' + d);
                GameUtils.playSound(520, 0.08, 'sine');
            }
            break;
        case DatingGame.CELL_TYPES.EVENT:
            if (cell.event) {
                var ev = cell.event;
                if (ev.goldDelta) this.player.gold = Math.max(0, this.player.gold + ev.goldDelta);
                if (ev.affectionDelta) {
                    this.affection[target.name] = Math.max(0, Math.min(100,
                        (this.affection[target.name] || 0) + ev.affectionDelta));
                }
                this.events.push(ev.text);
            }
            break;
        case DatingGame.CELL_TYPES.RIVAL:
            var delta = GameUtils.rand(5, 15);
            this.affection[target.name] = Math.max(0, (this.affection[target.name] || 0) - delta);
            this.events.push('😡 情敌' + target.name + '出现，好感-' + delta);
            GameUtils.playSound(150, 0.15, 'square');
            break;
        case DatingGame.CELL_TYPES.NORMAL:
            this.events.push('📍 普通格子，继续前行');
            break;
    }
};

/** 投资功能：小游戏几率获得双倍/亏损 */
DatingGame.prototype._invest = function() {
    if (this.player.gold < 50) {
        GameHub.showToast('💰 至少需要50两才能投资！');
        return;
    }
    // 简化：50%几率赚钱100%，50%亏光
    if (Math.random() < 0.5) {
        this.player.gold *= 2;
        this.score += 100;
        this.events.push('📈 投资大获成功！金钱翻倍！');
        GameUtils.playSound(660, 0.2, 'sine');
    } else {
        this.player.gold = Math.floor(this.player.gold * 0.3);
        this.score = Math.max(0, this.score - 50);
        this.events.push('📉 投资失败！损失惨重...');
        GameUtils.playSound(200, 0.3, 'square');
    }
    this.save();
    this.render();
};

DatingGame.prototype._giveGift = function() {
    if (this.player.gold < 20) { GameHub.showToast('💰 金钱不足！'); return; }
    var self = this;
    var html = '<div style="text-align:center;padding:10px;">送礼物给谁？<br>';
    this.targets.forEach(function(t, i) {
        html += '<button class="game-btn" data-target="' + i + '" style="margin:4px;padding:6px 14px;">' +
            t.icon + ' ' + t.name + '</button>';
    });
    html += '</div>';
    var area = document.getElementById('game-play-area');
    if (!area) return;
    var overlay = document.createElement('div');
    overlay.style.cssText = 'position:absolute;inset:0;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;z-index:10;';
    overlay.innerHTML = html;
    area.appendChild(overlay);
    overlay.querySelectorAll('[data-target]').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var t = self.targets[parseInt(this.dataset.target)];
            self.player.gold -= 20;
            var d = GameUtils.rand(8, 18);
            self.affection[t.name] = Math.min(100, (self.affection[t.name] || 0) + d);
            t.gifts++;
            self.events.push('🎁 送给' + t.name + '礼物，好感+' + d);
            overlay.parentNode.removeChild(overlay);
            self.save();
            self.render();
        });
    });
};

DatingGame.prototype._endDay = function() {
    this.day++;
    this.turns = 0;
    this.position = 0;
    // 每天消耗
    if (this.day % 3 === 0) {
        this.player.gold = Math.max(0, this.player.gold - 10);
        this.events.push('🌙 日常开支 -10两');
    }
    this.events.push('--- 第' + this.day + '天开始 ---');
    this.save();
    this.render();
};

DatingGame.prototype._checkWinLose = function() {
    var self = this;
    this.targets.forEach(function(t) {
        if ((self.affection[t.name] || 0) >= 90) {
            self.state = 'over';
            self.gameOver();
            GameHub.showToast('💕 恭喜！' + t.icon + t.name + '接受了你的心意！最终得分: ' + self.score);
        }
    });
    if (this.player.gold <= 0 && this.day > 5) {
        this.state = 'over';
        this.gameOver();
        GameHub.showToast('💀 一贫如洗，感情之路也走到了尽头...');
    }
};

DatingGame.prototype.save = function() {
    var data = {
        mode: this.mode,
        player: this.player,
        targets: this.targets,
        board: this.board,
        position: this.position,
        turns: this.turns,
        affection: this.affection,
        events: this.events,
        day: this.day,
        gold: this.player.gold,
        score: this.score,
        state: this.state
    };
    GameUtils.save(this.saveKey, data);
};

DatingGame.prototype.load = function() {
    var data = GameUtils.load(this.saveKey);
    if (data) {
        this.mode = data.mode || 'male';
        this.player = data.player || { name: '玩家', gold: 100 };
        this.targets = data.targets || [];
        this.board = data.board || [];
        this.position = data.position || 0;
        this.turns = data.turns || 0;
        this.affection = data.affection || {};
        this.events = data.events || [];
        this.day = data.day || 1;
        this.score = data.score || 0;
        this.state = data.state || 'running';
        return data;
    }
    return null;
};

DatingGame.prototype.togglePause = function() {
    GameEngine.prototype.togglePause.call(this);
};

DatingGame.prototype.quit = function() {
    this.state = 'idle';
    GameHub.closeGame();
};

window.DatingGame = DatingGame;