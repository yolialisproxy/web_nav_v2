/**
 * core-vitals.js - Core Web Vitals 优化脚本
 * 目标：提升 LCP、INP、CLS 到优秀水平
 */

(function (global) {
    'use strict';

    var Vitals = {
        // ===================== LCP 优化 =====================

        /**
         * 关键资源预加载
         * 在HTML头部内联调用，预加载首屏关键资源
         */
        preloadCritical: function () {
            var resources = [
                { href: 'assets/fontawesome-free-6.4.0/fonts/fa-solid-900.woff2', as: 'font', type: 'font/woff2' },
                { href: 'assets/images/logo.png', as: 'image' },
                { href: 'assets/css/core.css', as: 'style' },
            ];
            resources.forEach(function (r) {
                var link = document.createElement('link');
                link.rel = 'preload';
                link.href = r.href;
                if (r.as) link.as = r.as;
                if (r.type) link.type = r.type;
                link.crossOrigin = 'anonymous';
                document.head.appendChild(link);
            });
        },

        /**
         * 非关键JS异步/延迟加载
         * 将非首屏必需的脚本标记为defer
         */
        deferNonCritical: function () {
            // 跳过：已在HTML中设置defer，此函数仅做安全兜底
            // 如果脚本已被标记defer则跳过，避免重复
            var scripts = document.querySelectorAll('script[src]:not([defer]):not([async])');
            scripts.forEach(function (s) {
                var src = s.src || '';
                // 跳过核心脚本（必须同步）和schema
                if (/schema\.js|state\.js|data\.js/.test(src)) return;
                // 跳过已加载完成的脚本
                if (s.readyState === 'loaded' || s.readyState === 'complete') return;
                s.defer = true;
            });
        },

        // ===================== CLS 优化 =====================

        /**
         * 为所有图片设置宽高比占位
         * 防止图片加载时布局偏移
         */
        reserveImageSpace: function () {
            var images = document.querySelectorAll('img[loading="lazy"]');
            images.forEach(function (img) {
                if (!img.width && !img.style.width) {
                    img.style.width = '48px';
                    img.style.height = '48px';
                    img.style.objectFit = 'cover';
                }
                if (!img.style.aspectRatio && img.naturalWidth && img.naturalHeight) {
                    img.style.aspectRatio = img.naturalWidth + '/' + img.naturalHeight;
                }
            });
        },

        /**
         * 骨架屏保持布局稳定
         * 确保骨架屏与真实内容尺寸一致
         */
        stabilizeSkeleton: function () {
            var skeleton = document.getElementById('skeleton-screen');
            if (!skeleton) return;
            // 骨架屏动画完成后平滑移除
            setTimeout(function () {
                skeleton.style.transition = 'opacity 0.4s ease';
                skeleton.style.opacity = '0';
                setTimeout(function () {
                    skeleton.style.display = 'none';
                }, 400);
            }, 1500);
        },

        // ===================== INP 优化 =====================

        /**
         * 使用 requestIdleCallback 处理非紧急任务
         * 减少主线程阻塞
         */
        deferIdleTasks: function () {
            if ('requestIdleCallback' in global) {
                requestIdleCallback(function () {
                    // 延迟加载标签云数据
                    if (typeof initTagManager === 'function') {
                        // 已经在主流程中初始化
                    }
                    // 延迟渲染历史记录
                    if (typeof window.favoriteUI !== 'undefined') {
                        try { window.favoriteUI._lazyRender(); } catch (e) {}
                    }
                }, { timeout: 2000 });
            }
        },

        /**
         * 事件委托优化
         * 减少事件监听器数量
         */
        setupEventDelegation: function () {
            var mainContent = document.getElementById('main-content');
            if (!mainContent) return;

            // 卡片点击事件委托
            mainContent.addEventListener('click', function (e) {
                var card = e.target.closest('.site-card');
                if (card && typeof trackSiteClick === 'function') {
                    trackSiteClick(card.getAttribute('aria-label') || '');
                }
            });

            // 标签过滤委托
            mainContent.addEventListener('click', function (e) {
                var tagBtn = e.target.closest('[data-tag]');
                if (tagBtn) {
                    e.stopPropagation();
                    // 标签过滤逻辑
                    if (typeof window.applyTagFilter === 'function') {
                        window.applyTagFilter(tagBtn.getAttribute('data-tag'));
                    }
                }
            });
        },

        // ===================== 综合性能优化 =====================

        /**
         * 图片懒加载增强
         * 原生lazyloading不支持的浏览器降级
         */
        enhanceLazyLoading: function () {
            if ('IntersectionObserver' in global) {
                // 处理 data-src 图片（真正的懒加载）
                var lazyImages = document.querySelectorAll('img[data-src]');
                var observer = new IntersectionObserver(function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) {
                            var img = entry.target;
                            if (img.dataset.src) {
                                img.src = img.dataset.src;
                                img.removeAttribute('data-src');
                                img.classList.add('lazy-loaded');
                            }
                            observer.unobserve(img);
                        }
                    });
                }, { rootMargin: '200px 0px' });

                lazyImages.forEach(function (img) { observer.observe(img); });

                // 为 card-icon 添加模糊占位（CLS优化）
                document.querySelectorAll('img.card-icon').forEach(function (img) {
                    if (!img.style.width) img.style.width = '48px';
                    if (!img.style.height) img.style.height = '48px';
                    img.style.objectFit = img.style.objectFit || 'cover';
                    // 添加模糊占位背景
                    img.style.background = 'var(--color-bg-card)';
                });
            }
        },

        /**
         * 字体显示优化
         * 使用font-display: swap减少FOIT
         */
        optimizeFonts: function () {
            if ('fonts' in document) {
                document.fonts.ready.then(function () {
                    document.documentElement.classList.add('fonts-loaded');
                });
            }
        },

        /**
         * 减少未使用的JS执行
         * 动态导入非核心模块
         */
        dynamicImportFallback: function () {
            // 如果浏览器不支持动态import，使用传统加载
            if (!('noModule' in HTMLScriptElement.prototype)) {
                // 降级：同步加载polyfill
                return;
            }
            // 动态导入重量级模块
            if ('import' in global) {
                // 按需加载（示例：仅在搜索页面加载高级搜索模块）
            }
        },

        // ===================== 性能报告 =====================

        /**
         * 性能指标上报
         */
        reportMetrics: function () {
            if (!('PerformanceObserver' in global)) return;

            var metrics = {};

            // FCP
            try {
                new PerformanceObserver(function (list) {
                    var entry = list.getEntries()[0];
                    if (entry) {
                        metrics.fcp = Math.round(entry.startTime);
                        console.log('[Vitals] FCP:', metrics.fcp, 'ms');
                    }
                }).observe({ type: 'first-contentful-paint', buffered: true });
            } catch (e) {}

            // LCP
            try {
                new PerformanceObserver(function (list) {
                    var entries = list.getEntries();
                    var last = entries[entries.length - 1];
                    if (last) {
                        metrics.lcp = Math.round(last.startTime + last.duration);
                        console.log('[Vitals] LCP:', metrics.lcp, 'ms');
                    }
                }).observe({ type: 'largest-contentful-paint', buffered: true });
            } catch (e) {}

            // CLS
            try {
                var clsValue = 0;
                new PerformanceObserver(function (list) {
                    list.getEntries().forEach(function (entry) {
                        if (entry.hadRecentInput) return;
                        clsValue += entry.value;
                    });
                    console.log('[Vitals] CLS:', clsValue.toFixed(3));
                }).observe({ type: 'layout-shift', buffered: true });
            } catch (e) {}

            // INP (兼容：首次INP或回退到FID)
            try {
                new PerformanceObserver(function (list) {
                    var entries = list.getEntries();
                    if (entries.length > 0) {
                        var inp = entries[entries.length - 1];
                        metrics.inp = Math.round(inp.processingStart - inp.startTime);
                        console.log('[Vitals] INP:', metrics.inp, 'ms');
                    }
                }).observe({ type: 'first-input', buffered: true });
            } catch (e) {}

            // 10秒后上报汇总
            setTimeout(function () {
                if (metrics.lcp || metrics.fcp) {
                    console.log('[Vitals Summary]', JSON.stringify(metrics));
                    // 可在此处上报到分析系统
                }
            }, 10000);
        },

        // ===================== 初始化 =====================

        init: function () {
            this.preloadCritical();
            this.deferNonCritical();
            this.reserveImageSpace();
            this.stabilizeSkeleton();
            this.deferIdleTasks();
            this.setupEventDelegation();
            this.enhanceLazyLoading();
            this.optimizeFonts();
            this.reportMetrics();
            console.log('[CoreVitals] 性能优化已启用');
        }
    };

    global.Vitals = Vitals;

    // 在DOM Ready时初始化
    if (global.document && global.document.readyState === 'loading') {
        global.document.addEventListener('DOMContentLoaded', function () {
            Vitals.init();
        });
    } else if (global.document) {
        Vitals.init();
    }

})(typeof window !== 'undefined' ? window : this);