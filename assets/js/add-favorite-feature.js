// 收藏功能注入脚本
(function() {
    'use strict';
    
    // 等待DOM加载
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFavoriteFeature);
    } else {
        initFavoriteFeature();
    }
    
    function initFavoriteFeature() {
        // console.log('[FavoriteFeature] 初始化收藏功能...');
        
        // 确保必须对象存在
        if (!window.favoriteManager) {
            console.warn('[FavoriteFeature] favoriteManager 不存在，收藏功能无效');
            return;
        }
        
        // 添加全局切换函数
        window.toggleSiteFavorite = function(btn, siteData) {
            if (!siteData || !siteData.name) return;
            
            const isFav = window.favoriteManager.isFavorite(siteData.name);
            
            if (isFav) {
                window.favoriteManager.remove(siteData.name);
                btn.innerHTML = '♡';
                btn.classList.remove('favorited');
            } else {
                window.favoriteManager.add({
                    name: siteData.name,
                    url: siteData.url || '',
                    description: siteData.description || '',
                    category: siteData.category || ''
                });
                btn.innerHTML = '❤️';
                btn.classList.add('favorited');
            }
            
            window.favoriteUI.updateFavoriteCount();
        };
        
        // console.log('[FavoriteFeature] 功能注入完成');
    }
})();
