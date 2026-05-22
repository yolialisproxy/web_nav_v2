"use strict";
/// <reference path="../global.d.ts" />
/**
 * data.js - 数据加载与索引管理 (V2.1)

 * 职责：加载 JSON，构建分类索引 + 标签索引，支持容错降级
 */
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) {
            try {
                step(generator.next(value));
            }
            catch (e) {
                reject(e);
            }
        }
        function rejected(value) {
            try {
                step(generator["throw"](value));
            }
            catch (e) {
                reject(e);
            }
        }
        function step(result) {
            if (result.done) {
                resolve(result.value);
            }
            else {
                adopt(result.value).then(fulfilled, rejected);
            }
        }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
class DataManager {
    constructor() {
        this.raw = null;
        this.sites = new Map();
        this.categories = {};
        this.mappings = new Map();
        this.tagIndex = new Map();
        this.tagCloud = new Map();
        this.isLoaded = false;
        this.version = null;
        this._loadError = null;
        this.tagIndexSorted = [];
    }
}
var dataManager = new DataManager();
window.dataManager = dataManager;
//# sourceMappingURL=data.js.map