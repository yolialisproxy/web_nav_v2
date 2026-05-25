declare global {
  interface Window {
    Monetization: any;
    StateUI: any;
    Toast: any;
    __errorInterceptorInitialized: any;
    _globalScrollHandler: any;
    _render: any;
    applyTagFilter: any;
    cardEl: any;
    clearStoredJsErrors: any;
    dataManager: any;
    favoriteManager: any;
    favoriteUI: any;
    getStoredJsErrors: any;
    initTagManager: any;
    localforage: any;
    paginatedRenderer: any;
    render: any;
    renderer: any;
    searchEngine: any;
    state: any;
    toast: any;
    toggleFavorite: any;
    toggleSiteFavorite: any;
    trackEvent: any;
    trackSiteClick: any;
    updateFavoriteButtons: any;
    webkitAudioContext: any;
  }

  interface EventTarget {
    value?: any;
    closest?: (selector: string) => Element | null;
    style?: CSSStyleDeclaration;
    dataset?: DOMStringMap;
    src?: string;
  }

  interface Element {
    value?: any;
    closest?: (selector: string) => Element | null;
    style?: CSSStyleDeclaration;
    dataset?: DOMStringMap;
    src?: string;
  }
}
export {}