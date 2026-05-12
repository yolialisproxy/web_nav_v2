/**
 * init-favorites.js - 收藏功能初始化
 * 必须在favorite.js和favorite-ui-bootstrap.js之后加载
 */

(function() {
    'use strict';
    
    function initFavoriteFeature() {
        // console.log('[FavoriteFeature] Initializing...');
        
        // 检查核心组件
        if (!window.favoriteManager) {
            console.error('[FavoriteFeature] ERROR: favoriteManager not found!');
            return;
        }
        
        if (!window.favoriteUI) {
            // console.log('[FavoriteFeature] Creating default UI...');
            
            // 创建基础UI
            window.favoriteUI = {
                modal: document.getElementById('favorite-modal'),
                favoriteList: document.getElementById('favorite-list'),
                
                open: function() {
                    if (this.modal) {
                        this.modal.style.display = 'flex';
                        this.render();
                    }
                },
                
                close: function() {
                    if (this.modal) {
                        this.modal.style.display = 'none';
                    }
                },
                
                render: function() {
                    if (!this.favoriteList) return;
                    
                    var favorites = window.favoriteManager.getAll();
                    var countEl = document.getElementById('favorite-count');
                    var emptyEl = document.getElementById('favorite-empty');
                    var clearBtn = document.getElementById('clear-favorites');
                    
                    if (countEl) {
                        countEl.textContent = 'Total: ' + favorites.length + ' items';
                    }
                    
                    if (favorites.length === 0) {
                        if (this.favoriteList) this.favoriteList.style.display = 'none';
                        if (emptyEl) emptyEl.style.display = 'block';
                        if (clearBtn) clearBtn.style.display = 'none';
                    } else {
                        if (this.favoriteList) {
                            this.favoriteList.style.display = 'block';
                            this.favoriteList.innerHTML = favorites.map(function(item) {
                                var cat = item.category || 'Uncategorized';
                                var desc = item.description || 'No description';
                                return '<div class="favorite-item">'
                                    + '<a href="pages/site-detail.html?name=' + encodeURIComponent(item.name) + '" style="flex:1;text-decoration:none;">'
                                    + '<span class="fav-site-name">' + item.name + '</span>'
                                    + '<span class="fav-site-category">' + cat + '</span>'
                                    + '<span class="fav-site-desc">' + desc + '</span>'
                                    + '</a>'
                                    + '<button class="fav-remove-btn" onclick="event.stopPropagation();window.favoriteManager.remove(\'' + item.name.replace(/'/g, "\\'") + '\');window.favoriteUI.render();window.updateFavoriteButtons();" style="margin-left:8px;">&times;</button>'
                                    + '</div>';
                            }).join('');
                        }
                        if (emptyEl) emptyEl.style.display = 'none';
                        if (clearBtn) clearBtn.style.display = 'block';
                    }
                },
                
                clear: function() {
                    if (confirm('Clear all favorites?')) {
                        window.favoriteManager.clear();
                        this.render();
                        updateFavoriteButtons();
                    }
                },
                
                exportData: function() {
                    try {
                        var data = JSON.stringify({
                            version: '2.0',
                            exportedAt: new Date().toISOString(),
                            count: window.favoriteManager.getCount(),
                            favorites: window.favoriteManager.getAll()
                        }, null, 2);
                        
                        var blob = new Blob([data], {type: 'application/json'});
                        var url = URL.createObjectURL(blob);
                        var a = document.createElement('a');
                        a.href = url;
                        a.download = 'webnav-favorites-' + new Date().toISOString().split('T')[0] + '.json';
                        a.click();
                        URL.revokeObjectURL(url);
                    } catch(e) {
                        console.error('Export failed:', e);
                    }
                },
                
                updateCount: function() {
                    var count = window.favoriteManager.getCount();
                    var badge = document.getElementById('favorite-badge');
                    
                    if (count === 0) {
                        if (badge) badge.style.display = 'none';
                    } else {
                        if (!badge) {
                            var toggle = document.getElementById('favorite-toggle');
                            if (toggle) {
                                badge = document.createElement('span');
                                badge.id = 'favorite-badge';
                                badge.className = 'favorite-badge';
                                toggle.appendChild(badge);
                            }
                        }
                        if (badge) {
                            badge.textContent = count;
                            badge.style.display = 'block';
                        }
                    }
                },
                
                toggle: function(element, name, url, description, category) {
                    if (window.favoriteManager.isFavorite(name)) {
                        window.favoriteManager.remove(name);
                        if (element) {
                            element.innerHTML = '♡';
                            element.classList.remove('favorited');
                        }
                    } else {
                        window.favoriteManager.add({
                            name: name,
                            url: url,
                            description: description || '',
                            category: category || ''
                        });
                        if (element) {
                            element.innerHTML = '❤️';
                            element.classList.add('favorited');
                        }
                    }
                    this.updateCount();
                }
            };
        }
        
        // 全局函数
        window.toggleFavorite = function(element, name, url, description, category) {
            if (window.favoriteUI && window.favoriteManager) {
                window.favoriteUI.toggle(element, name, url, description, category);
                updateFavoriteButtons();
            }
        };
        
        window.updateFavoriteButtons = function() {
            document.querySelectorAll('.favorite-btn').forEach(function(btn) {
                var container = btn.closest('.site-card-container, .site-card');
                var titleEl = container ? container.querySelector('.card-title, .fav-site-name') : null;
                if (titleEl && window.favoriteManager) {
                    var isFav = window.favoriteManager.isFavorite(titleEl.textContent.trim());
                    btn.innerHTML = isFav ? '❤️' : '♡';
                    btn.classList.toggle('favorited', isFav);
                }
            });
        };
        
        // 启动
        window.favoriteUI.updateCount();
        
        // 其他页面的按钮初始化
        setTimeout(function() {
            document.querySelectorAll('.site-card a[href*="site-detail"]').forEach(function(link) {
                link.addEventListener('click', function(e) {
                    // 确保在详情页也能更新按钮
                    setTimeout(updateFavoriteButtons, 100);
                });
            });
        }, 500);
        
        // console.log('[FavoriteFeature] Initialized successfully!');
        // console.log('[FavoriteFeature] Current count:', window.favoriteManager.getCount());
    }
    
    // 延迟初始化确保DOM准备就绪
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFavoriteFeature);
    } else {
        setTimeout(initFavoriteFeature, 100);
    }
})();
