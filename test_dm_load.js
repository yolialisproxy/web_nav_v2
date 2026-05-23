"use strict";
// 测试DataManager的load方法是否真的设置isLoaded
const fs = require('fs');
const { JSDOM } = require('jsdom');
// 创建一个简单的DOM环境
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
global.window = dom.window;
global.document = window.document;
// 现在加载我们的JavaScript文件
const dataJs = fs.readFileSync('./assets/js/data.js', 'utf8');
const stateJs = fs.readFileSync('./assets/js/state.js', 'utf8');
// 执行这些脚本以创建全局对象
eval(dataJs);
eval(stateJs);
console.log('全局对象创建完成');
console.log(`window.dataManager存在: ${!!window.dataManager}`);
console.log(`window.state存在: ${!!window.state}`);
if (window.dataManager) {
    console.log(`初始isLoaded: ${window.dataManager.isLoaded}`);
    console.log(`初始raw: ${window.dataManager.raw}`);
}
// 现在测试加载
(async () => {
    try {
        console.log('开始调用dataManager.load()...');
        await window.dataManager.load();
        console.log('dataManager.load()调用完成');
        console.log(`加载后isLoaded: ${window.dataManager.isLoaded}`);
        console.log(`加载后raw长度: ${window.dataManager.raw ? window.dataManager.raw.length : 0}`);
        console.log(`加载后sites大小: ${window.dataManager.sites.size}`);
        // 同时检查state
        if (window.state) {
            const stateSites = window.state.get('sites');
            console.log(`state.sites: ${stateSites ? stateSites.length : 0} 条`);
        }
    }
    catch (e) {
        console.error('加载过程中发生错误:', e);
    }
})();
//# sourceMappingURL=test_dm_load.js.map