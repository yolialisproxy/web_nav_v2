/**
 * favorite.js - 收藏功能模块 (V3)
 * 功能：本地存储收藏的站点，支持访问计数、搜索、分类、导出
 */

class FavoriteManager {
    constructor() {
        this.key = 'webnav_favorites_v2';
        this.visitKey = 'webnav_favorites_visits_v2';
        this._memoryFavorites = null;
        this._memoryVisits = null;
        this.favorites = this.loadFromStorage();
        this.visitCounts = this.loadVisits();
    }

    // ===== 存储：收藏数据 =====

    loadFromStorage() {
        try {
            const data = localStorage.getItem(this.key);
            if (data) {
                const parsed = JSON.parse(data);
                if (Array.isArray(parsed)) {
                    this._memoryFavorites = parsed;
                    return parsed;
                }
            }
            if (this._memoryFavorites) {
                console.warn('[FavoriteManager] localStorage 数据格式异常，已使用内存备份');
                return this._memoryFavorites;
            }
            return [];
        } catch (e) {
            console.error('[FavoriteManager] 加载收藏数据失败:', e);
            if (this._memoryFavorites) {
                console.warn('[FavoriteManager] localStorage 不可用，已降级为内存存储');
                return this._memoryFavorites;
            }
            return [];
        }
    }

    saveToStorage() {
        try {
            localStorage.setItem(this.key, JSON.stringify(this.favorites));
            this._memoryFavorites = [...this.favorites];
            return true;
        } catch (e) {
            console.error('[FavoriteManager] 保存收藏数据到 localStorage 失败:', e);
            this._memoryFavorites = [...this.favorites];
            return false;
        }
    }

    // ===== 存储：访问计数 =====

    loadVisits() {
        try {
            const data = localStorage.getItem(this.visitKey);
            if (data) {
                const parsed = JSON.parse(data);
                if (parsed && typeof parsed === 'object') {
                    this._memoryVisits = parsed;
                    return parsed;
                }
            }
            return this._memoryVisits || {};
        } catch (e) {
            console.error('[FavoriteManager] 加载访问记录失败:', e);
            return this._memoryVisits || {};
        }
    }

    saveVisits() {
        try {
            localStorage.setItem(this.visitKey, JSON.stringify(this.visitCounts));
        } catch (e) {
            console.error('[FavoriteManager] 保存访问记录失败:', e);
        }
    }

    // ===== 核心 CRUD =====

    add(site) {
        if (this.isFavorite(site.name)) {
            return { success: false, message: '已收藏' };
        }

        const favoriteItem = {
            ...site,
            addedAt: new Date().toISOString(),
            favoriteId: this.generateId()
        };

        this.favorites.push(favoriteItem);
        this.saveToStorage();
        this.emit('favoriteAdded', favoriteItem);
        return { success: true, message: '收藏成功' };
    }

    remove(siteName) {
        const index = this.favorites.findIndex(f => f.name === siteName);
        if (index === -1) {
            return { success: false, message: '未找到收藏项' };
        }

        const removed = this.favorites.splice(index, 1)[0];
        this.saveToStorage();
        this.emit('favoriteRemoved', removed);
        return { success: true, message: '取消收藏' };
    }

    clear() {
        this.favorites = [];
        this.saveToStorage();
        this.emit('favoriteCleared');
    }

    // ===== 查询方法 =====

    getAll() {
        return [...this.favorites].sort((a, b) =>
            new Date(b.addedAt) - new Date(a.addedAt)
        );
    }

    getRecent(limit) {
        const result = [...this.favorites].sort((a, b) =>
            new Date(b.addedAt) - new Date(a.addedAt)
        );
        if (limit) result.splice(limit);
        return result;
    }

    getMostVisited(limit) {
        const result = [...this.favorites].sort((a, b) =>
            (this.visitCounts[b.name] || 0) - (this.visitCounts[a.name] || 0)
        );
        if (limit) result.splice(limit);
        return result;
    }

    getByCategory() {
        const grouped = {};
        this.favorites.forEach(f => {
            const cat = f.category || '未分类';
            if (!grouped[cat]) grouped[cat] = [];
            grouped[cat].push(f);
        });
        // 按分类内收藏时间排序
        Object.keys(grouped).forEach(cat => {
            grouped[cat].sort((a, b) => new Date(b.addedAt) - new Date(a.addedAt));
        });
        return grouped;
    }

    search(query) {
        if (!query || !query.trim()) return this.getAll();
        const q = query.toLowerCase().trim();
        return this.favorites.filter(f =>
            f.name.toLowerCase().includes(q) ||
            (f.description && f.description.toLowerCase().includes(q)) ||
            (f.category && f.category.toLowerCase().includes(q)) ||
            (f.url && f.url.toLowerCase().includes(q))
        ).sort((a, b) => new Date(b.addedAt) - new Date(a.addedAt));
    }

    isFavorite(siteName) {
        return this.favorites.some(f => f.name === siteName);
    }

    getCount() {
        return this.favorites.length;
    }

    // ===== 访问计数 =====

    recordVisit(siteName) {
        if (!siteName) return;
        if (!this.visitCounts[siteName]) {
            this.visitCounts[siteName] = 0;
        }
        this.visitCounts[siteName]++;
        this.saveVisits();
    }

    getVisitCount(siteName) {
        return this.visitCounts[siteName] || 0;
    }

    // ===== 导出/导入 =====

    export() {
        return JSON.stringify({
            version: '3.0',
            exportedAt: new Date().toISOString(),
            count: this.getCount(),
            favorites: this.getAll()
        }, null, 2);
    }

    import(jsonStr) {
        try {
            const data = JSON.parse(jsonStr);
            if (!data || !Array.isArray(data.favorites)) {
                return { success: false, message: '数据格式错误' };
            }
            const imported = data.favorites.filter(f => f && f.name);
            let added = 0;
            imported.forEach(item => {
                if (!this.isFavorite(item.name)) {
                    this.favorites.push({
                        ...item,
                        favoriteId: this.generateId(),
                        addedAt: item.addedAt || new Date().toISOString()
                    });
                    added++;
                }
            });
            this.saveToStorage();
            this.emit('favoriteImported', { count: added });
            return { success: true, message: `成功导入 ${added} 个收藏`, added };
        } catch (e) {
            return { success: false, message: '导入失败: ' + e.message };
        }
    }

    // ===== 工具方法 =====

    generateId() {
        return 'fav_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // ===== 事件系统 =====

    listeners = {};

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    off(event, callback) {
        if (!this.listeners[event]) return;
        this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }

    emit(event, data) {
        if (!this.listeners[event]) return;
        this.listeners[event].forEach(callback => callback(data));
    }
}

const favoriteManager = new FavoriteManager();
window.favoriteManager = favoriteManager;