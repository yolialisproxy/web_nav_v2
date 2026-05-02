/**
 * render.js - 渲染引擎
 * 职责：DOM 渲染、状态UI输出
 */

// 状态UI 渲染器
const StateUI = {
    loading() {
        return `
            <div class="state-container state-loading">
                <div class="loading-spinner"></div>
                <div class="state-title">正在加载站点数据<span class="loading-dots"></span></div>
                <div class="state-desc">首次加载可能需要几秒钟时间，请稍候</div>
            </div>
        `;
    },

    error(message = '\u52a0\u8f7d\u6570\u636e\u5931\u8d25', retryCallback = null) {
        const button = retryCallback ?
            `<div class="state-action">
                <button class="state-button" onclick="(${retryCallback.toString()})()">重\u8bd5\u52a0\u8f7d</button>
            </div>` : '';

        return `
            <div class="state-container state-error">
                <div class="state-icon">⚠️</div>
                <div class="state-title">嗅嗅，出问题了</div>
                <div class="state-desc">${message}</div>
                ${button}
            </div>
        `;
    },

    empty(message = '\u8be5\u5206\u7c7b\u4e0b\u8fd8\u6ca1\u6709\u7ad9\u70b9') {
        return `
            <div class="state-container state-empty">
                <div class="state-icon">📦</div>
                <div class="state-title">暂\u65e0\u5185\u5bb9</div>
                <div class="state-desc">${message}</div>
            </div>
        `;
    },

    searchEmpty(query) {
        return `
            <div class="state-container state-empty">
                <div class="state-icon">🔍</div>
                <div class="state-title">未找\u5230\u5339\u914d\u7684\u7ad9\u70b9</div>
                <div class="state-desc">没\u6709\u627e\u5230\u4e0e "${query}" \u76f8\u5173\u7684\u7ad9\u70b9\uff0c\u8bf7\u5c1d\u8bd5\u5176\u4ed6\u5173\u952e\u8bcd</div>
            </div>
        `;
    }
};

window.StateUI = StateUI;

// 核\u5fc3\u6e32\u67d3\u51fd\u6570：渲\u67d3\u7ad9\u70b9\u5217\u8868
function renderSites(sites, containerId = 'main-content') {
    const container = document.getElementById(containerId);

    if (!container) return;

    if (sites === null || sites === undefined) {
        container.innerHTML = StateUI.loading();
        return;
    }

    if (sites === false) {
        container.innerHTML = StateUI.error('\u65e0\u6cd5\u52a0\u8f7d\u7ad9\u70b9\u6570\u636e\uff0c\u8bf7\u68c0\u67e5\u7f51\u7edc\u8fde\u63a5\u540e\u91cd\u8bd5', window.loadData);
        return;
    }

    if (Array.isArray(sites) && sites.length === 0) {
        container.innerHTML = StateUI.empty();
        return;
    }

    // 正\u5e38\u6e32\u67d3\u7ad9\u70b9\u5217\u8868
    let html = '<div class="grid">';
    sites.forEach(site => {
        // 安\u5168\u751f\u6210\u94fe\u63a5 - 处\u7406\u65e0\u6548URL
        let linkUrl = '#';
        let linkTarget = '';
        let relAttr = '';
        if (site.url) {
            try {
                new URL(site.url); // 验\u8bc1URL\u662f\u5426\u6709\u6548
                linkUrl = site.url;
                linkTarget = 'target="_blank"';
                relAttr = 'rel="noopener"';
            } catch (e) {
                linkUrl = '#';
            }
        }
        html += `
            <a href="${linkUrl}" class="site" ${linkTarget} ${relAttr} data-title="${site.title || ''}">
                <strong>${site.title || 'Untitled'}</strong>
                <span>${site.description || site.url || ''}</span>
            </a>
        `;
    });
    html += '</div>';

    container.innerHTML = html;
}

window.renderSites = renderSites;

/**
 * 规\u8303：Menu_System.md, Haptic_Feel.md, Technical_Architecture.md
 */

class Renderer {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.container = document.getElementById('main-content');
    }

    renderSidebar(state) {
        const categories = dataManager.categories;
        let html = '';

        Object.entries(categories).forEach(([catId, cat]) => {
            const isCatActive = state.sidebar.activeCategoryId === catId;

            html += `
                <div class="menu-group">
                    <div class="menu-category ${isCatActive ? 'active' : ''}" data-cat-id="${catId}">
                        <div class="category-header">${cat.name}</div>
                        <div class="category-content" style="display: ${isCatActive ? 'block' : 'none'}">
                            ${this._renderSubCategories(cat, state)}
                        </div>
                    </div>
                </div>
            `;
        });

        this.sidebar.innerHTML = html;
        this._bindSidebarEvents();
    }

    _renderSubCategories(cat, state) {
        let html = '';
        Object.entries(cat.subCategories || {}).forEach(([subId, sub]) => {
            const isSubExpanded = state.sidebar.activeSubCategoryId === subId;

            html += `
                <div class="menu-subcategory ${isSubExpanded ? 'expanded' : ''}" data-sub-id="${subId}">
                    <div class="subcategory-header">
                        <svg class="subcategory-arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"></path></svg>
                        ${sub.name}
                    </div>
                    <div class="subcategory-content" style="display: ${isSubExpanded ? 'block' : 'none'}">
                        ${this._renderLeafCategories(sub, state)}
                    </div>
                </div>
            `;
        });
        return html;
    }

    _renderLeafCategories(sub, state) {
        let html = '';
        Object.entries(sub.leafCategories || {}).forEach(([leafId, leaf]) => {
            const isLeafActive = state.sidebar.activeLeafId === leafId;
            html += `
                <a href="#" class="menu-leaf ${isLeafActive ? 'active' : ''}" data-leaf-id="${leafId}">
                    ${leaf.name}
                </a>
            `;
        });
        return html;
    }

    renderView(state) {
        if (state.currentView === 'category') {
            const leafId = state.sidebar.activeLeafId;
            const catId = state.sidebar.activeCategoryId;
            const subId = state.sidebar.activeSubCategoryId;

            if (!leafId || !catId) {
                this.container.innerHTML = this._getEmptyState();
                return;
            }

            // 构\u5efa\u5b8c\u6574\u4e09\u7ea7\u5206\u7c7b\u8def\u5f84\u7528\u4e8e\u67e5\u8be2
            const fullLeafId = subId && leafId !== subId ? `${catId}/${subId}/${leafId}` : `${catId}/${leafId}`;
            const sites = dataManager.getSitesByLeafId(fullLeafId);
            if (sites.length === 0) {
                this.container.innerHTML = this._getEmptyState('\u8be5\u5206\u7c7b\u6682\u65e0\u5185\u5bb9');
                return;
            }

            this.container.innerHTML = this._createCardGridHtml(sites);
            this._bindCardEvents();
        } else if (state.currentView === 'search') {
            this._renderSearchResults(state);
        }
    }

    // 卡\u7247\u89c6\u56fe - \u5e26\u641c\u7d22\u9ad8\u4eae
    _createCardGridHtml(sites) {
        let html = '<div class="card-grid">';
        sites.forEach(site => {
            html += this._createCardHtml(site);
        });
        html += '</div>';
        return html;
    }

    _createCardHtml(site) {
        // 检\u6d4b\u662f\u5426\u4e3a\u641c\u7d22\u7ed3\u679c\u5e76\u5e94\u7528\u9ad8\u4eae
        const query = site._query;
        const name = query && SearchEngine.highlight
            ? SearchEngine.highlight(site.title, query)
            : site.title;
        const desc = query && SearchEngine.highlight
            ? SearchEngine.highlight(site.description, query)
            : site.description;

        // 安\u5168\u83b7\u53d6favicon domain
        let faviconDomain = '';
        if (site.url) {
            try {
                const urlObj = new URL(site.url);
                faviconDomain = urlObj.hostname;
            } catch (e) {
                // URL\u65e0\u6548\u65f6\u4f7f\u7528\u9ed8\u8ba4\u56fe\u6807
                faviconDomain = '';
            }
        }
        const faviconSrc = faviconDomain
            ? `https://www.google.com/s2/favicons?domain=${faviconDomain}&sz=32`
            : 'assets/images/favicon.png';

        return `
            <a href="${site.url || '#'}" target="_blank" class="site site-card" data-id="${site.id}">
                <img src="${faviconSrc}" class="card-icon" onerror="this.onerror=null;this.src='assets/images/favicon.png';">
                <span class="card-title">${name}</span>
                <span class="card-desc">${desc}</span>
            </a>
        `;
    }

    _getEmptyState(msg = '\u8bf7\u9009\u62e9\u4e00\u4e2a\u5206\u7c7b\u5f00\u59cb\u6d4f\u89c8') {
        return `
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--color-text-dim); text-align:center; opacity:0.6">
                <div style="font-size:48px; margin-bottom:16px">📁</div>
                <p>${msg}</p>
            </div>
        `;
    }

    _renderSearchResults(state) {
        const results = state.search.results;
        if (results.length === 0) {
            this.container.innerHTML = StateUI.searchEmpty(state.search.query);
            return;
        }
        this.container.innerHTML = this._createCardGridHtml(results);
        this._bindCardEvents();
    }

    _bindSidebarEvents() {
        this.sidebar.querySelectorAll('.menu-category').forEach(el => {
            el.addEventListener('click', (e) => {
                e.stopPropagation();
                const catId = el.dataset.catId;
                state.set('sidebar.activeCategoryId', catId);
                // 点\u51fb\u5927\u7c7b\u65f6\u6e05\u9664\u641c\u7d22
                state.set('search.active', false);
                state.set('currentView', 'category');
                state.set('search.query', '');

                // Don't auto-expand subcategory - let user click to expand
            });
        });

        this.sidebar.querySelectorAll('.menu-subcategory').forEach(el => {
            el.addEventListener('click', (e) => {
                e.stopPropagation();
                const subId = el.dataset.subId;
                const isExpanded = state.get('sidebar.activeSubCategoryId') === subId;
                state.set('sidebar.activeSubCategoryId', isExpanded ? null : subId);
            });
        });

        this.sidebar.querySelectorAll('.menu-leaf').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                state.set('sidebar.activeLeafId', el.dataset.leafId);
                // 点\u51fb\u53f6\u5b50\u65f6\u5207\u56de\u5206\u7c7b\u89c6\u56fe
                state.set('currentView', 'category');
                state.set('search.active', false);
            });
        });
    }

    _bindCardEvents() {
        this.container.querySelectorAll('.site-card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left - rect.width / 2) * 0.05;
                const y = (e.clientY - rect.top - rect.height / 2) * 0.05;
                card.style.transform = `translate(${x}px, ${y}px) scale(1.02)`;
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = `translate(0, 0) scale(1)`;
            });
        });
    }
}

const renderer = new Renderer();
window.renderer = renderer;

