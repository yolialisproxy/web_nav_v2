/**
 * render.js - DOM 渲染引擎
 * 职责：将 State 和 Data 转换为 DOM
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
        return `
            <a href="${site.url}" target="_blank" class="site-card" data-id="${site.id}">
                <img src="${site.icon}" class="card-icon" onerror="this.src='https://via.placeholder.com/32'">
                <span class="card-title">${site.name}</span>
                <span class="card-desc">${site.desc}</span>
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
