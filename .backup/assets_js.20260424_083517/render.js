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
                <div class="state-desc">首次加载可能需要几秒时间，请稍候</div>
            </div>
        `;
    },

    error(message = '加载数据失败', retryCallback = null) {
        const button = retryCallback ?
            `<div class="state-action">
                <button class="state-button" onclick="(${retryCallback.toString()})()">重试加载</button>
            </div>` : '';

        return `
            <div class="state-container state-error">
                <div class="state-icon">⚠️</div>
                <div class="state-title">哎呀，出问题了</div>
                <div class="state-desc">${message}</div>
                ${button}
            </div>
        `;
    },

    empty(message = '该分类下还没有站点') {
        return `
            <div class="state-container state-empty">
                <div class="state-icon">📭</div>
                <div class="state-title">暂无内容</div>
                <div class="state-desc">${message}</div>
            </div>
        `;
    },

    searchEmpty(query) {
        return `
            <div class="state-container state-empty">
                <div class="state-icon">🔍</div>
                <div class="state-title">未找到匹配的网站</div>
                <div class="state-desc">没有找到与 "${query}" 相关的站点，请尝试其他关键词</div>
            </div>
        `;
    }
};

window.StateUI = StateUI;

function renderSites(sites, containerId = 'view-container') {
    const container = document.getElementById(containerId);

    if (!container) return;

    if (sites === null || sites === undefined) {
        container.innerHTML = StateUI.loading();
        return;
    }

    if (sites === false) {
        container.innerHTML = StateUI.error('无法加载站点数据，请检查网络连接后重试', window.loadData);
        return;
    }

    if (Array.isArray(sites) && sites.length === 0) {
        container.innerHTML = StateUI.empty();
        return;
    }

    // 正常渲染站点列表
    let html = '<div class="grid">';
    sites.forEach(site => {
        html += `
            <a href="${site.url}" class="site" target="_blank" rel="noopener" data-title="${site.title}">
                <strong>${site.title}</strong>
                <span>${site.description || site.url}</span>
            </a>
        `;
    });
    html += '</div>';

    container.innerHTML = html;
}

window.renderSites = renderSites;

/**
 * 规范：Menu_System.md, Haptic_Feel.md, Technical_Architecture.md
 */

class Renderer {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.container = document.getElementById('view-container');
        this.topNav = document.getElementById('top-nav');
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
                        <span class="subcategory-arrow">▶</span>
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
            if (!leafId) {
                this.container.innerHTML = this._getEmptyState();
                return;
            }

            const sites = dataManager.getSitesByLeafId(leafId);
            if (sites.length === 0) {
                this.container.innerHTML = this._getEmptyState('该分类暂无内容');
                return;
            }

            this.container.innerHTML = `
                <div class="card-grid">
                    ${sites.map(site => this._createCardHtml(site)).join('')}
                </div>
            `;
            this._bindCardEvents();
        } else if (state.currentView === 'search') {
            this._renderSearchResults(state);
        }
    }

    _createCardHtml(site) {
        // 检测是否为搜索结果并应用高亮
        const query = site._query;
        const name = query ? SearchEngine.highlight(site.name, query) : site.name;
        const desc = query ? SearchEngine.highlight(site.desc, query) : site.desc;

        return `
            <a href="${site.url}" target="_blank" class="site-card" data-id="${site.id}">
                <img src="${site.icon}" class="card-icon" onerror="if(!this.dataset.error) {this.dataset.error='1'; this.src='assets/images/favicon.png'; this.onerror=null;}">
                <span class="card-title">${name}</span>
                <span class="card-desc">${desc}</span>
            </a>
        `;
    }

    _getEmptyState(msg = '请选择一个分类开始浏览') {
        return `
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--color-text-dim); text-align:center; opacity:0.6">
                <div style="font-size:48px; margin-bottom:16px">📂</div>
                <p>${msg}</p>
            </div>
        `;
    }

    _renderSearchResults(state) {
        const results = state.search.results;
        if (results.length === 0) {
            this.container.innerHTML = this._getEmptyState('未找到匹配结果');
            return;
        }
        this.container.innerHTML = `
            <div class="card-grid">
                ${results.map(site => this._createCardHtml(site)).join('')}
            </div>
        `;
        this._bindCardEvents();
    }

    _bindSidebarEvents() {
        this.sidebar.querySelectorAll('.menu-category').forEach(el => {
            el.addEventListener('click', (e) => {
                e.stopPropagation();
                const catId = el.dataset.catId;
                state.set('sidebar.activeCategoryId', catId);

                const firstSub = el.querySelector('.menu-subcategory');
                if (firstSub) {
                    state.set('sidebar.activeSubCategoryId', firstSub.dataset.subId);
                    const firstLeaf = firstSub.querySelector('.menu-leaf');
                    if (firstLeaf) {
                        state.set('sidebar.activeLeafId', firstLeaf.dataset.leafId);
                    }
                }
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
