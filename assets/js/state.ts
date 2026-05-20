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
            filterTags: [],
            searchMode: false      // 是否在搜索覆盖层模式
        };
        this._subscribers = [];
        // LocalForage 缓存配置
        this._cache = {
            version: 1,
            keys: {
                sites: 'nav_sites_v1',
                tags: 'nav_tags_v1',
                sidebar: 'nav_sidebar_v1',
                theme: 'nav_theme_v1'
            },
            ttl: {
                sites: 24 * 60 * 60 * 1000,    // 24h
                tags: 60 * 60 * 1000,           // 1h
                sidebar: 7 * 24 * 60 * 60 * 1000, // 7d
                theme: 0  // 永不过期
            }
        };
        this._cacheReady = false;
        this._initCache();  // 异步初始化缓存
        // 标签系统（从 tags.js 合并而来）
        this.tagAll = new Map();      // tag -> count
        this.tagSites = new Map();   // site id -> tags[]
        this.activeTags = new Set();
        this._tagInitialized = false;
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

    // ═══════════════════════════════════════════════
    // LocalForage 缓存层
    // ═══════════════════════════════════════════════

    /** 异步初始化 localforage */
    async _initCache() {
        if (this._cacheReady || typeof localforage === 'undefined') {
            // localforage 未加载时降级到 localStorage
            this._cacheBackend = localStorage;
            this._cacheReady = true;
            return;
        }
        try {
            await localforage.config({
                name: 'nav_web',
                storeName: 'cache_v1',
                version: this._cache.version
            });
            this._cacheBackend = localforage;
            this._cacheReady = true;
            // 后台恢复
            this._restoreFromCache();
        } catch (e) {
            console.warn('[State] LocalForage 不可用，降级到 localStorage', e);
            this._cacheBackend = localStorage;
            this._cacheReady = true;
        }
    }

    /** 从缓存恢复状态 */
    _restoreFromCache() {
        if (!this._cacheReady) return;

        const restore = async (key) => {
            try {
                const raw = await this._cacheBackend.getItem(key);
                if (!raw) return null;
                const {value, ts} = raw;
                // TTL 检查
                const ttl = this._cache.ttl[key.split('_')[1]] || 0;
                if (ttl > 0 && Date.now() - ts > ttl) {
                    await this._cacheBackend.removeItem(key);
                    return null;
                }
                return value;
            } catch (e) {
                return null;
            }
        };

        // 并行恢复
        Promise.all([
            restore(this._cache.keys.sites),
            restore(this._cache.keys.tags),
            restore(this._cache.keys.sidebar),
            restore(this._cache.keys.theme)
        ]).then(([sites, tagsData, sidebar, theme]) => {
            if (sites && Array.isArray(sites)) {
                this._state.sites = sites;
                this._notify();
            }
            if (tagsData && tagsData.allTags) {
                this.tagAll = new Map(Object.entries(tagsData.allTags));
                this.tagSites = new Map(Object.entries(tagsData.tagSites).map(([k, v]) => [parseInt(k), v]));
                this.activeTags = new Set(tagsData.activeTags || []);
            }
            if (sidebar) {
                this._state.sidebar = {...this._state.sidebar, ...sidebar};
            }
            if (theme && ['light', 'dark', 'system'].includes(theme)) {
                this._state.theme = theme;
                document.documentElement.dataset.theme = this._resolveTheme(theme);
            }
            this._notify();
        });
    }

    /** 保存到缓存（增量） */
    async _saveToCache(key, value) {
        if (!this._cacheReady) return;
        try {
            const payload = {
                value,
                ts: Date.now(),
                v: this._cache.version
            };
            await this._cacheBackend.setItem(key, payload);
        } catch (e) {
            // 静默失败（配额超限等）
        }
    }

    /** 强制清空所有缓存 */
    async clearCache() {
        if (!this._cacheReady) return;
        try {
            const keys = await this._cacheBackend.keys();
            for (const key of keys) {
                if (key.startsWith('nav_')) await this._cacheBackend.removeItem(key);
            }
            console.log('[State] 缓存已清空');
        } catch (e) {
            console.warn('[State] 清空缓存失败', e);
        }
    }


    // ═══════════════════════════════════════════════
    // 标签系统（从 tags.js 合并）
    // ═══════════════════════════════════════════════

    /** 初始化标签索引 */
    async loadTags(dataManager) {
        if (this._tagInitialized) return;
        let loadedFromJson = false;

        try {
            const resp = await fetch('data/tag_index.json');
            if (resp.ok) {
                const tagIndex = await resp.json();
                tagIndex.forEach(t => this.tagAll.set(t.tag, t.count));
                loadedFromJson = true;
            }
        } catch (e) {
            // 忽略，将从站点数据构建
        }

        this._buildTagsFromSites(dataManager);
        this._tagInitialized = true;
        // 标签数据变更后持久化
        const tagsData = {
            allTags: Object.fromEntries(this.tagAll),
            tagSites: Object.fromEntries(Array.from(this.tagSites.entries()).map(([k, v]) => [k, v])),
            activeTags: Array.from(this.activeTags)
        };
        this._saveToCache(this._cache.keys.tags, tagsData);
    }

    /** 从站点数据构建标签索引 */
    _buildTagsFromSites(dm) {
        this.tagAll.clear();
        this.tagSites.clear();

        if (!dm || !dm.sites) return;

        dm.sites.forEach(site => {
            if (!site.tags || !Array.isArray(site.tags)) return;
            const validTags = [];
            site.tags.forEach(tag => {
                if (!tag || typeof tag !== 'string') return;
                const key = tag.trim().toLowerCase();
                if (!key) return;
                validTags.push(tag.trim());
                if (!this.tagAll.has(key)) this.tagAll.set(key, 0);
                this.tagAll.set(key, this.tagAll.get(key) + 1);
            });
            if (validTags.length > 0) this.tagSites.set(site.id, validTags);
        });
    }

    /** 获取站点的标签 */
    getSiteTags(site) {
        if (site && site.tags) return site.tags;
        if (site && this.tagSites.has(site.id)) return this.tagSites.get(site.id);
        return [];
    }

    /** 根据标签筛选站点 */
    filterByTags(sites, tags) {
        if (!tags || !tags.length) return sites;
        const tagSet = new Set(tags.map(t => t.toLowerCase()));
        return sites.filter(site => {
            const keys = this.getSiteTags(site).map(t => t.toLowerCase());
            return Array.from(tagSet).some(t => keys.includes(t));
        });
    }

    /** 切换标签激活状态 */
    toggleTag(tag, mode = 'toggle') {
        const key = tag.toLowerCase();
        if (mode === 'toggle') {
            this.activeTags.has(key) ? this.activeTags.delete(key) : this.activeTags.add(key);
        } else if (mode === 'set') {
            this.activeTags.clear(); this.activeTags.add(key);
        } else if (mode === 'clear') {
            this.activeTags.clear();
        } else if (mode === 'exact') {
            this.activeTags.clear(); this.activeTags.add(key);
        }
        return this.activeTags.size;
    }

    /** 获取激活的标签列表 */
    getActiveTags() {
        return Array.from(this.activeTags);
    }

    /** 渲染标签云 UI */
    renderTagCloud(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;
        const limit = options.limit || 50;

        const tags = [];
        this.tagAll.forEach((count, tag) => {
            tags.push({ tag, count, active: this.activeTags.has(tag) });
        });
        tags.sort((a, b) => b.count - a.count);
        tags.splice(limit);

        if (tags.length === 0) {
            container.innerHTML = '<div class="tag-cloud"><span class="tag-pill" style="opacity:0.5">暂无标签</span></div>';
            return;
        }

        let html = '<div class="tag-cloud">';
        tags.forEach(t => {
            const size = Math.max(0.8, Math.min(1.6, 0.8 + t.count / 500));
            html += `<a href="#" class="tag-pill ${t.active ? 'active' : ''}" ` +
                    `data-tag="${t.tag}" style="font-size:${size}em" ` +
                    `title="${t.tag} (${t.count} sites)" tabindex="0" role="button" aria-pressed="${t.active}">` +
                    `${this._escapeHtml(t.tag)}<span class="tag-count">${t.count}</span></a>`;
        });
        html += '</div>';
        container.innerHTML = html;

        container.querySelectorAll('.tag-pill').forEach(el => {
            const handler = (e) => {
                e.preventDefault(); e.stopPropagation();
                const tag = el.dataset.tag;
                this.toggleTag(tag);
                this.renderTagCloud(containerId, options);
                this._notify();
                window.dispatchEvent(new CustomEvent('tags-filter-changed', {
                    detail: { tags: this.getActiveTags() }
                }));
            };
            el.addEventListener('click', handler);
            el.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault(); handler(e);
                }
            });
        });
    }

    /** 标签相关：禁用警告 */
    get tagManagerDeprecationNotice() {
        console.warn('[State] window.tagManager 已废弃，请使用 state.tags 相关 API');
        return null;
    }

    // ═══════════════════════════════════════════════
    // 视图切换：网格 / 列表 / 分类
    // ═══════════════════════════════════════════════
    setView(mode) {
        if (!['grid', 'list', 'category', 'games'].includes(mode)) {
            console.warn('[State] 无效视图模式:', mode);
            return;
        }
        this.set('currentView', mode);
    }


}

const state = new State();
window.state = state;