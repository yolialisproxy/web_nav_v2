// Global variables used in the web_nav_v2 project
import type { DataManager } from './data';
import type { State } from './state';

declare var dataManager: DataManager;
declare var toggleSearch: () => void;
declare var initTagManager: () => void;
declare var trackSiteClick: (siteId: string) => void;
declare var applyTagFilter: (tag: string) => void;
declare var updateFavoriteButtons: () => void;
declare var toggleFavorite: (siteId: string) => void;
declare var toggleSiteFavorite: (siteId: string) => void;
declare var localforage: any;
// TrackEvent is a built-in browser type, we can declare it as any for simplicity
declare var TrackEvent: any;