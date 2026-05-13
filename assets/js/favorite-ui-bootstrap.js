// favorite-ui-bootstrap.js - 收藏UI启动脚本 (V3)
// 增强功能：搜索、分类分组、最近/最多访问排序、一键收藏、实时计数
(function() {
    'use strict';

    // ===== 构建单个收藏项HTML =====
    function buildFavoriteItem(site, showCategory) {
        var cat = site.category || '未分类';
        var desc = site.description || '暂无描述';
        var safeName = site.name.replace(/'/g, "\\'").replace(/"/g, '&quot;');
        var visitCount = window.favoriteManager ? window.favoriteManager.getVisitCount(site.name) : 0;
        var visitStr = visitCount > 0 ? '<span class="fav-visit-count">' + visitCount + ' 次访问</span>' : '';

        var html = '<div class="favorite-item" data-name="' + safeName + '">';
        html += '<a href="pages/site-detail.html?name=' + encodeURIComponent(site.name) + '" style="flex:1;text-decoration:none;" onclick="window.favoriteManager && window.favoriteManager.recordVisit(\'' + safeName + '\')">';
        if (showCategory && cat !== '未分类') {
            html += '<span class="fav-site-cat-badge">' + cat + '</span>';
        }
        html += '<span class="fav-site-name">' + site.name + '</span>';
        html += '<span class="fav-site-desc">' + desc + '</span>';
        html += visitStr;
        html += '</a>';
        html += '<button class="fav-remove-btn" data-name="' + safeName + '" title="移除收藏">&times;</button>';
        html += '</div>';
        return html;
    }

    // ===== 按分类构建分组HTML =====
    function buildGroupedList(favorites) {
        var grouped = window.favoriteManager.getByCategory();
        var cats = Object.keys(grouped).sort(function(a, b) {
            var ca = a.charCodeAt(0);
            var cb = b.charCodeAt(0);
            return ca - cb;
        });

        var html = '';
        cats.forEach(function(cat) {
            var items = grouped[cat];
            html += '<div class="fav-group">';
            html += '<div class="fav-group-header">' + cat + ' <span class="fav-group-count">(' + items.length + ')</span></div>';
            html += '<div class="fav-group-items">';
            items.forEach(function(site) {
                html += buildFavoriteItem(site, false);
            });
            html += '</div></div>';
        });
        return html;
    }

    // ===== 构建分组标签切换栏 =====
    function buildGroupTabs() {
        return '<div class="fav-group-tabs">' +
            '<button class="fav-group-tab active" data-group="all">全部</button>' +
            '<button class="fav-group-tab" data-group="category">分类</button>' +
            '<button class="fav-group-tab" data-group="recent">最近收藏</button>' +
            '<button class="fav-group-tab" data-group="frequent">最多访问</button>' +
        '</div>';
    }

    if (!window.favoriteUI) {
        window.favoriteUI = {
            modal: document.getElementById('favorite-modal'),
            favoriteList: document.getElementById('favorite-list'),
            currentGroup: 'all',
            searchQuery: '',

            // ===== 统计信息HTML =====
            _buildStats: function(favorites) {
                var total = favorites.length;
                var cats = {};
                var totalVisits = 0;
                favorites.forEach(function(f) {
                    var c = f.category || '未分类';
                    cats[c] = (cats[c] || 0) + 1;
                    totalVisits += window.favoriteManager.getVisitCount(f.name);
                });
                var catCount = Object.keys(cats).length;
                return '<div class="favorite-stats">' +
                    '<span class="stat-item">共 <strong>' + total + '</strong> 项</span>' +
                    '<span class="stat-sep">|</span>' +
                    '<span class="stat-item">' + catCount + ' 个分类</span>' +
                    (totalVisits > 0 ? '<span class="stat-sep">|</span><span class="stat-item">累计 ' + totalVisits + ' 次访问</span>' : '') +
                '</div>';
            },

            // ===== 渲染列表 =====
            renderList: function() {
                if (!this.favoriteList || !window.favoriteManager) return;

                var favorites = window.favoriteManager.getAll();
                var count = window.favoriteManager.getCount();
                var countEl = document.getElementById('favorite-count');
                var emptyEl = document.getElementById('favorite-empty');
                var clearBtn = document.getElementById('clear-favorites');

                if (countEl) countEl.textContent = 'Total: ' + count + ' items';

                if (count === 0) {
                    if (this.favoriteList) this.favoriteList.style.display = 'none';
                    if (emptyEl) emptyEl.style.display = 'block';
                    if (clearBtn) clearBtn.style.display = 'none';
                    return;
                }

                if (this.favoriteList) {
                    this.favoriteList.style.display = 'block';
                    if (emptyEl) emptyEl.style.display = 'none';
                    if (clearBtn) clearBtn.style.display = 'block';

                    var html = '';

                    if (this.searchQuery && this.searchQuery.trim()) {
                        // 搜索模式
                        var results = window.favoriteManager.search(this.searchQuery);
                        html += '<div class="favorite-search-info">搜索 "' + this._escapeHtml(this.searchQuery) + '"，找到 ' + results.length + ' 个结果</div>';
                        if (results.length > 0) {
                            html += '<div class="fav-count-info">' + this._buildStats(results) + '</div>';
                            results.forEach(function(site) {
                                html += buildFavoriteItem(site, true);
                            });
                        } else {
                            html += '<div class="favorite-empty"><p>未找到匹配的收藏</p></div>';
                        }
                    } else {
                        // 非搜索模式：按分组视图渲染
                        html += '<div class="fav-count-info">' + this._buildStats(favorites) + '</div>';

                        switch (this.currentGroup) {
                            case 'category':
                                html += buildGroupedList(favorites);
                                break;
                            case 'recent':
                                var recent = window.favoriteManager.getRecent();
                                recent.forEach(function(site) {
                                    html += buildFavoriteItem(site, true);
                                });
                                break;
                            case 'frequent':
                                var frequent = window.favoriteManager.getMostVisited();
                                frequent.forEach(function(site) {
                                    html += buildFavoriteItem(site, true);
                                });
                                break;
                            default:
                                // 全部列表
                                favorites.forEach(function(site) {
                                    html += buildFavoriteItem(site, true);
                                });
                                break;
                        }
                    }

                    this.favoriteList.innerHTML = html;
                }

                // 绑定删除按钮事件
                this._bindRemoveButtons();
                // 绑定分组标签事件
                this._bindGroupTabs();
                // 绑定搜索事件
                this._bindSearch();
            },

            // ===== 搜索功能 =====
            _bindSearch: function() {
                var self = this;
                var searchInput = document.getElementById('favorite-search-input');
                if (!searchInput) return;

                searchInput.value = this.searchQuery || '';

                searchInput.oninput = function(e) {
                    self.searchQuery = e.target.value;
                    var count = window.favoriteManager.getCount();
                    var clearBtn = document.getElementById('clear-favorites');
                    var searchClear = document.getElementById('favorite-search-clear');

                    // 切换搜索清除按钮
                    if (searchClear) {
                        searchClear.style.display = e.target.value.trim() ? 'block' : 'none';
                    }

                    if (e.target.value.trim()) {
                        if (clearBtn) clearBtn.style.display = 'none';
                    } else {
                        if (clearBtn) clearBtn.style.display = (count > 0) ? 'block' : 'none';
                    }

                    self.renderList();
                };

                var searchClear = document.getElementById('favorite-search-clear');
                if (searchClear) {
                    searchClear.onclick = function() {
                        searchInput.value = '';
                        self.searchQuery = '';
                        self.renderList();
                        searchInput.focus();
                    };
                }
            },

            // ===== 分组标签切换 =====
            _bindGroupTabs: function() {
                var self = this;
                var tabs = document.querySelectorAll('.fav-group-tab');
                if (!tabs) return;

                tabs.forEach(function(tab) {
                    tab.onclick = function() {
                        tabs.forEach(function(t) { t.classList.remove('active'); });
                        this.classList.add('active');
                        self.currentGroup = this.getAttribute('data-group');
                        self.renderList();
                    };
                });
            },

            // ===== 绑定删除按钮 =====
            _bindRemoveButtons: function() {
                var self = this;
                if (!this.favoriteList) return;

                this.favoriteList.querySelectorAll('.fav-remove-btn').forEach(function(btn) {
                    btn.onclick = function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        var name = btn.getAttribute('data-name');
                        if (name && window.favoriteManager) {
                            window.favoriteManager.remove(name);
                            self.renderList();
                            self.updateCount();
                            if (typeof updateFavoriteButtons === 'function') updateFavoriteButtons();
                        }
                    };
                });
            },

            // ===== HTML转义 =====
            _escapeHtml: function(text) {
                if (!text) return '';
                var div = document.createElement('div');
                div.appendChild(document.createTextNode(text));
                return div.innerHTML;
            },

            // ===== 清空所有 =====
            clearAll: function() {
                if (window.favoriteManager && confirm('确定要清空所有收藏吗？')) {
                    window.favoriteManager.clear();
                    this.searchQuery = '';
                    this.currentGroup = 'all';
                    var searchInput = document.getElementById('favorite-search-input');
                    if (searchInput) searchInput.value = '';
                    this.renderList();
                    this.updateCount();
                    if (typeof updateFavoriteButtons === 'function') updateFavoriteButtons();
                }
            },

            // ===== 导出收藏 =====
            exportFavorites: function() {
                if (!window.favoriteManager) return;
                try {
                    var favorites = window.favoriteManager.getAll();
                    var data = JSON.stringify({
                        version: '3.0',
                        exportedAt: new Date().toISOString(),
                        count: favorites.length,
                        favorites: favorites
                    }, null, 2);
                    var blob = new Blob([data], { type: 'application/json' });
                    var url = URL.createObjectURL(blob);
                    var a = document.createElement('a');
                    a.href = url;
                    a.download = 'webnav-favorites-' + new Date().toISOString().split('T')[0] + '.json';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                } catch(e) {
                    console.error('Export failed:', e);
                    alert('Export failed: ' + e.message);
                }
            },

            // ===== 一键收藏当前页面 =====
            collectCurrentPage: function() {
                if (!window.favoriteManager) return;

                // 优先尝试从当前详情页获取信息
                var siteData = this._getCurrentSiteData();
                if (!siteData || !siteData.name) {
                    // 尝试从当前URL获取
                    siteData = this._getSiteFromCurrentURL();
                }

                if (siteData && siteData.name) {
                    if (window.favoriteManager.isFavorite(siteData.name)) {
                        alert('该站点已在收藏夹中');
                        return;
                    }
                    var result = window.favoriteManager.add(siteData);
                    if (result.success) {
                        this.renderList();
                        this.updateCount();
                        if (typeof updateFavoriteButtons === 'function') updateFavoriteButtons();
                        alert('已收藏: ' + siteData.name);
                    } else {
                        alert(result.message);
                    }
                } else {
                    // 手动输入
                    var name = prompt('请输入站点名称:');
                    if (!name || !name.trim()) return;
                    var url = prompt('请输入站点URL:', window.location.href);
                    var desc = prompt('请输入描述（可选）:', '');
                    var cat = prompt('请输入分类（可选）:', '');

                    var result = window.favoriteManager.add({
                        name: name.trim(),
                        url: url || window.location.href,
                        description: desc || '',
                        category: cat || ''
                    });
                    if (result.success) {
                        this.renderList();
                        this.updateCount();
                        if (typeof updateFavoriteButtons === 'function') updateFavoriteButtons();
                        alert('已收藏: ' + name);
                    } else {
                        alert(result.message);
                    }
                }
            },

            // 从详情页当前展示的站点提取数据
            _getCurrentSiteData: function() {
                var siteNameEl = document.querySelector('.site-detail-header h1, .detail-title, h1.detail-name');
                var siteDescEl = document.querySelector('.site-detail-desc, .detail-desc, .detail-description p');
                var siteCatEl = document.querySelector('.breadcrumb, .site-breadcrumb, .detail-breadcrumb');
                var siteLinkEl = document.querySelector('.site-detail-header a, .detail-url a');

                var name = siteNameEl ? siteNameEl.textContent.trim() : '';
                if (!name) return null;

                return {
                    name: name,
                    url: siteLinkEl ? siteLinkEl.href : (window.location.href.split('?')[0]),
                    description: siteDescEl ? siteDescEl.textContent.trim() : '',
                    category: siteCatEl ? siteCatEl.textContent.replace(/^.+\s*>\s*/, '').trim() : ''
                };
            },

            // 从当前URL匹配已知站点
            _getSiteFromCurrentURL: function() {
                if (!window.dataManager) return null;
                var currentHost = window.location.hostname;
                var allSites = window.dataManager.getAllSites ? window.dataManager.getAllSites() : [];
                for (var i = 0; i < allSites.length; i++) {
                    try {
                        var siteUrl = new URL(allSites[i].url);
                        if (siteUrl.hostname === currentHost) {
                            return allSites[i];
                        }
                    } catch(e) {}
                }
                return null;
            },

            // ===== 更新导航栏收藏数量 =====
            updateCount: function() {
                if (!window.favoriteManager) return;
                var count = window.favoriteManager.getCount();
                var badge = document.getElementById('favorite-badge');

                if (count === 0) {
                    if (badge) badge.style.display = 'none';
                } else {
                    if (!badge) {
                        var toggleBtn = document.getElementById('favorite-toggle');
                        if (toggleBtn) {
                            badge = document.createElement('span');
                            badge.id = 'favorite-badge';
                            badge.className = 'favorite-badge';
                            toggleBtn.appendChild(badge);
                        }
                    }
                    if (badge) {
                        badge.textContent = count;
                        badge.style.display = 'block';
                    }
                }
            },

            // ===== 切换收藏按钮状态（用于详情页卡片） =====
            toggle: function(btn, name, url, description, category) {
                if (!window.favoriteManager) return;

                var isFav = window.favoriteManager.isFavorite(name);

                if (isFav) {
                    window.favoriteManager.remove(name);
                    if (btn) {
                        btn.innerHTML = '♡';
                        btn.classList.remove('favorited');
                    }
                } else {
                    window.favoriteManager.add({
                        name: name,
                        url: url || '',
                        description: description || '',
                        category: category || ''
                    });
                    if (btn) {
                        btn.innerHTML = '❤️';
                        btn.classList.add('favorited');
                    }
                }

                this.updateCount();
            },

            // ===== 初始化 =====
            init: function() {
                if (window.favoriteManager) {
                    this.updateCount();
                }
                window.toggleSiteFavorite = this.toggle.bind(this);

                // 监听收藏变化，实时更新badge
                if (window.favoriteManager) {
                    window.favoriteManager.on('favoriteAdded', function() {
                        window.favoriteUI.updateCount();
                        if (window.favoriteUI.modal && window.favoriteUI.modal.classList.contains('active')) {
                            window.favoriteUI.renderList();
                        }
                    });
                    window.favoriteManager.on('favoriteRemoved', function() {
                        window.favoriteUI.updateCount();
                        if (window.favoriteUI.modal && window.favoriteUI.modal.classList.contains('active')) {
                            window.favoriteUI.renderList();
                        }
                    });
                    window.favoriteManager.on('favoriteCleared', function() {
                        window.favoriteUI.updateCount();
                        if (window.favoriteUI.modal && window.favoriteUI.modal.classList.contains('active')) {
                            window.favoriteUI.renderList();
                        }
                    });
                    window.favoriteManager.on('favoriteImported', function() {
                        window.favoriteUI.updateCount();
                        if (window.favoriteUI.modal && window.favoriteUI.modal.classList.contains('active')) {
                            window.favoriteUI.renderList();
                        }
                    });
                }

                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Escape' && window.favoriteUI) {
                        window.favoriteUI.closeModal();
                    }
                });
            }
        };

        window.favoriteUI.init();
    }
})();