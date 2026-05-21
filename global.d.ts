// Global type declarations for web_nav_v2
// Any properties not yet typed are declared any to reduce noise during migration

declare var localStorage: Storage;
declare var sessionStorage: Storage;

// Data manager and state globals
declare var dataManager: any;
declare var appState: any;
declare var state: any;

// Favorites and game globals
declare var favoriteManager: any;
declare var games: any;

// Utility namespaces
declare var render: any;
declare var search: any;

// DOM utility globals from external libs ( Stripe, etc )
declare var Stripe: any;

interface Window {
  dataManager?: any;
  appState?: any;
  favoriteManager?: any;
  games?: any;
  render?: any;
  search?: any;
  localforage?: any;
}
