/**
 * favorite.js - 收藏功能模块
 * 功能：本地存储收藏的站点
 */

class FavoriteManager {
    constructor() {
        this.key = 'webnav_favorites_v2';
        this.favorites = this.loadFromStorage();
    }
    
    loadFromStorage() {
        try {
            const data = localStorage.getItem(this.key);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('[FavoriteManager] 加载收藏数据失败:', e);
            return [];
        }
    }
    
    saveToStorage() {
        try {
            localStorage.setItem(this.key, JSON.stringify(this.favorites));
            return true;
        } catch (e) {
            console.error('[FavoriteManager] 保存收藏数据失败:', e);
            return false;
        }
    }
    
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
    
    getAll() {
        return [...this.favorites].sort((a, b) => 
            new Date(b.addedAt) - new Date(a.addedAt)
        );
    }
    
    isFavorite(siteName) {
        return this.favorites.some(f => f.name === siteName);
    }
    
    getCount() {
        return this.favorites.length;
    }
    
    clear() {
        this.favorites = [];
        this.saveToStorage();
        this.emit('favoriteCleared');
    }
    
    generateId() {
        return 'fav_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    listeners = {};
    
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    emit(event, data) {
        if (!this.listeners[event]) return;
        this.listeners[event].forEach(callback => callback(data));
    }
}

const favoriteManager = new FavoriteManager();
window.favoriteManager = favoriteManager;

// console.log('[FavoriteManager] 初始化完成，当前收藏数:', favoriteManager.getCount());
