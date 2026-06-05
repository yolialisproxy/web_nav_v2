// 测试验证函数
const fs = require('fs');
const sites = JSON.parse(fs.readFileSync('./data/websites.json', 'utf8'));

console.log(`总共 ${sites.length} 条数据`);

// 复制验证逻辑
const valid = sites.filter(site => {
    if (!site || typeof site !== 'object') {
        console.log('失败: !site || typeof site !== \'object\'', site);
        return false;
    }
    if (!site.name || typeof site.name !== 'string') {
        console.log('失败: !site.name || typeof site.name !== \'string\'', site);
        return false;
    }
    if (!site.category || typeof site.category !== 'string') {
        console.log('失败: !site.category || typeof site.category !== \'string\'', site);
        return false;
    }
    if (!site.url || typeof site.url !== 'string') {
        console.log('失败: !site.url || typeof site.url !== \'string\'', site);
        return false;
    }
    try { 
        new URL(site.url); 
    } catch (e) {
        console.log('失败: URL验证失败', site.url, e.message);
        return false;
    }
    return true;
});

console.log(`有效数据: ${valid.length}`);
console.log(`无效数据: ${sites.length - valid.length}`);

if (valid.length === 0 && sites.length > 0) {
    console.log('全部站点验证失败！');
    
    // 检查前几条数据为什么失败
    for (let i = 0; i < Math.min(5, sites.length); i++) {
        const site = sites[i];
        console.log(`\\n检查第 ${i+1} 条数据:`);
        console.log(`  site:`, !!site);
        console.log(`  typeof site:`, typeof site);
        console.log(`  site.name:`, site.name, typeof site.name);
        console.log(`  site.category:`, site.category, typeof site.category);
        console.log(`  site.url:`, site.url, typeof site.url);
        
        if (site.url) {
            try {
                new URL(site.url);
                console.log(`  URL: 有效`);
            } catch (e) {
                console.log(`  URL: 无效 - ${e.message}`);
            }
        }
    }
}

// Make this file a module to avoid redeclaration errors
export {};
