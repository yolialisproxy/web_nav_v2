/**
 * tags.js - ⚠️ DEPRECATED
 * 此模块已被 state.js 合并。保留仅作向后兼容。
 * 请迁移到 state.loadTags() / state.tags* API。
 */

// 废弃的 TagManager 类（保留结构以防引用）
class TagManager {
    constructor(dataManager) {
        console.warn('[TagManager] 此类已废弃，请使用 State 的标签 API');
        this.dataManager = dataManager;
        // 桥接到 state（如果可用）
        if (window.state) {
            this._state = window.state;
        }
    }
    async load() {
        console.warn('[TagManager] 使用 state.loadTags() 替代');
        if (this._state && this.dataManager) await this._state.loadTags(this.dataManager);
    }
    filterByActiveTags(sites) {
        console.warn('[TagManager] 使用 state.filterByTags() 替代');
        return this._state ? this._state.filterByTags(sites, this._state.getActiveTags()) : sites;
    }
    getActiveTags() {
        console.warn('[TagManager] 使用 state.getActiveTags() 替代');
        return this._state ? this._state.getActiveTags() : [];
    }
    toggleTag(tag, mode) {
        console.warn('[TagManager] 使用 state.toggleTag() 替代');
        return this._state ? this._state.toggleTag(tag, mode) : 0;
    }
    // ... 其余方法已省略，请直接使用 state API
}

// 废弃的初始化函数
function initTagManager(dm) {
    console.warn('[initTagManager] 已废弃，请使用 state.loadTags(dataManager)');
    if (window.state) {
        window.state.loadTags(dm);
        return null;
    }
    return new TagManager(dm);
}

// 不暴露 window.tagManager
window.TagManager = TagManager;
window.initTagManager = initTagManager;

// 兼容性警告
console.info('[tags.js] 此文件已废弃，标签功能已移至 state.js');
