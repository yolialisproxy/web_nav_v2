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
    stop(): void 
  };
};
declare var _isRecent: (key: any) => boolean;

interface FavoriteManager {
  listeners: any[];
  key: string;
  visitKey: string;
  _memoryFavorites: any;
  _memoryVisits: any;
  isFavorite(id: number): boolean;
  getVisitCount(id: number): number;
  // 其他方法...
}

// Utility namespaces
declare var render: any;
declare var search: any;

// DOM utility globals from external libs ( Stripe, etc )
declare var Stripe: any;

// Global functions
declare function initTagManager(): void;
declare function trackSiteClick(): void;
declare function updateFavoriteButtons(): void;
declare function toggleFavorite(): void;
declare function toggleSiteFavorite(): void;
declare function trackEvent(): void;

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
  initTagManager?: () => void;
  trackSiteClick?: () => void;
  updateFavoriteButtons?: () => void;
  toggleFavorite?: () => void;
  toggleSiteFavorite?: () => void;
  trackEvent?: () => void;
  GameHub?: {
    currentGame: string | null;
    stop(gameKey: string): void;
  };
}

declare var localforage: any;
