/**
 * Real-time Service for Supabase Webhooks
 * Handles real-time updates and performance optimizations
 */

import { getBackendBaseUrl } from './baseUrl';

class RealtimeService {
  constructor() {
    this.subscribers = new Map();
    this.eventSource = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.isConnected = false;
  }

  /**
   * Initialize real-time connection
   */
  async initialize() {
    try {
      const baseUrl = getBackendBaseUrl();
      console.log('🔄 Initializing real-time service...');
      
      // For now, use polling-based approach since SSE might have CORS issues
      this.startPollingUpdates();
      
      return true;
    } catch (error) {
      console.error('Failed to initialize real-time service:', error);
      return false;
    }
  }

  /**
   * Subscribe to real-time updates for specific event types
   */
  subscribe(eventType, callback) {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, []);
    }
    
    this.subscribers.get(eventType).push(callback);
    console.log(`📡 Subscribed to ${eventType} updates`);
    
    // Return unsubscribe function
    return () => this.unsubscribe(eventType, callback);
  }

  /**
   * Unsubscribe from real-time updates
   */
  unsubscribe(eventType, callback) {
    const subscribers = this.subscribers.get(eventType);
    if (subscribers) {
      const index = subscribers.indexOf(callback);
      if (index > -1) {
        subscribers.splice(index, 1);
      }
    }
  }

  /**
   * Notify subscribers of updates
   */
  notifySubscribers(eventType, data) {
    const subscribers = this.subscribers.get(eventType);
    if (subscribers) {
      subscribers.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in ${eventType} subscriber:`, error);
        }
      });
    }
  }

  /**
   * Start polling for updates (fallback approach)
   */
  startPollingUpdates() {
    // Poll for webhook status updates every 30 seconds
    setInterval(() => {
      this.checkForUpdates();
    }, 30000);
    
    console.log('📊 Started polling for real-time updates');
  }

  /**
   * Check for updates from backend
   */
  async checkForUpdates() {
    try {
      // This would check for recent webhook activities
      // For now, just maintain connection status
      this.isConnected = true;
      this.reconnectAttempts = 0;
    } catch (error) {
      console.warn('Update check failed:', error);
      this.isConnected = false;
    }
  }

  /**
   * Trigger manual refresh for specific data types
   */
  triggerRefresh(dataType, userId = null) {
    console.log(`🔄 Triggering refresh for ${dataType}`);
    
    const refreshData = {
      type: dataType,
      userId: userId,
      timestamp: new Date().toISOString()
    };

    // Notify subscribers that data should be refreshed
    this.notifySubscribers('refresh_required', refreshData);
    this.notifySubscribers(`${dataType}_refresh`, refreshData);
  }

  /**
   * Handle alignment score updates
   */
  onAlignmentUpdate(callback) {
    return this.subscribe('alignment_update', callback);
  }

  /**
   * Handle journal sentiment updates
   */
  onJournalSentimentUpdate(callback) {
    return this.subscribe('journal_sentiment_update', callback);
  }

  /**
   * Handle analytics updates
   */
  onAnalyticsUpdate(callback) {
    return this.subscribe('analytics_update', callback);
  }

  /**
   * Handle HRM insights updates
   */
  onHRMInsightsUpdate(callback) {
    return this.subscribe('hrm_insights_update', callback);
  }

  /**
   * Handle cache invalidation notifications
   */
  onCacheInvalidation(callback) {
    return this.subscribe('cache_invalidation', callback);
  }

  /**
   * Simulate webhook events for testing
   */
  simulateWebhookEvent(eventType, data) {
    console.log(`🧪 Simulating webhook event: ${eventType}`, data);
    this.notifySubscribers(eventType, data);
  }

  /**
   * Get connection status
   */
  getConnectionStatus() {
    return {
      connected: this.isConnected,
      subscribers: Array.from(this.subscribers.keys()),
      subscriberCount: Array.from(this.subscribers.values()).reduce((total, subs) => total + subs.length, 0)
    };
  }

  /**
   * Cleanup connections
   */
  cleanup() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    
    this.subscribers.clear();
    this.isConnected = false;
    console.log('🧹 Real-time service cleaned up');
  }
}

// Export singleton instance
const realtimeService = new RealtimeService();

export default realtimeService;

/**
 * React Hook for real-time subscriptions
 */
export const useRealtimeUpdates = (eventTypes = [], callback) => {
  const React = require('react');
  const { useEffect, useRef } = React;
  
  const callbackRef = useRef(callback);
  const unsubscribeFunctions = useRef([]);
  
  // Update callback ref when callback changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);
  
  useEffect(() => {
    // Initialize real-time service
    realtimeService.initialize();
    
    // Subscribe to specified event types
    unsubscribeFunctions.current = eventTypes.map(eventType => 
      realtimeService.subscribe(eventType, (data) => {
        if (callbackRef.current) {
          callbackRef.current(eventType, data);
        }
      })
    );
    
    // Cleanup on unmount
    return () => {
      unsubscribeFunctions.current.forEach(unsubscribe => unsubscribe());
      unsubscribeFunctions.current = [];
    };
  }, [eventTypes.join(',')]); // Re-run when event types change
  
  return realtimeService.getConnectionStatus();
};

/**
 * Hook for alignment score updates
 */
export const useAlignmentUpdates = (callback) => {
  return useRealtimeUpdates(['alignment_update', 'refresh_required'], (eventType, data) => {
    if (eventType === 'alignment_update' || (eventType === 'refresh_required' && data.type === 'alignment')) {
      callback(data);
    }
  });
};

/**
 * Hook for journal sentiment updates
 */
export const useJournalSentimentUpdates = (callback) => {
  return useRealtimeUpdates(['journal_sentiment_update', 'refresh_required'], (eventType, data) => {
    if (eventType === 'journal_sentiment_update' || (eventType === 'refresh_required' && data.type === 'journal_sentiment')) {
      callback(data);
    }
  });
};

/**
 * Hook for analytics updates
 */
export const useAnalyticsUpdates = (callback) => {
  return useRealtimeUpdates(['analytics_update', 'refresh_required'], (eventType, data) => {
    if (eventType === 'analytics_update' || (eventType === 'refresh_required' && data.type === 'analytics')) {
      callback(data);
    }
  });
};