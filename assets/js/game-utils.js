/**
 * Game Utilities - 游戏公共工具
 */
var GameUtils = {
    // 存档
    save: function(key, data) {
        try { localStorage.setItem('gn_game_' + key, JSON.stringify(data)); } catch(e) {}
    },
    load: function(key) {
        try { return JSON.parse(localStorage.getItem('gn_game_' + key)); } catch(e) { return null; }
    },
    clear: function(key) {
        try { localStorage.removeItem('gn_game_' + key); } catch(e) {}
    },
    // 音效生成（Web Audio API，简单蜂鸣）
    playSound: function(freq, duration, type) {
        try {
            var ctx = GameUtils._audioCtx || (GameUtils._audioCtx = new (window.AudioContext || window.webkitAudioContext)());
            var osc = ctx.createOscillator();
            var gain = ctx.createGain();
            osc.type = type || 'square';
            osc.frequency.value = freq;
            gain.gain.value = 0.08;
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + duration);
        } catch(e) {}
    },
    // 随机整数
    rand: function(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; },
    // 洗牌（Fisher-Yates）
    shuffle: function(arr) {
        var a = arr.slice();
        for (var i = a.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var t = a[i]; a[i] = a[j]; a[j] = t;
        }
        return a;
    },
    // 创建SVG元素字符串
    svgEl: function(tag, attrs) {
        var el = '<svg xmlns="http://www.w3.org/2000/svg" ' + Object.keys(attrs).map(function(k) {
            return k + '="' + attrs[k] + '"';
        }).join(' ') + '></svg>';
        return el;
    },
    // 格式化时间
    formatTime: function(ms) {
        var s = Math.floor(ms / 1000);
        var m = Math.floor(s / 60);
        s = s % 60;
        return (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
    },
    // 深度克隆
    clone: function(obj) { return JSON.parse(JSON.stringify(obj)); },
    // 节流
    throttle: function(fn, delay) {
        var last = 0;
        return function() {
            var now = Date.now();
            if (now - last >= delay) { last = now; fn.apply(this, arguments); }
        };
    }
};