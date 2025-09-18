import { useState, useEffect, useCallback, useRef } from 'react';
import { apiService, UserStats, PillarHealth } from '../services/apiService';
import { websocketService, WebSocketEventHandlers } from '../services/websocketService';

export interface RealTimeDataState {
  userStats: UserStats | null;
  pillarHealth: PillarHealth[];
  isLoading: boolean;
  error: string | null;
  isConnected: boolean;
  lastUpdated: Date | null;
}

export interface UseRealTimeDataOptions {
  enableWebSocket?: boolean;
  pollingInterval?: number; // milliseconds
  autoRefresh?: boolean;
}

export function useRealTimeData(options: UseRealTimeDataOptions = {}) {
  const {
    enableWebSocket = true,
    pollingInterval = 30000, // 30 seconds default
    autoRefresh = true
  } = options;

  const [state, setState] = useState<RealTimeDataState>({
    userStats: null,
    pillarHealth: [],
    isLoading: true,
    error: null,
    isConnected: false,
    lastUpdated: null
  });

  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const retryCountRef = useRef(0);
  const maxRetries = 3;

  // Update state helper
  const updateState = useCallback((updates: Partial<RealTimeDataState>) => {
    setState(prev => ({
      ...prev,
      ...updates,
      lastUpdated: new Date()
    }));
  }, []);

  // Fetch data from API
  const fetchData = useCallback(async (showLoading = false) => {
    try {
      if (showLoading) {
        updateState({ isLoading: true, error: null });
      }

      // Fetch both user stats and pillar health in parallel
      const [userStatsResult, pillarHealthResult] = await Promise.allSettled([
        apiService.getUserStats(),
        apiService.getPillarHealth()
      ]);

      // Handle user stats result
      let userStats: UserStats | null = null;
      if (userStatsResult.status === 'fulfilled') {
        userStats = userStatsResult.value;
        retryCountRef.current = 0; // Reset retry count on success
      } else {
        console.error('Failed to fetch user stats:', userStatsResult.reason);
      }

      // Handle pillar health result
      let pillarHealth: PillarHealth[] = [];
      if (pillarHealthResult.status === 'fulfilled') {
        pillarHealth = pillarHealthResult.value;
      } else {
        console.error('Failed to fetch pillar health:', pillarHealthResult.reason);
      }

      updateState({
        userStats,
        pillarHealth,
        isLoading: false,
        error: null
      });

    } catch (error) {
      console.error('Failed to fetch real-time data:', error);
      retryCountRef.current++;
      
      // Only show error if we've exhausted retries
      if (retryCountRef.current >= maxRetries) {
        updateState({
          isLoading: false,
          error: error instanceof Error ? error.message : 'Failed to fetch data'
        });
      } else {
        // Retry after a short delay
        setTimeout(() => fetchData(false), 2000 * retryCountRef.current);
      }
    }
  }, [updateState]);

  // WebSocket event handlers
  const wsHandlers: WebSocketEventHandlers = {
    onConnect: () => {
      // Silent connection handling
      updateState({ isConnected: true });
      
      // Request updates for our data types
      websocketService.requestUpdates(['user_stats', 'pillar_health']);
    },

    onDisconnect: () => {
      // Silent disconnection handling
      updateState({ isConnected: false });
    },

    onError: (error) => {
      // Silent error handling - don't log or show errors
      updateState({ 
        isConnected: false,
        error: null // Never show connection errors
      });
    },

    onUserStatsUpdated: (data) => {
      // Silent stats update
      updateState({
        userStats: data,
        error: null
      });
    },

    onPillarHealthUpdated: (data) => {
      // Silent pillar health update
      if (Array.isArray(data)) {
        updateState({
          pillarHealth: data,
          error: null
        });
      } else if (data.pillar_id) {
        // Single pillar update
        setState(prev => ({
          ...prev,
          pillarHealth: prev.pillarHealth.map(p => 
            p.pillar_id === data.pillar_id ? data : p
          ),
          lastUpdated: new Date()
        }));
      }
    },

    onReconnect: () => {
      // Silent reconnection handling
      fetchData(false);
    }
  };

  // Setup polling
  const startPolling = useCallback(() => {
    if (pollingIntervalRef.current) return;

    pollingIntervalRef.current = setInterval(() => {
      if (!enableWebSocket || !websocketService.isConnected()) {
        // Silent polling
        fetchData(false);
      }
    }, pollingInterval);
  }, [enableWebSocket, pollingInterval, fetchData]);

  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  // Manual refresh function
  const refresh = useCallback(() => {
    // Silent manual refresh
    fetchData(true);
  }, [fetchData]);

  // Initialize data and connections
  useEffect(() => {
    // Initial data fetch
    fetchData(true);

    // Setup WebSocket if enabled
    if (enableWebSocket) {
      websocketService.connect(wsHandlers).catch(() => {
        // Complete silence - no logging, no error state
        updateState({ 
          isConnected: false,
          error: null
        });
      });
    }

    // Setup polling if auto-refresh is enabled
    if (autoRefresh) {
      startPolling();
    }

    // Cleanup function
    return () => {
      stopPolling();
      if (enableWebSocket) {
        websocketService.stopUpdates(['user_stats', 'pillar_health']);
      }
    };
  }, [enableWebSocket, autoRefresh, startPolling, stopPolling, fetchData]);

  // Handle visibility changes (pause/resume updates when tab is hidden/visible)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        stopPolling();
      } else if (autoRefresh) {
        startPolling();
        // Refresh data when tab becomes visible
        fetchData(false);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [autoRefresh, startPolling, stopPolling, fetchData]);

  // Return state and methods
  return {
    ...state,
    refresh,
    startPolling,
    stopPolling,
    
    // Computed values
    hasData: !!(state.userStats || state.pillarHealth.length > 0),
    isStale: state.lastUpdated ? Date.now() - state.lastUpdated.getTime() > pollingInterval * 2 : false,
    
    // Helper methods
    getPillarHealth: (pillarId: string) => 
      state.pillarHealth.find(p => p.pillar_id === pillarId),
    
    getConnectionStatus: () => websocketService.getConnectionState(),
  };
}

// Hook for individual pillar real-time data
export function usePillarRealTimeData(pillarId: string) {
  const [pillarData, setPillarData] = useState<{
    health: PillarHealth | null;
    analytics: any | null;
    isLoading: boolean;
    error: string | null;
  }>({
    health: null,
    analytics: null,
    isLoading: true,
    error: null
  });

  const fetchPillarData = useCallback(async () => {
    try {
      setPillarData(prev => ({ ...prev, isLoading: true, error: null }));

      const [healthResult, analyticsResult] = await Promise.allSettled([
        apiService.getPillarHealth(pillarId),
        apiService.getPillarAnalytics(pillarId)
      ]);

      const health = healthResult.status === 'fulfilled' 
        ? healthResult.value[0] || null 
        : null;

      const analytics = analyticsResult.status === 'fulfilled'
        ? analyticsResult.value
        : null;

      setPillarData({
        health,
        analytics,
        isLoading: false,
        error: null
      });

    } catch (error) {
      setPillarData(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch pillar data'
      }));
    }
  }, [pillarId]);

  useEffect(() => {
    fetchPillarData();

    // Subscribe to pillar-specific updates
    const handlePillarUpdate = (data: any) => {
      if (data.pillar_id === pillarId) {
        setPillarData(prev => ({
          ...prev,
          health: data,
          error: null
        }));
      }
    };

    websocketService.subscribe('onPillarHealthUpdated', handlePillarUpdate);

    return () => {
      websocketService.unsubscribe('onPillarHealthUpdated');
    };
  }, [pillarId, fetchPillarData]);

  return {
    ...pillarData,
    refresh: fetchPillarData
  };
}