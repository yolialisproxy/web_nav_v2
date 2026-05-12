// favorite-ui-bootstrap.js - 收藏UI启动脚本
(function() {
    'use strict';
    
    // 创建全局的收藏UI实例
    if (!window.favoriteUI) {
        // 从favorite-toggle.js动态创建实例
        // 这里使用简化版本
        window.favoriteUI = {
            modal: document.getElementById('favorite-modal'),
            favoriteList: document.getElementById('favorite-list'),
            
            openModal: function() {
                if (this.modal) {
                    this.modal.style.display = 'flex';
                    this.renderList();
                }
            },
            
            closeModal: function() {
                if (this.modal) {
                    this.modal.style.display = 'none';
                }
            },
            
            renderList: function() {
                if (!this.favoriteList || !window.favoriteManager) return;
                
                const favorites = window.favoriteManager.getAll();
                const count = window.favoriteManager.getCount();
                const countEl = document.getElementById('favorite-count');
                const emptyEl = document.getElementById('favorite-empty');
                const clearBtn = document.getElementById('clear-favorites');
                
                if (countEl) countEl.textContent = `总计 ${count} 个`;
                
                if (count === 0) {
                    if (this.favoriteList) this.favoriteList.style.display = 'none';
                    if (emptyEl) emptyEl.style.display = 'block';
                    if (clearBtn) clearBtn.style.display = 'none';
                } else {
                    if (this.favoriteList) {
                        this.favoriteList.style.display = 'block';
                        this.favoriteList.innerHTML = favorites.map(function(site) {
                            return '<div class="favorite-item">'
                                + '<a href="pages/site-detail.html?name=' + encodeURIComponent(site.name) + '" style="flex:1;margin-right:12px;text-decoration:none;">'
                                + '<div class="fav-site-name">' + site.name + '</div>'
                                + '<div class="fav-site-category">' + (site.category || '') + '</div>'
                                + '<div class="fav-site-desc">' + (site.description || '暂无描述') + '</div>'
                                + '</a>'
                                + '<button class="fav-remove-btn" onclick="event.stopPropagation();if(window.favoriteManager){window.favoriteManager.remove(\'' + site.name.replace(/'/g, "\\'") + '\');if(window.favoriteUI){window.favoriteUI.renderList();}}" style="margin-left:12px;">&times;</button>'
                                + '</div>';
                        }).join('');
                    }
                    if (emptyEl) emptyEl.style.display = 'none';
                    if (clearBtn) clearBtn.style.display = 'block';
                }
            },
            
            clearAll: function() {
                if (window.favoriteManager && confirm('确定要清空所有收藏吗？')) {
                    window.favoriteManager.clear();
                    this.renderList();
                    this.updateCount();
                }
            },
            
            exportFavorites: function() {
                if (!window.favoriteManager) return;
                try {
                    var data = window.favoriteManager.export();
                    var blob = new Blob([data], { type: 'application/json' });
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
            
            toggleFavorite: function(btn, siteData) {
                if (!window.favoriteManager || !siteData) return;
                
                var isFav = window.favoriteManager.isFavorite(siteData.name);
                
                if (isFav) {
                    window.favoriteManager.remove(siteData.name);
                    if (btn) {
                        btn.innerHTML = '♡';
                        btn.classList.remove('favorited');
                    }
                } else {
                    window.favoriteManager.add({
                        name: siteData.name,
                        url: siteData.url || '',
                        description: siteData.description || '',
                        category: siteData.category || ''
                    });
                    if (btn) {
                        btn.innerHTML = '❤️';
                        btn.classList.add('favorited');
                    }
                }
                
                this.updateCount();
            },
            
            init: function() {
                // 监听收藏变化
                if (window.favoriteManager) {
                    // 初始计数
                    this.updateCount();
                    // console.log('[FavoriteUI] UI启动完成');
                }
                
                // 绑定全局函数供按钮调用
                window.toggleSiteFavorite = this.toggleFavorite.bind(this);
            }
        };
        
        // 启动UI
        window.favoriteUI.init();
    }
})();
