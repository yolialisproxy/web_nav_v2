/**
 * app.js - 入口与胶水代码
 * 职责：初始化、事件调度、路由同步
 * 规范：Technical_Architecture.md 4.1
 */

async function init() {
    window.renderSites = renderSites;
    renderSites(null);

    await dataManager.load();
    initSearchEngine(dataManager);

    state.subscribe((s) => {
        // // console.log('[STATE]', JSON.parse(JSON.stringify(s.sidebar)));
        renderer.renderSidebar(s);
        renderer.renderView(s);
        syncStateToHash(s);
    });

    window.addEventListener('hashchange', () => {
        syncHashToState();
    });

    const categories = Object.entries(dataManager.categories);
    const hashLoaded = syncHashToState();

    if (!hashLoaded && categories.length > 0) {
        // Set first category as active (expanded)
        const [firstCatId] = categories[0];
        state.set('sidebar.activeCategoryId', firstCatId);
        // NOTE: Do NOT pre-set subcategory or leaf state.
        // Let user interaction expand subcategories.
    }

    window.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            toggleSearch();
        }
    });

    const searchInput = document.getElementById('search-input');
    const searchClear = document.getElementById('search-clear');

    if (searchInput) {
        let searchDebounceTimer = null;
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value;
            state.set('search.query', query);
            if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
            searchDebounceTimer = setTimeout(() => {
                if (!window.searchEngine) return;
                const results = searchEngine.query(query);
                state.set('search.results', results);
                if (query.length > 0) {
                    state.set('search.active', true);
                    state.set('currentView', 'search');
                } else {
                    state.set('search.active', false);
                    state.set('currentView', 'category');
                }
            }, 200);
        });
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') toggleSearch();
        });
        if (searchClear && searchInput) {
            searchInput.addEventListener('input', () => {
                searchClear.classList.toggle('hidden', searchInput.value.length === 0);
            });
            searchClear.addEventListener('click', () => {
                searchInput.value = '';
                searchClear.classList.add('hidden');
                searchInput.focus();
                state.set('search.query', '');
                state.set('search.results', []);
                state.set('currentView', 'category');
            });
        }
    }

    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    if (sidebarToggle && sidebar && sidebarOverlay) {
        function toggleSidebar() {
            const isOpen = !sidebar.classList.contains('-translate-x-full');
            if (isOpen) {
                sidebar.classList.add('-translate-x-full');
                sidebarOverlay.classList.add('hidden');
            } else {
                sidebar.classList.remove('-translate-x-full');
                sidebarOverlay.classList.remove('hidden');
            }
        }
        sidebarToggle.addEventListener('click', toggleSidebar);
        sidebarOverlay.addEventListener('click', toggleSidebar);
    }

    const searchOverlay = document.getElementById('search-overlay');
    const searchOverlayInput = document.getElementById('search-overlay-input');
    const searchOverlayClear = document.getElementById('search-overlay-clear');

    function toggleSearch() {
        const active = state.get('search.active');
        state.set('search.active', !active);
        state.set('currentView', !active ? 'search' : 'category');
        if (searchOverlay) {
            if (!active) {
                searchOverlay.classList.remove('hidden');
                setTimeout(() => {
                    if (searchOverlayInput) {
                        searchOverlayInput.focus();
                        searchOverlayInput.value = state.get('search.query') || '';
                        if (window.searchEngine && searchOverlayInput.value) {
                            const results = searchEngine.query(searchOverlayInput.value);
                            state.set('search.results', results);
                        }
                    }
                }, 50);
            } else {
                searchOverlay.classList.add('hidden');
            }
        }
    }

    if (searchOverlayInput) {
        let overlayDebounceTimer = null;
        searchOverlayInput.addEventListener('input', (e) => {
            const query = e.target.value;
            state.set('search.query', query);
            if (searchInput) searchInput.value = query;
            if (overlayDebounceTimer) clearTimeout(overlayDebounceTimer);
            overlayDebounceTimer = setTimeout(() => {
                if (!window.searchEngine) return;
                const results = searchEngine.query(query);
                state.set('search.results', results);
            }, 200);
        });
        searchOverlayInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') toggleSearch();
        });
        if (searchOverlayClear) {
            searchOverlayInput.addEventListener('input', () => {
                searchOverlayClear.classList.toggle('hidden', searchOverlayInput.value.length === 0);
            });
            searchOverlayClear.addEventListener('click', () => {
                searchOverlayInput.value = '';
                searchOverlayClear.classList.add('hidden');
                if (searchInput) searchInput.value = '';
                state.set('search.query', '');
                state.set('search.results', []);
                searchOverlayInput.focus();
            });
        }
    }

    if (searchOverlay) {
        searchOverlay.addEventListener('click', (e) => {
            if (e.target === searchOverlay) toggleSearch();
        });
    }

    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && state.get('search.active')) {
            toggleSearch();
        }
    });

    state._notify();
}

init();

document.addEventListener('error', function(e) {
    const target = e.target;
    if (target.tagName === 'IMG' && target.classList.contains('card-icon')) {
        if (!target.dataset.error) {
            target.dataset.error = '1';
            target.src = 'assets/images/favicon.png';
            target.onerror = null;
        }
    }
}, true);

function syncStateToHash(s) {
    const parts = [];
    if (s.sidebar.activeCategoryId) {
        parts.push(`category=${encodeURIComponent(s.sidebar.activeCategoryId)}`);
    }
    if (s.sidebar.activeSubCategoryId) {
        parts.push(`sub=${encodeURIComponent(s.sidebar.activeSubCategoryId)}`);
    }
    if (s.sidebar.activeLeafId) {
        parts.push(`leaf=${encodeURIComponent(s.sidebar.activeLeafId)}`);
    }
    const newHash = parts.length > 0 ? `#${parts.join('&')}` : '';
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


// Global error capture
window.addEventListener('error', (e) => {
    console.warn('[Global Error]', e.error?.message || e.message);
    if (e.target && e.target.tagName === 'IMG') {
        e.target.src = 'assets/images/favicon.png';
    }
});
