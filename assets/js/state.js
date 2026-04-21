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
            const k = keys[i];
            // 边界检查：如果路径节点不存在，优雅降级不崩溃
            if (target[k] === undefined || target[k] === null) {
                console.warn(`[State] 尝试写入不存在的路径: "${key}"，节点 "${k}" 未定义，操作已忽略`);
                return;
            }
            // 检查不是对象/数组类型时无法继续嵌套访问
            if (typeof target[k] !== 'object') {
                console.warn(`[State] 路径 "${key}" 节点 "${k}" 不是可嵌套类型，操作已忽略`);
                return;
            }
            target = target[k];
        }

        const lastKey = keys[keys.length - 1];
        // 最终节点也检查父对象有效性
        if (!target || typeof target !== 'object') {
            console.warn(`[State] 无效路径 "${key}"，无法写入`);
            return;
        }

        if (target[lastKey] === value) return;

        target[lastKey] = value;

        if (key === 'theme') {
            localStorage.setItem('theme', value);
            document.documentElement.dataset.theme = this._resolveTheme(value);
        }

        this._notify();
    }

    get(key) {
        try {
            return key.split('.').reduce((obj, k) => (obj && typeof obj === 'object' ? obj[k] : undefined), this._state);
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
