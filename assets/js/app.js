/**
 * app.js - 应用入口与路由调度 (V3)
 * 职责：初始化、事件调度、SPA路由、键盘快捷键
 * 修复：统一所有功能到一个入口点
 */

/**
 * 主题切换功能 (暗色/亮色/系统自动)
 */
function initThemeToggle() {
    const toggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    if (!toggleBtn || !themeIcon) {
        console.warn('[Theme] 主题切换按钮缺失');
        return;
    }
    
    // 更新按钮图标
    function updateThemeIcon(theme) {
        const displayTheme = theme === 'system' ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : theme;
        if (displayTheme === 'dark') {
            // 月亮图标
            themeIcon.setAttribute('d', 'M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z');
        } else {
            // 太阳图标
            themeIcon.setAttribute('d', 'M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zM9 7a1 1 0 011 1v1a1 1 0 11-2 0V8a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0V8a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0V8a1 1 0 011-1zM5 11a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm-8 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5 19a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1z');
        }
        toggleBtn.setAttribute('title', displayTheme === 'dark' ? '切换到亮色模式' : '切换到暗色模式');
    }
    
    // 初始更新
    updateThemeIcon(state.get('theme'));
    
    // 监听状态变化
    state.subscribe(function(s) {
        if (s.theme) {
            updateThemeIcon(s.theme);
        }
    });
    
    // 绑定点击事件
    toggleBtn.addEventListener('click', function() {
        const currentTheme = state.get('theme');
        let newTheme;
        if (currentTheme === 'light') {
            newTheme = 'dark';
        } else if (currentTheme === 'dark') {
            newTheme = 'system';
        } else {
            newTheme = 'light';
        }
        state.set('theme', newTheme);
    });
}


async function init() {
    // 暴露全局函数
    window.renderSites = renderSites;

    // 骨架屏已经在HTML中默认显示，无需额外设置
    // 只需确保state.loading为true
    if (state) state.set('loading', true);

    // 加载数据（带缓存降级）
    let dataLoaded = false;
    try {
        await dataManager.load();
        dataLoaded = true;
    } catch (e) {
        console.error('[App] 数据加载失败:', e);
        // 尝试从缓存恢复
        try {
            const cached = dataManager._loadCache();
            if (cached && cached.length > 0) {
                // // // console.log('[App] 从缓存恢复数据:', cached.length, '条');
                dataManager.raw = cached;
                dataManager._buildIndexes();
                dataManager.isLoaded = true;
                dataLoaded = true;
            }
        } catch(cacheErr) {
            console.error('[App] 缓存恢复也失败:', cacheErr);
        }

        if (!dataLoaded) {
            renderSites(false);
            return;
        }
    }

    // 初始化标签系统
    try {
        await initTagManager(dataManager);
        await tagManager.load();
        renderTagCloud('tag-cloud-container');
    } catch (e) {
        console.warn('[App] 标签系统初始化失败:', e);
    }

    // 搜索引擎初始化（后台任务）
    try { initSearchEngine(dataManager); } catch(e) { console.warn('[App] 搜索初始化失败:', e.message); }
    // 初始化主题切换
    initThemeToggle();


    // 初始化收藏
    if (window.favoriteManager) {
        try {
            window.favoriteUI.updateCount();
        } catch(e) {
            console.warn('[App] 收藏计数初始化失败:', e);
        }
    }

    // 初始化盈利模块
    Monetization.init({ enabled: true });

    // Toast通知
    Toast.init && Toast.init();

    // 状态订阅 - 驱动UI渲染
    state.subscribe(function(s) {
        try { renderer.renderSidebar(s); } catch(e) { console.error('[APP] Sidebar error:', e); }
        try { renderer.renderView(s); } catch(e) { console.error('[APP] View error:', e); }
        syncStateToHash(s);
    });

    // URL hash 路由
    window.addEventListener('hashchange', function() {
        syncHashToState();
    });

    // 初始路由
    var categories = Object.entries(dataManager.categories);
    var hashLoaded = syncHashToState();

    if (!hashLoaded && categories.length > 0) {
        var firstCatId = categories[0][0];
        state.set('sidebar.activeCategoryId', firstCatId);

        var firstCat = dataManager.categories[firstCatId];
        if (firstCat) {
            var subCats = firstCat.subCategories;
            if (subCats) {
                var firstSubId = Object.keys(subCats)[0];
                if (firstSubId) {
                    state.set('sidebar.activeSubCategoryId', firstSubId);
                    var subCat = subCats[firstSubId];
                    if (subCat && subCat.leafCategories) {
                        var leafIds = Object.keys(subCat.leafCategories);
                        if (leafIds[0]) state.set('sidebar.activeLeafId', leafIds[0]);
                    }
                }
            }
        }
    }

    // ===== 搜索功能（顶栏输入框） =====
    var searchInput = document.getElementById('search-input');
    var searchClear = document.getElementById('search-clear');
    var searchSuggestions = document.getElementById('search-suggestions');

    if (searchInput) {
        var searchDebounceTimer = null;

        searchInput.addEventListener('input', function(e) {
            var query = e.target.value.trim();
            state.set('search.query', query);

            if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
            searchDebounceTimer = setTimeout(function() {
                if (!window.searchEngine) return;

                if (query.length > 0) {
                    var suggestions = searchEngine.suggest(query);
                    renderSearchSuggestions(suggestions, query);

                    var results = searchEngine.query(query);
                    state.set('search.results', results);
                    state.set('search.active', true);
                    state.set('currentView', 'search');
                } else {
                    hideSearchSuggestions();
                    state.set('search.active', false);
                    state.set('search.results', []);
                    state.set('currentView', 'category');
                }
            }, 150);
        });

        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                hideSearchSuggestions();
                toggleSearch();
            }
            if (e.key === 'Enter') {
                e.preventDefault();
                hideSearchSuggestions();
            }
        });

        searchInput.addEventListener('focus', function() {
            if (searchInput.value.length > 0) {
                showSearchSuggestions();
            }
        });

        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-container')) {
                hideSearchSuggestions();
            }
        });

        if (searchClear) {
            searchInput.addEventListener('input', function() {
                searchClear.classList.toggle('hidden', searchInput.value.length === 0);
            });
            searchClear.addEventListener('click', function() {
                searchInput.value = '';
                searchClear.classList.add('hidden');
                searchInput.focus();
                hideSearchSuggestions();
                state.set('search.query', '');
                state.set('search.results', []);
                state.set('search.active', false);
                state.set('currentView', 'category');
            });
        }
    }

    // ===== 侧边栏切换 =====
    var sidebarToggle = document.getElementById('sidebar-toggle');
    var sidebar = document.getElementById('sidebar');
    var sidebarOverlay = document.getElementById('sidebar-overlay');

    function closeSidebar() {
        if (sidebar) sidebar.classList.add('-translate-x-full');
        if (sidebarOverlay) {
            sidebarOverlay.classList.add('hidden');
            sidebarOverlay.classList.remove('visible');
            sidebarOverlay.setAttribute('aria-hidden', 'true');
        }
        document.body.classList.remove('sidebar-open');
        if (sidebarToggle) sidebarToggle.setAttribute('aria-expanded', 'false');
    }

    function openSidebar() {
        if (sidebar) sidebar.classList.remove('-translate-x-full');
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove('hidden');
            sidebarOverlay.classList.add('visible');
            sidebarOverlay.setAttribute('aria-hidden', 'false');
        }
        document.body.classList.add('sidebar-open');
        if (sidebarToggle) sidebarToggle.setAttribute('aria-expanded', 'true');
    }

    if (sidebarToggle && sidebar && sidebarOverlay) {
        sidebarToggle.addEventListener('click', function() {
            var isOpen = !sidebar.classList.contains('-translate-x-full');
            if (isOpen) closeSidebar(); else openSidebar();
        });
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // ===== 侧边栏导航点击（事件委托） =====
    var sidebarContent = document.getElementById('sidebar-content');
    if (sidebarContent) {
        sidebarContent.addEventListener('click', function(e) {
            var navItem = e.target.closest('.nav-item[data-category]');
            if (navItem) {
                var cat = navItem.getAttribute('data-category');
                // 切换子分类展开/折叠
                var next = navItem.nextElementSibling;
                if (next && next.classList.contains('nav-children')) {
                    var isExpanded = next.style.display !== 'none';
                    // 折叠所有其他子菜单
                    sidebarContent.querySelectorAll('.nav-children').forEach(function(c) {
                        if (c !== next) c.style.display = 'none';
                    });
                    next.style.display = isExpanded ? 'none' : 'block';
                }
                if (cat) {
                    state.set('sidebar.activeCategoryId', cat);
                    state.set('sidebar.activeSubCategoryId', null);
                    state.set('sidebar.activeLeafId', null);
                    closeSidebar();
                }
                e.preventDefault();
                return;
            }

            var subItem = e.target.closest('.nav-sub-item[data-sub]');
            if (subItem) {
                var subCat = subItem.getAttribute('data-sub');
                var parentItem = subItem.closest('.nav-item');
                var mainCat = parentItem ? parentItem.getAttribute('data-category') : null;
                if (mainCat && subCat) {
                    state.set('sidebar.activeCategoryId', mainCat);
                    state.set('sidebar.activeSubCategoryId', subCat);
                    state.set('sidebar.activeLeafId', subCat);
                }
                closeSidebar();
                e.preventDefault();
            }
        });
    }

    // ===== 搜索覆盖层 =====
    var searchOverlay = document.getElementById('search-overlay');
    var searchOverlayInput = document.getElementById('search-overlay-input');
    var searchOverlayClear = document.getElementById('search-overlay-clear');

    function toggleSearch() {
        var active = state.get('search.active');
        state.set('search.active', !active);
        state.set('currentView', !active ? 'search' : 'category');

        if (searchOverlay) {
            if (!active) {
                searchOverlay.classList.remove('hidden');
                searchOverlay.setAttribute('aria-hidden', 'false');
                requestAnimationFrame(function() {
                    if (searchOverlayInput) {
                        searchOverlayInput.focus();
                        var query = state.get('search.query') || '';
                        searchOverlayInput.value = query;
                        if (window.searchEngine && query) {
                            var results = searchEngine.query(query);
                            state.set('search.results', results);
                            renderOverlaySearchResults(results, query);
                        }
                    }
                });
            } else {
                searchOverlay.classList.add('hidden');
                searchOverlay.setAttribute('aria-hidden', 'true');
            }
        }
    }

    if (searchOverlayInput) {
        var overlayDebounceTimer = null;

        searchOverlayInput.addEventListener('input', function(e) {
            var query = e.target.value;
            state.set('search.query', query);
            if (searchInput) searchInput.value = query;

            if (overlayDebounceTimer) clearTimeout(overlayDebounceTimer);
            overlayDebounceTimer = setTimeout(function() {
                if (!window.searchEngine) return;
                var results = searchEngine.query(query);
                state.set('search.results', results);
                renderOverlaySearchResults(results, query);
            }, 150);
        });

        searchOverlayInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') toggleSearch();
        });

        if (searchOverlayClear) {
            searchOverlayInput.addEventListener('input', function() {
                searchOverlayClear.classList.toggle('hidden', searchOverlayInput.value.length === 0);
            });
            searchOverlayClear.addEventListener('click', function() {
                searchOverlayInput.value = '';
                searchOverlayClear.classList.add('hidden');
                if (searchInput) searchInput.value = '';
                searchOverlayInput.focus();
                state.set('search.query', '');
                state.set('search.results', []);
                renderOverlaySearchResults([], '');
            });
        }
    }

    if (searchOverlay) {
        searchOverlay.addEventListener('click', function(e) {
            if (e.target === searchOverlay) toggleSearch();
        });
    }

    window.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && state.get('search.active')) {
            toggleSearch();
        }
    });

    // 全局键盘快捷键
    window.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            toggleSearch();
        }
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            toggleSidebar();
        }
    });

    // 触发初始渲染
    state._notify();
}

function renderSearchSuggestions(suggestions, query) {
    var container = document.getElementById('search-suggestions');
    if (!container) return;

    if (suggestions.length === 0) {
        hideSearchSuggestions();
        return;
    }

    var html = '<div class="state-container" style="padding:6px">';
    suggestions.forEach(function(s) {
        html += '<a href="#" class="overlay-search-item" style="padding:6px 10px;border-radius:var(--radius-sm);margin-bottom:2px" ' +
                'onclick="event.preventDefault();document.getElementById(\'search-input\').value=\'' + s.name.replace(/'/g, "\\'") + '\';hideSearchSuggestions();state.set(\'search.query\',\'' + s.name + '\');if(window.searchEngine){var r=searchEngine.query(\'' + s.name + '\');state.set(\'search.results\',r);state.set(\'search.active\',true);state.set(\'currentView\',\'search\');}" ' +
                'aria-label="' + s.name + '">' +
                '<span class="osi-icon" style="width:24px;height:24px;border-radius:4px;background:rgba(255,255,255,0.05);display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0">🔍</span>' +
                '<div style="flex:1;min-width:0">' +
                '<div class="osi-name" style="font-size:13px">' + _escapeHtml(s.name) + '</div>' +
                '<div class="osi-desc" style="font-size:11px">' + _escapeHtml(s.url || '') + '</div>' +
                '</div>' +
                '</a>';
    });
    html += '</div>';

    container.innerHTML = html;
    showSearchSuggestions();
}

function showSearchSuggestions() {
    var container = document.getElementById('search-suggestions');
    if (container) {
        container.classList.remove('hidden');
        container.style.display = 'block';
    }
}

function hideSearchSuggestions() {
    var container = document.getElementById('search-suggestions');
    if (container) {
        container.classList.add('hidden');
        container.style.display = 'none';
    }
}

function syncStateToHash(s) {
    const parts = [];
    if (s.sidebar.activeCategoryId) {
        parts.push('category=' + encodeURIComponent(s.sidebar.activeCategoryId));
    }
    if (s.sidebar.activeSubCategoryId) {
        parts.push('sub=' + encodeURIComponent(s.sidebar.activeSubCategoryId));
    }
    if (s.sidebar.activeLeafId) {
        parts.push('leaf=' + encodeURIComponent(s.sidebar.activeLeafId));
    }
    const newHash = parts.length > 0 ? '#' + parts.join('&') : '';
    if (window.location.hash !== newHash) {
        history.replaceState(null, '', newHash);
    }
}

function syncHashToState() {
    const hash = window.location.hash.slice(1);
    if (!hash) return false;
    const params = new URLSearchParams(hash);
    const category = params.get('category');
    const sub = params.get('sub');
    const leaf = params.get('leaf');
    let loaded = false;
    if (category && dataManager.categories[category]) {
        state.set('sidebar.activeCategoryId', category);
        loaded = true;
        if (sub) {
            const cat = dataManager.categories[category];
            if (cat.subCategories && cat.subCategories[sub]) {
                state.set('sidebar.activeSubCategoryId', sub);
                if (leaf) {
                    const subCat = cat.subCategories[sub];
                    if (subCat.leafCategories && subCat.leafCategories[leaf]) {
                        state.set('sidebar.activeLeafId', leaf);
                    }
                }
            }
        }
    }
    return loaded;
}

window.renderer = renderer;
window.state = state;
window.dataManager = dataManager;
window.searchEngine = searchEngine;

// 全局错误捕获
window.addEventListener('error', function(e) {
    console.warn('[Global Error]', e.error ? e.error.message : e.message);
    if (e.target && e.target.tagName === 'IMG') {
        e.target.src = 'assets/images/favicon.png';
    }
});

// 页面加载完成初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    setTimeout(init, 0);
}