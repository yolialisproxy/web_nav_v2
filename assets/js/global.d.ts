interface Window {
    state: any;
    dataManager: any;
    favoriteManager?: any;
    favoriteUI?: any;
    Monetization?: any;
    searchEngine?: any;
    Toast?: any;
    renderer?: any;
    paginatedRenderer?: any;
    initSearchEngine: (dm: any) => void;
    getStoredJsErrors: () => any[];
    clearStoredJsErrors: () => void;
    __errorInterceptorInitialized?: boolean;
    localforage: any;
    trackSiteClick: (name: string) => void;
    renderSites: (append: boolean) => void;
}

interface HTMLElement {
    dataset: DOMStringMap;
}

declare const SearchEngine: {
    prototype: any;
    new (dm: any): any;
    highlight(text: string, query: string): string;
};

declare const StateUI: {
    loading(): string;
    error(msg: string): string;
    empty(msg: string): string;
    searchEmpty(q: string): string;
};