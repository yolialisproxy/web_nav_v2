/**
 * state.js - 全局状态机 (V2.1)
 * 职责：唯一真理源，状态变更通知，骨架屏控制
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
            filterTags: [],
            loading: true,         // 全局加载状态
            searchMode: false      // 是否在搜索覆盖层模式
        };
        this._subscribers = [];
        this._isNotifying = false; // 防止 _notify 重入导致的无限循环
    }

    set(key, value) {
        const keys = key.split('.');
        let target = this._state;

        for (let i = 0; i < keys.length - 1; i++) {
            const k = keys[i];
            if (target[k] === undefined || target[k] === null) {
                console.warn(`[State] 尝试写入不存在的路径: "${key}"，节点 "${k}" 未定义`);
                return;
            }
            if (typeof target[k] !== 'object') {
                console.warn(`[State] 路径 "${key}" 节点 "${k}" 不是可嵌套类型`);
                return;
            }
            target = target[k];
        }

        const lastKey = keys[keys.length - 1];
        if (!target || typeof target !== 'object') {
            console.warn(`[State] 无效路径 "${key}"`);
            return;
        }

        if (target[lastKey] === value) return;

        target[lastKey] = value;

        if (key === 'theme') {
            localStorage.setItem('theme', value);
            document.documentElement.dataset.theme = this._resolveTheme(value);
        }

        // 骨架屏控制：数据加载完成后隐藏
        if (key === 'loading' && value === false) {
            this._hideSkeleton();
        }

        this._notify();
    }

    get(key) {
        try {
            return key.split('.').reduce((obj, k) =>
                (obj && typeof obj === 'object' ? obj[k] : undefined), this._state);
        } catch (e) {
            console.warn(`[State] 读取路径失败: "${key}"`, e);
            return undefined;
        }
    }

    subscribe(callback) {
        this._subscribers.push(callback);
        return () => {
            this._subscribers = this._subscribers.filter(cb => cb !== callback);
        };
    }

    _notify() {
        if (this._isNotifying) return;
        this._isNotifying = true;
        try {
            this._subscribers.forEach(cb => cb(this._state));
        } finally {
            this._isNotifying = false;
        }
    }

    _resolveTheme(theme) {
        if (theme === 'system') {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return theme;
    }

    _hideSkeleton() {
        const skeleton = document.getElementById('skeleton-screen');
        if (skeleton) {
            skeleton.classList.add('hidden');
            setTimeout(() => skeleton.remove(), 500);
        }
    }
}

const state = new State();
window.state = state;