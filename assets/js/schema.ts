/**
 * schema.js - Schema.org 结构化数据动态生成脚本 (V1.0)
 * 职责：为所有页面生成并注入 JSON-LD 结构化数据，支持 Organization / WebSite / ItemList / BreadcrumbList
 * 用法：在 </body> 前通过 <script src="assets/js/schema.js"></script> 引入
 * 可被其他页面引用，调用全局函数 window.schemaRenderer.update() 刷新数据
 */

(function (global) {
    'use strict';

    // ===================== 配置 =====================
    const CONFIG = {
        siteUrl: 'https://yolialisproxy.github.io/web_nav_v2/',
        siteName: '啃魂导航',
        orgName: '啃魂导航',
        orgAlternateName: 'WebNav V3',
        orgDescription: '面向开发者的智能导航站，聚合AI工具、编程工具、设计资源及技术网站',
        orgLogo: 'assets/images/logo.png',
        orgSameAs: ['https://github.com/yolialisproxy/web_nav_v2'],
        defaultLocale: 'zh-CN',
        enLocale: 'en',
        ogImage: 'https://yolialisproxy.github.io/web_nav_v2/assets/images/logo.png',
        // 静态链接集合（用于 ItemList）
        staticLinks: [
            { name: '首页', url: 'https://yolialisproxy.github.io/web_nav_v2/' },
            { name: 'AI 工具', url: 'https://yolialisproxy.github.io/web_nav_v2/#category=AI' },
            { name: '编程工具', url: 'https://yolialisproxy.github.io/web_nav_v2/#category=编程' },
            { name: '设计资源', url: 'https://yolialisproxy.github.io/web_nav_v2/#category=设计' },
            { name: '开发者工具', url: 'https://yolialisproxy.github.io/web_nav_v2/#category=工具' }
        ]
    };

    // ===================== 工具函数 =====================

    /** 获取当前页面完整 URL */
    function getCurrentUrl() {
        return global.location ? global.location.href : CONFIG.siteUrl;
    }

    /** 安全获取文本内容 */
    function safeText(el) {
        return el ? (el.textContent || el.innerText || '').trim() : '';
    }

    /** 获取站点评分/统计信息（从 dataManager） */
    function getSiteStats() {
        try {
            if (global.dataManager && typeof global.dataManager.getStats === 'function') {
                return global.dataManager.getStats();
            }
        } catch (e) { /* ignore */ }
        return null;
    }

    /** 从当前 URL hash 解析面包屑路径 */
    function parseBreadcrumbsFromHash() {
        var crumbs = [];
        var hash = '';
        try {
            hash = global.location.hash || '';
        } catch (e) { /* ignore */ }

        // 总是包含首页
        crumbs.push({ name: '首页', url: CONFIG.siteUrl });

        if (hash) {
            var params = new URLSearchParams(hash.slice(1));
            var category = params.get('category');
            var sub = params.get('sub');
            var leaf = params.get('leaf');

            if (category && global.dataManager && global.dataManager.categories) {
                var cat = global.dataManager.categories[category];
                if (cat) {
                    crumbs.push({ name: cat.name, url: CONFIG.siteUrl + '#category=' + encodeURIComponent(category) });
                    if (sub && cat.subCategories && cat.subCategories[sub]) {
                        crumbs.push({ name: cat.subCategories[sub].name, url: CONFIG.siteUrl + '#category=' + encodeURIComponent(category) + '&sub=' + encodeURIComponent(sub) });
                        if (leaf && cat.subCategories[sub].leafCategories && cat.subCategories[sub].leafCategories[leaf]) {
                            crumbs.push({ name: cat.subCategories[sub].leafCategories[leaf].name, url: CONFIG.siteUrl + '#category=' + encodeURIComponent(category) + '&sub=' + encodeURIComponent(sub) + '&leaf=' + encodeURIComponent(leaf) });
                        }
                    }
                }
            }
        } else {
            // 尝试从页面标题/内容推断
            var title = safeText(global.document.querySelector('h1, .view-header, .page-title'));
            if (title && title !== '啃魂导航') {
                crumbs.push({ name: title, url: getCurrentUrl() });
            }
        }

        return crumbs;
    }

    /** 构建完整的 URL（绝对路径） */
    function toAbsoluteUrl(relUrl) {
        if (!relUrl) return CONFIG.siteUrl;
        if (relUrl.startsWith('http')) return relUrl;
        // 确保不以 / 开头时拼接
        return CONFIG.siteUrl.replace(/\/+$/, '') + '/' + relUrl.replace(/^\/+/, '');
    }

    // ===================== Schema 构建函数 =====================

    /** 构建 Organization 对象 */
    function buildOrganization() {
        var org = {
            '@type': 'Organization',
            '@id': CONFIG.siteUrl + '#organization',
            'name': CONFIG.orgName,
            'alternateName': CONFIG.orgAlternateName,
            'url': CONFIG.siteUrl,
            'description': CONFIG.orgDescription
        };
        if (CONFIG.orgLogo) {
            org.logo = toAbsoluteUrl(CONFIG.orgLogo);
        }
        if (CONFIG.orgSameAs && CONFIG.orgSameAs.length > 0) {
            org.sameAs = CONFIG.orgSameAs;
        }
        return org;
    }

    /** 构建 WebSite 对象 */
    function buildWebSite() {
        return {
            '@type': 'WebSite',
            '@id': CONFIG.siteUrl + '#website',
            'name': CONFIG.siteName,
            'url': CONFIG.siteUrl,
            'description': CONFIG.orgDescription,
            'publisher': { '@id': CONFIG.siteUrl + '#organization' },
            'inLanguage': CONFIG.defaultLocale,
            'potentialAction': {
                '@type': 'SearchAction',
                'target': {
                    '@type': 'EntryPoint',
                    'urlTemplate': CONFIG.siteUrl + '?search={search_term_string}'
                },
                'query-input': 'required name=search_term_string'
            }
        };
    }

    /** 构建 ItemList（站点列表） */
    function buildItemList(sites) {
        var items = [];
        var allSites = [];

        // 尝试从 dataManager 获取全部站点
        try {
            if (global.dataManager && typeof global.dataManager.getAllSites === 'function') {
                allSites = global.dataManager.getAllSites();
            }
        } catch (e) { /* ignore */ }

        // 如果传入了 sites 数组则使用，否则使用 dataManager
        var siteList = (sites && sites.length > 0) ? sites : allSites;
        if (!siteList || siteList.length === 0) {
            siteList = CONFIG.staticLinks;
        }

        siteList.forEach(function (site, index) {
            if (site.url && site.name) {
                items.push({
                    '@type': 'ItemList',
                    'position': index + 1,
                    'name': site.name || ('站点 ' + (index + 1)),
                    'description': site.description || '',
                    'url': site.url.startsWith('http') ? site.url : CONFIG.siteUrl + site.url
                });
            }
        });

        return items;
    }

    /** 构建 BreadcrumbList */
    function buildBreadcrumbList(customCrumbs) {
        var crumbs = customCrumbs || parseBreadcrumbsFromHash();
        var items = crumbs.map(function (crumb, index) {
            var itemUrl = crumb.url || (CONFIG.siteUrl + '#category=' + encodeURIComponent(crumb.name));
            return {
                '@type': 'ListItem',
                'position': index + 1,
                'name': crumb.name || ('第 ' + (index + 1) + ' 级'),
                'item': toAbsoluteUrl(itemUrl)
            };
        });

        return {
            '@type': 'BreadcrumbList',
            '@id': getCurrentUrl() + '#breadcrumb',
            'name': '页面导航',
            'numberOfItems': items.length,
            'itemListElement': items
        };
    }

    /** 构建 ImageGallery（可选，增强搜索展示） */
    function buildImageGallery(images) {
        if (!images || images.length === 0) return null;
        return {
            '@type': 'ImageGallery',
            'name': CONFIG.siteName + ' - 截图展示',
            'image': images.map(function (img) {
                return {
                    '@type': 'ImageObject',
                    'url': toAbsoluteUrl(img.url || img),
                    'caption': img.caption || img.alt || CONFIG.siteName
                };
            })
        };
    }

    // ===================== 主渲染函数 =====================

    /**
     * 生成并注入完整的 JSON-LD 结构化数据
     * @param {Object} options - 配置选项
     * @param {Array} options.sites - 可选的站点数组（覆盖默认数据源）
     * @param {Array} options.breadcrumbs - 可选的面包屑数组 [{name, url}]
     * @param {boolean} options.includeItemList - 是否包含 ItemList（默认 false）
     * @param {Array} options.images - 可选的图片数组用于 ImageGallery
     */
    function renderSchema(options) {
        options = options || {};

        var graph = [];

        // 1. Organization
        graph.push(buildOrganization());

        // 2. WebSite
        graph.push(buildWebSite());

        // 3. BreadcrumbList（动态生成）
        graph.push(buildBreadcrumbList(options.breadcrumbs));

        // 4. ItemList（可选）
        if (options.includeItemList) {
            var items = buildItemList(options.sites);
            if (items.length > 0) {
                graph.push({
                    '@type': 'CollectionPage',
                    '@id': getCurrentUrl() + '#collection',
                    'name': CONFIG.siteName + ' - 资源列表',
                    'description': CONFIG.orgDescription,
                    'mainEntity': {
                        '@type': 'ItemList',
                        'numberOfItems': items.length,
                        'itemListElement': items
                    }
                });
            }
        }

        // 5. ImageGallery（可选）
        if (options.images && options.images.length > 0) {
            var gallery = buildImageGallery(options.images);
            if (gallery) graph.push(gallery);
        }

        // 注入到页面
        var el = global.document.getElementById('schema-org-data');
        if (!el) {
            // 创建新的 script 标签
            el = global.document.createElement('script');
            el.type = 'application/ld+json';
            el.id = 'schema-org-data';
            var head = global.document.head || global.document.getElementsByTagName('head')[0];
            head.appendChild(el);
        }
        el.textContent = JSON.stringify({ '@context': 'https://schema.org', '@graph': graph }, null, 2);

        // 同时更新页面 meta description（如果数据中有点评数/统计）
        try {
            var stats = getSiteStats();
            if (stats && stats.sites) {
                var descEl = global.document.querySelector('meta[name="description"]');
                if (descEl) {
                    var enhancedDesc = '啃魂导航是面向开发者的全能导航站，聚合AI工具、编程工具、设计资源及技术网站。' +
                        '已收录 ' + (stats.sites || 0) + ' 个优质站点，涵盖 ' + (stats.categories || 0) + ' 个分类，' +
                        (stats.tags || 0) + ' 个标签。';
                    if (enhancedDesc.length <= 320) {
                        descEl.setAttribute('content', enhancedDesc);
                    }
                }
            }
        } catch (e) { /* ignore */ }
    }

    // ===================== 更新函数（供外部调用） =====================

    /**
     * 动态更新面包屑结构化数据（用于 SPA 路由变化时）
     * @param {Array} breadcrumbs - 面包屑数组 [{name, url}]
     */
    function updateBreadcrumb(breadcrumbs) {
        var graph = [
            buildOrganization(),
            buildWebSite(),
            buildBreadcrumbList(breadcrumbs)
        ];

        var el = global.document.getElementById('schema-org-data');
        if (!el) {
            el = global.document.createElement('script');
            el.type = 'application/ld+json';
            el.id = 'schema-org-data';
            var head = global.document.head || global.document.getElementsByTagName('head')[0];
            head.appendChild(el);
        }
        el.textContent = JSON.stringify({ '@context': 'https://schema.org', '@graph': graph }, null, 2);
    }

    /**
     * 完整更新（从 dataManager 重新加载数据后调用）
     */
    function update() {
        renderSchema({ includeItemList: true });
    }

    // ===================== 自动初始化 =====================

    function init() {
        // 如果页面已存在静态 schema 标签则保留（由后端/模板生成）
        // 否则自动渲染基础 schema
        var existingEl = global.document.getElementById('schema-org-data');
        if (existingEl && existingEl.textContent && existingEl.textContent.trim().length > 0) {
            // 页面已有静态结构化数据，仅追加动态增强
            try {
                var parsed = JSON.parse(existingEl.textContent);
                if (parsed && parsed['@graph']) {
                    // 已存在完整的静态 schema，不重复覆盖
                    return;
                }
            } catch (e) { /* ignore, fall through to render */ }
        }
        // 基础渲染
        renderSchema({ includeItemList: false });
    }

    // 暴露全局 API
    global.schemaRenderer = {
        render: renderSchema,
        update: update,
        updateBreadcrumb: updateBreadcrumb,
        buildOrganization: buildOrganization,
        buildWebSite: buildWebSite,
        buildBreadcrumbList: buildBreadcrumbList,
        buildItemList: buildItemList
    };

    // DOM Ready 后初始化
    if (global.document && global.document.readyState === 'loading') {
        global.document.addEventListener('DOMContentLoaded', init);
    } else if (global.document) {
        init();
    }

})(typeof window !== 'undefined' ? window : this);