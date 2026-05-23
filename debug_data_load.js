"use strict";
// 调试数据加载过程
const fs = require('fs');
const http = require('http');
const url = require('url');
// 复制DataManager类的关键部分
class MockDataManager {
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
        if (this.isLoaded)
            return Promise.resolve();
        try {
            console.log('[DataManager] 开始加载数据...');
            // 读取本地文件而不是通过fetch
            const rawData = fs.readFileSync('./data/websites.json', 'utf8');
            const text = rawData;
            if (!text || text.trim().length === 0) {
                throw new Error('数据文件为空');
            }
            this.raw = JSON.parse(text);
            console.log(`[DataManager] 原始数据长度: ${this.raw.length}`);
            if (!Array.isArray(this.raw)) {
                throw new Error('数据格式错误：期望数组');
            }
            // 数据格式验证
            console.log('[DataManager] 开始数据验证...');
            this.raw = this._validateSites(this.raw);
            console.log(`[DataManager] 验证后数据长度: ${this.raw.length}`);
            this._buildIndexes();
            this.isLoaded = true;
            this._loadError = null;
            console.log('[DataManager] 数据加载成功!');
            return Promise.resolve();
        }
        catch (e) {
            this._loadError = e;
            console.error('[DataManager] 加载失败:', e);
            throw e;
        }
    }
    _validateSites(sites) {
        const valid = sites.filter(site => {
            if (!site || typeof site !== 'object')
                return false;
            if (!site.name || typeof site.name !== 'string')
                return false;
            if (!site.category || typeof site.category !== 'string')
                return false;
            if (!site.url || typeof site.url !== 'string')
                return false;
            try {
                new URL(site.url);
            }
            catch (_b) {
                return false;
            }
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
    _buildIndexes() {
        console.log('[DataManager] 开始构建索引...');
        this.categories = {};
        this.sites = new Map();
        this.mappings = new Map();
        this.tagIndex = new Map();
        this.tagCloud = new Map();
        let siteId = 0;
        this.raw.forEach(site => {
            // 跳过无效数据
            if (!site || !site.category)
                return;
            // 数据清洗：规范化字段
            site.id = siteId++;
            site.name = (site.name || '').trim();
            site.description = (site.description || '').trim();
            site.category = (site.category || '').trim();
            site.url = (site.url || '').trim();
            if (!site.name || !site.category)
                return;
            this.sites.set(site.id, site);
            // 分类索引构建
            try {
                this._addToCategoryIndex(site);
            }
            catch (e) {
                console.warn(`[DataManager] 分类索引构建失败 for site ${site.name}:`, e);
            }
            // 标签索引构建
            try {
                this._addToTagIndex(site);
            }
            catch (e) {
                console.warn(`[DataManager] 标签索引构建失败 for site ${site.name}:`, e);
            }
        });
        // 按热度排序标签云
        const sortedTags = [...this.tagCloud.values()].sort((a, b) => b.count - a.count);
        this.tagIndexSorted = sortedTags;
        console.log(`[DataManager] 索引构建完成: ${this.sites.size} 站点, ${Object.keys(this.categories).length} 分类, ${this.tagCloud.size} 标签`);
    }
    _addToCategoryIndex(site) {
        const parts = site.category.split('/').filter(Boolean);
        let cat, sub, leaf;
        if (parts.length >= 3) {
            [cat, sub, leaf] = parts;
        }
        else if (parts.length === 2) {
            [cat, sub] = parts;
            leaf = sub;
        }
        else {
            cat = parts[0];
            sub = cat;
            leaf = cat;
        }
        // 规范化名称
        cat = cat.trim();
        sub = sub.trim();
        leaf = leaf.trim();
        if (!this.categories[cat])
            this.categories[cat] = { name: cat, subCategories: {} };
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
        if (!this.mappings.has(leafId))
            this.mappings.set(leafId, []);
        this.mappings.get(leafId).push(site.id);
        if (leaf === sub) {
            const subLevelId = `${cat}/${sub}`;
            if (!this.mappings.has(subLevelId))
                this.mappings.set(subLevelId, []);
            this.mappings.get(subLevelId).push(site.id);
        }
    }
    _addToTagIndex(site) {
        if (!site.tags || !Array.isArray(site.tags))
            return;
        site.tags.forEach(tag => {
            if (!tag || typeof tag !== 'string')
                return;
            const key = tag.trim().toLowerCase();
            if (!key)
                return;
            if (!this.tagIndex.has(key)) {
                this.tagIndex.set(key, new Set());
                this.tagCloud.set(key, { tag, count: 0, sites: [] });
            }
            this.tagIndex.get(key).add(site.id);
            const entry = this.tagCloud.get(key);
            entry.count++;
            if (entry.sites.length < 10)
                entry.sites.push(site.name);
        });
    }
}
// 运行调试
(async () => {
    const dm = new MockDataManager();
    try {
        await dm.load();
        console.log('\n=== 加载结果 ===');
        console.log(`isLoaded: ${dm.isLoaded}`);
        console.log(`raw length: ${dm.raw ? dm.raw.length : 0}`);
        console.log(`sites size: ${dm.sites.size}`);
        console.log(`categories count: ${Object.keys(dm.categories).length}`);
        console.log(`tagCloud size: ${dm.tagCloud.size}`);
    }
    catch (e) {
        console.error('加载过程中发生错误:', e);
    }
})();
//# sourceMappingURL=debug_data_load.js.map