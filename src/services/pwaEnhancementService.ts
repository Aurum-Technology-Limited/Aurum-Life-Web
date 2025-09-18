/**
 * Phase 2: PWA Enhancement Service
 * Enhanced mobile experience with offline support and installability
 */

interface OfflineData {
  pillars: any[];
  areas: any[];
  projects: any[];
  tasks: any[];
  journalEntries: any[];
  settings: any;
  lastSync: string;
}

interface InstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

interface PWACapabilities {
  isInstallable: boolean;
  isStandalone: boolean;
  hasNotifications: boolean;
  hasOfflineCapability: boolean;
  hasBackgroundSync: boolean;
  hasShare: boolean;
}

class PWAEnhancementService {
  private isOnline = navigator.onLine;
  private installPrompt: InstallPromptEvent | null = null;
  private offlineData: OfflineData | null = null;
  private syncQueue: Array<{ action: string; data: any; timestamp: string }> = [];
  private capabilities: PWACapabilities;

  constructor() {
    this.capabilities = this.detectCapabilities();
    this.initializeEventListeners();
    this.loadOfflineData();
    this.registerServiceWorker();
  }

  private detectCapabilities(): PWACapabilities {
    return {
      isInstallable: false, // Will be updated when beforeinstallprompt fires
      isStandalone: window.matchMedia('(display-mode: standalone)').matches || 
                   (window.navigator as any).standalone === true,
      hasNotifications: 'Notification' in window && 'serviceWorker' in navigator,
      hasOfflineCapability: 'serviceWorker' in navigator && 'caches' in window,
      hasBackgroundSync: 'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype,
      hasShare: 'share' in navigator
    };
  }

  private initializeEventListeners() {
    // Online/offline detection
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.handleOnlineStatusChange(true);
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.handleOnlineStatusChange(false);
    });

    // Install prompt handling
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.installPrompt = e as InstallPromptEvent;
      this.capabilities.isInstallable = true;
      this.notifyInstallAvailable();
    });

    // App installed detection
    window.addEventListener('appinstalled', () => {
      this.installPrompt = null;
      this.capabilities.isInstallable = false;
      this.notifyAppInstalled();
    });

    // Visibility change for background sync
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.isOnline) {
        this.processOfflineQueue();
      }
    });

    // Handle PWA navigation
    window.addEventListener('popstate', this.handlePWANavigation.bind(this));
  }

  private async registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
      console.log('Service Worker not supported');
      return;
    }

    // Skip service worker registration in development or iframe environments
    if (this.shouldSkipServiceWorkerRegistration()) {
      console.log('Service Worker registration skipped for this environment');
      return;
    }

    try {
      // Determine which service worker to use based on environment
      const isDevelopment = this.isDevelopmentEnvironment();
      const swPath = isDevelopment ? '/sw-mock.js' : '/sw.js';
      
      // Try to register the appropriate service worker
      let registration;
      try {
        registration = await navigator.serviceWorker.register(swPath);
        console.log(`${isDevelopment ? 'Mock ' : ''}Service Worker registered:`, registration);
      } catch (swError) {
        // If main service worker fails, try mock as fallback
        if (!isDevelopment) {
          console.log('Production service worker failed, trying mock fallback');
          registration = await navigator.serviceWorker.register('/sw-mock.js');
          console.log('Mock Service Worker registered as fallback:', registration);
        } else {
          throw swError;
        }
      }

      // Handle service worker updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.notifyUpdateAvailable();
            }
          });
        }
      });

      // Listen for messages from service worker
      navigator.serviceWorker.addEventListener('message', this.handleServiceWorkerMessage.bind(this));

    } catch (error) {
      console.log('Service Worker registration failed (this is normal in development):', error.message);
      // Don't throw error - just log and continue without service worker
    }
  }

  private shouldSkipServiceWorkerRegistration(): boolean {
    // Skip in iframe environments (like Figma)
    if (window !== window.top) {
      return true;
    }

    return false;
  }

  private isDevelopmentEnvironment(): boolean {
    const hostname = window.location.hostname;
    
    // Development indicators
    return (
      hostname.includes('figma') || 
      hostname.includes('localhost') ||
      hostname.includes('127.0.0.1') ||
      hostname.includes('dev') ||
      hostname.includes('preview') ||
      hostname.includes('staging') ||
      // If not HTTPS and not localhost, likely development
      (window.location.protocol !== 'https:' && hostname !== 'localhost')
    );
  }

  private handleServiceWorkerMessage(event: MessageEvent) {
    const { type, data } = event.data;

    switch (type) {
      case 'BACKGROUND_SYNC':
        this.handleBackgroundSync(data);
        break;
      case 'PUSH_NOTIFICATION':
        this.handlePushNotification(data);
        break;
      case 'CACHE_UPDATE':
        this.handleCacheUpdate(data);
        break;
    }
  }

  private handleOnlineStatusChange(isOnline: boolean) {
    console.log(`App is now ${isOnline ? 'online' : 'offline'}`);
    
    // Dispatch custom event for components to react
    window.dispatchEvent(new CustomEvent('aurumConnectionChange', {
      detail: { isOnline, hasOfflineData: !!this.offlineData }
    }));

    if (isOnline) {
      this.processOfflineQueue();
      this.syncWithServer();
    } else {
      this.ensureOfflineDataAvailable();
    }
  }

  private loadOfflineData() {
    try {
      const stored = localStorage.getItem('aurum-offline-data');
      if (stored) {
        this.offlineData = JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Failed to load offline data:', error);
    }
  }

  private saveOfflineData() {
    if (!this.offlineData) return;

    try {
      localStorage.setItem('aurum-offline-data', JSON.stringify(this.offlineData));
    } catch (error) {
      console.warn('Failed to save offline data:', error);
    }
  }

  /**
   * Cache data for offline use
   */
  async cacheDataForOffline(data: Partial<OfflineData>) {
    this.offlineData = {
      pillars: data.pillars || this.offlineData?.pillars || [],
      areas: data.areas || this.offlineData?.areas || [],
      projects: data.projects || this.offlineData?.projects || [],
      tasks: data.tasks || this.offlineData?.tasks || [],
      journalEntries: data.journalEntries || this.offlineData?.journalEntries || [],
      settings: data.settings || this.offlineData?.settings || {},
      lastSync: new Date().toISOString()
    };

    this.saveOfflineData();

    // Also cache in service worker cache
    if ('caches' in window) {
      try {
        const cache = await caches.open('aurum-offline-data-v1');
        await cache.put('/offline-data', new Response(JSON.stringify(this.offlineData)));
      } catch (error) {
        console.warn('Failed to cache data in service worker:', error);
      }
    }
  }

  /**
   * Get offline data
   */
  getOfflineData(): OfflineData | null {
    return this.offlineData;
  }

  /**
   * Check if app can work offline
   */
  canWorkOffline(): boolean {
    return this.capabilities.hasOfflineCapability && !!this.offlineData;
  }

  /**
   * Add action to offline queue
   */
  queueOfflineAction(action: string, data: any) {
    this.syncQueue.push({
      action,
      data,
      timestamp: new Date().toISOString()
    });

    // Save queue to localStorage
    try {
      localStorage.setItem('aurum-sync-queue', JSON.stringify(this.syncQueue));
    } catch (error) {
      console.warn('Failed to save sync queue:', error);
    }

    // If online, process immediately
    if (this.isOnline) {
      this.processOfflineQueue();
    }
  }

  private async processOfflineQueue() {
    if (this.syncQueue.length === 0) return;

    console.log(`Processing ${this.syncQueue.length} queued actions...`);

    const actionsToProcess = [...this.syncQueue];
    this.syncQueue = [];

    for (const queuedAction of actionsToProcess) {
      try {
        await this.processQueuedAction(queuedAction);
      } catch (error) {
        console.error('Failed to process queued action:', error);
        // Re-add to queue if processing fails
        this.syncQueue.push(queuedAction);
      }
    }

    // Update localStorage
    localStorage.setItem('aurum-sync-queue', JSON.stringify(this.syncQueue));
  }

  private async processQueuedAction(queuedAction: { action: string; data: any; timestamp: string }) {
    // This would integrate with your real-time data service
    console.log('Processing queued action:', queuedAction.action);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Dispatch event to notify components
    window.dispatchEvent(new CustomEvent('aurumOfflineActionProcessed', {
      detail: queuedAction
    }));
  }

  private async syncWithServer() {
    if (!this.isOnline) return;

    try {
      console.log('Syncing with server...');
      
      // This would fetch latest data from server
      // and update offline cache
      
      window.dispatchEvent(new CustomEvent('aurumSyncComplete', {
        detail: { success: true, timestamp: new Date().toISOString() }
      }));
      
    } catch (error) {
      console.error('Sync failed:', error);
      
      window.dispatchEvent(new CustomEvent('aurumSyncComplete', {
        detail: { success: false, error: error.message }
      }));
    }
  }

  private ensureOfflineDataAvailable() {
    if (!this.offlineData) {
      // Try to load from cache or create minimal dataset
      this.createMinimalOfflineData();
    }
  }

  private createMinimalOfflineData() {
    // Create a minimal dataset for offline use
    this.offlineData = {
      pillars: JSON.parse(localStorage.getItem('aurum-pillars') || '[]'),
      areas: JSON.parse(localStorage.getItem('aurum-areas') || '[]'),
      projects: JSON.parse(localStorage.getItem('aurum-projects') || '[]'),
      tasks: JSON.parse(localStorage.getItem('aurum-tasks') || '[]'),
      journalEntries: JSON.parse(localStorage.getItem('aurum-journal-entries') || '[]'),
      settings: JSON.parse(localStorage.getItem('aurum-settings') || '{}'),
      lastSync: new Date().toISOString()
    };

    this.saveOfflineData();
  }

  /**
   * Prompt user to install PWA
   */
  async promptInstall(): Promise<boolean> {
    if (!this.installPrompt) {
      return false;
    }

    try {
      await this.installPrompt.prompt();
      const choiceResult = await this.installPrompt.userChoice;
      
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
        return true;
      } else {
        console.log('User dismissed the install prompt');
        return false;
      }
    } catch (error) {
      console.error('Error showing install prompt:', error);
      return false;
    }
  }

  /**
   * Share content using Web Share API
   */
  async shareContent(data: { title: string; text?: string; url?: string }): Promise<boolean> {
    if (!this.capabilities.hasShare) {
      // Fallback to copying to clipboard
      await this.copyToClipboard(`${data.title}\n${data.text || ''}\n${data.url || ''}`);
      return true;
    }

    try {
      await navigator.share(data);
      return true;
    } catch (error) {
      console.error('Error sharing content:', error);
      return false;
    }
  }

  private async copyToClipboard(text: string) {
    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
  }

  /**
   * Request notification permissions
   */
  async requestNotificationPermission(): Promise<boolean> {
    if (!this.capabilities.hasNotifications) {
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission === 'denied') {
      return false;
    }

    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  /**
   * Show local notification
   */
  async showNotification(title: string, options: NotificationOptions = {}) {
    if (!await this.requestNotificationPermission()) {
      return;
    }

    // Show via service worker for better persistence
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      try {
        navigator.serviceWorker.controller.postMessage({
          type: 'SHOW_NOTIFICATION',
          title,
          options: {
            ...options,
            icon: '/icons/icon-192x192.png',
            badge: '/icons/badge-72x72.png'
          }
        });
        return;
      } catch (error) {
        console.log('Service worker notification failed, using fallback:', error.message);
      }
    }

    // Fallback to direct notification
    try {
      new Notification(title, {
        ...options,
        icon: '/icons/icon-192x192.png'
      });
    } catch (error) {
      console.log('Direct notification failed:', error.message);
      // Dispatch custom event as final fallback
      window.dispatchEvent(new CustomEvent('aurumNotificationFallback', {
        detail: { title, options }
      }));
    }
  }

  /**
   * Register for background sync
   */
  async registerBackgroundSync(tag: string) {
    if (!this.capabilities.hasBackgroundSync) {
      return false;
    }

    // Skip if service worker registration was skipped
    if (this.shouldSkipServiceWorkerRegistration()) {
      console.log('Background sync skipped - service worker not available');
      return false;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register(tag);
      return true;
    } catch (error) {
      console.log('Background sync registration failed (this is normal in development):', error.message);
      return false;
    }
  }

  private handleBackgroundSync(data: any) {
    // Handle background sync completion
    console.log('Background sync completed:', data);
  }

  private handlePushNotification(data: any) {
    // Handle push notification
    console.log('Push notification received:', data);
  }

  private handleCacheUpdate(data: any) {
    // Handle cache update
    console.log('Cache updated:', data);
  }

  private handlePWANavigation(event: PopStateEvent) {
    // Handle PWA-specific navigation
    if (this.capabilities.isStandalone) {
      // Custom navigation handling for standalone mode
      console.log('PWA navigation:', event.state);
    }
  }

  private notifyInstallAvailable() {
    window.dispatchEvent(new CustomEvent('aurumInstallAvailable'));
  }

  private notifyAppInstalled() {
    window.dispatchEvent(new CustomEvent('aurumAppInstalled'));
  }

  private notifyUpdateAvailable() {
    window.dispatchEvent(new CustomEvent('aurumUpdateAvailable'));
  }

  /**
   * Get PWA capabilities
   */
  getCapabilities(): PWACapabilities {
    return { ...this.capabilities };
  }

  /**
   * Get connection status
   */
  getConnectionStatus() {
    return {
      isOnline: this.isOnline,
      canWorkOffline: this.canWorkOffline(),
      queuedActions: this.syncQueue.length,
      lastSync: this.offlineData?.lastSync
    };
  }

  /**
   * Force refresh of offline data
   */
  async refreshOfflineData() {
    if (this.isOnline) {
      await this.syncWithServer();
    } else {
      this.ensureOfflineDataAvailable();
    }
  }

  /**
   * Clear offline data and cache
   */
  async clearOfflineData() {
    this.offlineData = null;
    localStorage.removeItem('aurum-offline-data');
    localStorage.removeItem('aurum-sync-queue');
    this.syncQueue = [];

    if ('caches' in window) {
      try {
        await caches.delete('aurum-offline-data-v1');
        await caches.delete('aurum-app-v1');
      } catch (error) {
        console.warn('Failed to clear caches:', error);
      }
    }
  }

  /**
   * Get offline data size
   */
  getOfflineDataSize(): number {
    if (!this.offlineData) return 0;
    
    try {
      return new Blob([JSON.stringify(this.offlineData)]).size;
    } catch {
      return 0;
    }
  }

  /**
   * Check if feature works offline
   */
  isFeatureAvailableOffline(feature: string): boolean {
    const offlineFeatures = [
      'pillars', 'areas', 'projects', 'tasks', 
      'journal', 'settings', 'search', 'analytics'
    ];
    
    return this.canWorkOffline() && offlineFeatures.includes(feature);
  }
}

export const pwaEnhancementService = new PWAEnhancementService();
export type { PWACapabilities, OfflineData };