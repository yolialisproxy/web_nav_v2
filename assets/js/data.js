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
            const response = await fetch('../data/websites.json');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            this.raw = await response.json();
            
            this._buildIndexes();
            this.isLoaded = true;
            // // // // // // // // // // // // // // // // // // // console.log('✅ WebNav V2: Data loaded and indexed successfully.');
        } catch (e) {
            console.error('❌ WebNav V2: Data load failed:', e);
            this._handleLoadError(e);
        }
    }

    _buildIndexes() {
        if (this.raw.sites) {
_buildIndexes() {
 this.categories = this.raw || {};
 this.sites = new Map();
 this.mappings = new Map();

 const traverse = (node) => {
  if (node.sites) {
   node.sites.forEach(site => {
    this.sites.set(site.id, site);
   });
  }
  if (node.subcategories) {
   Object.values(node.subCategories).forEach(child => {
    traverse(child);
   });
  }
  if (node.minor_categories) {
   Object.values(node.minor_categories).forEach(child => {
    traverse(child);
   });
  }
 };

Object.values(this.categories).forEach(category => {
  traverse(category);
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
        const container = document.getElementById('view-container');
        if (container) {
            container.innerHTML = `
                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--color-text-dim); text-align:center;">
                    <p>数据加载失败，请检查网络连接</p>
                    <button onclick="location.reload()" style="margin-top:12px; padding:8px 16px; cursor:pointer; background:var(--color-primary); color:white; border:none; border-radius:4px;">重试</button>
                </div>
            `;
        }
    }
}

const dataManager = new DataManager();
window.dataManager = dataManager;
