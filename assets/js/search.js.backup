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
            const matches = { name: false, desc: false, tags: [] };

            if (site.title.toLowerCase().includes(query)) {
                score += 100;
                matches.name = true;
            }
            if (site.description.toLowerCase().includes(query)) {
                score += 30;
                matches.desc = true;
            }
            if (site.tags && site.tags.some(t => {
                const match = t.toLowerCase().includes(query);
                if (match) matches.tags.push(t);
                return match;
            })) {
                score += 50;
            }

            return { site, score, matches };
        })
        .filter(res => res.score > 0)
        .sort((a, b) => b.score - a.score);

        return results.slice(0, 50).map(res => ({
            ...res.site,
            _matches: res.matches,
            _query: text
        }));
    }

    /**
     * 高亮搜索结果文本
     * @param {string} text 原始文本
     * @param {string} query 搜索关键词
     * @returns {string} 带高亮标记的HTML
     */
    static highlight(text, query) {
        if (!query || !text) return text;
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark class="search-highlight">$1</mark>');
    }
}

let searchEngine;

function initSearchEngine(dataManager) {
    searchEngine = new SearchEngine(dataManager);
    window.searchEngine = searchEngine;
    return searchEngine;
}

// Global exports
window.searchEngine = searchEngine;
window.initSearchEngine = initSearchEngine;
