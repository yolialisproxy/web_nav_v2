/**
 * app.js - 入口与胶水代码
 * 职责：初始化、事件调度、路由同步
 * 规范：Technical_Architecture.md 4.1
 */

async function init() {
    // 立即显示加载状态
    renderSites(null);

    // 1. 加载数据
    await dataManager.load();

    // 1.5 初始化搜索
    initSearchEngine(dataManager);

    // 2. 订阅状态变更，驱动 UI 更新 + Hash 路由同步
    state.subscribe((s) => {
        renderer.renderSidebar(s);
        renderer.renderView(s);

        // 状态变更时自动同步到 URL Hash
        syncStateToHash(s);
    });

    // 3. Hash 路由监听 - 监听 URL 变化
    window.addEventListener('hashchange', () => {
        syncHashToState();
    });

    // 3. 从URL Hash初始化状态 或 回退到默认
    const categories = Object.entries(dataManager.categories);
    const hashLoaded = syncHashToState();

    // 只有当Hash中没有有效参数时才使用默认第一个分类
    if (!hashLoaded && categories.length > 0) {
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
    // 防抖计时器
    let searchDebounceTimer = null;

    searchInput.addEventListener('input', (e) => {
      const query = e.target.value;
      state.set('search.query', query);

      // 清除之前的计时器
      if (searchDebounceTimer) clearTimeout(searchDebounceTimer);

      // 200ms 防抖延迟
      searchDebounceTimer = setTimeout(() => {
        // 安全检查：确保 searchEngine 已初始化
        if (!window.searchEngine) return;

        const results = searchEngine.query(query);
        state.set('search.results', results);
      }, 200);
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

// 全局图标加载失败兜底
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


/**
 * Hash 路由双向同步系统
 * 格式: #category=xxx&sub=xxx&leaf=xxx
 * 支持刷新、后退、链接分享
 */

/**
 * 将当前状态同步到 URL Hash
 */
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

    // 避免循环触发: 只有当hash实际变化时才修改
    if (window.location.hash !== newHash) {
        // 使用 replaceState 不添加历史记录条目 (避免每次点击产生多余历史记录)
        history.replaceState(null, '', newHash);
    }
}

/**
 * 从 URL Hash 读取并同步到全局状态
 * @returns {boolean} 是否成功从Hash加载有效状态
 */
function syncHashToState() {
    const hash = window.location.hash.slice(1);
    if (!hash) return false;

    const params = new URLSearchParams(hash);
    const category = params.get('category');
    const sub = params.get('sub');
    const leaf = params.get('leaf');

    let loaded = false;

    // 验证分类是否真实存在
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
