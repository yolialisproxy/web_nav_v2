// 错误拦截器 - 捕获所有浏览器错误并存储到localStorage
(function() {
    // 检查是否已经初始化
    if (window.__errorInterceptorInitialized) {
        return;
    }
    window.__errorInterceptorInitialized = true;
    
    // 错误存储键
    const ERROR_STORAGE_KEY = 'web_nav_v2_js_errors';
    const MAX_ERRORS = 50; // 最多存储50个错误
    
    // 获取现有错误或初始化空数组
    function getStoredErrors() {
        try {
            const stored = localStorage.getItem(ERROR_STORAGE_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            // 如果解析失败，返回空数组
            return [];
        }
    }
    
    // 存储错误
    function storeError(errorInfo) {
        try {
            const errors = getStoredErrors();
            errors.push({
                timestamp: new Date().toISOString(),
                ...errorInfo
            });
            
            // 保持错误数量在限制内
            if (errors.length > MAX_ERRORS) {
                errors.splice(0, errors.length - MAX_ERRORS);
            }
            
            localStorage.setItem(ERROR_STORAGE_KEY, JSON.stringify(errors));
        } catch (e) {
            // 如果存储失败，静默失败以避免递归错误
            console.error('Failed to store error:', e);
        }
    }
    
    // 捕获未处理的Promise rejection
    window.addEventListener('unhandledrejection', function(event) {
        storeError({
            type: 'unhandledrejection',
            message: event.reason ? (event.reason.message || String(event.reason)) : 'Unknown promise rejection',
            stack: event.reason && event.reason.stack ? event.reason.stack : undefined,
            promise: event.promise
        });
    });
    
    // 捕获全局错误
    window.addEventListener('error', function(event) {
        storeError({
            type: 'error',
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            stack: event.error && event.error.stack ? event.error.stack : undefined
        });
        
        // 让浏览器处理默认行为（返回false不会阻止默认处理）
        return false;
    });
    
    // 提供获取错误的方法
    window.getStoredJsErrors = function() {
        return getStoredErrors();
    };
    
    // 提供清除错误的方法
    window.clearStoredJsErrors = function() {
        localStorage.removeItem(ERROR_STORAGE_KEY);
    };
    
    console.log('JavaScript error interceptor initialized');
})();