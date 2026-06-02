// Global type declarations for web_nav_v2
// Any properties not yet typed are declared any to reduce noise during migration

declare var localStorage: Storage;
declare var sessionStorage: Storage;

// Data manager and state globals
declare var dataManager: any;
declare var appState: any;
declare var state: any;

// Favorites and game globals
declare var favoriteManager: FavoriteManager;
declare var games: {
  [key: string]: { 
    name: string; 
    icon: string; 
    desc: string; 
    cat: string; 
    rating: number; 
    constructor: any;
    stop?: () => void;
  };
};
declare var _isRecent: (key: any) => boolean;

interface FavoriteManager {
  listeners: { [key: string]: any[] };
  key: string;
  visitKey: string;
  _memoryFavorites: any;
  _memoryVisits: any;
  favorites: any[];
  visitCounts: any;
  isFavorite(siteName: string): boolean;
  getVisitCount(siteName: string): number;
  // 其他方法...
}

// Utility namespaces
declare var render: any;
declare var search: any;

// DOM utility globals from external libs ( Stripe, etc )
declare var Stripe: any;

// Global functions
declare function updateFavoriteButtons(): void;
declare function updateFavoriteButtons(element: any, name: string, url: string, description: string, category: string): void;
declare function toggleFavorite(): void;
declare function toggleFavorite(element: any, name: string, url: string, description: string, category: string): void;
declare function toggleSiteFavorite(): void;
declare function trackEvent(): void;
declare function applyTagFilter(tag: string): void;
declare function initTagManager(): void;
declare function trackSiteClick(label: string): void;

// PerformanceEntry extensions
interface PerformanceEntry {
  fcp?: number;
  lcp?: number;
  inp?: number;
  processingStart?: number;
  hadRecentInput?: boolean;
  value?: number;
}

// Extend Window
interface Window {
  dataManager?: any;
  appState?: any;
  favoriteManager?: any;
  games?: any;
  render?: any;
  search?: any;
  localforage?: any;
  GameEngine?: any;
  GameUtils?: any;
  GameHub?: any;
  Tetris?: any;
  initTagManager?: () => void;
  trackSiteClick?: (label: string) => void;
  updateFavoriteButtons?: { (): void; (element: any, name: string, url: string, description: string, category: string): void; };
  toggleFavorite?: { (): void; (element: any, name: string, url: string, description: string, category: string): void; };
  toggleSiteFavorite?: () => void;
  trackEvent?: () => void;
  applyTagFilter?: (tag: string) => void;
}

declare var localforage: any;

// Game utils
declare var GameUtils: any;

// UI and data managers
declare var favoriteUI: any;

// Tetris game - declared as any to support legacy JS patterns
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare var Tetris: any;