/**
 * render.js - 渲染引擎 (V3.1)
 * 职责：DOM渲染、分页管理、视图切换、骨架屏控制
 * 优化：分页加载(每页40条)，避免一次性渲染3800+ DOM节点
 * 新增：虚拟滚动DOM回收（超过3页时自动回收最早的页面DOM并保留滚动位置）
 */

const PAGE_SIZE = 40;
// 最大保留的渲染页数（超过此值触发DOM回收）
const MAX_RENDERED_PAGES = 3;

const StateUI = {
    loading() {
        return '<div class="state-container state-loading">' +
            '<div class="loading-spinner"></div>' +
            '<div class="state-title">正在加载<span class="loading-dots"></span></div>' +
            '</div>';
    },
    error(msg) {
        return '<div class="state-container state-error">' +
            '<div class="state-icon">⚠️</div>' +
            '<div class="state-title">加载失败</div>' +
            '<div class="state-desc">' + msg + '</div>' +
            '<button class="btn btn-primary" style="margin-top:12px" onclick="window.location.reload()">重新加载</button>' +
            '</div>';
    },
    empty(msg) {
        return '<div class="state-container state-empty">' +
            '<div class="state-icon">📁</div>' +
            '<div class="state-title">暂无内容</div>' +
            '<div class="state-desc">' + msg + '</div>' +
            '</div>';
    },
    searchEmpty(q) {
        return '<div class="state-container state-empty">' +
            '<div class="state-icon">🔍</div>' +
            '<div class="state-title">未找到匹配</div>' +
            '<div class="state-desc">未找到与 "' + _escapeHtml(q) + '" 相关内容</div>' +
            '</div>';
    }
}

window.StateUI = StateUI;

/**
 * 更新页面 SEO meta（title / description / og:title / og:description）
 * SPA 路由切换后调用，保证每页都有差异化的 meta 信息
 */
function updatePageMeta({ title, description }) {
    if (title) {
        document.title = title;
        var ogTitle = document.querySelector('meta[property="og:title"]');
        if (ogTitle) ogTitle.setAttribute('content', title);
    }
    if (description) {
        var metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc) metaDesc.setAttribute('content', description);
        var ogDesc = document.querySelector('meta[property="og:description"]');
        if (ogDesc) ogDesc.setAttribute('content', description);
    }
}

/**
 * 分页渲染器（含DOM回收）
 */
class PaginatedRenderer {
    constructor(pageSize = PAGE_SIZE) {
        this.pageSize = pageSize;
        this.currentPage = 0;
        this.currentSites = [];
        this.totalPages = 0;
        this.isSearchMode = false;
        // 虚拟滚动：追踪当前在DOM中渲染的页面索引
        this._renderedPages = [];
    }

    setData(sites) {
        this.currentSites = sites || [];
        this.totalPages = Math.ceil(this.currentSites.length / this.pageSize);
        this.currentPage = 0;
        this._renderedPages = [];
    }

    getCurrentPageData() {
        const start = this.currentPage * this.pageSize;
        const end = start + this.pageSize;
        // 修复：返回当前页数据而非从0开始的全部数据
        return this.currentSites.slice(start, end);
    }

    hasMore() {
        return this.currentPage < this.totalPages - 1;
    }

    nextPage() {
        if (this.hasMore()) {
            this.currentPage++;
            return true;
        }
        return false;
    }

    reset() {
        this.currentPage = 0;
        this._renderedPages = [];
    }

    /** 标记某页已渲染到DOM中 */
    markPageRendered(pageIdx) {
        if (!this._renderedPages.includes(pageIdx)) {
            this._renderedPages.push(pageIdx);
        }
    }

    /** 标记某页已从DOM中移除 */
    markPageRemoved(pageIdx) {
        var idx = this._renderedPages.indexOf(pageIdx);
        if (idx !== -1) {
            this._renderedPages.splice(idx, 1);
        }
    }

    /** 获取最早渲染的页面索引 */
    getOldestRenderedPage() {
        return this._renderedPages.length > 0 ? this._renderedPages[0] : -1;
    }

    /** 是否需要回收（超过最大保留页数） */
    needsRecycling() {
        return this._renderedPages.length > MAX_RENDERED_PAGES;
    }

    /** 获取当前DOM中卡片总数 */
    getRenderedCardCount() {
        var grid = document.getElementById('sites-grid');
        return grid ? grid.querySelectorAll('.site-card').length : 0;
    }

    /** 获取当前DOM中的页数 */
    getRenderedPageCount() {
        return this._renderedPages.length;
    }
}

const paginatedRenderer = new PaginatedRenderer();
window.paginatedRenderer = paginatedRenderer;

/* ========== 纯函数：构建HTML ========== */

function _escapeHtml(text) {
    if (!text) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

function _buildCard(site, pageIdx) {
    var url = '#';
    var target = '';
    var rel = '';
    if (site.url) {
        try {
            new URL(site.url);
            url = site.url;
            target = 'target="_blank"';
            rel = 'rel="noopener noreferrer"';
        } catch(e) {}
    }
    var favicon = 'assets/images/favicon.png';
    if (site.url) {
        try {
            var hn = new URL(site.url).hostname;
            favicon = 'https://www.google.com/s2/favicons?domain=' + encodeURIComponent(hn) + '&sz=32';
        } catch(e) {}
    }
    var title = site.name || '';
    var desc = site.description || '';

    if (site._query) {
        title = SearchEngine ? SearchEngine.highlight(title, site._query) : title;
        desc = SearchEngine ? SearchEngine.highlight(desc, site._query) : desc;
    }

    // 虚拟滚动：为卡片添加 data-page 属性以便回收
    var dataAttr = '';
    if (pageIdx !== undefined) {
        dataAttr = ' data-page="' + pageIdx + '"';
    }

    var isFav = window.favoriteManager && window.favoriteManager.isFavorite(title);
           var favClass = isFav ? 'favorite-btn favorited' : 'favorite-btn';
           var favIcon = isFav ? '♥' : '♡';
           return '<a href="' + url + '" class="site site-card" data-site-id="' + site.id + '" data-site-name="' + _escapeHtml(title) + '"' + dataAttr + ' ' + target + ' ' + rel +
           ' aria-label="' + _escapeHtml(title) + '"' +
           (url !== '#' ? ' onclick="trackSiteClick(\'' + _escapeHtml(site.name) + '\')"' : '') +
           '>' +
           '<img src="' + favicon + '" class="card-icon" loading="lazy" alt="" ' +
           'onerror="this.onerror=null;this.src=\'assets/images/favicon.png\';">' +
           '<span class="card-title">' + title + '</span>' +
           '<span class="card-desc">' + desc + '</span>' +
           '<button class="' + favClass + '" data-action="toggle-favorite" aria-label="收藏" title="收藏站点">' + favIcon + '</button>' +
           '</a>';
}

function _buildGrid(sites, append, pageIdx) {
    if (!sites || sites.length === 0) {
        return '';
    }
    var html = '';
    if (!append) {
        html = '<div class="grid" id="sites-grid">';
    }
    sites.forEach(function(site) {
        html += _buildCard(site, pageIdx);
    });
    if (!append) {
        html += '</div>';
        html += '<div id="page-loading-indicator" class="page-loading-indicator" style="display:none">' +
                '<div class="loading-spinner-small"></div><span>加载更多...</span></div>';
    }
    return html;
}

function _getBreadcrumb(cid, sid, lid) {
    var parts = [];
    var cat = dataManager ? dataManager.categories[cid] : null;
    if (cat) parts.push(cat.name);
    if (sid && cat && cat.subCategories && cat.subCategories[sid]) {
        parts.push(cat.subCategories[sid].name);
    }
    if (lid && lid !== sid && cat && cat.subCategories && cat.subCategories[sid]) {
        var sub = cat.subCategories[sid];
        if (sub.leafCategories && sub.leafCategories[lid]) {
            parts.push(sub.leafCategories[lid].name);
        }
    }
    return parts.join(' <span class="bc-sep">›</span> ') || '全部';
}

/* ========== 核心渲染函数 ========== */

/**
 * 渲染站点列表（SPA统一入口）
 */
function renderSites(sites, containerId) {
    var cid = containerId || 'main-content';
    var container = document.getElementById(cid);
    if (!container) return;

    if (sites === null) {
        container.innerHTML = StateUI.loading();
        return;
    }
    if (sites === false) {
        container.innerHTML = StateUI.error('无法加载数据，请检查网络连接后重试');
        return;
    }

    // 应用标签筛选
    var activeTags = state.get('filterTags') || [];
    if (activeTags.length > 0 && state.tagAll.size > 0) {
        sites = state.filterByTags(sites, state.getActiveTags());
    }

    paginatedRenderer.setData(sites);
    paginatedRenderer.isSearchMode = false;

    if (sites.length === 0) {
        container.innerHTML = StateUI.empty('当前分类暂无站点');
        return;
    }

    // 构建工具栏
    var toolbarHtml = '<div class="view-toolbar">' +
        '<div class="toolbar-left">' +
        '<button class="view-btn view-grid active" onclick="setViewMode(\'grid\')" aria-label="网格视图" title="网格视图">⊞</button>' +
        '<button class="view-btn view-list" onclick="setViewMode(\'list\')" aria-label="列表视图" title="列表视图">☰</button>' +
        '</div>' +
        '<div class="toolbar-right">' +
        '<select class="sort-select" onchange="handleSortChange(this.value)" aria-label="排序方式">' +
        '<option value="default">默认排序</option>' +
        '<option value="name-asc">名称 ↑</option>' +
        '<option value="name-desc">名称 ↓</option>' +
        '</select>' +
        '</div>' +
        '</div>';

    var gridHtml = _buildGrid(paginatedRenderer.getCurrentPageData(), false, 0);
    container.innerHTML = toolbarHtml + gridHtml;
    paginatedRenderer.markPageRendered(0);
    _setupInfiniteScroll(container);
    bindCardEvents();

    // 恢复视图和排序状态
    var savedViewMode = localStorage.getItem('kunhun-nav-view-mode') || 'grid';
    setViewMode(savedViewMode);

    var savedSort = localStorage.getItem('kunhun-nav-sort-order') || 'default';
    var sortSelect = container.querySelector('.sort-select');
    if (sortSelect) {
        sortSelect.value = savedSort;
        // 如果之前有排序，重新应用
        if (savedSort !== 'default') {
            handleSortChange(savedSort);
        }
    }

    // 动画
    setTimeout(function() {
        container.querySelectorAll('.site-card').forEach(function(card, i) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(10px)';
            card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            setTimeout(function() {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 30 + i * 20);
        });
    }, 50);
}

// 列表视图渲染（分页 + 工具栏 + 无限滚动）
function renderSitesList(sites, containerId) {
    var cid = containerId || 'main-content';
    var container = document.getElementById(cid);
    if (!container) return;

    if (sites === null) {
        container.innerHTML = StateUI.loading();
        return;
    }
    if (sites === false) {
        container.innerHTML = StateUI.error('无法加载数据');
        return;
    }
    if (sites.length === 0) {
        container.innerHTML = StateUI.empty('暂无站点');
        return;
    }

    paginatedRenderer.setData(sites);
    paginatedRenderer.isSearchMode = false;

    // 工具栏（与网格视图保持一致）
    var toolbarHtml = '<div class="view-toolbar">' +
        '<div class="toolbar-left">' +
        '<button class="view-btn view-grid" onclick="setViewMode(\'grid\')" aria-label="网格视图" title="网格视图">⊞</button>' +
        '<button class="view-btn view-list active" onclick="setViewMode(\'list\')" aria-label="列表视图" title="列表视图">☰</button>' +
        '</div>' +
        '<div class="toolbar-right">' +
        '<select class="sort-select" onchange="handleSortChange(this.value)" aria-label="排序方式">' +
        '<option value="default">默认排序</option>' +
        '<option value="name-asc">名称 ↑</option>' +
        '<option value="name-desc">名称 ↓</option>' +
        '<option value="url-asc">URL ↑</option>' +
        '</select>' +
        '</div>' +
        '</div>';

    // 列表项渲染（复用 _buildListItems 构建器，避免重复 code）
    var listHtml = _buildListItems(paginatedRenderer.getCurrentPageData(), 0);
    container.innerHTML = toolbarHtml + listHtml;
    paginatedRenderer.markPageRendered(0);
    _setupInfiniteScroll(container);
    bindCardEvents();

    // 恢复排序状态
    var savedSort = localStorage.getItem('kunhun-nav-sort-order') || 'default';
    var sortSelect = container.querySelector('.sort-select');
    if (sortSelect) {
        sortSelect.value = savedSort;
        if (savedSort !== 'default') {
            handleSortChange(savedSort);
        }
    }
}

/** 构建列表项 HTML（独立构建器，供 renderSitesList + 分页加载复用） */
function _buildListItems(sites, pageIdx) {
    if (!sites || sites.length === 0) return '';
    var html = '<div class="sites-list">';
    sites.forEach(function(site) {
        // 使用 Google Favicon Service（与卡片视图一致）
        var favicon = 'assets/images/favicon.png';
        try {
            favicon = 'https://www.google.com/s2/favicons?domain=' + encodeURIComponent(new URL(site.url).hostname) + '&sz=32';
        } catch(e) {}

        var desc  = site.description ? site.description.replace(/"/g, '&quot;') : '暂无描述';
        var tags  = site.tags ? site.tags.map(function(t) { return '<span class="tag-pill small">' + t + '</span>'; }).join('') : '';
        var safeName = (site.name || '').replace(/"/g, '&quot;');

        html += '<div class="site-list-item" data-id="' + (site.id || '') + '" data-page="' + pageIdx + '">' +
            '<div class="site-list-content">' +
            '<div class="site-list-header">' +
            '<img src="' + favicon + '" alt="" class="site-list-favicon" loading="lazy" onerror="this.style.display=\'none\'">' +
            '<a href="' + (site.url || '#') + '" target="_blank" rel="noopener" class="site-list-name" title="' + safeName + '">' + safeName + '</a>' +
            '<span class="site-list-arrow">→</span>' +
            '<button class="favorite-btn" data-action="toggle-favorite" aria-label="收藏" title="收藏站点">♡</button>' +
            '</div>' +
            '<div class="site-list-desc">' + desc + '</div>' +
            '<div class="site-list-meta">' + tags + '</div>' +
            '</div>' +
            '</div>';
    });
    html += '</div>';
    return html;
}

// 游戏大厅渲染
function renderGamesHub(containerId) {
    var cid = containerId || 'main-content';
    var container = document.getElementById(cid);
    if (!container) return;

    var html = '<div class="games-hub">';
    html += '  <div class="games-header"><h2>🎮 游戏中心</h2><p class="games-subtitle">选择一款游戏开始娱乐</p></div>';
    html += '  <div class="games-grid">';

    var gameDefs = window.GameHub ? Object.entries(window.GameHub.games) : [];
    gameDefs.forEach(function([key, game]) {
        var icon = game.icon || '🎯';
        var name = game.name || key;
        var desc = game.desc || '游戏';
        var cat = game.cat || 'other';
        html += '<a href="#game=' + key + '" class="game-card" data-game="' + key + '" title="' + desc + '">';
        html += '  <div class="game-icon">' + icon + '</div>';
        html += '  <div class="game-name">' + name + '</div>';
        html += '  <div class="game-category">' + cat + '</div>';
        html += '</a>';
    });

    html += '  </div>';
    html += '</div>';

    container.innerHTML = html;

    // 游戏卡片点击：通过 hash 触发路由（state -> renderView）
    container.querySelectorAll('.game-card').forEach(function(el) {
        el.addEventListener('click', function(e) {
            e.preventDefault();
            var gameKey = el.dataset.game;
            window.location.hash = 'game=' + gameKey;
        });
    });
}



/**
 * 渲染分类视图（SPA视图）
 */
function renderCategoryView(catId, subId, leafId) {
    var cid = catId;
    var sid = subId;
    var lid = leafId || subId;

    if (!cid) {
        document.getElementById('main-content').innerHTML = StateUI.empty('请选择左侧分类浏览');
        return;
    }

    var fullId = sid && lid !== sid ? cid + '/' + sid + '/' + lid : cid + '/' + lid;
    var sites = dataManager.getSitesByLeafId(fullId);

    paginatedRenderer.isSearchMode = false;
    paginatedRenderer.setData(sites);
    paginatedRenderer.reset();

    var container = document.getElementById('main-content');

    // SEO meta 差异化：按分类生成 title + description
    var breadcrumb = _getBreadcrumb(cid, sid, lid);
    if (breadcrumb) {
        updatePageMeta({
            title: '啃魂导航 - ' + breadcrumb,
            description: '啃魂导航 | ' + breadcrumb + ' 分类，共 ' + sites.length + ' 个优质站点'
        });
    }

    // 面包屑
    var html = '<div class="view-header">' +
            '<div class="view-breadcrumb">' + _getBreadcrumb(cid, sid, lid) + '</div>' +
            '<div class="view-meta">' + sites.length + ' 个站点</div>' +
            '</div>';

    // 工具栏
    html += '<div class="view-toolbar">' +
            '<div class="toolbar-left">' +
            '<button class="view-btn view-grid active" onclick="setViewMode(\'grid\')" aria-label="网格视图" title="网格视图">⊞</button>' +
            '<button class="view-btn view-list" onclick="setViewMode(\'list\')" aria-label="列表视图" title="列表视图">☰</button>' +
            '</div>' +
            '<div class="toolbar-right">' +
            '<select class="sort-select" onchange="handleSortChange(this.value)" aria-label="排序方式">' +
            '<option value="default">默认排序</option>' +
            '<option value="name-asc">名称 ↑</option>' +
            '<option value="name-desc">名称 ↓</option>' +
            '<option value="url-asc">URL ↑</option>' +
            '</select>' +
            '</div>' +
            '</div>';

    // 标签筛选器
    var activeTags = state.get('filterTags') || [];
    if (state.tagAll.size > 0) {
        html += '<div class="tag-filter-bar">';
        html += '<span class="tag-filter-label">🏷️ 筛选:</span>';
        activeTags.forEach(function(tag) {
            html += '<button class="tag-active-filter" data-tag="' + _escapeHtml(tag) + '">' +
                    _escapeHtml(tag) + ' ×</button>';
        });
        var topTags = dataManager.tagIndexSorted.slice(0, 10);
        topTags.forEach(function(t) {
            var isActive = activeTags.includes(t.tag);
            if (!isActive) {
                html += '<button class="tag-suggest" data-tag="' + _escapeHtml(t.tag) + '">+' + t.tag + '(' + t.count + ')</button>';
            }
        });
        html += '</div>';
    }

    // 站点网格
    html += _buildGrid(paginatedRenderer.getCurrentPageData(), false, 0);
    paginatedRenderer.markPageRendered(0);

    container.innerHTML = html;
    _setupInfiniteScroll(container);
    bindCardEvents();
    _bindTagFilters();

    // 恢复排序状态
    var savedSort = localStorage.getItem('kunhun-nav-sort-order') || 'default';
    var sortSelect = container.querySelector('.sort-select');
    if (sortSelect) {
        sortSelect.value = savedSort;
        if (savedSort !== 'default') {
            // 需要重新获取当前分类的站点数据并排序
            var currentSites = paginatedRenderer.currentSites;
            if (currentSites) {
                // 延迟应用排序，确保数据已加载
                setTimeout(function() {
                    handleSortChange(savedSort);
                }, 0);
            }
        }
    }
}

/* ========== 搜索渲染 ========== */

function _renderSearchResults(s) {
    paginatedRenderer.isSearchMode = true;
    paginatedRenderer.setData(s.search.results);
    paginatedRenderer.reset();

    var container = document.getElementById('main-content');
    if (!container) return;

    if (s.search.results.length === 0) {
        container.innerHTML = StateUI.searchEmpty(s.search.query);
    } else {
        var headerHtml = '<div class="search-result-header">搜索 "<strong>' + _escapeHtml(s.search.query) +
                         '</strong>"，共 ' + s.search.results.length + ' 个结果</div>';
        container.innerHTML = headerHtml + _buildGrid(paginatedRenderer.getCurrentPageData(), false, 0);
        paginatedRenderer.markPageRendered(0);
    }
    _setupInfiniteScroll(container);
    bindCardEvents();
}

/* 渲染搜索覆盖层中的结果列表 */
function renderOverlaySearchResults(results, query) {
    var container = document.getElementById('search-results');
    if (!container) return;

    if (results.length === 0) {
        container.innerHTML = '<div class="state-container state-empty" style="padding:20px">' +
            '<div class="state-icon">🔍</div>' +
            '<div class="state-desc">未找到与 "' + _escapeHtml(query) + '" 相关的内容</div>' +
            '</div>';
        return;
    }

    var html = '';
    var baseUrl = window.location.origin || '';
    results.slice(0, 50).forEach(function(site) {
        var icon = '🌐';
        if (site.name && site.name.includes('GitHub')) icon = '🐙';
        else if (site.name && site.name.includes('AI')) icon = '🤖';
        else if (site.name && site.name.includes('Tool')) icon = '🔧';
        else if (site.name && site.name.includes('Design')) icon = '🎨';

        var siteUrl = site.url || '';
        html += '<a href="' + _escapeHtml(siteUrl) + '" class="overlay-search-item" target="_blank" rel="noopener noreferrer" aria-label="' + _escapeHtml(site.name) + '">' +
                '<img src="https://www.google.com/s2/favicons?domain=' + encodeURIComponent((siteUrl.match(/\/\/[^\\/]+/) || [''])[0].replace('//','')) + '&sz=32" class="osi-icon" loading="lazy" alt="" onerror="this.src=\'assets/images/favicon.png\';">' +
                '<div style="flex:1;min-width:0;">' +
                '<div class="osi-name">' + _escapeHtml(site.name) + '</div>' +
                '<div class="osi-desc">' + _escapeHtml(site.description || '暂无描述') + '</div>' +
                '</div>' +
                '<span class="osi-icon" style="width:auto;font-size:18px;">' + icon + '</span>' +
                '</a>';
    });
    container.innerHTML = html;
}

/* ========== 视图模式切换 ========== */
var currentViewMode = 'grid';

function setViewMode(mode) {
    currentViewMode = mode;
    // 持久化
    try {
        localStorage.setItem('kunhun-nav-view-mode', mode);
    } catch (e) {}

    // 更新工具栏按钮状态
    var btns = document.querySelectorAll('.view-btn');
    btns.forEach(function(b) { b.classList.remove('active'); });

    if (mode === 'list') {
        // 列表模式：检查 DOM 是否已经是 .sites-list，否则触发 state 驱动全量重渲染
        var existingList = document.querySelector('.sites-list');
        if (existingList) {
            // DOM 结构已正确，仅更新按钮
            var listBtn = document.querySelector('.view-btn.view-list');
            if (listBtn) listBtn.classList.add('active');
        } else {
            // 切换为列表：通过 state 触发，确保 toolbar 和 list-DOM 完整替换
            if (state && typeof state.set === 'function') {
                state.set('currentView', 'list');
            }
        }
    } else {
        // 网格模式：检查 #sites-grid 是否存在
        var existingGrid = document.getElementById('sites-grid');
        if (existingGrid) {
            // DOM 结构已正确，切换 CSS 类 + 按钮状态
            existingGrid.classList.remove('list-mode');
            var gridBtn = document.querySelector('.view-btn.view-grid');
            if (gridBtn) gridBtn.classList.add('active');
        } else {
            // 切换为网格：通过 state 触发重渲染
            if (state && typeof state.set === 'function') {
                state.set('currentView', 'grid');
            }
        }
    }
}

function handleSortChange(value) {
    // 持久化排序选择
    try {
        localStorage.setItem('kunhun-nav-sort-order', value);
    } catch (e) {}

    var sites = paginatedRenderer.currentSites;
    if (!sites) return;

    // 复制数组以免影响原始数据顺序
    sites = sites.slice();

    switch (value) {
        case 'name-asc':
            sites.sort(function(a, b) { return (a.name || '').localeCompare(b.name || ''); });
            break;
        case 'name-desc':
            sites.sort(function(a, b) { return (b.name || '').localeCompare(a.name || ''); });
            break;
        case 'url-asc':
            sites.sort(function(a, b) { return (a.url || '').localeCompare(b.url || ''); });
            break;
        default:
            // 恢复默认顺序
            sites.sort(function(a, b) { return (a.id || 0) - (b.id || 0); });
    }

    paginatedRenderer.reset();
    paginatedRenderer.setData(sites);

    // 根据当前视图模式选择渲染函数
    if (currentViewMode === 'list') {
        renderSitesList(sites, 'main-content');
    } else {
        renderSites(sites, 'main-content');
    }
}

/* ========== 虚拟滚动：DOM回收 ========== */

/**
 * 回收最早的页面DOM
 * @param {HTMLElement} grid - sites-grid 元素
 */
function _recycleOldestPage(grid) {
    var oldestPage = paginatedRenderer.getOldestRenderedPage();
    if (oldestPage < 0) return;

    var oldCards = grid.querySelectorAll('[data-page="' + oldestPage + '"]');
    if (oldCards.length === 0) {
        paginatedRenderer.markPageRemoved(oldestPage);
        return;
    }

    // 回收前记录滚动位置和grid高度，用于补偿滚动偏移
    var scrollTopBefore = window.pageYOffset;
    var gridScrollHeightBefore = grid.scrollHeight;

    // 移除旧卡片
    oldCards.forEach(function(card) {
        card.remove();
    });

    // 补偿滚动位置，保持视觉位置不变
    var gridScrollHeightAfter = grid.scrollHeight;
    var heightDiff = gridScrollHeightBefore - gridScrollHeightAfter;
    if (heightDiff > 0) {
        window.scrollTo(window.pageXOffset, scrollTopBefore - heightDiff);
    }

    paginatedRenderer.markPageRemoved(oldestPage);
}

/* ========== 无限滚动 ========== */

function _removeSentinel() {
    var old = document.getElementById('infinite-scroll-sentinel');
    if (old) {
        if (old._observer) old._observer.disconnect();
        old.remove();
    }
    if (window._globalScrollHandler) {
        window.removeEventListener('scroll', window._globalScrollHandler);
        window._globalScrollHandler = null;
    }
}

function _setupInfiniteScroll(container) {
    _removeSentinel();
    if (!paginatedRenderer.hasMore()) return;

    var sentinel = document.createElement('div');
    sentinel.id = 'infinite-scroll-sentinel';
    sentinel.setAttribute('aria-hidden', 'true');
    container.appendChild(sentinel);

    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            if (entries[0].isIntersecting) _loadNextPage(container);
        }, { rootMargin: '300px' });
        observer.observe(sentinel);
        sentinel._observer = observer;
    } else {
        window._globalScrollHandler = function() {
            if (window.innerHeight + window.pageYOffset >= document.documentElement.scrollHeight - 400) {
                _loadNextPage(container);
            }
        };
        window.addEventListener('scroll', window._globalScrollHandler);
    }
}

/**
 * 加载下一页（含DOM回收与loading指示器）
 */
function _loadNextPage(container) {
    if (!paginatedRenderer.nextPage()) {
        _removeSentinel();
        return;
    }

    // 显示 loading 指示器
    var loadingIndicator = document.getElementById('page-loading-indicator');
    if (loadingIndicator) loadingIndicator.style.display = 'flex';

    var currentPageIdx = paginatedRenderer.currentPage;
    var nextData = paginatedRenderer.getCurrentPageData();  // 仅当前页数据
    var grid = document.getElementById('sites-grid');
    if (!grid) {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        return;
    }

    // 创建当前页卡片（带动画类和data-page属性）
    var fragment = document.createDocumentFragment();
    nextData.forEach(function(site) {
        var card = document.createElement('a');
        card.className = 'site site-card animate-in';
        card.setAttribute('data-page', currentPageIdx);
        card.href = site.url || '#';
        card.setAttribute('aria-label', site.name || '');
        if (site.url) {
            try { new URL(site.url); card.target = '_blank'; card.rel = 'noopener noreferrer'; } catch(e) {}
        }

        var favicon = 'assets/images/favicon.png';
        if (site.url) {
            try { favicon = 'https://www.google.com/s2/favicons?domain=' + new URL(site.url).hostname + '&sz=32'; } catch(e) {}
        }

        var title = site.name || '';
        var desc = site.description || '';
        if (site._query) {
            title = SearchEngine ? SearchEngine.highlight(title, site._query) : title;
            desc = SearchEngine ? SearchEngine.highlight(desc, site._query) : desc;
        }

        card.innerHTML = '<img src="' + favicon + '" class="card-icon" loading="lazy" alt="" ' +
                          'onerror="this.onerror=null;this.src=\'assets/images/favicon.png\';">' +
                          '<span class="card-title">' + title + '</span>' +
                          '<span class="card-desc">' + desc + '</span>';
        fragment.appendChild(card);
    });

    grid.appendChild(fragment);
    paginatedRenderer.markPageRendered(currentPageIdx);
    bindCardEvents();

    // DOM回收：当渲染页面超过阈值时，移除最早的页面
    if (paginatedRenderer.needsRecycling()) {
        _recycleOldestPage(grid);
    }

    if (!paginatedRenderer.hasMore()) _removeSentinel();

    // 隐藏 loading 指示器
    if (loadingIndicator) loadingIndicator.style.display = 'none';

    // 仅对新加载的卡片执行入场动画
    setTimeout(function() {
        grid.querySelectorAll('.animate-in[data-page="' + currentPageIdx + '"]').forEach(function(card) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(10px)';
            card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            requestAnimationFrame(function() {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            });
        });
    }, 30);
}

/**
 * 绑定卡片点击事件
 */
function bindCardEvents() {
    try {
        var main = document.getElementById('main-content');
        if (!main) return;

        // 事件委托：一次性绑定，处理所有卡片收藏点击
        main.addEventListener('click', function(e) {
            var btn = e.target.closest('[data-action="toggle-favorite"]');
            if (!btn) return;

            e.preventDefault();
            e.stopPropagation();

            var card = btn.closest('.site-card');
            if (!card) return;

            // 通过 data-site-id 从 dataManager 获取完整 site 对象
            var siteId = parseInt(card.getAttribute('data-site-id'), 10);
            var site = null;
            if (window.dataManager && typeof window.dataManager.getSite === 'function') {
                site = window.dataManager.getSite(siteId);
            }

            if (!site) {
                console.warn('[CardEvents] 无法获取站点数据 id:', siteId);
                return;
            }

            // 调用 toggle
            if (window.favoriteManager && typeof window.favoriteManager.toggle === 'function') {
                var result = window.favoriteManager.toggle(site);
                if (result && result.success) {
                    // 实时更新按钮状态
                    var isFav = window.favoriteManager.isFavorite(site.name);
                    btn.textContent = isFav ? '♥' : '♡';
                    btn.classList.toggle('favorited', isFav);
                    // 更新收藏计数
                    if (window.favoriteUI && typeof window.favoriteUI.updateCount === 'function') {
                        window.favoriteUI.updateCount();
                    }
                    // 可选：toast 提示
                    if (window.Toast && typeof window.Toast.show === 'function') {
                        window.Toast.show(isFav ? '已添加到收藏' : '已取消收藏', isFav ? 'success' : 'info');
                    }
                }
            } else {
                console.warn('[CardEvents] favoriteManager 不可用');
            }
        });

        // 标记绑定完成
        var cards = document.querySelectorAll('.site-card');
        cards.forEach(function(card) { card._eventsBound = true; });

    } catch(e) {
        console.error('[CardEvents] 绑定失败:', e);
    }
}


/**
 * 绑定标签筛选器事件
 */


/**
 * 绑定标签筛选器事件（简化版 - 避免 state 递归）
 */
function _bindTagFilters() {
    var bar = document.querySelector('.tag-filter-bar');
    if (!bar) return;

    bar.querySelectorAll('.tag-suggest, .tag-active-filter').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var tag = this.getAttribute('data-tag');
            // 视觉切换：由完整标签系统（state.toggleTag + renderTagCloud）负责实际筛选
            if (this.classList.contains('tag-suggest')) {
                this.classList.remove('tag-suggest');
                this.classList.add('tag-active-filter');
                this.innerHTML = tag + ' ×';
            } else {
                this.classList.remove('tag-active-filter');
                this.classList.add('tag-suggest');
                this.innerHTML = '+' + tag + '(' + (this.dataset.count || '') + ')';
            }
        });
    });
}


/**
 * 导出渲染器桥接对象，供 app.js 使用
 */
window.renderer = {
    renderSidebar: renderSidebar,
    renderView: renderView,
    renderCategoryView: renderCategoryView,
    renderSites: renderSites
};


/**
 * 渲染侧边栏激活状态（根据 state 更新 DOM class）
 * @param {Object} s - 当前状态对象
 */
function renderSidebar(s) {
    try {
        var activeCat = s.sidebar.activeCategoryId;
        var activeSub = s.sidebar.activeSubCategoryId;
        var activeLeaf = s.sidebar.activeLeafId;

        // 移除所有激活状态
        document.querySelectorAll('.nav-item.active, .nav-sub-item.active, .nav-leaf-item.active')
            .forEach(el => el.classList.remove('active'));

        if (!activeCat) return;

        // 激活顶级分类
        var catEl = document.querySelector('.nav-item[data-category="' + activeCat + '"]');
        if (catEl) catEl.classList.add('active');

        // 激活子分类（如果有）
        if (activeSub) {
            var subEl = document.querySelector('.nav-sub-item[data-sub="' + activeSub + '"]');
            if (subEl) subEl.classList.add('active');
        }

        // 激活叶子分类（如果有）
        if (activeLeaf && activeLeaf !== activeSub) {
            var leafEl = document.querySelector('.nav-leaf-item[data-leaf="' + activeLeaf + '"]');
            if (leafEl) leafEl.classList.add('active');
        }
    } catch(e) {
        // // console.log('[Render] renderSidebar error:', e.message);
    }
}

/**
 * 渲染主视图（状态驱动的视图路由）
 * @param {Object} s - 当前状态对象
 */
function renderView(s) {
    try {
        var currentView = s.currentView;
        var isSearch = s.searchMode || currentView === 'search';

        if (isSearch) {
            var query = s.search.query;
            var results = s.search.results;
            if (query && results && results.length > 0) {
                _renderSearchResults(results, query);
            } else if (query) {
                var container = document.getElementById('main-content');
                if (container) container.innerHTML = StateUI.searchEmpty(query);
            }
            return;
        }

        // 分类视图
        // 视图模式：网格 / 列表
        var view = s.currentView;
        if (view === 'grid' || view === 'list') {
            var sites = state.get('sites') || [];
            var renderFn = view === 'grid' ? renderSites : renderSitesList;
            renderFn(sites, 'main-content');
            return;
        // 游戏大厅视图
        if (view === 'games') {
            // 解析 hash: #game=<key> 启动游戏，否则显示大厅
            var gameHash = location.hash.match(/game=([a-z0-9]+)/);
            if (gameHash && window.GameHub) {
                var gameKey = gameHash[1];
                // 渲染游戏容器（全屏覆盖）
                GameHub.renderContainer();
                // 异步启动游戏
                setTimeout(function() { GameHub.startGame(gameKey); }, 50);
            } else {
                renderGamesHub('main-content');
            }
            return;
        }
        }


        var activeCat = s.sidebar.activeCategoryId;
        var activeSub = s.sidebar.activeSubCategoryId;
        var activeLeaf = s.sidebar.activeLeafId;

        if (activeCat) {
            renderCategoryView(activeCat, activeSub, activeLeaf);
        } else if (window.dataManager && window.dataManager.isLoaded) {
            var allSites = window.dataManager.raw || [];
            renderSites(allSites);
        }
    } catch(e) {
        // // console.log('[Render] renderView error:', e.message);
    }
}