"use strict";
/**
 * app.js - 应用入口与路由调度 (V3)
 * 职责:初始化,事件调度,SPA路由,键盘快捷键
 * 修复:统一所有功能到一个入口点
 */
var _a;
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
        }
        else {
            // 太阳图标
            themeIcon.setAttribute('d', 'M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zM9 7a1 1 0 011 1v1a1 1 0 11-2 0V8a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0V8a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0V8a1 1 0 011-1zM5 11a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm-8 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5 19a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4 0a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1z');
        }
        toggleBtn.setAttribute('title', displayTheme === 'dark' ? '切换到亮色模式' : '切换到暗色模式');
    }
    // 初始更新
    updateThemeIcon(state.get('theme'));
    // 监听状态变化
    state.subscribe(function (s) {
        if (s.theme) {
            updateThemeIcon(s.theme);
        }
    });
    // 绑定点击事件
    toggleBtn.addEventListener('click', function () {
        const currentTheme = state.get('theme');
        let newTheme;
        if (currentTheme === 'light') {
            newTheme = 'dark';
        }
        else if (currentTheme === 'dark') {
            newTheme = 'system';
        }
        else {
            newTheme = 'light';
        }
        state.set('theme', newTheme);
    });
}
async function init() {
    console.log('[App] init started');
    // 暴露全局函数
    window.renderSites = renderSites;
    // 骨架屏已经在HTML中默认显示,无需额外设置
    // 只需确保state.loading为true
    if (state)
        state.set('loading', true);
    // 加载数据（带缓存降级）
    let dataLoaded = false;
    try {
        await window.dataManager.load();
        dataLoaded = true;
        console.log('[App] window.dataManager.load succeeded, raw length: ', window.dataManager.raw.length);
    }
    catch (e) {
        console.error('[App] 数据加载失败:', e);
        // 尝试从缓存恢复
        try {
            const cached = window.dataManager._loadCache();
            if (cached && cached.length > 0) {
                // // // console.log('[App] 从缓存恢复数据:', cached.length, '条');
                window.dataManager.raw = cached;
                window.dataManager._buildIndexes();
                window.dataManager.isLoaded = true;
                dataLoaded = true;
                console.log('[App] window.dataManager.load from cache succeeded, raw length: ', window.dataManager.raw.length);
            }
        }
        catch (cacheErr) {
            console.error('[App] 缓存恢复也失败:', cacheErr);
        }
    }
    if (!dataLoaded) {
        renderSites(false, 'main-content');
        return;
    }
    await state.loadTags(window.dataManager); // 标签系统已集成到 State
}
// 将 window.dataManager.raw 同步入 state.sites,确保数据源唯一
// 使用 state.set 触发订阅者重渲染,保持 UI 与数据一致
if (window.dataManager.raw && window.dataManager.raw.length > 0) {
    console.log('[App] window.dataManager.raw length: ', window.dataManager.raw.length);
    try {
        console.log('[App] Setting state.sites with length: ', window.dataManager.raw.length);
        state.set('sites', window.dataManager.raw);
        console.log('[App] state.sites set, length: ', state.get('sites').length);
        console.log('[App] state.sites set successfully');
    }
    catch (_e) {
        console.warn('[App] state.sites set失败', _e);
    }
}
// 初始化标签系统
try {
    state.renderTagCloud('tag-cloud-container');
}
catch (e) {
    console.warn('[App] 标签系统初始化失败:', e);
}
// 搜索引擎初始化（后台任务）
try {
    initSearchEngine(window.dataManager);
}
catch (e) {
    console.warn('[App] 搜索初始化失败:', e.message);
}
// 初始化主题切换
initThemeToggle();
// 初始化收藏
if (window.favoriteManager) {
    try {
        window.favoriteUI.updateCount();
    }
    catch (e) {
        console.warn('[App] 收藏计数初始化失败:', e);
    }
}
// 初始化盈利模块
if (typeof window.Monetization !== "undefined" && window.Monetization.init) {
    window.Monetization.init({ enabled: true });
}
// Toast通知
((_a = window.Toast) === null || _a === void 0 ? void 0 : _a.init) && window.Toast.init();
// 标签云展开/收起（tag-cloud-toggle）\n    var tagToggle = document.getElementById('tag-cloud-toggle');\n    var tagContainer = document.getElementById('tag-cloud-container');\n    if (tagToggle && tagContainer) {\n        tagToggle.setAttribute('role', 'button');\n        tagToggle.setAttribute('tabindex', '0');\n        tagToggle.addEventListener('click', function() {\n            var expanded = tagToggle.getAttribute('aria-expanded') === 'true';\n            tagToggle.setAttribute('aria-expanded', !expanded);\n            tagContainer.style.display = expanded ? 'none' : '';\n        });\n        tagToggle.addEventListener('keydown', function(e) {\n            if ((e as KeyboardEvent).key === 'Enter' || (e as KeyboardEvent).key === ' ') {\n                e.preventDefault();\n                tagToggle.click();\n            }\n        });\n    }\n    // 状态订阅 - 驱动UI渲染
state.subscribe(function (s) {
    try {
        renderer.renderSidebar(s);
    }
    catch (e) {
        console.error('[APP] Sidebar error:', e);
    }
    // 视图切换按钮绑定（Phase 7）
    var viewGridBtn = document.getElementById('view-grid');
    var viewListBtn = document.getElementById('view-list');
    if (viewGridBtn && viewListBtn) {
        // 从 state 恢复激活状态
        var currentView = state.get('currentView') || 'grid';
        if (currentView === 'grid') {
            viewGridBtn.classList.add('active');
            viewGridBtn.setAttribute('aria-pressed', 'true');
            viewListBtn.setAttribute('aria-pressed', 'false');
        }
        else if (currentView === 'list') {
            viewListBtn.classList.add('active');
            viewListBtn.setAttribute('aria-pressed', 'true');
            viewGridBtn.setAttribute('aria-pressed', 'false');
        }
        viewGridBtn.addEventListener('click', function () {
            state.setView('grid');
            viewGridBtn.classList.add('active');
            viewListBtn.classList.remove('active');
            viewGridBtn.setAttribute('aria-pressed', 'true');
            viewListBtn.setAttribute('aria-pressed', 'false');
        });
        viewListBtn.addEventListener('click', function () {
            state.setView('list');
            viewListBtn.classList.add('active');
            viewGridBtn.classList.remove('active');
            viewListBtn.setAttribute('aria-pressed', 'true');
            viewGridBtn.setAttribute('aria-pressed', 'false');
        });
    }
    try {
        renderer.renderView(s);
    }
    catch (e) {
        console.error('[APP] View error:', e);
    }
    syncStateToHash(s);
});
// URL hash 路由
window.addEventListener('hashchange', function () {
    syncHashToState();
});
// 初始路由
var categories = Object.entries(window.dataManager.categories);
var hashLoaded = syncHashToState();
if (!hashLoaded && categories.length > 0) {
    var firstCatId = categories[0][0];
    state.set('sidebar.activeCategoryId', firstCatId);
    var firstCat = window.dataManager.categories[firstCatId];
    if (firstCat) {
        var subCats = firstCat.subCategories;
        if (subCats) {
            var firstSubId = Object.keys(subCats)[0];
            if (firstSubId) {
                state.set('sidebar.activeSubCategoryId', firstSubId);
                var subCat = subCats[firstSubId];
                if (subCat && subCat.leafCategories) {
                    var leafIds = Object.keys(subCat.leafCategories);
                    if (leafIds[0])
                        state.set('sidebar.activeLeafId', leafIds[0]);
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
    searchInput.addEventListener('input', function (e) {
        var query = (e.target as HTMLInputElement).value.trim();
        state.set('search.query', query);
        if (searchDebounceTimer)
            clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(function () {
            if (!window.searchEngine)
                return;
            if (query.length > 0) {
                var suggestions = searchEngine.suggest(query);
                renderSearchSuggestions(suggestions, query);
                var results = searchEngine.query(query);
                state.set('search.results', results);
                state.set('search.active', true);
                state.set('currentView', 'search');
            }
            else {
                hideSearchSuggestions();
                state.set('search.active', false);
                state.set('search.results', []);
                state.set('currentView', 'category');
            }
        }, 150);
    });
    searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            hideSearchSuggestions();
            toggleSearch();
        }
        if (e.key === 'Enter') {
            e.preventDefault();
            hideSearchSuggestions();
        }
    });
    searchInput.addEventListener('focus', function () {
        if ((searchInput as HTMLInputElement).value.length > 0) {
            showSearchSuggestions();
        }
    });
    document.addEventListener('click', function (e) {
        if (! (e.target as HTMLElement).closest('.search-container')) {
            hideSearchSuggestions();
        }
    });
    if (searchClear) {
        searchInput.addEventListener('input', function () {
            searchClear.classList.toggle('hidden', (searchInput as HTMLInputElement).value.length === 0);
        });
            searchClear.addEventListener('click', function () {
                (searchInput as HTMLInputElement).value = '';
                searchClear.classList.add('hidden');
                (searchInput as HTMLInputElement).focus();
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
    if (sidebar)
        sidebar.classList.add('-translate-x-full');
    if (sidebarOverlay) {
        sidebarOverlay.classList.add('hidden');
        sidebarOverlay.classList.remove('visible');
        sidebarOverlay.setAttribute('aria-hidden', 'true');
    }
    document.body.classList.remove('sidebar-open');
    if (sidebarToggle)
        sidebarToggle.setAttribute('aria-expanded', 'false');
}
function openSidebar() {
    if (sidebar)
        sidebar.classList.remove('-translate-x-full');
    if (sidebarOverlay) {
        sidebarOverlay.classList.remove('hidden');
        sidebarOverlay.classList.add('visible');
        sidebarOverlay.setAttribute('aria-hidden', 'false');
    }
    document.body.classList.add('sidebar-open');
    if (sidebarToggle)
        sidebarToggle.setAttribute('aria-expanded', 'true');
}
if (sidebarToggle && sidebar && sidebarOverlay) {
    sidebarToggle.addEventListener('click', function () {
        var isOpen = !sidebar.classList.contains('-translate-x-full');
        if (isOpen)
            closeSidebar();
        else
            openSidebar();
    });
    sidebarOverlay.addEventListener('click', closeSidebar);
}
// ===== 侧边栏导航点击（事件委托） =====
var sidebarContent = document.getElementById('sidebar-content');
if (sidebarContent) {
    sidebarContent.addEventListener('click', function (e) {
        var navItem = (e.target as HTMLElement).closest('.nav-item[data-category]');
        if (navItem) {
            var cat = navItem.getAttribute('data-category');
            // 切换子分类展开/折叠
            var next = navItem.nextElementSibling;
            if (next && next.classList.contains('nav-children')) {
                var isExpanded = (next as HTMLElement).style.display !== 'none';
                // 折叠所有其他子菜单
                sidebarContent.querySelectorAll('.nav-children').forEach(function (c) {
                    if (c !== next)
                        (c as HTMLElement).style.display = 'none';
                });
                (next as HTMLElement).style.display = isExpanded ? 'none' : 'block';
            }
            if (cat) {
                state.set('sidebar.activeCategoryId', cat);
                // Auto-resolve first sub/leaf so renderCategoryView has a valid fullId.
                // Without this, sub/leaf stay null → getSitesByLeafId("cat/null") → 0 results.
                var dm = window.dataManager;
                if (dm && dm.categories && dm.categories[cat]) {
                    var subs = dm.categories[cat].subCategories;
                    if (subs) {
                        var subIds = Object.keys(subs);
                        if (subIds.length > 0) {
                            var firstSubId = subIds[0];
                            var firstSub = subs[firstSubId];
                            if (firstSub && firstSub.leafCategories) {
                                var leafIds = Object.keys(firstSub.leafCategories);
                                if (leafIds.length > 0) {
                                    // Pick the first leaf that has sites
                                    for (var li = 0; li < leafIds.length; li++) {
                                        if (firstSub.leafCategories[leafIds[li]].siteIds.length > 0) {
                                            state.set('sidebar.activeSubCategoryId', firstSubId);
                                            state.set('sidebar.activeLeafId', leafIds[li]);
                                            break;
                                        }
                                    }
                                    // Fallback: any leaf
                                    if (!state.get('sidebar.activeLeafId') && leafIds.length > 0) {
                                        state.set('sidebar.activeSubCategoryId', firstSubId);
                                        state.set('sidebar.activeLeafId', leafIds[0]);
                                    }
                                }
                            }
                        }
                    }
                }
                closeSidebar();
            }
            e.preventDefault();
            return;
        }
        var subItem = (e.target as HTMLElement).closest('.nav-sub-item[data-sub]');
        if (subItem) {
            var subCat = subItem.getAttribute('data-sub');
            var parentItem = subItem.closest('.nav-item');
            var mainCat = parentItem ? parentItem.getAttribute('data-category') : null;
            if (mainCat && subCat) {
                state.set('sidebar.activeCategoryId', mainCat);
                state.set('sidebar.activeSubCategoryId', subCat);
                // Find the first leaf under this subcategory that has sites
                var leafId = null;
                if (window.dataManager && window.dataManager.categories &&
                    window.dataManager.categories[mainCat] &&
                    window.dataManager.categories[mainCat].subCategories &&
                    window.dataManager.categories[mainCat].subCategories[subCat] &&
                    window.dataManager.categories[mainCat].subCategories[subCat].leafCategories) {
                    var leafCategories = window.dataManager.categories[mainCat].subCategories[subCat].leafCategories;
                    var leafIds = Object.keys(leafCategories);
                    // First, try to find a leaf that actually has sites
                    for (var i = 0; i < leafIds.length; i++) {
                        var lid = leafIds[i];
                        if (leafCategories[lid].siteIds && leafCategories[lid].siteIds.length > 0) {
                            leafId = lid;
                            break;
                        }
                    }
                    // If no leaf with sites found, use the first leaf (if any)
                    if (leafId === null && leafIds.length > 0) {
                        leafId = leafIds[0];
                    }
                }
                state.set('sidebar.activeLeafId', leafId);
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
            requestAnimationFrame(function () {
                if (searchOverlayInput) {
                    (searchOverlayInput as HTMLInputElement).focus();
                    var query = state.get('search.query') || '';
                    (searchOverlayInput as HTMLInputElement).value = query;
                    if (window.searchEngine && query) {
                        var results = searchEngine.query(query);
                        state.set('search.results', results);
                        renderOverlaySearchResults(results, query);
                    }
                }
            });
        }
        else {
            searchOverlay.classList.add('hidden');
            searchOverlay.setAttribute('aria-hidden', 'true');
        }
    }
}
if (searchOverlayInput) {
    var overlayDebounceTimer = null;
            searchOverlayInput.addEventListener('input', function (e) {
        var query = (e.target as HTMLInputElement).value;
        state.set('search.query', query);
        if (searchInput)
            (searchInput as HTMLInputElement).value = query;
        if (overlayDebounceTimer)
            clearTimeout(overlayDebounceTimer);
        overlayDebounceTimer = setTimeout(function () {
            if (!window.searchEngine)
                return;
            var results = searchEngine.query(query);
            state.set('search.results', results);
            renderOverlaySearchResults(results, query);
        }, 150);
    });
    searchOverlayInput.addEventListener('keydown', function (e) {
        if (e.key === 'Escape')
            toggleSearch();
    });
    if (searchOverlayClear) {
        searchOverlayInput.addEventListener('input', function () {
                (searchOverlayClear as HTMLElement).classList.toggle('hidden', (searchOverlayInput as HTMLInputElement).value.length === 0);
        });
        searchOverlayClear.addEventListener('click', function () {
            (searchOverlayInput as HTMLInputElement).value = '';
            searchOverlayClear.classList.add('hidden');
            if (searchInput)
                (searchInput as HTMLInputElement).value = '';
            searchOverlayInput.focus();
            state.set('search.query', '');
            state.set('search.results', []);
            renderOverlaySearchResults([], '');
        });
    }
}
if (searchOverlay) {
    searchOverlay.addEventListener('click', function (e) {
        if (e.target === searchOverlay)
            toggleSearch();
    });
}
window.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && state.get('search.active')) {
        toggleSearch();
    }
});
// 全局键盘快捷键
window.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        toggleSearch();
    }
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        toggleSearch();
    }
});
// 触发初始渲染
// Phase 13: PWA 安装提示
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
    var banner = document.getElementById('install-banner');
    if (banner)
        banner.classList.add('show');
});
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        navigator.serviceWorker.register('/sw.js')
            .then(function (reg) {
            // console.log('[PWA] ServiceWorker 注册成功: scope=' + reg.scope);
        })
            .catch(function (err) {
            // console.warn('[PWA] ServiceWorker 注册失败:', err);
        });
        // PWA 安装按钮处理
        var installBtn = document.getElementById('install-btn');
        var dismissBtn = document.getElementById('install-dismiss');
        if (installBtn) {
            installBtn.addEventListener('click', function () {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then(function (choiceResult) {
                        if (choiceResult.outcome === 'accepted') {
                            // 用户接受安装
                        }
                        deferredPrompt = null;
                        var banner = document.getElementById('install-banner');
                        if (banner)
                            banner.classList.add('hidden');
                    });
                }
            });
        }
        if (dismissBtn) {
            dismissBtn.addEventListener('click', function () {
                var banner = document.getElementById('install-banner');
                if (banner) {
                    banner.classList.add('hidden');
                    banner.classList.add('dont-show');
                }
            });
        }
        // 监听 appinstalled 事件
        window.addEventListener('appinstalled', function () {
            var banner = document.getElementById('install-banner');
            if (banner) {
                banner.classList.add('dont-show');
            }
        });
    });
}
state._notify();
// 游戏关闭按钮（如果存在）
var gameCloseBtn = document.getElementById('game-close-btn');
if (gameCloseBtn) {
    gameCloseBtn.addEventListener('click', function () {
        if (window.GameHub && GameHub.currentGame)
            GameHub.closeGame();
        window.location.hash = '';
        state.setView('grid');
    });
}
function renderSearchSuggestions(suggestions, query) {
    var container = document.getElementById('search-suggestions');
    if (!container)
        return;
    if (suggestions.length === 0) {
        hideSearchSuggestions();
        return;
    }
    var html = '<div class="state-container" style="padding:6px">';
    suggestions.forEach(function (s) {
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
    // Phase 9: 游戏路由支持 (#games 大厅 / #game=<key> 启动游戏)
    if (hash === 'games' && window.GameHub) {
        state.setView('games');
        return true;
    }
    var gameMatch = hash.match(/^game=([a-z0-9]+)$/);
    if (gameMatch && window.GameHub) {
        var gameKey = gameMatch[1];
        state.setView('games');
        // 异步启动游戏（等待 DOM 渲染后）
        // 游戏启动由 renderView 的 games 分支处理
        // GameHub.startGame(gameKey);
        return true;
    }
    if (!hash)
        return false;
    const params = new URLSearchParams(hash);
    const category = params.get('category');
    const sub = params.get('sub');
    const leaf = params.get('leaf');
    let loaded = false;
    if (category && window.dataManager.categories[category]) {
        state.set('sidebar.activeCategoryId', category);
        loaded = true;
        if (sub) {
            const cat = window.dataManager.categories[category];
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
// 暴露全局变量
window.state = state;
window.dataManager = window.dataManager;
window.searchEngine = searchEngine;
window.renderer = renderer;
// 全局错误捕获
window.addEventListener('error', function (e) {
    console.warn('[Global Error]', e.error ? e.error.message : e.message);
    if (e.target && (e.target as HTMLElement).tagName === 'IMG') {
        (e.target as HTMLElement).src = 'assets/images/favicon.png';
    }
});
// 页面加载完成初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
}
else {
    setTimeout(init, 0);
}
//# sourceMappingURL=app.js.map