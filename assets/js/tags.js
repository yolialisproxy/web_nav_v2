/**
 * tags.js - 标签系统模块 (V2.1)
 * 功能：标签索引、筛选、UI渲染
 * 修复：当 tag_index.json 不存在时，从站点数据动态构建标签索引
 */

// 全局单例
let tagManager = null;

class TagManager {
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.allTags = new Map();  // tag -> count
        this.siteTags = new Map(); // site id -> tags[]
        this.activeTags = new Set();
        this._initialized = false;
    }

    async load() {
        if (this._initialized) return;

        let loadedFromJson = false;

        // 尝试从 tag_index.json 加载（向后兼容）
        try {
            const resp = await fetch('data/tag_index.json');
            if (resp.ok) {
                const tagIndex = await resp.json();
                tagIndex.forEach(t => {
                    this.allTags.set(t.tag, t.count);
                });
                loadedFromJson = true;
                // // // // console.log(`[TagManager] 从 tag_index.json 加载了 ${this.allTags.size} 个标签`);
            }
        } catch (e) {
            // tag_index.json 不存在时忽略，将从站点数据构建
            // // // // console.log('[TagManager] tag_index.json 不可用，将从站点数据构建标签');
        }

        // 无论是否从 JSON 加载成功，都从当前站点数据重新构建标签
        this._buildFromSiteData();

        this._initialized = true;
        if (!loadedFromJson) {
            // // // // console.log(`[TagManager] 从站点数据构建了 ${this.allTags.size} 个标签`);
        }
    }

    /**
     * 从当前 DataManager 的站点数据中动态构建标签索引
     * 这确保了即使没有 tag_index.json 标签也能正常工作
     */
    _buildFromSiteData() {
        this.allTags.clear();
        this.siteTags.clear();

        if (!this.dataManager || !this.dataManager.sites) return;

        this.dataManager.sites.forEach(site => {
            if (!site.tags || !Array.isArray(site.tags)) return;

            const validTags = [];
            site.tags.forEach(tag => {
                if (!tag || typeof tag !== 'string') return;
                const key = tag.trim().toLowerCase();
                if (!key) return;

                validTags.push(tag.trim());

                if (!this.allTags.has(key)) {
                    this.allTags.set(key, 0);
                }
                this.allTags.set(key, this.allTags.get(key) + 1);
            });

            if (validTags.length > 0) {
                this.siteTags.set(site.id, validTags);
            }
        });
    }

    /**
     * 获取站点的标签
     */
    getSiteTags(site) {
        if (site && site.tags) return site.tags;
        if (site && this.siteTags.has(site.id)) return this.siteTags.get(site.id);
        return [];
    }

    /**
     * 搜索与标签匹配的站点
     */
    findSitesByTag(tag) {
        if (!this.dataManager || !this.dataManager.sites.size) return [];
        const key = tag.toLowerCase();
        const results = [];
        this.dataManager.sites.forEach(site => {
            const siteTagKeys = this.getSiteTags(site).map(t => t.toLowerCase());
            if (siteTagKeys.includes(key)) {
                results.push(site);
            }
        });
        return results;
    }

    /**
     * 切换标签筛选
     */
    toggleTag(tag, mode = 'toggle') {
        const key = tag.toLowerCase();
        if (mode === 'toggle') {
            if (this.activeTags.has(key)) {
                this.activeTags.delete(key);
            } else {
                this.activeTags.add(key);
            }
        } else if (mode === 'set') {
            this.activeTags.clear();
            this.activeTags.add(key);
        } else if (mode === 'clear') {
            this.activeTags.clear();
        } else if (mode === 'exact') {
            this.activeTags.clear();
            this.activeTags.add(key);
        }
        return this.activeTags.size;
    }

    isActive(tag) {
        return this.activeTags.has(tag.toLowerCase());
    }

    getActiveTags() {
        return Array.from(this.activeTags);
    }

    /**
     * 根据当前标签筛选站点
     */
    filterByActiveTags(sites) {
        if (!this.activeTags.size) return sites;
        const activeTagsArr = Array.from(this.activeTags);
        return sites.filter(site => {
            const siteTagKeys = this.getSiteTags(site).map(t => t.toLowerCase());
            return activeTagsArr.some(tag => siteTagKeys.includes(tag));
        });
    }

    /**
     * 渲染标签云UI
     */
    renderTagCloud(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const limit = options.limit || 50;

        const tags = [];
        this.allTags.forEach((count, tag) => {
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

        // 绑定事件
        container.querySelectorAll('.tag-pill').forEach(el => {
            const toggleHandler = (e) => {
                e.preventDefault();
                e.stopPropagation();
                const tag = el.dataset.tag;
                this.toggleTag(tag);
                this.renderTagCloud(containerId, options);
                this._applyFilter();
            };
            el.addEventListener('click', toggleHandler);
            el.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleHandler(e);
                }
            });
        });
    }

    _escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

    _applyFilter() {
        state._notify();
        const event = new CustomEvent('tags-filter-changed', {
            detail: { tags: this.getActiveTags() }
        });
        window.dispatchEvent(event);
    }

    /**
     * 销毁清理
     */
    destroy() {
        this.allTags.clear();
        this.siteTags.clear();
        this.activeTags.clear();
        this._initialized = false;
    }
}
function initTagManager(dm) {
    if (tagManager) tagManager.destroy();
    tagManager = new TagManager(dm);
    window.tagManager = tagManager;
    return tagManager;
}

window.TagManager = TagManager;
window.initTagManager = initTagManager;