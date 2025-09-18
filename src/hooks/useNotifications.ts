import { useEffect, useState, useCallback } from 'react';
import { useAppStore } from '../stores/basicAppStore';
import { realTimeNotificationService, RealTimeNotification, NotificationPreferences } from '../services/realTimeNotificationService';
import { privacyConsentService } from '../services/privacyConsentService';

export interface NotificationHookState {
  notifications: RealTimeNotification[];
  unreadCount: number;
  connectionStatus: any;
  preferences: NotificationPreferences;
  isLoading: boolean;
  error: string | null;
}

export interface NotificationHookActions {
  markAsRead: (notificationIds: string[]) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  removeNotification: (id: string) => void;
  updatePreferences: (preferences: Partial<NotificationPreferences>) => Promise<void>;
  sendTestNotification: () => Promise<void>;
  subscribe: (callback: (notification: RealTimeNotification) => void) => () => void;
  refresh: () => Promise<void>;
  requestBrowserPermission: () => Promise<NotificationPermission>;
}

export function useNotifications(): NotificationHookState & NotificationHookActions {
  const [notifications, setNotifications] = useState<RealTimeNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState(realTimeNotificationService.getConnectionStatus());
  const [preferences, setPreferences] = useState<NotificationPreferences>(
    realTimeNotificationService.getPreferences()
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Store integration for legacy compatibility
  const addNotification = useAppStore(state => state.addNotification);

  // Load initial notifications
  const loadNotifications = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const history = await realTimeNotificationService.getNotificationHistory(100);
      setNotifications(history);
      setUnreadCount(history.filter(n => !n.isRead).length);
    } catch (err) {
      setError('Failed to load notifications');
      console.error('Failed to load notifications:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Subscribe to real-time notifications
  useEffect(() => {
    const handleNewNotification = (notification: RealTimeNotification) => {
      setNotifications(prev => [notification, ...prev.slice(0, 99)]);
      setUnreadCount(prev => prev + 1);

      // Add to legacy store for compatibility
      addNotification({
        type: notification.priority === 'urgent' ? 'error' :
              notification.priority === 'high' ? 'warning' :
              notification.type === 'goal_achievement' ? 'success' : 'info',
        title: notification.title,
        message: notification.message,
        isRead: false,
      });

      // Log notification for privacy compliance
      privacyConsentService.logDataUsage(
        'collect',
        'preferences',
        'Real-time notification received',
        notification.source === 'ai',
        'legitimate_interest'
      );
    };

    // Subscribe to real-time notifications - returns subscription ID, not unsubscribe function
    const subscriptionId = realTimeNotificationService.subscribe(handleNewNotification);

    // Handle notification actions
    const handleNotificationAction = (event: CustomEvent) => {
      const action = event.detail;
      
      // Log action for privacy compliance
      privacyConsentService.logDataUsage(
        'process',
        'preferences',
        `Notification action: ${action.action}`,
        false,
        'legitimate_interest'
      );

      // Handle different action types
      switch (action.action) {
        case 'navigate':
          if (action.data?.section) {
            // Get the current store instance and navigate
            const store = useAppStore.getState();
            store.setActiveSection(action.data.section, action.data.settingsSection);
            console.log('Navigated to:', action.data.section);
          }
          break;
        case 'dismiss':
          // Handle dismiss action - notification is automatically removed
          console.log('Notification dismissed');
          break;
        default:
          console.log('Unknown notification action:', action.action);
      }
    };

    window.addEventListener('aurumNotificationAction', handleNotificationAction);

    // Update connection status periodically
    const statusInterval = setInterval(() => {
      setConnectionStatus(realTimeNotificationService.getConnectionStatus());
    }, 10000);

    // Initial load
    loadNotifications();

    return () => {
      // Unsubscribe using the subscription ID
      realTimeNotificationService.unsubscribe(subscriptionId);
      window.removeEventListener('aurumNotificationAction', handleNotificationAction);
      clearInterval(statusInterval);
    };
  }, [addNotification, loadNotifications]);

  // Update preferences when they change
  useEffect(() => {
    setPreferences(realTimeNotificationService.getPreferences());
  }, []);

  // Actions
  const markAsRead = useCallback(async (notificationIds: string[]) => {
    try {
      await realTimeNotificationService.markAsRead(notificationIds);
      setNotifications(prev => 
        prev.map(n => notificationIds.includes(n.id) ? { ...n, isRead: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - notificationIds.length));
    } catch (err) {
      setError('Failed to mark notifications as read');
      console.error('Failed to mark notifications as read:', err);
    }
  }, []);

  const markAllAsRead = useCallback(async () => {
    const unreadIds = notifications.filter(n => !n.isRead).map(n => n.id);
    if (unreadIds.length > 0) {
      await markAsRead(unreadIds);
    }
  }, [notifications, markAsRead]);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
    const notification = notifications.find(n => n.id === id);
    if (notification && !notification.isRead) {
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
  }, [notifications]);

  const updatePreferences = useCallback(async (newPreferences: Partial<NotificationPreferences>) => {
    setIsLoading(true);
    setError(null);
    try {
      await realTimeNotificationService.updatePreferences(newPreferences);
      setPreferences(realTimeNotificationService.getPreferences());

      // Log preference update for privacy compliance
      privacyConsentService.logDataUsage(
        'process',
        'preferences',
        'Notification preferences updated',
        false,
        'consent'
      );
    } catch (err) {
      setError('Failed to update notification preferences');
      console.error('Failed to update notification preferences:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendTestNotification = useCallback(async () => {
    try {
      await realTimeNotificationService.sendTestNotification();
    } catch (err) {
      setError('Failed to send test notification');
      console.error('Failed to send test notification:', err);
    }
  }, []);

  const subscribe = useCallback((callback: (notification: RealTimeNotification) => void) => {
    const subscriptionId = realTimeNotificationService.subscribe(callback);
    return () => realTimeNotificationService.unsubscribe(subscriptionId);
  }, []);

  const refresh = useCallback(async () => {
    await loadNotifications();
    setConnectionStatus(realTimeNotificationService.getConnectionStatus());
  }, [loadNotifications]);

  const requestBrowserPermission = useCallback(async () => {
    try {
      const permission = await realTimeNotificationService.requestBrowserPermission();
      // Update connection status to reflect new permission
      setConnectionStatus(realTimeNotificationService.getConnectionStatus());
      return permission;
    } catch (err) {
      setError('Failed to request browser permission');
      throw err;
    }
  }, []);

  return {
    // State
    notifications,
    unreadCount,
    connectionStatus,
    preferences,
    isLoading,
    error,
    
    // Actions
    markAsRead,
    markAllAsRead,
    removeNotification,
    updatePreferences,
    sendTestNotification,
    subscribe,
    refresh,
    requestBrowserPermission,
  };
}

export default useNotifications;