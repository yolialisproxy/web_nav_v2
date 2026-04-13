/**
 * data.js - 数据加载与索引系统
 * 职责：加载 JSON，构建三层检索索引
 * 规范：Data_Spec.md, Technical_Architecture.md 4.1
 */

class DataManager {
    constructor() {
        this.raw = null;
        this.sites = new Map(); // SiteID -> SiteObject
        this.categories = {};     // CategoryID -> CategoryObject
        this.mappings = new Map(); // LeafID -> SiteID[]
        this.isLoaded = false;
    }

    async load() {
        try {
            const response = await fetch('./data/websites.json');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            this.raw = await response.json();
            
            this._buildIndexes();
            this.isLoaded = true;
            console.log('WebNav V2: Data loaded and indexed successfully.');
        } catch (e) {
            console.error('WebNav V2: Data load failed:', e);
            this._handleLoadError(e);
        }
    }

    _buildIndexes() {
        // 1. 索引所有网站 (Sites)
        if (this.raw.sites) {
            Object.entries(this.raw.sites).forEach(([id, site]) => {
                this.sites.set(id, site);
            });
        }

        // 2. 索引分类树 (Categories)
        this.categories = this.raw.categories || {};

        // 3. 建立叶子类 -> 网站列表的映射 (Mappings)
        // 递归遍历分类树寻找 leafCategories
        const traverse = (node) => {
            if (node.subCategories) {
                Object.values(node.subCategories).forEach(traverse);
            }
            if (node.leafCategories) {
                Object.entries(node.leafCategories).forEach(([leafId, leaf]) => {
                    this.mappings.set(leafId, leaf.siteIds || []);
                });
            }
        };
        traverse(this.categories);
    }

    getSitesByLeafId(leafId) {
        const siteIds = this.mappings.get(leafId) || [];
        return siteIds.map(id => this.sites.get(id)).filter(Boolean);
    }

    getAllSites() {
        return Array.from(this.sites.values());
    }

    _handleLoadError(error) {
        const container = document.getElementById('view-container');
        if (container) {
            container.innerHTML = `
                <<divdiv style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--color-text-dim); text-align:center;">
                    <<pp>数据加载失败，请检查网络连接</p>
                    <<buttonbutton onclick="location.reload()" style="margin-top:12px; padding:8px 16px; cursor:pointer; background:var(--color-primary); color:white; border:none; border-radius:4px;">重试</button>
                </div>
            `;
        }
    }
}

const dataManager = new DataManager();
window.dataManager = dataManager;
