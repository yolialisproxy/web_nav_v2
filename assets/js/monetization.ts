/**
 * monetization.js - 盈利模式脚本
 * 功能：广告管理、推荐站点展示、CTA横幅、数据上报
 */

(function (global) {
    'use strict';

    var Monetization = {
        // 是否启用盈利模式（上线后设为true）
        enabled: false,

        // Google AdSense client ID（上线时替换为真实ID）
        adsenseClientId: null,

        // 推荐站点（联盟营销）
        recommendedSites: [
            { name: 'Vercel', url: 'https://vercel.com', desc: '前端部署平台', icon: '🚀' },
            { name: 'Railway', url: 'https://railway.app', desc: '全栈云服务平台', icon: '🌐' },
            { name: 'GitHub', url: 'https://github.com', desc: '代码托管与协作', icon: '🐙' },
            { name: 'Notion', url: 'https://notion.so', desc: '全能笔记与协作', icon: '📝' },
            { name: 'Figma', url: 'https://figma.com', desc: 'UI设计协作工具', icon: '🎨' },
            { name: 'Cursor', url: 'https://cursor.sh', desc: 'AI代码编辑器', icon: '💻' },
            { name: 'Whisper', url: 'https://openai.com/research/whisper', desc: '语音识别模型', icon: '🎙️' }
        ],

        init: function (options) {
            if (options) {
                this.enabled = options.enabled || false;
                this.adsenseClientId = options.adsenseClientId || null;
            }
            this._injectStyles();
            this._renderRecommended();
            this._renderCTABanner();
            this._setupPerformanceObserver();
        },

        // 注入盈利模式样式
        _injectStyles: function () {
            var existing = document.getElementById('monetization-styles');
            if (existing) return;
            var css = document.createElement('link');
            css.id = 'monetization-styles';
            css.rel = 'stylesheet';
            css.href = 'assets/css/monetization.css';
            document.head.appendChild(css);
        },

        // 在侧边栏渲染推荐站点
        _renderRecommended: function () {
            var sidebar = document.getElementById('sidebar-content');
            if (!sidebar || !this.recommendedSites.length) return;

            var html = '<div class="recommended-section">' +
                '<h3>🔥 推荐工具</h3>' +
                '<div class="recommended-grid">';

            this.recommendedSites.forEach(function (site) {
                html += '<a href="' + site.url + '" target="_blank" rel="noopener sponsored noreferrer" ' +
                    'class="recommended-item" data-track="recommended-click" data-name="' + site.name + '">' +
                    '<div class="rec-icon">' + site.icon + '</div>' +
                    '<div class="rec-name">' + site.name + '</div>' +
                    '</a>';
            });

            html += '</div></div>';

            // 插入到侧边栏导航下方
            var nav = sidebar.querySelector('nav') || sidebar;
            nav.insertAdjacentHTML('beforeend', html);
        },

        // CTA横幅（顶部或底部）
        _renderCTABanner: function () {
            var header = document.getElementById('header');
            if (!header || !this.enabled) return;

            var banner = document.createElement('div');
            banner.className = 'cta-banner';
            banner.innerHTML =
                '<h3>🔧 发现更好的开发工具</h3>' +
                '<p>我们精心筛选了数千个优质工具，助你效率倍增</p>' +
                '<a href="https://vercel.com" target="_blank" rel="noopener sponsored noreferrer" class="cta-btn" ' +
                'data-track="cta-click">立即体验推荐工具 →</a>';

            header.parentNode.insertBefore(banner, header);
        },

        // 性能监控上报
        _setupPerformanceObserver: function () {
            if (!global.PerformanceObserver) return;

            try {
                var observer = new PerformanceObserver(function (list) {
                    list.getEntries().forEach(function (entry) {
                        if (entry.name === 'first-contentful-paint' || entry.name === 'largest-contentful-paint') {
                            // 上报到分析系统
                            // // console.log('[Perf]', entry.name, ':', Math.round(entry.startTime), 'ms');
                        }
                    });
                });
                observer.observe({ type: 'paint', buffered: true });

                // LCP 监控
                var lcpObserver = new PerformanceObserver(function (list) {
                    var entries = list.getEntries();
                    var last = entries[entries.length - 1];
                    if (last) {
                        // // console.log('[LCP]', Math.round(last.startTime + last.duration), 'ms');
                    }
                });
                lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
            } catch (e) {
                // 静默失败
            }
        },

        // 事件追踪
        trackEvent: function (category, action, label) {
            if (!this.enabled) return;
            // // console.log('[Track]', category, action, label);
            // 接入 Google Analytics 或其他统计工具
        }
    };

    global.Monetization = Monetization;

    // DOM Ready 自动初始化
    if (global.document && global.document.readyState !== 'loading') {
        setTimeout(function () { Monetization.init(); }, 100);
    } else {
        global.document.addEventListener('DOMContentLoaded', function () {
            Monetization.init();
        });
    }

})(typeof window !== 'undefined' ? window : this);