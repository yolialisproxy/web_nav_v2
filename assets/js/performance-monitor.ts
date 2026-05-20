// performance-monitor.js - 性能监控上报
(function() {
    function sendMetric(name, value, type) {
        // 使用 navigator.sendBeacon 上报（不影响页面性能）
        var data = JSON.stringify({
            name: name,
            value: value,
            type: type || 'perf',
            url: location.href,
            ts: Date.now()
        });
        if (navigator.sendBeacon) {
            var blob = new Blob([data], {type: 'application/json'});
            navigator.sendBeacon('/api/metrics', blob);
        }
    }

    // Web Vitals
    if ('PerformanceObserver' in window) {
        new PerformanceObserver(function(list) {
            list.getEntries().forEach(function(entry) {
                sendMetric('lcp', Math.round(entry.startTime + entry.duration), 'web-vital');
            });
        }).observe({type: 'largest-contentful-paint', buffered: true});

        new PerformanceObserver(function(list) {
            list.getEntries().forEach(function(entry) {
                if (!entry.hadRecentInput) {
                    sendMetric('cls', entry.value.toFixed(3), 'web-vital');
                }
            });
        }).observe({type: 'layout-shift', buffered: true});

        new PerformanceObserver(function(list) {
            var entries = list.getEntries();
            if (entries.length > 0) {
                var last = entries[entries.length - 1];
                sendMetric('fid', Math.round(last.processingStart - last.startTime), 'web-vital');
            }
        }).observe({type: 'first-input', buffered: true});
    }

    // 页面加载时间
    window.addEventListener('load', function() {
        var timing = performance.timing;
        var loadTime = timing.loadEventEnd - timing.navigationStart;
        sendMetric('page_load', loadTime, 'page');
        sendMetric('dom_ready', timing.domContentLoadedEventEnd - timing.navigationStart, 'page');
    });

    // 错误监控
    window.addEventListener('error', function(e) {
        sendMetric('js_error', e.message + ' @ ' + (e.filename || '') + ':' + (e.lineno || 0), 'error');
    });

    // 自定义事件
    window.trackEvent = function(category, action, label) {
        sendMetric(category + ':' + action, label || '', 'event');
    };
})();
