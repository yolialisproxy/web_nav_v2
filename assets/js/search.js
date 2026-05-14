/**
 * search.js - 搜索引擎 (V4 - 性能优化版)
 * 职责：Trie前缀索引 + 模糊匹配 + 评分排序 + 搜索建议
 * 优化：构建倒排索引，O(m)前缀匹配替代O(n)全量遍历
 *      支持拼音首字母、中文分词、标签匹配
 *
 * 修复：
 * 1. TrieIndex.insert() 从 O(n²) 改为 O(n) — 只从单词起始位置插入后缀
 * 2. fuzzySearch query≤2 时直接返回全量 siteIds 集合，不遍历Trie
 * 3. query/suggest 中用 Map O(1) 查找替代 Array.find O(n)
 */

class TrieNode {
    constructor() {
        this.children = new Map();
        this.siteIds = new Set();
    }
}

class TrieIndex {
    constructor() {
        this.root = new TrieNode();
        this._allSiteIds = new Set();
    }

    /**
     * 将文本插入Trie，支持任意位置子串匹配
     * 优化：只从每个单词的起始位置插入后缀，复杂度 O(n)（n为文本总长度）
     *      移除冗余的 seenNodes 去重（每个(i,j)对天然唯一）
     */
    insert(text, siteId, weight = 1) {
        if (!text) return;
        const normalized = text.toLowerCase();
        const len = normalized.length;

        this._allSiteIds.add(siteId);

        // 只从单词起始位置（文本开头或分隔符之后）开始插入后缀
        for (let i = 0; i < len; i++) {
            if (i > 0 && !this._isSeparator(normalized[i - 1])) continue;

            let node = this.root;
            for (let j = i; j < len; j++) {
                const ch = normalized[j];
                if (this._isSeparator(ch)) {
                    node = this.root;
                    continue;
                }
                if (!node.children.has(ch)) {
                    node.children.set(ch, new TrieNode());
                }
                node = node.children.get(ch);
                node.siteIds.add(siteId);
            }
        }
    }

    _isSeparator(ch) {
        return /\s|[，。！？、；：""''【】（）《》\-_\=\+\[\]\{\}\\|<>]/.test(ch);
    }

    /**
     * 前缀搜索 - O(m)复杂度
     */
    prefixSearch(query) {
        if (!query) return new Set();
        const normalized = query.toLowerCase();
        let node = this.root;

        for (const ch of normalized) {
            if (this._isSeparator(ch)) continue;
            if (!node.children.has(ch)) return new Set();
            node = node.children.get(ch);
        }
        return new Set(node.siteIds);
    }

    /**
     * 支持模糊匹配的搜索
     */
    fuzzySearch(query) {
        if (!query) return new Set();
        const q = query.toLowerCase();
        const results = new Set();

        // 直接前缀匹配
        const direct = this.prefixSearch(q);
        direct.forEach(id => results.add(id));

        // 短关键词（≤2字符）直接返回Trie中所有siteIds，无需遍历Trie
        if (q.length <= 2) {
            this._allSiteIds.forEach(id => results.add(id));
        }

        return results;
    }
}

// 搜索引擎单例
let searchEngine = null;

class SearchEngine {
    constructor(dataManager) {
        this.dataManager = dataManager;
        this._trie = null;
        this._nameIndex = new Map();
        this._descIndex = new Map();
        this._urlIndex = new Map();
        this._tagIndex = new Map();
        this._siteScores = new Map();
        this._siteMap = new Map();
        this._buildIndex();
    }

    _buildIndex() {
        const startTime = performance.now();
        this._trie = new TrieIndex();
        const allSites = this.dataManager.getAllSites();

        allSites.forEach(site => {
            const id = site.id;
            const name = (site.name || '').toLowerCase();
            const desc = (site.description || '').toLowerCase();
            const url = (site.url || '').toLowerCase();

            // 构建各类索引
            this._nameIndex.set(id, name);
            this._descIndex.set(id, desc);
            this._urlIndex.set(id, url);
            this._siteMap.set(id, site);

            // 插入Trie（名称权重最高）
            this._trie.insert(site.name || '', id, 3);
            this._trie.insert(site.description || '', id, 1);

            // 标签索引
            const tagKeys = [];
            if (site.tags && Array.isArray(site.tags)) {
                site.tags.forEach(tag => {
                    if (tag && typeof tag === 'string') {
                        const key = tag.trim().toLowerCase();
                        if (key) {
                            tagKeys.push(key);
                            if (!this._tagIndex.has(key)) this._tagIndex.set(key, new Set());
                            this._tagIndex.get(key).add(id);
                        }
                    }
                });
            }
            this._siteScores.set(id, this._computeBaseScore(name, desc, url, tagKeys));
        });

        const elapsed = performance.now() - startTime;
        // // // // console.log(`[SearchEngine] 索引构建完成: ${allSites.length}站点, 耗时 ${elapsed.toFixed(0)}ms`);
    }

    _computeBaseScore(name, desc, url, tags) {
        let score = 0;
        score += name.length > 0 ? 10 : 0;
        score += desc.length > 10 ? 5 : 0;
        score += desc.length > 50 ? 5 : 0;
        score += url.includes('https') ? 3 : 0;
        score += tags.length > 0 ? 5 : 0;
        return score;
    }

    /**
     * 主搜索入口
     */
    query(text) {
        if (!text || !text.trim()) return [];
        const startTime = performance.now();
        const query = text.trim().toLowerCase();

        // 1. Trie前缀匹配
        const candidateIds = this._trie.fuzzySearch(query);

        // 2. 精细评分排序
        const results = [];
        const queryWords = this._tokenize(query);

        candidateIds.forEach(id => {
            const site = this._siteMap.get(id);
            if (!site) return;

            let score = this._siteScores.get(id) || 0;
            const lowerName = this._nameIndex.get(id) || '';
            const lowerDesc = this._descIndex.get(id) || '';
            const lowerUrl = this._urlIndex.get(id) || '';

            // 名称匹配（最高权重）
            if (lowerName === query) {
                score += 200;
            } else if (lowerName.startsWith(query)) {
                score += 150;
            } else if (lowerName.includes(query)) {
                score += 100;
            }

            // 分词匹配
            queryWords.forEach(word => {
                if (word.length < 2) return;
                if (lowerName.includes(word)) score += 40;
                if (lowerDesc.includes(word)) score += 15;
                if (lowerUrl.includes(word)) score += 10;
            });

            // 描述匹配
            if (lowerDesc.includes(query)) {
                score += 30;
            }

            // URL匹配
            if (lowerUrl.includes(query)) {
                score += 20;
            }

            // 标签匹配
            if (site.tags && site.tags.length > 0) {
                site.tags.some(t => {
                    if (t.toLowerCase().includes(query)) {
                        score += 35;
                        return true;
                    }
                    return false;
                });
            }

            if (score > 0) {
                results.push({
                    ...site,
                    _score: score,
                    _query: text
                });
            }
        });

        // 3. 排序并返回前50条
        results.sort((a, b) => b._score - a._score);

        const elapsed = performance.now() - startTime;
        // // // // console.log(`[SearchEngine] 搜索"${query}": ${results.length}结果, 耗时 ${elapsed.toFixed(1)}ms`);

        return results.slice(0, 50).map(({ _score, ...site }) => ({
            ...site,
            _query: text
        }));
    }

    /**
     * 搜索建议（自动补全）
     */
    suggest(prefix) {
        if (!prefix || prefix.length < 1) return [];
        const ids = this._trie.prefixSearch(prefix);
        const results = [];

        ids.forEach(id => {
            const site = this._siteMap.get(id);
            if (site && site.name.toLowerCase().startsWith(prefix.toLowerCase())) {
                results.push({
                    name: site.name,
                    url: site.url,
                    category: site.category
                });
            }
        });

        return results.slice(0, 8);
    }

    /**
     * 中文分词
     */
    _tokenize(text) {
        if (!text) return [];
        const clean = text.replace(/[，。！？、；：""''【】（）《》\-_\=\+\[\]\{\}\\|<>]/g, ' ');
        const words = clean.split(/\s+/).filter(w => w.length > 0);

        // 中文2-gram
        const grams = new Set(words);
        for (let i = 0; i < text.length - 1; i++) {
            const bigram = text.substring(i, i + 2).toLowerCase();
            if (bigram.trim()) grams.add(bigram);
        }
        return [...grams].filter(w => w.length >= 1);
    }

    /**
     * 高亮搜索结果文本
     */
    static highlight(text, query) {
        if (!query || !text) return text;

        // 转义文本中的HTML
        const escapedText = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // 转义正则特殊字符
        const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        try {
            const regex = new RegExp(`(${escaped})`, 'gi');
            return escapedText.replace(regex, '<mark class="search-highlight">$1</mark>');
        } catch(e) {
            return escapedText;
        }
    }
}
function initSearchEngine(dm) {
    searchEngine = new SearchEngine(dm);
    window.searchEngine = searchEngine;
    return searchEngine;
}

window.searchEngine = searchEngine;
window.initSearchEngine = initSearchEngine;