/**
 * data.js - 数据加载与索引管理 (V2.1)
 * 职责：加载 JSON，构建分类索引 + 标签索引，支持容错降级
 */

class DataManager {
    constructor() {
        this.raw = null;
        this.sites = new Map();
        this.categories = {};
        this.mappings = new Map();
        this.tagIndex = new Map();
        this.tagCloud = new Map();
        this.isLoaded = false;
        this.version = null;
        this._loadError = null;
    }

    async load() {
        if (this.isLoaded) return Promise.resolve();

        // 清理旧版本缓存（兼容性迁移）
        try {
            const oldCacheKey = 'webnav_sites_cache_v2';
            if (localStorage.getItem(oldCacheKey)) {
                localStorage.removeItem(oldCacheKey);
                // console.log('[DataManager] 已清理旧版本缓存');
            }
        } catch (e) {}

        // 显示加载状态
        if (state) state.set('loading', true);

        try {
            const cacheBust = Date.now();
            const response = await fetch(`data/websites.json?v=${cacheBust}`, {
                headers: { 'Cache-Control': 'no-cache' }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const text = await response.text();
            if (!text || text.trim().length === 0) {
                throw new Error('数据文件为空');
            }

            this.raw = JSON.parse(text);

            if (!Array.isArray(this.raw)) {
                throw new Error('数据格式错误：期望数组');
            }

            // 数据格式验证
            this._validateSites(this.raw);

            this._buildIndexes();
            this.isLoaded = true;
            this._loadError = null;

            // 保存到 localStorage 缓存以便恢复
            this._saveCache();

            // 设置版本信息
            if (this.raw.length > 0 && this.raw[0].version) {
                this.version = this.raw[0].version;
            }

            // 广播数据加载完成
            const evt = new CustomEvent('data-loaded');
            window.dispatchEvent(evt);

            // 标记加载完成（触发骨架屏隐藏）
            if (state) state.set('loading', false);

        } catch (e) {
            this._loadError = e;
            console.error('[DataManager] 加载失败:', e);

            // 尝试从 localStorage 缓存恢复
            const cached = this._loadCache();
            if (cached) {
                console.warn('[DataManager] 已从缓存恢复数据');
                this.raw = cached;
                this._buildIndexes();
                this.isLoaded = true;
                this._loadError = null;
                if (state) state.set('loading', false);
                return Promise.resolve();
            }

            // 即使加载失败也要隐藏骨架屏，显示错误状态
            if (state) state.set('loading', false);

            // 渲染有意义的错误信息
            this._renderError(e);

            throw e;
        }
    }

    _buildIndexes() {
        this.categories = {};
        this.sites = new Map();
        this.mappings = new Map();
        this.tagIndex = new Map();
        this.tagCloud = new Map();

        let siteId = 0;

        this.raw.forEach(site => {
            // 跳过无效数据
            if (!site || !site.category) return;

            // 数据清洗：规范化字段
            site.id = siteId++;
            site.name = (site.name || '').trim();
            site.description = (site.description || '').trim();
            site.category = (site.category || '').trim();
            site.url = (site.url || '').trim();

            if (!site.name) return;

            this.sites.set(site.id, site);

            // 分类索引构建
            try {
                this._addToCategoryIndex(site);
            } catch (e) {
                console.warn(`[DataManager] 分类索引构建失败 for site ${site.name}:`, e);
            }

            // 标签索引构建
            try {
                this._addToTagIndex(site);
            } catch (e) {
                console.warn(`[DataManager] 标签索引构建失败 for site ${site.name}:`, e);
            }
        });

        // 按热度排序标签云
        const sortedTags = [...this.tagCloud.values()].sort((a, b) => b.count - a.count);
        this.tagIndexSorted = sortedTags;

        // // // // console.log(`[DataManager] 索引构建完成: ${this.sites.size} 站点, ${Object.keys(this.categories).length} 分类, ${this.tagCloud.size} 标签`);
    }

    _addToCategoryIndex(site) {
        const parts = site.category.split('/').filter(Boolean);
        let cat, sub, leaf;

        if (parts.length >= 3) {
            [cat, sub, leaf] = parts;
        } else if (parts.length === 2) {
            [cat, sub] = parts;
            leaf = sub;
        } else {
            cat = parts[0];
            sub = cat;
            leaf = cat;
        }

        // 规范化名称
        cat = cat.trim();
        sub = sub.trim();
        leaf = leaf.trim();

        if (!this.categories[cat]) this.categories[cat] = { name: cat, subCategories: {} };
        if (!this.categories[cat].subCategories[sub]) {
            this.categories[cat].subCategories[sub] = { name: sub, leafCategories: {} };
        }
        if (!this.categories[cat].subCategories[sub].leafCategories[leaf]) {
            this.categories[cat].subCategories[sub].leafCategories[leaf] = { name: leaf, siteIds: [] };
        }

        const leafNode = this.categories[cat].subCategories[sub].leafCategories[leaf];
        leafNode.siteIds.push(site.id);

        // 映射关系
        const leafId = `${cat}/${sub}/${leaf}`;
        if (!this.mappings.has(leafId)) this.mappings.set(leafId, []);
        this.mappings.get(leafId).push(site.id);

        if (leaf === sub) {
            const subLevelId = `${cat}/${sub}`;
            if (!this.mappings.has(subLevelId)) this.mappings.set(subLevelId, []);
            this.mappings.get(subLevelId).push(site.id);
        }
    }

    _addToTagIndex(site) {
        if (!site.tags || !Array.isArray(site.tags)) return;

        site.tags.forEach(tag => {
            if (!tag || typeof tag !== 'string') return;
            const key = tag.trim().toLowerCase();
            if (!key) return;

            if (!this.tagIndex.has(key)) {
                this.tagIndex.set(key, new Set());
                this.tagCloud.set(key, { tag, count: 0, sites: [] });
            }
            this.tagIndex.get(key).add(site.id);
            const entry = this.tagCloud.get(key);
            entry.count++;
            if (entry.sites.length < 10) entry.sites.push(site.name);
        });
    }

_validateSites(sites) {
        const valid = sites.filter(site => {
            if (!site || typeof site !== 'object') return false;
            if (!site.name || typeof site.name !== 'string') return false;
            if (!site.category || typeof site.category !== 'string') return false;
            if (!site.url || typeof site.url !== 'string') return false;
            try { new URL(site.url); } catch { return false; }
            return true;
        });
        const invalid = sites.length - valid.length;
        if (invalid > 0) {
            console.warn(`[DataManager] 数据格式验证: 跳过 ${invalid} 条无效站点数据`);
        }
        if (valid.length === 0 && sites.length > 0) {
            console.warn('[DataManager] 全部站点验证失败，启用宽松模式');
            return sites;
        }
        return valid;
    }

    _saveCache() {
        try {
            const cacheData = {
                version: 'v3',
                timestamp: Date.now(),
                data: this.raw
            };
            localStorage.setItem('webnav_sites_cache', JSON.stringify(cacheData));
            // // console.log('[DataManager] 数据已缓存');
        } catch (e) {
            console.warn('[DataManager] 缓存保存失败:', e);
        }
    }

    _loadCache() {
        try {
            const cached = localStorage.getItem('webnav_sites_cache');
            if (!cached) return null;

            const parsed = JSON.parse(cached);
            if (!parsed || !parsed.data || !Array.isArray(parsed.data)) {
                console.warn('[DataManager] 缓存格式无效，清除旧缓存');
                localStorage.removeItem('webnav_sites_cache');
                return null;
            }

            // 检查缓存版本
            if (parsed.version !== 'v3') {
                // console.log('[DataManager] 缓存版本不匹配，忽略缓存');
                return null;
            }

            // 检查缓存过期时间
            const maxAge = 7 * 24 * 60 * 60 * 1000; // 7天
            if (Date.now() - parsed.timestamp > maxAge) {
                // console.log('[DataManager] 缓存已过期');
                localStorage.removeItem('webnav_sites_cache');
                return null;
            }

            // 验证数据格式
            this._validateSites(parsed.data);
            // console.log('[DataManager] 从缓存恢复数据（版本: ' + parsed.version + '）');
            return parsed.data;
        } catch (e) {
            console.warn('[DataManager] 缓存加载失败:', e);
            localStorage.removeItem('webnav_sites_cache');
        }
        return null;
    }

    _renderError(error) {
        const container = document.getElementById('site-container');
        if (!container) return;
        container.innerHTML =
            '<div class="error-state" style="text-align:center;padding:60px 20px;">' +
            '<div style="font-size:48px;margin-bottom:16px;">⚠️</div>' +
            '<h2 style="margin-bottom:8px;">数据加载失败</h2>' +
            '<p style="color:var(--text-secondary);max-width:500px;margin:0 auto 20px;">' +
            '原因: ' + (error.message || String(error)) + '<br/>' +
            '建议检查网络连接或稍后重试。' +
            '</p>' +
            '<button onclick="window.dataManager.load()" style="padding:10px 24px;cursor:pointer;">重试加载</button>' +
            '</div>';
    }

    getSitesByLeafId(leafId) {
        let siteIds = [];
        if (this.mappings.has(leafId)) {
            siteIds = this.mappings.get(leafId) || [];
        } else {
            const parts = leafId.split('/');
            if (parts.length === 2) {
                const altId = parts[0] + '/' + parts[1] + '/' + parts[1];
                if (this.mappings.has(altId)) siteIds = this.mappings.get(altId) || [];
            } else if (parts.length === 1 && parts[0]) {
                // 尝试匹配分类级
                const catId = parts[0] + '/' + parts[0];
                if (this.mappings.has(catId)) siteIds = this.mappings.get(catId) || [];
                else {
                    // 聚合该分类下所有子分类的站点
                    const cat = this.categories[parts[0]];
                    if (cat && cat.subCategories) {
                        Object.values(cat.subCategories).forEach(sub => {
                            if (sub.leafCategories) {
                                Object.values(sub.leafCategories).forEach(leaf => {
                                    siteIds.push(...leaf.siteIds);
                                });
                            }
                        });
                    }
                }
            }
        }
        return siteIds.map(id => this.sites.get(id)).filter(Boolean);
    }

    getAllSites() {
        return Array.from(this.sites.values());
    }

    /**
     * Get single site by ID
     * @param {number} siteId
     * @returns {Object|null}
     */
    getSite(siteId) {
        return this.sites.get(siteId) || null;
    }

    getSitesByCategory(catId) {
        const cat = this.categories[catId];
        if (!cat) return [];
        const siteIds = [];
        Object.values(cat.subCategories || {}).forEach(sub => {
            Object.values(sub.leafCategories || {}).forEach(leaf => {
                siteIds.push(...leaf.siteIds);
            });
        });
        return [...new Set(siteIds)].map(id => this.sites.get(id)).filter(Boolean);
    }

    getCategory(catId) {
        return this.categories[catId] || null;
    }

    getTagCloud(limit = 50) {
        return (this.tagIndexSorted || []).slice(0, limit);
    }

    filterByTags(sites, tags) {
        if (!tags || tags.length === 0) return sites;
        const tagSet = new Set(tags.map(t => t.toLowerCase()));
        return sites.filter(site =>
            site.tags && site.tags.some(t => tagSet.has(t.toLowerCase()))
        );
    }

    getStats() {
        const categories = Object.keys(this.categories);
        let totalSites = 0;
        let totalTags = this.tagCloud.size;
        categories.forEach(cat => {
            const catObj = this.categories[cat];
            Object.values(catObj.subCategories || {}).forEach(sub => {
                Object.values(sub.leafCategories || {}).forEach(leaf => {
                    totalSites += leaf.siteIds.length;
                });
            });
        });
        return { categories: categories.length, sites: totalSites, tags: totalTags };
    }
}

const dataManager = new DataManager();
window.dataManager = dataManager;