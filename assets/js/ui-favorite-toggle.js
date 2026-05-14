/**
 * ui-favorite-toggle.js - 收藏切换UI控制
 * 功能：卡片收藏按钮和弹窗管理
 */

class FavoriteUI {
    constructor() {
        this.modal = null;
        this.favoriteList = null;
        this.init();
    }

    init() {
        this.createModal();
        this.bindGlobalEvents();
        this.updateFavoriteCount();

        // // // // console.log('[FavoriteUI] UI控制初始化完成');
    }

    createModal() {
        const modalHTML = `
            <div id="favorite-modal" class="modal-overlay" style="display: none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>我的收藏</h3>
                        <button class="modal-close" onclick="favoriteUI.closeModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div id="favorite-count" class="favorite-count">总计 0 个</div>
                        <div id="favorite-list" class="favorite-list"></div>
                        <div id="favorite-empty" class="favorite-empty">
                            <p>📁 还没有收藏任何站点</p>
                            <p>去浏览并收藏你喜欢的网站吧！</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-primary" onclick="favoriteUI.clearAll()" id="clear-favorites" style="display: none;">
                            🗑️ 清空所有
                        </button>
                        <button class="btn btn-secondary" onclick="favoriteUI.exportFavorites()">
                            📋 导出数据
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        this.modal = document.getElementById('favorite-modal');
        this.favoriteList = document.getElementById('favorite-list');

        // 绑定全局函数
        window.favoriteUI = this;
    }

    bindGlobalEvents() {
        // 监听收藏变化
        favoriteManager.on('favoriteAdded', () => this.updateFavoriteCount());
        favoriteManager.on('favoriteRemoved', () => this.updateFavoriteCount());
        favoriteManager.on('favoriteCleared', () => this.updateFavoriteCount());
    }

    // 创建收藏按钮
    createFavoriteButton(site) {
        const isFav = favoriteManager.isFavorite(site.name);
        const button = document.createElement('button');
        button.className = `favorite-btn ${isFav ? 'favorited' : ''}`;
        button.innerHTML = isFav ? '❤️' : '♡';
        button.title = isFav ? '取消收藏' : '收藏该站点';
        button.onclick = (e) => {
            e.stopPropagation();
            this.toggleFavorite(site, button);
        };
        return button;
    }

    // 切换收藏状态
    toggleFavorite(site, button) {
        if (favoriteManager.isFavorite(site.name)) {
            favoriteManager.remove(site.name);
            if (button) {
                button.innerHTML = '♡';
                button.classList.remove('favorited');
                button.title = '收藏该站点';
            }
            this.showToast('已取消收藏');
        } else {
            favoriteManager.add(site);
            if (button) {
                button.innerHTML = '❤️';
                button.classList.add('favorited');
                button.title = '取消收藏';
            }
            this.showToast('收藏成功！');
        }

        // 在站点详情页更新按钮
        this.updateDetailPageButton(site.name, favoriteManager.isFavorite(site.name));
    }

    // 更新详情页按钮
    updateDetailPageButton(siteName, isFav) {
        const detailBtn = document.getElementById('favorite-detail-btn');
        if (detailBtn) {
            if (isFav) {
                detailBtn.innerHTML = '❤️ 取消收藏';
            } else {
                detailBtn.innerHTML = '♡ 收藏该站点';
            }
        }
    }

    // 打开收藏弹窗
    openModal() {
        this.renderList();
        this.modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    // 关闭弹窗
    closeModal() {
        this.modal.style.display = 'none';
        document.body.style.overflow = '';
    }

    // 渲染收藏列表
    renderList() {
        const favorites = favoriteManager.getAll();
        const count = favoriteManager.getCount();

        document.getElementById('favorite-count').textContent = `总计 ${count} 个`;

        if (count === 0) {
            this.favoriteList.style.display = 'none';
            document.getElementById('favorite-empty').style.display = 'block';
            document.getElementById('clear-favorites').style.display = 'none';
        } else {
            this.favoriteList.style.display = 'block';
            document.getElementById('favorite-empty').style.display = 'none';
            document.getElementById('clear-favorites').style.display = 'block';

            this.favoriteList.innerHTML = favorites.map(site => `
                <div class="favorite-item">
                    <a href="javascript:void(0)" onclick="window.location.href='pages/site-detail.html?name=${encodeURIComponent(site.name)}'">
                        <div class="fav-site-info">
                            <div class="fav-site-name">${site.name}</div>
                            <div class="fav-site-category">${site.category}</div>
                            <div class="fav-site-desc">${site.description || '暂无描述'}</div>
                        </div>
                    </a>
                    <button class="fav-remove-btn" onclick="event.stopPropagation(); favoriteUI.removeFavorite('${site.name}')">&times;</button>
                </div>
            `).join('');
        }
    }

    // 移除单个收藏
    removeFavorite(siteName) {
        favoriteManager.remove(siteName);
        this.renderList();
        this.showToast('已移除收藏');
    }

    // 清空收藏
    clearAll() {
        if (confirm('确定要清空所有收藏吗？')) {
            favoriteManager.clear();
            this.renderList();
            this.showToast('已清空收藏');
        }
    }

    // 导出收藏
    exportFavorites() {
        const data = favoriteManager.export();
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `webnav-favorites-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        this.showToast('导出成功！');
    }

    // 显示提示
    showToast(message) {
        // 移除已有的toast
        const existing = document.querySelector('.toast-notification');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translate(-50%, 0)';
        }, 10);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translate(-50%, -20px)';
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }

    // 更新收藏计数
    updateFavoriteCount() {
        const count = favoriteManager.getCount();
        let badge = document.getElementById('favorite-badge');

        if (count === 0) {
            if (badge) badge.remove();
        } else {
            if (!badge) {
                // 创建计数badge
                const toggleBtn = document.getElementById('favorite-toggle');
                if (toggleBtn) {
                    badge = document.createElement('span');
                    badge.id = 'favorite-badge';
                    badge.className = 'favorite-badge';
                    toggleBtn.appendChild(badge);
                }
            }
            if (badge) {
                badge.textContent = count;
            }
        }
    }
}

// CSS样式
const favoriteCSS = `
/* 收藏按钮 */
.favorite-btn {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    font-size: 18px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin-left: 12px !important;
}

.favorite-btn:hover {
    background: rgba(124, 58, 237, 0.3) !important;
    transform: scale(1.15) !important;
    border-color: var(--accent-primary) !important;
}

.favorite-btn.favorited {
    background: rgba(124, 58, 237, 0.2) !important;
    color: #ff6b9d !important;
    border-color: rgba(255, 107, 157, 0.5) !important;
    animation: favoritePulse 0.5s ease;
}

@keyframes favoritePulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.3); }
    100% { transform: scale(1.15); }
}

/* 收藏弹窗 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8) !important;
    backdrop-filter: blur(10px) !important;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.modal-content {
    background: linear-gradient(135deg, rgba(20, 20, 35, 0.95), rgba(10, 10, 20, 0.98)) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px !important;
    padding: 0 !important;
    width: 90% !important;
    max-width: 600px !important;
    max-height: 80vh !important;
    overflow: hidden !important;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5) !important;
}

.modal-header {
    padding: 20px 24px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
}

.modal-header h3 {
    color: #fff !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

.modal-close {
    background: none !important;
    border: none !important;
    color: rgba(255, 255, 255, 0.6) !important;
    font-size: 28px !important;
    cursor: pointer !important;
    padding: 0 !important;
    width: 40px !important;
    height: 40px !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.3s ease !important;
}

.modal-close:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #fff !important;
}

.modal-body {
    padding: 24px !important;
    overflow-y: auto !important;
    max-height: 50vh !important;
}

.favorite-count {
    color: rgba(255, 255, 255, 0.6) !important;
    font-size: 14px !important;
    margin-bottom: 16px !important;
}

.favorite-list {
    display: flex;
    flex-direction: column;
    gap: 12px !important;
}

.favorite-item {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    transition: all 0.3s ease !important;
}

.favorite-item:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    transform: translateX(4px) !important;
}

.fav-site-info {
    flex: 1 !important;
    margin-right: 12px !important;
}

.fav-site-name {
    color: #fff !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    margin-bottom: 4px !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}

.fav-site-category {
    color: var(--accent-secondary) !important;
    font-size: 12px !important;
    margin-bottom: 6px !important;
}

.fav-site-desc {
    color: rgba(255, 255, 255, 0.5) !important;
    font-size: 12px !important;
    line-height: 1.5 !important;
    display: -webkit-box !important;
    -webkit-line-clamp: 2 !important;
    -webkit-box-orient: vertical !important;
    overflow: hidden !important;
}

.fav-remove-btn {
    background: none !important;
    border: none !important;
    color: rgba(255, 255, 255, 0.4) !important;
    font-size: 20px !important;
    cursor: pointer !important;
    padding: 4px !important;
    border-radius: 4px !important;
    transition: all 0.3s ease !important;
    flex-shrink: 0 !important;
}

.fav-remove-btn:hover {
    color: #ff6b6b !important;
    background: rgba(255, 107, 107, 0.1) !important;
}

.favorite-empty {
    text-align: center !important;
    padding: 40px 20px !important;
    color: rgba(255, 255, 255, 0.4) !important;
}

.favorite-empty p {
    margin: 12px 0 !important;
    font-size: 14px !important;
}

.modal-footer {
    padding: 16px 24px !important;
    border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
    display: flex !important;
    justify-content: flex-end !important;
    gap: 12px !important;
}

.btn {
    padding: 10px 20px !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

.btn-primary {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
    color: #fff !important;
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #fff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(124, 58, 237, 0.3) !important;
}

.favorite-badge {
    position: absolute !important;
    top: -8px !important;
    right: -8px !important;
    background: #ff6b9d !important;
    color: #fff !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    min-width: 18px !important;
    height: 18px !important;
    border-radius: 9px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 4px !important;
}

.toast-notification {
    position: fixed !important;
    top: 20px !important;
    left: 50% !important;
    transform: translate(-50%, -20px) !important;
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.95), rgba(167, 139, 250, 0.95)) !important;
    color: #fff !important;
    padding: 12px 24px !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    z-index: 1001 !important;
    box-shadow: 0 8px 30px rgba(124, 58, 237, 0.4) !important;
    opacity: 0 !important;
    transition: all 0.3s ease !important;
}
`;

// 注册CSS
const style = document.createElement('style');
style.textContent = favoriteCSS;
document.head.appendChild(style);

// // // // console.log('[FavoriteUI] CSS注册完成');
