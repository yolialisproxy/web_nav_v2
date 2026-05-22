"use strict";
/// <reference path="../global.d.ts" />

/**
 * data.js - 数据加载与索引管理 (V2.1)

 * 职责：加载 JSON，构建分类索引 + 标签索引，支持容错降级
 */
var __awaiter: any = (this && this.__awaiter) || function (thisArg: any, _arguments: any, P: any, generator: any) {
    function adopt(value: any) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value: any) {
            try {
                step(generator.next(value));
            }
            catch (e) {
                reject(e);
            }
        }
        function rejected(value: any) {
            try {
                step(generator["throw"](value));
            }
            catch (e) {
                reject(e);
            }
        }
        function step(result: any) {
            if (result.done) {
                resolve(result.value);
            } else {
                adopt(result.value).then(fulfilled, rejected);
            }
        }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
            } else {
                adopt(result.value).then(fulfilled, rejected);
            }
        }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
class DataManager {
            raw: any = null;
            sites: Map<number, any> = new Map();
            categories: any = {};
            mappings: Map<string, number[]> = new Map();
            tagIndex: Map<string, Set<number>> = new Map();
            tagCloud: Map<string, { tag: string; count: number; sites: string[] }> = new Map();
            isLoaded: boolean = false;
            version: any = null;
            _loadError: any = null;
            tagIndexSorted: any[] = [];
        }
var dataManager = new DataManager();
(window as any).dataManager = dataManager;
//# sourceMappingURL=data.js.map