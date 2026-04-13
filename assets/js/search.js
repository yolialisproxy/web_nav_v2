/**
 * search.js - 搜索引擎
 * 职责：实现快速模糊匹配与评分排序
 * 规范：Interaction_Flow.md 3.1
 */

class SearchEngine {
    constructor(dataManager) {
        this.dataManager = dataManager;
    }

    query(text) {
        if (!text) return [];
        
        const query = text.toLowerCase();
        const allSites = this.dataManager.getAllSites();
        
        const results = allSites.map(site => {
            let score = 0;
            if (site.name.toLowerCase().includes(query)) score += 100;
            if (site.desc.toLowerCase().includes(query)) score += 30;
            if (site.tags && site.tags.some(t => t.toLowerCase().includes(query))) score += 50;
            
            return { site, score };
        })
        .filter(res => res.score > 0)
        .sort((a, b) => b.score - a.score);

        return results.slice(0, 50).map(res => res.site);
    }
}

const searchEngine = new SearchEngine(dataManager);
window.searchEngine = searchEngine;
