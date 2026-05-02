/**
 * render.js - 渲染引擎
 * 职责：DOM 渲染、状态UI输出
 */

const StateUI = {
    loading() {
        return '<div class="state-container state-loading"><div class="loading-spinner"></div><div class="state-title">正在加载<span class="loading-dots"></span></div></div>';
    },
    error(msg) {
        return '<div class="state-container state-error"><div class="state-icon">⚠️</div><div class="state-title">加载失败</div><div class="state-desc">' + msg + '</div></div>';
    },
    empty(msg) {
        return '<div class="state-container state-empty"><div class="state-icon">📁</div><div class="state-title">暂无内容</div><div class="state-desc">' + msg + '</div></div>';
    },
    searchEmpty(q) {
        return '<div class="state-container state-empty"><div class="state-icon">🔍</div><div class="state-title">未找到匹配</div><div class="state-desc">未找到与 "' + q + '" 相关内容</div></div>';
    }
};

window.StateUI = StateUI;

function renderSites(sites, containerId) {
    var cid = containerId || 'main-content';
    var container = document.getElementById(cid);
    if (!container) return;
    if (sites === null || sites === undefined) {
        container.innerHTML = StateUI.loading();
        return;
    }
    if (sites === false) {
        container.innerHTML = StateUI.error('无法加载数据');
        return;
    }
    if (Array.isArray(sites) && sites.length === 0) {
        container.innerHTML = StateUI.empty();
        return;
    }
    var html = '<div class="grid">';
    sites.forEach(function(site) {
        var url = '#';
        var target = '';
        var rel = '';
        if (site.url) {
            try {
                new URL(site.url);
                url = site.url;
                target = 'target="_blank"';
                rel = 'rel="noopener"';
            } catch(e) {}
        }
        var favicon = 'assets/images/favicon.png';
        if (site.url) {
            try {
                var hn = new URL(site.url).hostname;
                favicon = 'https://www.google.com/s2/favicons?domain=' + hn + '&sz=32';
            } catch(e) {}
        }
        var title = site.title || '';
        var desc = site.description || '';
        html += '<a href="' + url + '" class="site site-card" ' + target + ' ' + rel + '>' +
            '<img src="' + favicon + '" class="card-icon" onerror="this.onerror=null;this.src=\'assets/images/favicon.png\';">' +
            '<span class="card-title">' + title + '</span>' +
            '<span class="card-desc">' + desc + '</span>' +
            '</a>';
    });
    html += '</div>';
    container.innerHTML = html;
    bindCardEvents();
}

window.renderSites = renderSites;

class Renderer {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarContent = document.getElementById('sidebar-content');
        this.container = document.getElementById('main-content');
    }

    renderSidebar(s) {
        var cats = s.sidebar.activeCategoryId;
        var h = '';
        var _this = this;
        Object.entries(dataManager.categories).forEach(function(_ref) {
            var cid = _ref[0];
            var c = _ref[1];
            var act = cats === cid;
            var subsHtml = _this._subs(c, s);
            h += '<div class="menu-group"><div class="menu-category ' + (act ? 'active' : '') + '" data-cat-id="' + cid + '">' +
                '<div class="category-header">' + c.name + '</div>' +
                '<div class="category-content" style="display:' + (act ? 'block' : 'none') + '">' + subsHtml + '</div>' +
                '</div></div>';
        });
        this.sidebarContent.innerHTML = h;
        this._bindSidebar();
    }

    _subs(cat, s) {
        var h = '';
        var activeSub = s.sidebar.activeSubCategoryId;
        var _this2 = this;
        Object.entries(cat.subCategories || {}).forEach(function(_ref2) {
            var sid = _ref2[0];
            var sub = _ref2[1];
            var exp = activeSub === sid;
            var leavesHtml = _this2._leaves(sub, s);
            h += '<div class="menu-subcategory ' + (exp ? 'expanded' : '') + '" data-sub-id="' + sid + '">' +
                '<div class="subcategory-header"><svg class="subcategory-arrow" viewBox="0 0 24 24" stroke-width="2"><path d="M9 5l7 7-7 7"/></svg>' + sub.name + '</div>' +
                '<div class="subcategory-content" style="display:' + (exp ? 'block' : 'none') + '">' + leavesHtml + '</div>' +
                '</div>';
        });
        return h;
    }

    _leaves(sub, s) {
        var h = '';
        var activeLeaf = s.sidebar.activeLeafId;
        Object.entries(sub.leafCategories || {}).forEach(function(_ref3) {
            var lid = _ref3[0];
            var leaf = _ref3[1];
            h += '<a href="#" class="menu-leaf ' + (activeLeaf === lid ? 'active' : '') + '" data-leaf-id="' + lid + '">' + leaf.name + '</a>';
        });
        return h;
    }

    renderView(s) {
        if (s.currentView === 'category') {
            var lid = s.sidebar.activeLeafId;
            var cid = s.sidebar.activeCategoryId;
            var sid = s.sidebar.activeSubCategoryId;
            if (!lid || !cid) {
                this.container.innerHTML = this._empty();
                return;
            }
            var fullId = sid && lid !== sid ? cid + '/' + sid + '/' + lid : cid + '/' + lid;
            var sites = dataManager.getSitesByLeafId(fullId);
            this.container.innerHTML = sites.length ? this._cards(sites) : this._empty('暂无内容');
        } else if (s.currentView === 'search') {
            this._searchResults(s);
        }
    }

    _cards(sites) {
        var h = '<div class="grid">';
        sites.forEach(function(site) {
            var url = '#';
            var fav = 'assets/images/favicon.png';
            if (site.url) {
                try {
                    new URL(site.url);
                    url = site.url;
                } catch(e) {}
                try {
                    var hn = new URL(site.url).hostname;
                    fav = 'https://www.google.com/s2/favicons?domain=' + hn + '&sz=32';
                } catch(e) {}
            }
            var title = site.title || '';
            var desc = site.description || '';
            h += '<a href="' + url + '" target="_blank" class="site site-card" rel="noopener">' +
                '<img src="' + fav + '" class="card-icon" onerror="this.src=\'assets/images/favicon.png\'">' +
                '<span class="card-title">' + title + '</span>' +
                '<span class="card-desc">' + desc + '</span>' +
                '</a>';
        });
        return h + '</div>';
    }

    _empty(msg) {
        if (msg === void 0) msg = '请选择一个分类';
        return '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:var(--color-text-dim);text-align:center;opacity:.6">' +
            '<div style="font-size:48px;margin-bottom:16px">📁</div><p>' + msg + '</p></div>';
    }

    _searchResults(s) {
        this.container.innerHTML = s.search.results.length ? this._cards(s.search.results) : StateUI.searchEmpty(s.search.query);
    }

    _bindSidebar() {
        var _this3 = this;
        this.sidebarContent.querySelectorAll('.menu-category').forEach(function(el) {
            el.addEventListener('click', function(e) {
                e.stopPropagation();
                var cid = el.dataset.catId;
                state.set('sidebar.activeCategoryId', cid);
                var cat = dataManager.categories[cid];
                if (cat) {
                    var subs = Object.keys(cat.subCategories || {});
                    if (subs[0]) {
                        state.set('sidebar.activeSubCategoryId', subs[0]);
                        var leaves = Object.keys(cat.subCategories[subs[0]].leafCategories || {});
                        if (leaves[0]) state.set('sidebar.activeLeafId', leaves[0]);
                    }
                }
                state.set('currentView', 'category');
                state.set('search.active', false);
            });
        });
        this.sidebarContent.querySelectorAll('.menu-subcategory').forEach(function(el) {
            el.addEventListener('click', function(e) {
                e.stopPropagation();
                var sid = el.dataset.subId;
                var exp = state.get('sidebar.activeSubCategoryId') === sid;
                state.set('sidebar.activeSubCategoryId', exp ? null : sid);
            });
        });
        this.sidebarContent.querySelectorAll('.menu-leaf').forEach(function(el) {
            el.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                state.set('sidebar.activeLeafId', el.dataset.leafId);
                state.set('currentView', 'category');
                state.set('search.active', false);
            });
        });
    }
}

var renderer = new Renderer();
window.renderer = renderer;

function bindCardEvents() {
    document.querySelectorAll('.site-card').forEach(function(card) {
        card.addEventListener('mousemove', function(e) {
            var r = card.getBoundingClientRect();
            var x = (e.clientX - r.left - r.width / 2) * 0.05;
            var y = (e.clientY - r.top - r.height / 2) * 0.05;
            card.style.transform = 'translate(' + x + 'px,' + y + 'px) scale(1.02)';
        });
        card.addEventListener('mouseleave', function() {
            card.style.transform = 'translate(0,0) scale(1)';
        });
    });
}

window.bindCardEvents = bindCardEvents;
