/**
 * WuxiaGame - 武侠世界（文字RPG + 战斗系统）
 */
var WuxiaGame = function() {
    GameEngine.call(this, { id: 'wuxia', title: '⚔️ 武侠世界' });
    this.player = null;
    this.scene = 'start';
    this.hp = 100;
    this.maxHp = 100;
    this.attack = 15;
    this.defense = 5;
    this.exp = 0;
    this.level = 1;
    this.gold = 100;
    this.inventory = [];
    this.enemy = null;
    this.storyLog = [];
};

WuxiaGame.prototype = Object.create(GameEngine.prototype);
WuxiaGame.prototype.constructor = WuxiaGame;

WuxiaGame.SCENES = {
    start: {
        text: '你是一名初入江湖的侠客，听闻江湖上近日风起云涌。一位老乞丐拦住你的去路……',
        choices: [
            { text: '上前询问', next: 'old_beggar_talk' },
            { text: '不予理会，继续前行', next: 'mountain_path' },
            { text: '赠予银两', next: 'old_beggar_gift' }
        ]
    },
    old_beggar_talk: {
        text: '老乞丐叹道："少侠，你命中有一劫。前方黑风山有妖邪作祟，若能除之，必有大造化。"说罢递给你一枚玉佩。',
        choices: [
            { text: '收下玉佩，前往黑风山', next: 'black_wind_mountain' },
            { text: '谢过老伯，继续赶路', next: 'mountain_path' }
        ],
        reward: { item: '平安玉佩', effect: 'defense+3' }
    },
    old_beggar_gift: {
        text: '老乞丐接过银两，浑浊的眼中闪过一丝光亮："好人有好报，少侠保重！"你感到内心一阵温暖。',
        goldCost: -20,
        choices: [
            { text: '前往黑风山', next: 'black_wind_mountain' },
            { text: '去镇上客栈', next: 'inn' }
        ]
    },
    mountain_path: {
        text: '山路崎岖，你小心翼翼地前行。突然草丛中窜出一只斑斓猛虎！',
        choices: [
            { text: '拔剑迎战！', next: 'fight_tiger' },
            { text: '尝试躲避', next: 'dodge_tiger' },
            { text: '丢下食物引开老虎', next: 'bait_tiger', goldCost: 15 }
        ]
    },
    black_wind_mountain: {
        text: '黑风山上阴风阵阵，你看到一个黑衣人正在作法，周围的村民被黑气缠绕。',
        choices: [
            { text: '立即出手攻击', next: 'fight_boss' },
            { text: '先观察，寻找破绽', next: 'observe_boss' },
            { text: '使用策略引开敌人', next: 'boss_strategy' }
        ]
    },
    fight_tiger: {
        text: '猛虎扑来！你闪身躲过，猛刺一剑！',
        choices: [],
        fight: { enemy: '斑斓猛虎', hp: 40, attack: 12, reward: { gold: 20, exp: 30 } }
    },
    dodge_tiger: {
        text: '你纵身跳上一块岩石，老虎扑空滑了下去。它似乎不饿，转身离去。',
        reward: { exp: 10 },
        choices: [
            { text: '继续前行', next: 'black_wind_mountain' },
            { text: '返回镇上', next: 'inn' }
        ]
    },
    bait_tiger: {
        text: '你扔出干肉，老虎嗅了嗅，追着食物跑远了。你得以安全通过。',
        choices: [
            { text: '继续前行', next: 'black_wind_mountain' }
        ]
    },
    observe_boss: {
        text: '你仔细观察，发现黑衣人的法器每隔三息闪烁一次，正是施法间隙！',
        reward: { exp: 15 },
        choices: [
            { text: '趁间隙发动突袭', next: 'fight_boss' },
            { text: '绕后偷袭', next: 'fight_boss_surprise' }
        ]
    },
    boss_strategy: {
        text: '你高声挑衅，黑衣人怒而出手，法器威力减弱了三成！你抓住了机会。',
        reward: { exp: 20 },
        choices: [
            { text: '全力攻击！', next: 'fight_boss' }
        ]
    },
    fight_boss: {
        text: '黑衣人大喝："哪来的小辈！"黑气向你涌来！',
        choices: [],
        fight: { enemy: '黑衣邪修', hp: 80, attack: 18, reward: { gold: 100, exp: 100, item: '黑灵珠' } }
    },
    fight_boss_surprise: {
        text: '你从暗处跃出，黑衣人措手不及！',
        reward: { exp: 10 },
        choices: [],
        fight: { enemy: '黑衣邪修', hp: 60, attack: 15, reward: { gold: 100, exp: 100, item: '黑灵珠' } }
    },
    inn: {
        text: '镇上的客栈灯火通明。老板娘热情地招呼："少侠要住店吗？住一晚恢复全部气血，只要50两银子！"',
        choices: [
            { text: '住店恢复(50两)', next: 'after_rest', goldCost: -50, effect: 'heal_full' },
            { text: '休息片刻(免费)', next: 'after_rest', effect: 'heal_half' },
            { text: '离开客栈', next: 'mountain_path' }
        ]
    },
    after_rest: {
        text: '你精神饱满地准备继续冒险……',
        choices: [
            { text: '前往黑风山', next: 'black_wind_mountain' },
            { text: '再逛逛小镇', next: 'market' }
        ]
    },
    market: {
        text: '小镇集市热闹非凡。药铺老板喊道："金疮药10两一瓶，攻击力提升5！"铁匠铺："好剑100两，攻击+10！"',
        choices: [
            { text: '购买金疮药(10两)', next: 'market', goldCost: -10, effect: 'attack+5' },
            { text: '购买好剑(100两)', next: 'market', goldCost: -100, effect: 'attack+10' },
            { text: '继续冒险', next: 'black_wind_mountain' }
        ]
    }
};

WuxiaGame.prototype.init = function() {
    GameEngine.prototype.init.call(this);
    this.player = { name: '侠客' };
    this.hp = 100;
    this.maxHp = 100;
    this.attack = 15;
    this.defense = 5;
    this.exp = 0;
    this.level = 1;
    this.gold = 100;
    this.inventory = [];
    this.scene = 'start';
    this.storyLog = [];
    this.fighting = false;
    this.render();
};

WuxiaGame.prototype.render = function() {
    var self = this;
    var html = '';

    // 状态栏
    html += '<div style="display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap;justify-content:center;">' +
        '<div style="background:rgba(0,0,0,0.3);padding:8px 16px;border-radius:6px;">' +
        '❤️ HP: <span id="wuxia-hp" style="color:#ff6b6b">' + this.hp + '/' + this.maxHp + '</span></div>' +
        '<div style="background:rgba(0,0,0,0.3);padding:8px 16px;border-radius:6px;">' +
        '⚔️ 攻击: <span style="color:#ffd700">' + this.attack + '</span></div>' +
        '<div style="background:rgba(0,0,0,0.3);padding:8px 16px;border-radius:6px;">' +
        '🛡️ 防御: <span style="color:#87ceeb">' + this.defense + '</span></div>' +
        '<div style="background:rgba(0,0,0,0.3);padding:8px 16px;border-radius:6px;">' +
        '💰 金钱: <span style="color:#90ee90">' + this.gold + '</span></div>' +
        '<div style="background:rgba(0,0,0,0.3);padding:8px 16px;border-radius:6px;">' +
        '⭐ 等级: Lv.' + this.level + ' (' + this.exp + ' EXP)</div></div>';

    if (this.fighting) {
        // 战斗界面
        var enemy = this.enemy;
        html += '<div style="text-align:center;margin-bottom:16px;">' +
            '<div style="font-size:20px;margin-bottom:8px;">⚔️ VS ' + enemy.name + '</div>' +
            '<div>敌人HP: <span style="color:#ff6b6b">' + enemy.hp + '/' + enemy.maxHp + '</span></div>' +
            '<div style="margin:8px 0;">' + this._generateHpBar(enemy.hp, enemy.maxHp, '#ff4444') + '</div>' +
            '<div>你的HP: <span style="color:#ff6b6b">' + this.hp + '/' + this.maxHp + '</span></div>' +
            '<div style="margin:8px 0;">' + this._generateHpBar(this.hp, this.maxHp, '#44ff44') + '</div></div>' +
            '<div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">' +
            '<button class="game-btn" style="padding:10px 20px;font-size:16px;" id="wuxia-attack">⚔️ 攻击</button>' +
            '<button class="game-btn" style="padding:10px 20px;font-size:16px;" id="wuxia-skill">💫 技能(SP:' + Math.min(this.exp, 30) + ')</button>' +
            '<button class="game-btn" style="padding:10px 20px;font-size:16px;" id="wuxia-defend">🛡️ 防御</button>' +
            '<button class="game-btn" style="padding:10px 20px;font-size:16px;" id="wuxia-flee">🏃 逃跑</button>' +
            '</div>';
    } else {
        // 剧情界面
        var scene = WuxiaGame.SCENES[this.scene];
        if (!scene) {
            html += '<div style="text-align:center;padding:40px;"><div style="font-size:48px;">🏆</div>' +
                '<div style="color:var(--color-text);font-size:18px;">冒险结束</div>' +
                '<div style="color:var(--color-text-dim);margin-top:8px;">你的战绩: 等级Lv.' + this.level + ' | 金钱' + this.gold + '两</div></div>';
        } else {
            html += '<div style="max-width:600px;margin:0 auto;text-align:center;">' +
                '<div style="background:rgba(0,0,0,0.3);padding:20px;border-radius:8px;margin-bottom:16px;' +
                'border:1px solid var(--color-border);font-size:15px;line-height:1.8;min-height:100px;">' +
                scene.text + '</div>';
            // 物品获得提示
            if (scene.reward && scene.reward.item) {
                html += '<div style="color:#ffd700;margin-bottom:12px;">🎁 获得: ' + scene.reward.item + '</div>';
            }
            // 选项
            if (scene.choices && scene.choices.length > 0) {
                html += '<div style="display:flex;flex-direction:column;gap:8px;align-items:center;">';
                scene.choices.forEach(function(choice, i) {
                    var disabled = '';
                    if (choice.goldCost && choice.goldCost < 0 && self.gold < Math.abs(choice.goldCost)) {
                        disabled = 'opacity:0.5;cursor:not-allowed;';
                    }
                    html += '<button class="game-btn" data-choice="' + i + '" style="padding:10px 30px;font-size:14px;' + disabled + '">' +
                        choice.text + (choice.goldCost ? ' (' + choice.goldCost + '两)' : '') + '</button>';
                });
                html += '</div>';
            }
            html += '</div>';
        }
        // 背包
        if (this.inventory.length > 0) {
            html += '<div style="margin-top:16px;text-align:center;"><div style="font-size:12px;color:var(--color-text-dim);">🎒 背包: ' +
                this.inventory.join('、') + '</div></div>';
        }
    }

    // 故事日志
    if (this.storyLog.length > 0) {
        html += '<div style="margin-top:16px;max-height:120px;overflow-y:auto;text-align:left;">' +
            '<div style="font-size:11px;color:var(--color-text-dim);border-top:1px solid var(--color-border);padding-top:8px;">';
        this.storyLog.slice(-5).forEach(function(log) {
            html += '<div>' + log + '</div>';
        });
        html += '</div></div>';
    }

    this.el.innerHTML = html;
    this._bindEvents();
};

WuxiaGame.prototype._generateHpBar = function(current, max, color) {
    var width = 200, ratio = current / max;
    return '<div style="width:' + width + 'px;height:14px;background:rgba(0,0,0,0.3);border-radius:7px;overflow:hidden;">' +
        '<div style="width:' + (width * ratio) + 'px;height:100%;background:' + color + ';border-radius:7px;transition:width .3s;"></div></div>';
};

WuxiaGame.prototype._bindEvents = function() {
    var self = this;
    // 剧情选择
    this.el.querySelectorAll('[data-choice]').forEach(function(btn) {
        btn.addEventListener('click', function() {
            if (self.state !== 'running') return;
            var idx = parseInt(this.dataset.choice);
            var choice = WuxiaGame.SCENES[self.scene].choices[idx];
            if (!choice) return;

            // 金钱消耗
            if (choice.goldCost && choice.goldCost < 0) {
                if (self.gold < Math.abs(choice.goldCost)) {
                    GameHub.showToast('💰 金钱不足！');
                    return;
                }
                self.gold += choice.goldCost;
            }

            // 治疗效果
            if (choice.effect === 'heal_full') self.hp = self.maxHp;
            if (choice.effect === 'heal_half') self.hp = Math.min(self.maxHp, self.hp + Math.floor(self.maxHp / 2));
            if (choice.effect === 'attack+5') self.attack += 5;
            if (choice.effect === 'attack+10') self.attack += 10;
            if (choice.effect === 'defense+3') self.defense += 3;

            // 奖励物品
            if (choice.reward && choice.reward.item && !self.inventory.includes(choice.reward.item)) {
                self.inventory.push(choice.reward.item);
                GameHub.showToast('🎁 获得: ' + choice.reward.item);
            }

            // 跳转
            if (choice.next === 'fight_tiger' || choice.next === 'fight_boss' || choice.next === 'fight_boss_surprise') {
                self._startFight(WuxiaGame.SCENES[choice.next].fight);
                self.scene = choice.next;
                self.storyLog.push('进入战斗: ' + WuxiaGame.SCENES[choice.next].fight.enemy);
            } else {
                self.scene = choice.next;
                self.exp += (choice.reward ? choice.reward.exp : 0);
                self.storyLog.push(WuxiaGame.SCENES[self.scene] ? '来到新场景' : '冒险继续...');
            }
            self._checkLevelUp();
            self.save();
            self.render();
        });
    });

    // 战斗按钮
    var attackBtn = document.getElementById('wuxia-attack');
    if (attackBtn) attackBtn.addEventListener('click', function() { self._playerAttack(); });
    var skillBtn = document.getElementById('wuxia-skill');
    if (skillBtn) skillBtn.addEventListener('click', function() { self._playerSkill(); });
    var defendBtn = document.getElementById('wuxia-defend');
    if (defendBtn) defendBtn.addEventListener('click', function() { self._playerDefend(); });
    var fleeBtn = document.getElementById('wuxia-flee');
    if (fleeBtn) fleeBtn.addEventListener('click', function() { self._playerFlee(); });
};

WuxiaGame.prototype._startFight = function(fightData) {
    this.fighting = true;
    this.enemy = {
        name: fightData.enemy,
        hp: fightData.hp,
        maxHp: fightData.hp,
        attack: fightData.attack,
        reward: fightData.reward
    };
    GameUtils.playSound(220, 0.2, 'sawtooth');
};

WuxiaGame.prototype._endFight = function(victory) {
    if (victory && this.enemy.reward) {
        var r = this.enemy.reward;
        this.gold += r.gold;
        this.exp += r.exp;
        if (r.item) this.inventory.push(r.item);
        GameHub.showToast('🎊 胜利！获得' + r.gold + '两、' + r.exp + 'EXP' + (r.item ? '、' + r.item : ''));
    } else if (!victory) {
        GameHub.showToast('💀 败北...伤势过重，倒地不起。');
    }
    this.fighting = false;
    this.enemy = null;
    this._checkLevelUp();
    this.save();
    setTimeout(function() { self.render(); }, 500);
};

WuxiaGame.prototype._playerAttack = function() {
    if (!this.fighting) return;
    var dmg = Math.max(1, this.attack - this.enemy.attack * 0.3 + GameUtils.rand(-3, 3));
    this.enemy.hp -= dmg;
    this.storyLog.push('你对' + this.enemy.name + '造成了' + dmg + '点伤害！');
    GameUtils.playSound(400, 0.1, 'square');
    if (this.enemy.hp <= 0) { this._endFight(true); return; }
    this._enemyAttack();
};

WuxiaGame.prototype._playerSkill = function() {
    if (!this.fighting) return;
    if (this.exp < 30) { GameHub.showToast('SP不足！需要30EXP'); return; }
    this.exp -= 30;
    var dmg = Math.max(5, this.attack * 2 + GameUtils.rand(-5, 10));
    this.enemy.hp -= dmg;
    this.storyLog.push('你施展绝招，造成' + dmg + '点巨大伤害！');
    GameUtils.playSound(600, 0.15, 'sawtooth');
    if (this.enemy.hp <= 0) { this._endFight(true); return; }
    this._enemyAttack();
};

WuxiaGame.prototype._playerDefend = function() {
    if (!this.fighting) return;
    var dmg = Math.max(0, Math.floor(this.enemy.attack * 0.4) - this.defense);
    this.hp -= dmg;
    this.storyLog.push('你防守，敌人攻击被削弱，只受到' + dmg + '点伤害。');
    GameUtils.playSound(300, 0.08, 'sine');
    if (this.hp <= 0) { this._endFight(false); this.hp = 0; return; }
};

WuxiaGame.prototype._playerFlee = function() {
    if (!this.fighting) return;
    if (Math.random() < 0.6) {
        this.storyLog.push('成功逃脱！');
        this.fighting = false;
        this.enemy = null;
        GameHub.showToast('成功逃脱！');
        GameUtils.playSound(500, 0.1, 'sine');
    } else {
        this.storyLog.push('逃跑失败！');
        GameUtils.playSound(200, 0.1, 'square');
        this._enemyAttack();
    }
};

WuxiaGame.prototype._enemyAttack = function() {
    if (!this.fighting) return;
    setTimeout(function() {
        var dmg = Math.max(1, this.enemy.attack - this.defense * 0.5 + GameUtils.rand(-3, 3));
        this.hp -= dmg;
        this.storyLog.push(this.enemy.name + '对你造成了' + dmg + '点伤害！');
        GameUtils.playSound(350, 0.1, 'square');
        if (this.hp <= 0) { this._endFight(false); this.hp = 0; return; }
        this.save();
        this.render();
    }.bind(this), 600);
};

WuxiaGame.prototype._checkLevelUp = function() {
    var needExp = this.level * 50;
    while (this.exp >= needExp) {
        this.exp -= needExp;
        this.level++;
        this.attack += 3;
        this.defense += 1;
        this.maxHp += 20;
        this.hp = this.maxHp;
        this.storyLog.push('🎉 升级！达到Lv.' + this.level + '！');
        GameHub.showToast('⬆️ 升级！Lv.' + this.level);
        needExp = this.level * 50;
    }
};

WuxiaGame.prototype.togglePause = function() {
    GameEngine.prototype.togglePause.call(this);
};

WuxiaGame.prototype.quit = function() {
    this.state = 'idle';
    GameHub.closeGame();
};

window.WuxiaGame = WuxiaGame;