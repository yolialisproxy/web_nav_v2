/**
 * app.js - 入口与胶水代码
 * 职责：初始化、事件调度、路由同步
 * 规范：Technical_Architecture.md 4.1
 */

async function init() {
    console.log('WebNav V2: Initializing...');

    // 1. 加载数据
    await dataManager.load();

    // 2. 订阅状态变更，驱动 UI 更新
    state.subscribe((s) => {
        renderer.renderSidebar(s);
        renderer.renderView(s);
    });

    // 3. 初始化默认状态
    // 默认展开第一个大类 -> 第一个中类 -> 第一个小类
    const categories = Object.entries(dataManager.categories);
    if (categories.length > 0) {
        const [firstCatId, firstCat] = categories[0];
        state.set('sidebar.activeCategoryId', firstCatId);
        
        const subCats = Object.entries(firstCat.subCategories || {});
        if (subCats.length > 0) {
            const [firstSubId, firstSub] = subCats[0];
            state.set('sidebar.activeSubCategoryId', firstSubId);
            
            const leafCats = Object.entries(firstSub.leafCategories || {});
            if (leafCats.length > 0) {
                const [firstLeafId] = leafCats[0];
                state.set('sidebar.activeLeafId', firstLeafId);
            }
        }
    }

    // 4. 绑定全局快捷键 (Ctrl+K / Cmd+K)
    window.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            toggleSearch();
        }
    });

    // 5. 初始渲染
    state._notify();
}

function toggleSearch() {
    const active = state.get('search.active');
    state.set('search.active', !active);
    state.set('currentView', !active ? 'search' : 'category');
    
    // 渲染搜索面板 (直接操作 DOM 保证最高响应速度)
    const overlay = document.getElementById('search-overlay');
    if (!overlay) {
        createSearchUI();
    }
    
    const searchOverlay = document.getElementById('search-overlay');
    if (!active) {
        searchOverlay.classList.add('active');
        setTimeout(() => {
            document.getElementById('search-input').focus();
        }, 50);
    } else {
        searchOverlay.classList.remove('active');
    }
}

function createSearchUI() {
    const overlay = document.createElement('div');
    overlay.id = 'search-overlay';
    overlay.className = 'search-overlay';
    overlay.innerHTML = `
        <<divdiv class="search-container">
            <<inputinput type="text" id="search-input" class="search-input" placeholder="快速搜索网站 (Ctrl+K)...">
        </div>
    `;
    document.body.appendChild(overlay);

    const input = document.getElementById('search-input');
    input.addEventListener('input', (e) => {
        const query = e.target.value;
        state.set('search.query', query);
        const results = searchEngine.query(query);
        state.set('search.results', results);
        
        if (query === '') {
            state.set('search.active', false);
            state.set('currentView', 'category');
            overlay.classList.remove('active');
        }
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            input.value = '';
            toggleSearch();
        }
    });
}

// 启动
init();
