/**
 * app.js - 入口与胶水代码
 * 职责：初始化、事件调度、路由同步
 * 规范：Technical_Architecture.md 4.1
 */

async function init() {
    // // // // console.log('WebNav V2: Initializing...');

    // 1. 加载数据
    await dataManager.load();

    // 2. 订阅状态变更，驱动 UI 更新
    state.subscribe((s) => {
        renderer.renderSidebar(s);
        renderer.renderView(s);
    });

    // 3. 初始化默认状态
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

  // Add search button click listener
  const searchButton = document.getElementById('search-button');
  if (searchButton) {
    searchButton.addEventListener('click', toggleSearch);
  }

  // Add search input listeners
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value;
      state.set('search.query', query);
      const results = searchEngine.query(query);
      state.set('search.results', results);
    });
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        toggleSearch();
      }
    });
  }

  // 5. 初始渲染
  state._notify();
}

function toggleSearch() {
  const active = state.get('search.active');
  state.set('search.active', !active);
  state.set('currentView', !active ? 'search' : 'category');
  
  const searchContainer = document.querySelector('.search-container');
  const searchInput = document.getElementById('search-input');
  if (searchContainer && searchInput) {
    if (!active) {
      searchContainer.classList.add('active');
      setTimeout(() => {
        searchInput.focus();
      }, 50);
    } else {
      searchContainer.classList.remove('active');
    }
  }
}



// 启动
init();
