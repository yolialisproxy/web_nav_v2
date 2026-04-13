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
                mode: 'expanded',
                activeCategoryId: null,
                activeSubCategoryId: null,
                activeLeafId: null
            },
            search: {
                active: false,
                query: '',
                results: []
            },
            currentView: 'category',
            filterTags: []
        };
        this._subscribers = [];
    }

    set(key, value) {
        const keys = key.split('.');
        let target = this._state;
        
        for (let i = 0; i < keys.length - 1; i++) {
            target = target[keys[i]];
        }
        
        const lastKey = keys[keys.length - 1];
        if (target[lastKey] === value) return;

        target[lastKey] = value;

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

const state = new State();
window.state = state;
