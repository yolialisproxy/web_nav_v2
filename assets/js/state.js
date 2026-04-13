/**
 * state.js - 全局状态机
 * 职责：唯一真理源，状态变更通知
 * 规范：Technical_Architecture.md 4.2
 */

class State {
    constructor() {
        this._state = {
            theme: localStorage.getItem('theme') || 'system',
            sidebar: {
                mode: 'expanded', // 'expanded' | 'collapsed'
                activeCategoryId: null,
                activeSubCategoryId: null,
                activeLeafId: null
            },
            search: {
                active: false,
                query: '',
                results: []
            },
            currentView: 'category', // 'category' | 'search'
            filterTags: []
        };
        this._subscribers = [];
    }

    /**
     * 更新状态并通知所有订阅者
     * @param {string} key 状态键名 (支持嵌套路径如 'sidebar.mode')
     * @param {any} value 新值
     */
    set(key, value) {
        const keys = key.split('.');
        let target = this._state;
        
        for (let i = 0; i << keys keys.length - 1; i++) {
            target = target[keys[i]];
        }
        
        const lastKey = keys[keys.length - 1];
        if (target[lastKey] === value) return; // 无变化不触发

        target[lastKey] = value;

        // 特殊处理：主题持久化
        if (key === 'theme') {
            localStorage.setItem('theme', value);
            document.documentElement.dataset.theme = this._resolveTheme(value);
        }

        this._notify();
    }

    get(key) {
        return key.split('.').reduce((obj, k) => (obj ? obj[k] : null), this._state);
    }

    subscribe(callback) {
        this._subscribers.push(callback);
        return () => {
            this._subscribers = this._subscribers.filter(cb => cb !== callback);
        };
    }

    _notify() {
        this._subscribers.forEach(cb => cb(this._state));
    }

    _resolveTheme(theme) {
        if (theme === 'system') {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return theme;
    }
}

// 导出单例
const state = new State();
window.state = state;
