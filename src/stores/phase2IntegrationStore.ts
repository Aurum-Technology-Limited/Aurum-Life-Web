/**
 * Phase 2 Integration Store
 * Manages all Phase 2 advanced features and their state
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { realTimeDataService, DataSyncEvent } from '../services/realTimeDataService';
import { advancedAnalyticsService, AIInsight, ProductivityMetrics, PillarHealth } from '../services/advancedAnalyticsService';
import { smartSearchService, SearchResult, SearchSuggestion } from '../services/smartSearchService';
import { pwaEnhancementService, PWACapabilities, OfflineData } from '../services/pwaEnhancementService';

interface Phase2State {
  // Real-time Data Sync
  isOnline: boolean;
  syncStatus: 'idle' | 'syncing' | 'error' | 'success';
  pendingChanges: number;
  lastSyncTime: string | null;
  
  // Advanced Analytics
  productivityMetrics: ProductivityMetrics | null;
  pillarHealthData: PillarHealth[];
  aiInsights: AIInsight[];
  analyticsLoading: boolean;
  
  // Smart Search
  searchResults: SearchResult[];
  searchSuggestions: SearchSuggestion[];
  searchLoading: boolean;
  searchHistory: string[];
  
  // PWA Features
  pwaCapabilities: PWACapabilities;
  installPromptAvailable: boolean;
  offlineDataSize: number;
  connectionStatus: 'online' | 'offline' | 'unstable';
  
  // UI State
  showInstallPrompt: boolean;
  showOfflineBanner: boolean;
  showSyncStatus: boolean;
}

interface Phase2Actions {
  // Real-time Data Sync Actions
  initializeRealTimeSync: () => void;
  publishDataChange: (event: Omit<DataSyncEvent, 'timestamp' | 'source'>) => void;
  setSyncStatus: (status: Phase2State['syncStatus']) => void;
  setOnlineStatus: (isOnline: boolean) => void;
  
  // Advanced Analytics Actions
  loadAnalytics: () => Promise<void>;
  generateInsights: () => Promise<void>;
  dismissInsight: (insightId: string) => void;
  trackAnalyticsEvent: (category: string, value: number, metadata?: Record<string, any>) => void;
  
  // Smart Search Actions
  performSearch: (query: string, filters?: any) => Promise<void>;
  getSearchSuggestions: (query: string) => Promise<void>;
  clearSearchResults: () => void;
  addToSearchHistory: (query: string) => void;
  
  // PWA Actions
  initializePWA: () => void;
  promptInstall: () => Promise<boolean>;
  shareContent: (data: { title: string; text?: string; url?: string }) => Promise<boolean>;
  cacheOfflineData: () => Promise<void>;
  clearOfflineData: () => Promise<void>;
  updatePWACapabilities: () => void;
  
  // UI Actions
  setShowInstallPrompt: (show: boolean) => void;
  setShowOfflineBanner: (show: boolean) => void;
  setShowSyncStatus: (show: boolean) => void;
}

export const usePhase2Store = create<Phase2State & Phase2Actions>()(
  subscribeWithSelector((set, get) => ({
    // Initial State
    isOnline: navigator.onLine,
    syncStatus: 'idle',
    pendingChanges: 0,
    lastSyncTime: null,
    
    productivityMetrics: null,
    pillarHealthData: [],
    aiInsights: [],
    analyticsLoading: false,
    
    searchResults: [],
    searchSuggestions: [],
    searchLoading: false,
    searchHistory: [],
    
    pwaCapabilities: {
      isInstallable: false,
      isStandalone: false,
      hasNotifications: false,
      hasOfflineCapability: false,
      hasBackgroundSync: false,
      hasShare: false
    },
    installPromptAvailable: false,
    offlineDataSize: 0,
    connectionStatus: 'online',
    
    showInstallPrompt: false,
    showOfflineBanner: false,
    showSyncStatus: false,

    // Real-time Data Sync Actions
    initializeRealTimeSync: () => {
      console.log('Initializing Phase 2 real-time sync...');
      
      // Subscribe to connection status changes
      const unsubscribeConnection = realTimeDataService.subscribe('connection_status' as any, (event: any) => {
        set({ 
          isOnline: event.connected,
          connectionStatus: event.connected ? 'online' : 'offline',
          syncStatus: event.connected ? 'success' : 'error'
        });
        
        if (!event.connected) {
          set({ showOfflineBanner: true });
        }
      });

      // Subscribe to sync events
      const unsubscribeSync = realTimeDataService.subscribe('pillar', (event) => {
        console.log('Pillar sync event received:', event);
        // Handle pillar updates in real-time
      });

      // Update sync status based on service status
      const updateSyncStatus = () => {
        const status = realTimeDataService.getSyncStatus();
        set({
          isOnline: status.isOnline,
          pendingChanges: status.pendingChanges,
          lastSyncTime: status.lastSync
        });
      };

      updateSyncStatus();
      const statusInterval = setInterval(updateSyncStatus, 5000);

      // Cleanup function (would be called on unmount)
      return () => {
        unsubscribeConnection?.();
        unsubscribeSync?.();
        clearInterval(statusInterval);
      };
    },

    publishDataChange: (event) => {
      realTimeDataService.publishLocalChange(event);
      set({ syncStatus: 'syncing', showSyncStatus: true });
      
      // Hide sync status after 2 seconds
      setTimeout(() => {
        set({ showSyncStatus: false });
      }, 2000);
    },

    setSyncStatus: (status) => {
      set({ syncStatus: status });
    },

    setOnlineStatus: (isOnline) => {
      set({ 
        isOnline,
        connectionStatus: isOnline ? 'online' : 'offline',
        showOfflineBanner: !isOnline
      });
    },

    // Advanced Analytics Actions
    loadAnalytics: async () => {
      set({ analyticsLoading: true });
      
      try {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 30); // Last 30 days

        const [metrics, pillarHealth, insights] = await Promise.all([
          advancedAnalyticsService.getProductivityMetrics(startDate, endDate),
          advancedAnalyticsService.analyzePillarHealth(),
          advancedAnalyticsService.getCurrentInsights()
        ]);

        set({
          productivityMetrics: metrics,
          pillarHealthData: pillarHealth,
          aiInsights: insights
        });
      } catch (error) {
        console.error('Failed to load analytics:', error);
      } finally {
        set({ analyticsLoading: false });
      }
    },

    generateInsights: async () => {
      try {
        const insights = await advancedAnalyticsService.generateAIInsights();
        set({ aiInsights: insights });
      } catch (error) {
        console.error('Failed to generate insights:', error);
      }
    },

    dismissInsight: (insightId) => {
      advancedAnalyticsService.dismissInsight(insightId);
      set(state => ({
        aiInsights: state.aiInsights.filter(insight => insight.id !== insightId)
      }));
    },

    trackAnalyticsEvent: (category, value, metadata) => {
      advancedAnalyticsService.recordDataPoint(category, value, metadata);
    },

    // Smart Search Actions
    performSearch: async (query, filters) => {
      set({ searchLoading: true });
      
      try {
        const results = await smartSearchService.search(query, filters);
        set({ searchResults: results });
        
        // Add to search history
        get().addToSearchHistory(query);
      } catch (error) {
        console.error('Search failed:', error);
        set({ searchResults: [] });
      } finally {
        set({ searchLoading: false });
      }
    },

    getSearchSuggestions: async (query) => {
      try {
        const suggestions = await smartSearchService.getSearchSuggestions(query);
        set({ searchSuggestions: suggestions });
      } catch (error) {
        console.error('Failed to get search suggestions:', error);
        set({ searchSuggestions: [] });
      }
    },

    clearSearchResults: () => {
      set({ searchResults: [], searchSuggestions: [] });
    },

    addToSearchHistory: (query) => {
      set(state => {
        const newHistory = [query, ...state.searchHistory.filter(q => q !== query)].slice(0, 10);
        return { searchHistory: newHistory };
      });
    },

    // PWA Actions
    initializePWA: () => {
      const capabilities = pwaEnhancementService.getCapabilities();
      const connectionStatus = pwaEnhancementService.getConnectionStatus();
      
      set({
        pwaCapabilities: capabilities,
        installPromptAvailable: capabilities.isInstallable,
        isOnline: connectionStatus.isOnline,
        offlineDataSize: pwaEnhancementService.getOfflineDataSize()
      });

      // Listen for PWA events
      window.addEventListener('aurumInstallAvailable', () => {
        set({ installPromptAvailable: true, showInstallPrompt: true });
      });

      window.addEventListener('aurumConnectionChange', (event: any) => {
        const { isOnline, hasOfflineData } = event.detail;
        set({ 
          isOnline,
          connectionStatus: isOnline ? 'online' : 'offline',
          showOfflineBanner: !isOnline && !hasOfflineData
        });
      });

      window.addEventListener('aurumAppInstalled', () => {
        set({ installPromptAvailable: false, showInstallPrompt: false });
      });
    },

    promptInstall: async () => {
      const success = await pwaEnhancementService.promptInstall();
      if (success) {
        set({ installPromptAvailable: false, showInstallPrompt: false });
      }
      return success;
    },

    shareContent: async (data) => {
      return await pwaEnhancementService.shareContent(data);
    },

    cacheOfflineData: async () => {
      try {
        // This would get current app data and cache it
        const mockData: Partial<OfflineData> = {
          pillars: JSON.parse(localStorage.getItem('aurum-pillars') || '[]'),
          areas: JSON.parse(localStorage.getItem('aurum-areas') || '[]'),
          projects: JSON.parse(localStorage.getItem('aurum-projects') || '[]'),
          tasks: JSON.parse(localStorage.getItem('aurum-tasks') || '[]'),
          journalEntries: JSON.parse(localStorage.getItem('aurum-journal-entries') || '[]'),
          settings: JSON.parse(localStorage.getItem('aurum-settings') || '{}')
        };

        await pwaEnhancementService.cacheDataForOffline(mockData);
        
        set({ 
          offlineDataSize: pwaEnhancementService.getOfflineDataSize(),
          showOfflineBanner: false
        });
      } catch (error) {
        console.error('Failed to cache offline data:', error);
      }
    },

    clearOfflineData: async () => {
      await pwaEnhancementService.clearOfflineData();
      set({ offlineDataSize: 0 });
    },

    updatePWACapabilities: () => {
      const capabilities = pwaEnhancementService.getCapabilities();
      set({ pwaCapabilities: capabilities });
    },

    // UI Actions
    setShowInstallPrompt: (show) => {
      set({ showInstallPrompt: show });
    },

    setShowOfflineBanner: (show) => {
      set({ showOfflineBanner: show });
    },

    setShowSyncStatus: (show) => {
      set({ showSyncStatus: show });
    }
  }))
);

// Selectors for common use cases
export const useRealTimeSync = () => usePhase2Store(state => ({
  isOnline: state.isOnline,
  syncStatus: state.syncStatus,
  pendingChanges: state.pendingChanges,
  lastSyncTime: state.lastSyncTime,
  publishDataChange: state.publishDataChange,
  initializeRealTimeSync: state.initializeRealTimeSync
}));

export const useAdvancedAnalytics = () => usePhase2Store(state => ({
  productivityMetrics: state.productivityMetrics,
  pillarHealthData: state.pillarHealthData,
  aiInsights: state.aiInsights,
  analyticsLoading: state.analyticsLoading,
  loadAnalytics: state.loadAnalytics,
  generateInsights: state.generateInsights,
  dismissInsight: state.dismissInsight,
  trackAnalyticsEvent: state.trackAnalyticsEvent
}));

export const useSmartSearch = () => usePhase2Store(state => ({
  searchResults: state.searchResults,
  searchSuggestions: state.searchSuggestions,
  searchLoading: state.searchLoading,
  searchHistory: state.searchHistory,
  performSearch: state.performSearch,
  getSearchSuggestions: state.getSearchSuggestions,
  clearSearchResults: state.clearSearchResults
}));

export const usePWAFeatures = () => usePhase2Store(state => ({
  pwaCapabilities: state.pwaCapabilities,
  installPromptAvailable: state.installPromptAvailable,
  offlineDataSize: state.offlineDataSize,
  connectionStatus: state.connectionStatus,
  showInstallPrompt: state.showInstallPrompt,
  showOfflineBanner: state.showOfflineBanner,
  promptInstall: state.promptInstall,
  shareContent: state.shareContent,
  cacheOfflineData: state.cacheOfflineData,
  clearOfflineData: state.clearOfflineData,
  setShowInstallPrompt: state.setShowInstallPrompt,
  setShowOfflineBanner: state.setShowOfflineBanner
}));

// Initialize Phase 2 features on store creation with timeout protection
if (typeof window !== 'undefined') {
  const store = usePhase2Store.getState();
  
  // Initialize all Phase 2 services with timeout protection and error handling
  setTimeout(() => {
    try {
      const initPromises = [
        Promise.race([
          Promise.resolve(store.initializeRealTimeSync()),
          new Promise((_, reject) => setTimeout(() => reject(new Error('RealTime sync timeout')), 2000))
        ]).catch(err => console.log('RealTime sync init failed (non-critical):', err.message)),
        
        Promise.race([
          Promise.resolve(store.initializePWA()),
          new Promise((_, reject) => setTimeout(() => reject(new Error('PWA init timeout')), 2000))
        ]).catch(err => console.log('PWA init failed (non-critical):', err.message)),
        
        Promise.race([
          store.loadAnalytics(),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Analytics load timeout')), 3000))
        ]).catch(err => console.log('Analytics load failed (non-critical):', err.message))
      ];

      Promise.allSettled(initPromises).then(results => {
        console.log('Phase 2 initialization completed with', results.filter(r => r.status === 'fulfilled').length, 'successes');
      });
    } catch (error) {
      console.log('Phase 2 initialization error (non-critical):', error);
    }
  }, 1000);
}