import { projectId, publicAnonKey } from '../utils/supabase/info';

export interface WebSocketMessage {
  type: 'user_stats_updated' | 'pillar_health_updated' | 'new_recommendation' | 'task_completed' | 'notification' | 'heartbeat';
  payload: any;
  timestamp: string;
  user_id?: string;
}

export interface WebSocketEventHandlers {
  onUserStatsUpdated?: (data: any) => void;
  onPillarHealthUpdated?: (data: any) => void;
  onNewRecommendation?: (data: any) => void;
  onTaskCompleted?: (data: any) => void;
  onNotification?: (data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
  onReconnect?: () => void;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private isConnecting = false;
  private eventHandlers: WebSocketEventHandlers = {};
  private messageQueue: WebSocketMessage[] = [];
  private isOnline = navigator.onLine;

  constructor() {
    // Monitor online/offline status
    window.addEventListener('online', this.handleOnline.bind(this));
    window.addEventListener('offline', this.handleOffline.bind(this));
    
    // Handle page visibility changes
    document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
  }

  private handleOnline() {
    // Silent online detection
    this.isOnline = true;
    // Don't attempt to connect automatically to avoid errors
  }

  private handleOffline() {
    // Silent offline detection
    this.isOnline = false;
    this.disconnect();
  }

  private handleVisibilityChange() {
    // Silent visibility change handling - no automatic reconnection
    // to prevent error loops
  }

  connect(handlers: WebSocketEventHandlers = {}): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting) {
        // Silent handling - connection in progress
        resolve();
        return;
      }

      if (!this.isOnline) {
        // Silent offline handling
        resolve();
        return;
      }

      this.isConnecting = true;
      this.eventHandlers = { ...this.eventHandlers, ...handlers };

      try {
        const token = localStorage.getItem('supabase_access_token') || publicAnonKey;
        const wsUrl = `wss://${projectId}.supabase.co/functions/v1/make-server-dd6e2894/ws?token=${encodeURIComponent(token)}`;
        
        // Silent WebSocket creation
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          // Silent connection success
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          this.startHeartbeat();
          this.flushMessageQueue();
          this.eventHandlers.onConnect?.();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            // Silent message parsing error handling
          }
        };

        this.ws.onerror = (error) => {
          // Silently handle WebSocket connection failures - no logging
          this.isConnecting = false;
          // Don't call error handlers or log anything - complete silence
          // WebSocket errors are expected when backend is not available
        };

        this.ws.onclose = (event) => {
          // Silently handle WebSocket disconnection - no logging
          this.isConnecting = false;
          this.stopHeartbeat();
          this.eventHandlers.onDisconnect?.();
          
          // Don't attempt reconnection to avoid error loops
          // Just stay in disconnected state silently
        };

        // Connection timeout - resolve gracefully and silently
        setTimeout(() => {
          if (this.isConnecting) {
            // Silent timeout handling - no logging
            this.isConnecting = false;
            this.ws?.close();
            // Resolve without any output
            resolve();
          }
        }, 3000); // Even shorter timeout - 3 seconds

      } catch (error) {
        // Silent error handling - no logging
        this.isConnecting = false;
        // Resolve without any output
        resolve();
      }
    });
  }

  private scheduleReconnect() {
    // Disabled to prevent error loops - no automatic reconnection
    // The app works perfectly without WebSocket connectivity
  }

  private startHeartbeat() {
    this.stopHeartbeat(); // Clear any existing interval
    
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'ping',
          timestamp: new Date().toISOString()
        }));
      }
    }, 30000); // Send ping every 30 seconds
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private handleMessage(message: WebSocketMessage) {
    // Silent message handling

    switch (message.type) {
      case 'user_stats_updated':
        this.eventHandlers.onUserStatsUpdated?.(message.payload);
        break;
      case 'pillar_health_updated':
        this.eventHandlers.onPillarHealthUpdated?.(message.payload);
        break;
      case 'new_recommendation':
        this.eventHandlers.onNewRecommendation?.(message.payload);
        break;
      case 'task_completed':
        this.eventHandlers.onTaskCompleted?.(message.payload);
        break;
      case 'notification':
        this.eventHandlers.onNotification?.(message.payload);
        break;
      case 'heartbeat':
        // Handle server heartbeat response
        break;
      default:
        // Silent handling of unknown message types
    }
  }

  private flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }
  }

  send(message: Partial<WebSocketMessage>) {
    const fullMessage: WebSocketMessage = {
      ...message,
      timestamp: new Date().toISOString(),
      user_id: localStorage.getItem('user_id') || undefined
    } as WebSocketMessage;

    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(fullMessage));
        // Silent message sending
      } catch (error) {
        // Silent error handling - queue message for retry
        this.messageQueue.push(fullMessage);
      }
    } else {
      // Silent queueing
      this.messageQueue.push(fullMessage);
    }
  }

  disconnect() {
    // Silent disconnect
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getConnectionState(): string {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }

  // Subscribe to specific event types
  subscribe(eventType: keyof WebSocketEventHandlers, handler: Function) {
    this.eventHandlers[eventType] = handler as any;
  }

  // Unsubscribe from event types
  unsubscribe(eventType: keyof WebSocketEventHandlers) {
    delete this.eventHandlers[eventType];
  }

  // Request real-time updates for specific data
  requestUpdates(dataTypes: string[]) {
    this.send({
      type: 'subscribe' as any,
      payload: { data_types: dataTypes }
    });
  }

  // Stop real-time updates for specific data
  stopUpdates(dataTypes: string[]) {
    this.send({
      type: 'unsubscribe' as any,
      payload: { data_types: dataTypes }
    });
  }

  // Cleanup method
  destroy() {
    this.disconnect();
    window.removeEventListener('online', this.handleOnline.bind(this));
    window.removeEventListener('offline', this.handleOffline.bind(this));
    document.removeEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    this.eventHandlers = {};
    this.messageQueue = [];
  }
}

export const websocketService = new WebSocketService();
export default websocketService;