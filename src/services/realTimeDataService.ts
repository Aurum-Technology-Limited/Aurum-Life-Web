/**
 * Phase 2: Real-Time Data Synchronization Service
 * Handles real-time data updates beyond notifications
 */

import { websocketService } from './websocketService';

interface DataSyncEvent {
  type: 'pillar' | 'area' | 'project' | 'task' | 'journal' | 'analytics';
  operation: 'create' | 'update' | 'delete' | 'bulk_update';
  data: any;
  userId: string;
  timestamp: string;
  source: 'local' | 'remote' | 'ai';
}

interface SyncState {
  lastSyncTime: string;
  pendingChanges: DataSyncEvent[];
  conflictResolution: 'latest_wins' | 'merge' | 'manual';
}

class RealTimeDataService {
  private subscribers: Map<string, Set<(event: DataSyncEvent) => void>> = new Map();
  private syncState: SyncState = {
    lastSyncTime: new Date().toISOString(),
    pendingChanges: [],
    conflictResolution: 'latest_wins'
  };
  private isConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor() {
    this.initializeWebSocketListeners();
    this.loadSyncState();
  }

  private initializeWebSocketListeners() {
    websocketService.subscribe('data_sync', (event) => {
      this.handleRemoteDataChange(event as DataSyncEvent);
    });

    websocketService.subscribe('connection_status', (status) => {
      this.isConnected = status.connected;
      if (status.connected) {
        this.reconnectAttempts = 0;
        this.syncPendingChanges();
      } else {
        this.handleDisconnection();
      }
    });
  }

  private loadSyncState() {
    try {
      const saved = localStorage.getItem('aurum-sync-state');
      if (saved) {
        this.syncState = { ...this.syncState, ...JSON.parse(saved) };
      }
    } catch (error) {
      console.warn('Failed to load sync state:', error);
    }
  }

  private saveSyncState() {
    try {
      localStorage.setItem('aurum-sync-state', JSON.stringify(this.syncState));
    } catch (error) {
      console.warn('Failed to save sync state:', error);
    }
  }

  /**
   * Subscribe to real-time data changes for a specific data type
   */
  subscribe(dataType: DataSyncEvent['type'], callback: (event: DataSyncEvent) => void) {
    if (!this.subscribers.has(dataType)) {
      this.subscribers.set(dataType, new Set());
    }
    this.subscribers.get(dataType)!.add(callback);

    // Return unsubscribe function
    return () => {
      const typeSubscribers = this.subscribers.get(dataType);
      if (typeSubscribers) {
        typeSubscribers.delete(callback);
        if (typeSubscribers.size === 0) {
          this.subscribers.delete(dataType);
        }
      }
    };
  }

  /**
   * Publish a local data change for synchronization
   */
  publishLocalChange(event: Omit<DataSyncEvent, 'timestamp' | 'source'>) {
    const fullEvent: DataSyncEvent = {
      ...event,
      timestamp: new Date().toISOString(),
      source: 'local'
    };

    // Add to pending changes if offline
    if (!this.isConnected) {
      this.syncState.pendingChanges.push(fullEvent);
      this.saveSyncState();
      console.log('Queued change for sync when online:', fullEvent.type, fullEvent.operation);
      return;
    }

    // Send immediately if online
    this.sendToServer(fullEvent);
    
    // Notify local subscribers
    this.notifySubscribers(fullEvent);
  }

  private async sendToServer(event: DataSyncEvent) {
    try {
      websocketService.send('data_sync', event);
      
      // Update last sync time on successful send
      this.syncState.lastSyncTime = event.timestamp;
      this.saveSyncState();
    } catch (error) {
      console.error('Failed to send data sync event:', error);
      
      // Add to pending changes if send fails
      this.syncState.pendingChanges.push(event);
      this.saveSyncState();
    }
  }

  private handleRemoteDataChange(event: DataSyncEvent) {
    // Check for conflicts
    const hasConflict = this.detectConflict(event);
    
    if (hasConflict) {
      this.resolveConflict(event);
    } else {
      // No conflict, apply change
      this.notifySubscribers(event);
      this.syncState.lastSyncTime = event.timestamp;
      this.saveSyncState();
    }
  }

  private detectConflict(remoteEvent: DataSyncEvent): boolean {
    // Check if we have a pending local change for the same data
    return this.syncState.pendingChanges.some(localEvent => 
      localEvent.type === remoteEvent.type &&
      localEvent.data?.id === remoteEvent.data?.id &&
      new Date(localEvent.timestamp) > new Date(remoteEvent.timestamp)
    );
  }

  private resolveConflict(remoteEvent: DataSyncEvent) {
    switch (this.syncState.conflictResolution) {
      case 'latest_wins':
        // Keep the most recent change
        const localEvent = this.syncState.pendingChanges.find(e => 
          e.type === remoteEvent.type && e.data?.id === remoteEvent.data?.id
        );
        
        if (localEvent && new Date(localEvent.timestamp) > new Date(remoteEvent.timestamp)) {
          // Local change is newer, ignore remote
          console.log('Conflict resolved: keeping local change (newer)');
        } else {
          // Remote change is newer, apply it
          this.notifySubscribers(remoteEvent);
          this.removeConflictingPendingChange(remoteEvent);
        }
        break;
        
      case 'merge':
        // Attempt to merge changes
        this.attemptMerge(remoteEvent);
        break;
        
      case 'manual':
        // Emit conflict event for manual resolution
        this.emitConflictEvent(remoteEvent);
        break;
    }
  }

  private removeConflictingPendingChange(remoteEvent: DataSyncEvent) {
    this.syncState.pendingChanges = this.syncState.pendingChanges.filter(localEvent =>
      !(localEvent.type === remoteEvent.type && localEvent.data?.id === remoteEvent.data?.id)
    );
    this.saveSyncState();
  }

  private attemptMerge(remoteEvent: DataSyncEvent) {
    // Simple merge strategy - combine non-conflicting fields
    const localEvent = this.syncState.pendingChanges.find(e => 
      e.type === remoteEvent.type && e.data?.id === remoteEvent.data?.id
    );

    if (localEvent && localEvent.data && remoteEvent.data) {
      const mergedData = { ...remoteEvent.data, ...localEvent.data };
      const mergedEvent: DataSyncEvent = {
        ...remoteEvent,
        data: mergedData,
        source: 'local',
        timestamp: new Date().toISOString()
      };

      this.notifySubscribers(mergedEvent);
      this.sendToServer(mergedEvent);
      this.removeConflictingPendingChange(remoteEvent);
    }
  }

  private emitConflictEvent(remoteEvent: DataSyncEvent) {
    // Emit a special conflict event that UI can handle
    window.dispatchEvent(new CustomEvent('aurumDataConflict', {
      detail: {
        remote: remoteEvent,
        local: this.syncState.pendingChanges.find(e => 
          e.type === remoteEvent.type && e.data?.id === remoteEvent.data?.id
        )
      }
    }));
  }

  private notifySubscribers(event: DataSyncEvent) {
    const typeSubscribers = this.subscribers.get(event.type);
    if (typeSubscribers) {
      typeSubscribers.forEach(callback => {
        try {
          callback(event);
        } catch (error) {
          console.error('Error in data sync subscriber:', error);
        }
      });
    }
  }

  private async syncPendingChanges() {
    if (this.syncState.pendingChanges.length === 0) return;

    console.log(`Syncing ${this.syncState.pendingChanges.length} pending changes...`);
    
    const changesToSync = [...this.syncState.pendingChanges];
    this.syncState.pendingChanges = [];
    this.saveSyncState();

    for (const change of changesToSync) {
      try {
        await this.sendToServer(change);
      } catch (error) {
        console.error('Failed to sync pending change:', error);
        // Re-add to pending if sync fails
        this.syncState.pendingChanges.push(change);
      }
    }

    this.saveSyncState();
  }

  private handleDisconnection() {
    this.reconnectAttempts++;
    console.log(`WebSocket disconnected. Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
    
    if (this.reconnectAttempts <= this.maxReconnectAttempts) {
      setTimeout(() => {
        if (!this.isConnected) {
          websocketService.connect();
        }
      }, Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000));
    }
  }

  /**
   * Force a full synchronization
   */
  async forcefulSync() {
    this.syncState.lastSyncTime = new Date(0).toISOString(); // Reset to force full sync
    await this.syncPendingChanges();
    
    // Request full sync from server
    websocketService.send('request_full_sync', {
      userId: this.getCurrentUserId(),
      lastSync: this.syncState.lastSyncTime
    });
  }

  private getCurrentUserId(): string {
    // Get from auth store or localStorage
    try {
      const authData = localStorage.getItem('aurum-auth');
      if (authData) {
        const parsed = JSON.parse(authData);
        return parsed.user?.id || 'anonymous';
      }
    } catch (error) {
      console.warn('Failed to get user ID for sync:', error);
    }
    return 'anonymous';
  }

  /**
   * Get current sync status
   */
  getSyncStatus() {
    return {
      isConnected: this.isConnected,
      lastSyncTime: this.syncState.lastSyncTime,
      pendingChanges: this.syncState.pendingChanges.length,
      reconnectAttempts: this.reconnectAttempts
    };
  }

  /**
   * Configure conflict resolution strategy
   */
  setConflictResolution(strategy: SyncState['conflictResolution']) {
    this.syncState.conflictResolution = strategy;
    this.saveSyncState();
  }

  /**
   * Clean up and disconnect
   */
  disconnect() {
    this.subscribers.clear();
    this.saveSyncState();
  }
}

export const realTimeDataService = new RealTimeDataService();
export type { DataSyncEvent, SyncState };