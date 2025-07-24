/**
 * Notification Context for Aurum Life
 * Handles browser notifications, notification preferences, and real-time updates
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';

const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const { user, token } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [preferences, setPreferences] = useState(null);
  const [browserPermission, setBrowserPermission] = useState('default');
  const [loading, setLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected'); // 'connected', 'connecting', 'disconnected'
  const [pollInterval, setPollInterval] = useState(null);

  // Browser notification permission management
  const requestBrowserPermission = useCallback(async () => {
    if (!('Notification' in window)) {
      console.warn('This browser does not support notifications');
      return 'denied';
    }

    if (Notification.permission === 'default') {
      const permission = await Notification.requestPermission();
      setBrowserPermission(permission);
      return permission;
    }

    setBrowserPermission(Notification.permission);
    return Notification.permission;
  }, []);

  // Show browser notification
  const showBrowserNotification = useCallback((title, message, options = {}) => {
    if (Notification.permission === 'granted') {
      const notification = new Notification(title, {
        body: message,
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        tag: 'aurum-life-notification',
        ...options
      });

      // Auto-close after 6 seconds
      setTimeout(() => {
        notification.close();
      }, 6000);

      notification.onclick = () => {
        window.focus();
        notification.close();
        // Could navigate to specific page based on notification type
      };

      return notification;
    }
    return null;
  }, []);

  // Fetch user notification preferences
  const fetchPreferences = useCallback(async () => {
    if (!user || !token) return;

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/preferences`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const prefs = await response.json();
        setPreferences(prefs);
        
        // Update browser permission state based on preferences
        if (prefs.browser_notifications && browserPermission === 'default') {
          await requestBrowserPermission();
        }
      } else {
        console.error('Failed to fetch notification preferences:', response.status);
      }
    } catch (error) {
      console.error('Error fetching notification preferences:', error);
    }
  }, [user, token, browserPermission, requestBrowserPermission]);

  // Update notification preferences
  const updatePreferences = useCallback(async (updates) => {
    if (!user || !token) return;

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/preferences`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        const updatedPrefs = await response.json();
        setPreferences(updatedPrefs);
        
        // Handle browser permission changes
        if (updates.browser_notifications === true && browserPermission !== 'granted') {
          await requestBrowserPermission();
        }
        
        return updatedPrefs;
      } else {
        console.error('Failed to update notification preferences:', response.status);
        return null;
      }
    } catch (error) {
      console.error('Error updating notification preferences:', error);
      return null;
    }
  }, [user, token, browserPermission, requestBrowserPermission]);

  // Fetch notifications from server
  const fetchNotifications = useCallback(async (unreadOnly = false) => {
    if (!user || !token) return;

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications?unread_only=${unreadOnly}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const notificationData = await response.json();
        setNotifications(notificationData);
        
        // Count unread notifications
        const unread = notificationData.filter(n => !n.read).length;
        setUnreadCount(unread);
        
        return notificationData;
      } else {
        console.error('Failed to fetch notifications:', response.status);
        return [];
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
      return [];
    }
  }, [user, token]);

  // Mark notification as read
  const markAsRead = useCallback(async (notificationId) => {
    if (!user || !token) return;

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // Update local state
        setNotifications(prev => 
          prev.map(n => 
            n.id === notificationId ? { ...n, read: true } : n
          )
        );
        
        // Update unread count
        setUnreadCount(prev => Math.max(0, prev - 1));
        
        return true;
      } else {
        console.error('Failed to mark notification as read:', response.status);
        return false;
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
      return false;
    }
  }, [user, token]);

  // Send test notification
  const sendTestNotification = useCallback(async () => {
    if (!user || !token) return;

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        
        // Show browser notification immediately
        showBrowserNotification(
          'Test Notification',
          'This is a test notification from Aurum Life!',
          { tag: 'test-notification' }
        );
        
        // Refresh notifications list
        setTimeout(() => {
          fetchNotifications();
        }, 2000);
        
        return result;
      } else {
        console.error('Failed to send test notification:', response.status);
        return null;
      }
    } catch (error) {
      console.error('Error sending test notification:', error);
      return null;
    }
  }, [user, token, showBrowserNotification, fetchNotifications]);

  // Enhanced polling for new notifications with smarter frequency
  useEffect(() => {
    if (!user || !token) {
      setConnectionStatus('disconnected');
      return;
    }

    setConnectionStatus('connecting');

    const pollNotifications = async () => {
      try {
        const newNotifications = await fetchNotifications();
        setConnectionStatus('connected');
        
        // Check for new unread notifications and show browser notifications
        if (preferences?.browser_notifications && browserPermission === 'granted') {
          const previousNotificationIds = new Set(notifications.map(n => n.id));
          const newUnreadNotifications = newNotifications.filter(
            n => !n.read && !previousNotificationIds.has(n.id)
          );
          
          // Show browser notifications for new unread notifications
          newUnreadNotifications.forEach(notification => {
            showBrowserNotification(
              notification.title,
              notification.message,
              {
                tag: `notification-${notification.id}`,
                data: notification,
                icon: '/favicon.ico',
                requireInteraction: notification.type === 'task_overdue', // Keep overdue notifications open
                actions: [
                  {
                    action: 'mark-read',
                    title: 'Mark as Read'
                  },
                  {
                    action: 'view',
                    title: 'View Task'
                  }
                ]
              }
            );
          });
        }
      } catch (error) {
        console.error('Error polling notifications:', error);
        setConnectionStatus('disconnected');
      }
    };

    // Initial fetch
    pollNotifications();

    // Smart polling: more frequent when there are active tasks, less frequent otherwise
    const getPollingInterval = () => {
      const hasRecentActivity = notifications.some(n => {
        const notificationTime = new Date(n.created_at);
        const now = new Date();
        const diffMinutes = (now - notificationTime) / (1000 * 60);
        return diffMinutes < 30; // Recent activity in last 30 minutes
      });
      
      return hasRecentActivity ? 15000 : 30000; // 15s if active, 30s otherwise
    };

    const interval = setInterval(pollNotifications, getPollingInterval());
    setPollInterval(interval);

    return () => {
      clearInterval(interval);
      setPollInterval(null);
      setConnectionStatus('disconnected');
    };
  }, [user, token, preferences, browserPermission, notifications, fetchNotifications, showBrowserNotification]);

  // Initialize preferences and browser permission
  useEffect(() => {
    if (user && token) {
      fetchPreferences();
    }
  }, [user, token, fetchPreferences]);

  // Update browser permission state
  useEffect(() => {
    if ('Notification' in window) {
      setBrowserPermission(Notification.permission);
    }
  }, []);

  const value = {
    // State
    notifications,
    unreadCount,
    preferences,
    browserPermission,
    loading,

    // Actions
    fetchNotifications,
    fetchPreferences,
    updatePreferences,
    markAsRead,
    sendTestNotification,
    requestBrowserPermission,
    showBrowserNotification
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext;