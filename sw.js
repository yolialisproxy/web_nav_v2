/**
 * Service Worker - 离线缓存与PWA支持
 * 缓存策略：Cache First for静态资源，Network First for数据文件
 */

const CACHE_NAME = 'webnav-v3-' + '20260512';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/assets/css/core.css',
    '/assets/css/theme-modern.css',
    '/assets/css/components.css',
    '/assets/css/responsive.css',
    '/assets/css/favorite-enhancements.css',
    '/assets/css/style.css',
    '/assets/js/state.js',
    '/assets/js/data.js',
    '/assets/js/search.js',
    '/assets/js/render.js',
    '/assets/js/tags.js',
    '/assets/js/favorite.js',
    '/assets/js/favorite-ui-bootstrap.js',
    '/assets/js/toast.js',
    '/assets/js/app.js',
];

// 安装阶段：缓存静态资源
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// 激活阶段：清理旧缓存
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys
                    .filter((key) => key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

// 请求拦截
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // 只处理同源请求
    if (url.origin !== self.location.origin) return;

    // 数据文件：Network First，失败时回退缓存
    if (url.pathname.includes('websites.json') || url.pathname.includes('data/')) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // 更新缓存
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, clone);
                    });
                    return response;
                })
                .catch(() => {
                    return caches.match(event.request);
                })
        );
        return;
    }

    // 静态资源：Cache First
    event.respondWith(
        caches.match(event.request).then((cached) => {
            if (cached) return cached;
            return fetch(event.request).then((response) => {
                // 缓存新资源
                if (response.status === 200) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, clone);
                    });
                }
                return response;
            });
        })
    );
});