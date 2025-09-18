import { websocketService, WebSocketEventHandlers } from './websocketService';
import { apiService } from './apiService';

export interface RealTimeNotification {
  id: string;
  type: 'task_reminder' | 'project_update' | 'pillar_milestone' | 'ai_insight' | 'system_alert' | 'goal_achievement' | 'deadline_approaching';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  actions?: NotificationAction[];
  metadata?: Record<string, any>;
  category: 'productivity' | 'insights' | 'system' | 'achievements' | 'reminders';
  source: 'system' | 'ai' | 'user' | 'schedule';
}

export interface NotificationAction {
  id: string;
  label: string;
  type: 'primary' | 'secondary' | 'danger';
  action: string;
  data?: Record<string, any>;
}

export interface NotificationPreferences {
  enabled: boolean;
  categories: {
    productivity: boolean;
    insights: boolean;
    system: boolean;
    achievements: boolean;
    reminders: boolean;
  };
  delivery: {
    realTime: boolean;
    email: boolean;
    browser: boolean;
    mobile: boolean;
  };
  priority: {
    low: boolean;
    medium: boolean;
    high: boolean;
    urgent: boolean;
  };
  quietHours: {
    enabled: boolean;
    start: string;
    end: string;
    timezone: string;
  };
  frequency: {
    immediate: boolean;
    digest: 'daily' | 'weekly' | 'never';
    maxPerHour: number;
  };
}

export interface NotificationSubscription {
  id: string;
  type: string;
  filters: Record<string, any>;
  preferences: Partial<NotificationPreferences>;
}

class RealTimeNotificationService {
  private subscribers: Map<string, Function> = new Map();
  private notificationQueue: RealTimeNotification[] = [];
  private preferences: NotificationPreferences = this.getDefaultPreferences();
  private subscriptions: NotificationSubscription[] = [];
  private isConnected = false;
  private rateLimitCounters = new Map<string, number>();

  constructor() {
    this.initializeWebSocketHandlers();
    this.loadPreferences();
    this.startRateLimitReset();
  }

  private getDefaultPreferences(): NotificationPreferences {
    return {
      enabled: true,
      categories: {
        productivity: true,
        insights: true,
        system: true,
        achievements: true,
        reminders: true,
      },
      delivery: {
        realTime: true,
        email: false,
        browser: true,
        mobile: false,
      },
      priority: {
        low: true,
        medium: true,
        high: true,
        urgent: true,
      },
      quietHours: {
        enabled: false,
        start: '22:00',
        end: '07:00',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      },
      frequency: {
        immediate: true,
        digest: 'daily',
        maxPerHour: 10,
      },
    };
  }

  private initializeWebSocketHandlers() {
    const handlers: WebSocketEventHandlers = {
      onNotification: (data) => this.handleWebSocketNotification(data),
      onTaskCompleted: (data) => this.handleTaskCompleted(data),
      onNewRecommendation: (data) => this.handleNewRecommendation(data),
      onPillarHealthUpdated: (data) => this.handlePillarHealthUpdate(data),
      onUserStatsUpdated: (data) => this.handleUserStatsUpdate(data),
      onConnect: () => {
        this.isConnected = true;
        this.syncSubscriptions();
        this.flushNotificationQueue();
      },
      onDisconnect: () => {
        this.isConnected = false;
      },
      onError: (error) => {
        console.log('Notification service WebSocket error - working offline');
      },
    };

    // Attempt to connect with silent error handling
    websocketService.connect(handlers).catch(() => {
      // Silent handling - service works without WebSocket
    });
  }

  private async handleWebSocketNotification(data: any) {
    try {
      const notification: RealTimeNotification = {
        id: data.id || this.generateId(),
        type: data.type || 'system_alert',
        priority: data.priority || 'medium',
        title: data.title || 'New Notification',
        message: data.message || '',
        timestamp: data.timestamp || new Date().toISOString(),
        isRead: false,
        actions: data.actions || [],
        metadata: data.metadata || {},
        category: data.category || 'system',
        source: data.source || 'system',
      };

      await this.processNotification(notification);
    } catch (error) {
      console.log('Error processing WebSocket notification');
    }
  }

  private async handleTaskCompleted(data: any) {
    const notification: RealTimeNotification = {
      id: this.generateId(),
      type: 'goal_achievement',
      priority: 'medium',
      title: 'Task Completed! 🎉',
      message: `You completed "${data.taskName}". Great progress on your goals!`,
      timestamp: new Date().toISOString(),
      isRead: false,
      category: 'achievements',
      source: 'system',
      metadata: { taskId: data.taskId, projectId: data.projectId },
      actions: [
        {
          id: 'view_progress',
          label: 'View Progress',
          type: 'primary',
          action: 'navigate',
          data: { section: 'Analytics' },
        },
      ],
    };

    await this.processNotification(notification);
  }

  private async handleNewRecommendation(data: any) {
    const notification: RealTimeNotification = {
      id: this.generateId(),
      type: 'ai_insight',
      priority: 'medium',
      title: 'New AI Insight Available',
      message: data.summary || 'We have a new recommendation to help optimize your workflow.',
      timestamp: new Date().toISOString(),
      isRead: false,
      category: 'insights',
      source: 'ai',
      metadata: { recommendationId: data.id, type: data.type },
      actions: [
        {
          id: 'view_insight',
          label: 'View Insight',
          type: 'primary',
          action: 'navigate',
          data: { section: 'AIInsights', recommendationId: data.id },
        },
      ],
    };

    await this.processNotification(notification);
  }

  private async handlePillarHealthUpdate(data: any) {
    if (data.healthScore < 0.3) {
      const notification: RealTimeNotification = {
        id: this.generateId(),
        type: 'pillar_milestone',
        priority: 'high',
        title: 'Pillar Needs Attention',
        message: `Your "${data.pillarName}" pillar health is low. Consider reviewing your goals and tasks.`,
        timestamp: new Date().toISOString(),
        isRead: false,
        category: 'productivity',
        source: 'system',
        metadata: { pillarId: data.pillarId, healthScore: data.healthScore },
        actions: [
          {
            id: 'review_pillar',
            label: 'Review Pillar',
            type: 'primary',
            action: 'navigate',
            data: { section: 'Pillars', pillarId: data.pillarId },
          },
        ],
      };

      await this.processNotification(notification);
    }
  }

  private async handleUserStatsUpdate(data: any) {
    // Create achievement notifications for milestones
    if (data.streaks?.dailyTaskCompletion >= 7) {
      const notification: RealTimeNotification = {
        id: this.generateId(),
        type: 'goal_achievement',
        priority: 'medium',
        title: '7-Day Streak! 🔥',
        message: 'Congratulations on completing tasks for 7 days straight!',
        timestamp: new Date().toISOString(),
        isRead: false,
        category: 'achievements',
        source: 'system',
        metadata: { achievement: 'daily_streak_7', streak: data.streaks.dailyTaskCompletion },
      };

      await this.processNotification(notification);
    }
  }

  private async processNotification(notification: RealTimeNotification) {
    // Check if notifications are enabled
    if (!this.preferences.enabled) return;

    // Check category preferences
    if (!this.preferences.categories[notification.category]) return;

    // Check priority preferences
    if (!this.preferences.priority[notification.priority]) return;

    // Check quiet hours
    if (this.isInQuietHours()) {
      if (notification.priority !== 'urgent') return;
    }

    // Rate limiting
    if (!this.checkRateLimit(notification.category)) return;

    // Store notification
    await this.storeNotification(notification);

    // Deliver notification
    await this.deliverNotification(notification);

    // Notify subscribers
    this.notifySubscribers(notification);
  }

  private isInQuietHours(): boolean {
    if (!this.preferences.quietHours.enabled) return false;

    const now = new Date();
    const timeZone = this.preferences.quietHours.timezone;
    const formatter = new Intl.DateTimeFormat('en-US', {
      timeZone,
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
    });

    const currentTime = formatter.format(now);
    const [currentHour, currentMinute] = currentTime.split(':').map(Number);
    const currentMinutes = currentHour * 60 + currentMinute;

    const [startHour, startMinute] = this.preferences.quietHours.start.split(':').map(Number);
    const startMinutes = startHour * 60 + startMinute;

    const [endHour, endMinute] = this.preferences.quietHours.end.split(':').map(Number);
    const endMinutes = endHour * 60 + endMinute;

    if (startMinutes < endMinutes) {
      return currentMinutes >= startMinutes && currentMinutes <= endMinutes;
    } else {
      return currentMinutes >= startMinutes || currentMinutes <= endMinutes;
    }
  }

  private checkRateLimit(category: string): boolean {
    const key = `${category}_${new Date().getHours()}`;
    const count = this.rateLimitCounters.get(key) || 0;
    
    if (count >= this.preferences.frequency.maxPerHour) {
      return false;
    }

    this.rateLimitCounters.set(key, count + 1);
    return true;
  }

  private startRateLimitReset() {
    setInterval(() => {
      this.rateLimitCounters.clear();
    }, 3600000); // Reset every hour
  }

  private async storeNotification(notification: RealTimeNotification) {
    try {
      // Store via API service
      await apiService.createNotification(notification);
    } catch (error) {
      // Fallback to local storage
      this.notificationQueue.push(notification);
      const stored = JSON.parse(localStorage.getItem('aurum_notifications') || '[]');
      stored.unshift(notification);
      localStorage.setItem('aurum_notifications', JSON.stringify(stored.slice(0, 100)));
    }
  }

  private async deliverNotification(notification: RealTimeNotification) {
    const delivery = this.preferences.delivery;

    // Real-time in-app delivery
    if (delivery.realTime) {
      this.showInAppNotification(notification);
    }

    // Browser notification
    if (delivery.browser && 'Notification' in window && Notification.permission === 'granted') {
      this.showBrowserNotification(notification);
    }

    // Email delivery (via API)
    if (delivery.email) {
      try {
        await apiService.sendEmailNotification(notification);
      } catch (error) {
        console.log('Email notification failed');
      }
    }
  }

  private showInAppNotification(notification: RealTimeNotification) {
    // Emit event for app components to catch
    window.dispatchEvent(new CustomEvent('aurumNotification', {
      detail: notification
    }));

    // Also show as toast notification if available
    if (typeof window !== 'undefined' && window.dispatchEvent) {
      try {
        // Import and use toast dynamically to avoid SSR issues
        import('../utils/toast').then(({ showSuccess, showError, showWarning, showInfo }) => {
          const duration = notification.priority === 'urgent' ? 10000 : 5000;
          const toastMessage = `${notification.title}: ${notification.message}`;
          
          if (notification.priority === 'urgent') {
            showError(toastMessage, { duration });
          } else if (notification.priority === 'high') {
            showWarning(toastMessage, { duration });
          } else if (notification.type === 'goal_achievement') {
            showSuccess(toastMessage, { duration });
          } else {
            showInfo(toastMessage, { duration });
          }
        }).catch(() => {
          // Fallback if toast utility not available
          console.log('Toast notification not available');
        });
      } catch (error) {
        console.log('Failed to show toast notification');
      }
    }
  }

  private showBrowserNotification(notification: RealTimeNotification) {
    try {
      // Check permission first
      if (Notification.permission !== 'granted') {
        return;
      }

      const options: NotificationOptions = {
        body: notification.message,
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        tag: notification.id,
        renotify: notification.priority === 'urgent',
        silent: notification.priority === 'low',
        requireInteraction: notification.priority === 'urgent',
        actions: notification.actions?.slice(0, 2).map(action => ({
          action: action.id,
          title: action.label,
        })) || [],
      };

      const browserNotification = new Notification(notification.title, options);

      // Handle click
      browserNotification.onclick = () => {
        window.focus();
        if (notification.actions?.[0]) {
          this.executeNotificationAction(notification.actions[0]);
        }
        browserNotification.close();
      };

      // Handle action buttons
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.addEventListener('notificationclick', (event) => {
          if (event.notification.tag === notification.id) {
            event.notification.close();
            
            if (event.action) {
              const action = notification.actions?.find(a => a.id === event.action);
              if (action) {
                this.executeNotificationAction(action);
              }
            } else if (notification.actions?.[0]) {
              this.executeNotificationAction(notification.actions[0]);
            }
            
            // Focus the window
            event.waitUntil(
              clients.matchAll().then(clientList => {
                if (clientList.length > 0) {
                  return clientList[0].focus();
                }
                return clients.openWindow('/');
              })
            );
          }
        });
      }

      // Auto-close non-urgent notifications
      if (notification.priority !== 'urgent') {
        setTimeout(() => {
          try {
            browserNotification.close();
          } catch (e) {
            // Notification may already be closed
          }
        }, 5000);
      }
    } catch (error) {
      console.log('Browser notification failed:', error);
    }
  }

  private executeNotificationAction(action: NotificationAction) {
    window.dispatchEvent(new CustomEvent('aurumNotificationAction', {
      detail: action
    }));
  }

  private notifySubscribers(notification: RealTimeNotification) {
    this.subscribers.forEach(callback => {
      try {
        callback(notification);
      } catch (error) {
        console.log('Subscriber notification failed');
      }
    });
  }

  private loadPreferences() {
    try {
      const stored = localStorage.getItem('aurum_notification_preferences');
      if (stored) {
        this.preferences = { ...this.preferences, ...JSON.parse(stored) };
      }
    } catch (error) {
      console.log('Failed to load notification preferences');
    }
  }

  private async syncSubscriptions() {
    if (!this.isConnected) return;

    try {
      // Send subscription preferences to server
      websocketService.send({
        type: 'configure_notifications' as any,
        payload: {
          preferences: this.preferences,
          subscriptions: this.subscriptions,
        },
      });
    } catch (error) {
      console.log('Failed to sync notification subscriptions');
    }
  }

  private flushNotificationQueue() {
    if (!this.isConnected) return;

    while (this.notificationQueue.length > 0) {
      const notification = this.notificationQueue.shift();
      if (notification) {
        this.processNotification(notification);
      }
    }
  }

  private generateId(): string {
    return `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Public API
  subscribe(callback: (notification: RealTimeNotification) => void): string {
    const id = this.generateId();
    this.subscribers.set(id, callback);
    return id;
  }

  unsubscribe(id: string) {
    this.subscribers.delete(id);
  }

  async updatePreferences(preferences: Partial<NotificationPreferences>) {
    this.preferences = { ...this.preferences, ...preferences };
    localStorage.setItem('aurum_notification_preferences', JSON.stringify(this.preferences));
    
    try {
      await apiService.updateNotificationPreferences(this.preferences);
    } catch (error) {
      console.log('Failed to sync preferences to server');
    }

    if (this.isConnected) {
      this.syncSubscriptions();
    }
  }

  getPreferences(): NotificationPreferences {
    return { ...this.preferences };
  }

  async createSubscription(subscription: Omit<NotificationSubscription, 'id'>): Promise<string> {
    const id = this.generateId();
    const fullSubscription = { ...subscription, id };
    this.subscriptions.push(fullSubscription);

    try {
      await apiService.createNotificationSubscription(fullSubscription);
    } catch (error) {
      console.log('Failed to create notification subscription');
    }

    if (this.isConnected) {
      this.syncSubscriptions();
    }

    return id;
  }

  async removeSubscription(id: string) {
    this.subscriptions = this.subscriptions.filter(sub => sub.id !== id);

    try {
      await apiService.deleteNotificationSubscription(id);
    } catch (error) {
      console.log('Failed to remove notification subscription');
    }

    if (this.isConnected) {
      this.syncSubscriptions();
    }
  }

  async getNotificationHistory(limit = 50): Promise<RealTimeNotification[]> {
    try {
      return await apiService.getNotificationHistory(limit);
    } catch (error) {
      // Fallback to local storage
      const stored = JSON.parse(localStorage.getItem('aurum_notifications') || '[]');
      return stored.slice(0, limit);
    }
  }

  async markAsRead(notificationIds: string[]) {
    try {
      await apiService.markNotificationsAsRead(notificationIds);
    } catch (error) {
      // Update local storage
      const stored = JSON.parse(localStorage.getItem('aurum_notifications') || '[]');
      const updated = stored.map((notif: RealTimeNotification) => 
        notificationIds.includes(notif.id) ? { ...notif, isRead: true } : notif
      );
      localStorage.setItem('aurum_notifications', JSON.stringify(updated));
    }
  }

  async createNotification(notification: Omit<RealTimeNotification, 'id' | 'timestamp' | 'isRead'>) {
    const fullNotification: RealTimeNotification = {
      ...notification,
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      isRead: false,
    };

    await this.processNotification(fullNotification);
    return fullNotification.id;
  }

  // Test notification for debugging
  async sendTestNotification() {
    const testNotification: RealTimeNotification = {
      id: this.generateId(),
      type: 'system_alert',
      priority: 'medium',
      title: 'Test Notification',
      message: 'This is a test notification from the real-time notification system.',
      timestamp: new Date().toISOString(),
      isRead: false,
      category: 'system',
      source: 'system',
      actions: [
        {
          id: 'dismiss',
          label: 'Dismiss',
          type: 'secondary',
          action: 'dismiss',
        },
      ],
    };

    await this.processNotification(testNotification);
    return testNotification.id;
  }

  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      websocketState: websocketService.getConnectionState(),
      queueLength: this.notificationQueue.length,
      subscriberCount: this.subscribers.size,
      subscriptionCount: this.subscriptions.length,
      browserPermission: typeof window !== 'undefined' && 'Notification' in window ? Notification.permission : 'unsupported',
    };
  }

  async requestBrowserPermission(): Promise<NotificationPermission> {
    if (typeof window === 'undefined' || !('Notification' in window)) {
      return 'denied';
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      
      // Update delivery preferences if permission granted
      if (permission === 'granted') {
        this.updatePreferences({
          delivery: {
            ...this.preferences.delivery,
            browser: true,
          },
        });
      }
      
      return permission;
    }

    return Notification.permission;
  }

  destroy() {
    this.subscribers.clear();
    this.subscriptions = [];
    this.notificationQueue = [];
    this.rateLimitCounters.clear();
    websocketService.destroy();
  }
}

export const realTimeNotificationService = new RealTimeNotificationService();
export default realTimeNotificationService;