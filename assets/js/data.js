/**
 * data.js - 数据加载与索引系统
 * 职责：加载 JSON，构建三层检索索引
 * 规范：Data_Spec.md, Technical_Architecture.md 4.1
 */

class DataManager {
    constructor() {
        this.raw = null;
        this.sites = new Map();
        this.categories = {};
        this.mappings = new Map();
        this.isLoaded = false;
    }

    async load() {
        try {
            const response = await fetch('data/websites.json');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            this.raw = await response.json();

            this._buildIndexes();
            this.isLoaded = true;
            //            // console.log('✅ WebNav V2: Data loaded and indexed successfully.');
        } catch (e) {
            console.error('❌ WebNav V2: Data load failed:', e);
            this._handleLoadError(e);
        }
    }

    _buildIndexes() {
        this.categories = {};
        this.sites = new Map();
        this.mappings = new Map();
        let siteId = 0;

        this.raw.forEach(site => {
            if (!site._cat) return;

            site.id = siteId++;
            this.sites.set(site.id, site);

            // 拆分四级分类路径
            const parts = site._cat.split('/').filter(Boolean);
            if (parts.length < 1) return;

            const [cat, sub, leaf] = parts;

            // 构建分类树
            if (!this.categories[cat]) {
                this.categories[cat] = { name: cat, subCategories: {} };
            }

            if (!this.categories[cat].subCategories[sub]) {
                this.categories[cat].subCategories[sub] = { name: sub, leafCategories: {} };
            }

            if (!this.categories[cat].subCategories[sub].leafCategories[leaf]) {
                this.categories[cat].subCategories[sub].leafCategories[leaf] = { name: leaf, siteIds: [] };
            }

            const leafNode = this.categories[cat].subCategories[sub].leafCategories[leaf];
            leafNode.siteIds.push(site.id);

            // 建立映射索引
            const leafId = `${cat}/${sub}/${leaf}`;
            if (!this.mappings.has(leafId)) {
                this.mappings.set(leafId, []);
            }
            this.mappings.get(leafId).push(site.id);
        });
    }

    getSitesByLeafId(leafId) {
        const siteIds = this.mappings.get(leafId) || [];
        return siteIds.map(id => this.sites.get(id)).filter(Boolean);
    }

    getAllSites() {
        return Array.from(this.sites.values());
    }

    _handleLoadError(error) {
        renderSites(false);
    }
}

const dataManager = new DataManager();
window.dataManager = dataManager;
