/**
 * Audit Logging Service for AI Data Usage Transparency
 * Tracks all AI interactions, data usage, and privacy-sensitive operations
 */

import { useAppStore } from '../stores/basicAppStore';

export interface AuditLogEntry {
  id: string;
  timestamp: Date;
  userId: string;
  action: string;
  component: string;
  dataType: 'personal' | 'sensitive' | 'public' | 'ai_generated';
  description: string;
  metadata: Record<string, any>;
  privacyLevel: 'low' | 'medium' | 'high' | 'critical';
  retentionPeriod: number; // days
  userConsent: boolean;
  purpose: string;
}

export interface DataUsageStats {
  totalAIInteractions: number;
  dataProcessed: {
    personal: number;
    sensitive: number;
    public: number;
    ai_generated: number;
  };
  retentionSummary: {
    toBeDeleted: number;
    activeRetention: number;
  };
  consentStatus: {
    granted: number;
    revoked: number;
    pending: number;
  };
}

class AuditLoggingService {
  private logs: AuditLogEntry[] = [];
  private storageKey = 'aurum-audit-logs';
  private maxRetentionDays = 365; // 1 year default
  private maxLogEntries = 10000; // Prevent memory issues

  constructor() {
    this.loadLogs();
    this.setupAutoCleanup();
  }

  /**
   * Log an AI interaction or data usage event
   */
  logEvent(
    action: string,
    component: string,
    dataType: AuditLogEntry['dataType'],
    description: string,
    metadata: Record<string, any> = {},
    privacyLevel: AuditLogEntry['privacyLevel'] = 'medium',
    purpose: string = 'System operation'
  ): void {
    const userId = this.getCurrentUserId();
    if (!userId) return;

    const entry: AuditLogEntry = {
      id: this.generateId(),
      timestamp: new Date(),
      userId,
      action,
      component,
      dataType,
      description,
      metadata: {
        ...metadata,
        userAgent: navigator.userAgent,
        url: window.location.href,
      },
      privacyLevel,
      retentionPeriod: this.getRetentionPeriod(privacyLevel),
      userConsent: this.hasUserConsent(dataType),
      purpose,
    };

    this.logs.push(entry);
    this.enforceLogLimits();
    this.saveLogs();
    
    // Emit event for real-time monitoring
    this.emitAuditEvent(entry);
  }

  /**
   * Log AI data processing events
   */
  logAIInteraction(
    aiService: string,
    inputData: any,
    outputData: any,
    processingType: 'analysis' | 'generation' | 'categorization' | 'embedding',
    userPrompt?: string
  ): void {
    this.logEvent(
      'ai_interaction',
      `ai_service_${aiService}`,
      'ai_generated',
      `AI ${processingType} performed`,
      {
        service: aiService,
        processingType,
        inputSize: JSON.stringify(inputData).length,
        outputSize: JSON.stringify(outputData).length,
        hasUserPrompt: !!userPrompt,
        promptLength: userPrompt?.length || 0,
      },
      'high',
      `AI-powered ${processingType} for user productivity enhancement`
    );
  }

  /**
   * Log privacy-sensitive operations
   */
  logPrivacySensitiveAction(
    action: string,
    component: string,
    dataAccessed: string[],
    purpose: string,
    userInitiated: boolean = true
  ): void {
    this.logEvent(
      action,
      component,
      'sensitive',
      `Privacy-sensitive action: ${action}`,
      {
        dataAccessed,
        userInitiated,
        consentRequired: true,
      },
      'critical',
      purpose
    );
  }

  /**
   * Log data export/sharing events
   */
  logDataExport(
    exportType: 'full_backup' | 'partial_export' | 'sharing',
    dataTypes: string[],
    destination: string,
    format: string
  ): void {
    this.logEvent(
      'data_export',
      'export_system',
      'personal',
      `Data exported: ${exportType}`,
      {
        exportType,
        dataTypes,
        destination,
        format,
        exportSize: 'calculated_at_export',
      },
      'critical',
      'User-requested data portability'
    );
  }

  /**
   * Get audit logs for transparency dashboard
   */
  getAuditLogs(
    startDate?: Date,
    endDate?: Date,
    component?: string,
    privacyLevel?: AuditLogEntry['privacyLevel']
  ): AuditLogEntry[] {
    let filtered = [...this.logs];

    if (startDate) {
      filtered = filtered.filter(log => log.timestamp >= startDate);
    }

    if (endDate) {
      filtered = filtered.filter(log => log.timestamp <= endDate);
    }

    if (component) {
      filtered = filtered.filter(log => log.component === component);
    }

    if (privacyLevel) {
      filtered = filtered.filter(log => log.privacyLevel === privacyLevel);
    }

    return filtered.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  /**
   * Get data usage statistics
   */
  getDataUsageStats(days: number = 30): DataUsageStats {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    const recentLogs = this.logs.filter(log => log.timestamp >= cutoffDate);

    const stats: DataUsageStats = {
      totalAIInteractions: recentLogs.filter(log => log.action === 'ai_interaction').length,
      dataProcessed: {
        personal: recentLogs.filter(log => log.dataType === 'personal').length,
        sensitive: recentLogs.filter(log => log.dataType === 'sensitive').length,
        public: recentLogs.filter(log => log.dataType === 'public').length,
        ai_generated: recentLogs.filter(log => log.dataType === 'ai_generated').length,
      },
      retentionSummary: {
        toBeDeleted: this.getLogsToBeDeleted().length,
        activeRetention: this.logs.length,
      },
      consentStatus: {
        granted: recentLogs.filter(log => log.userConsent).length,
        revoked: recentLogs.filter(log => !log.userConsent).length,
        pending: 0, // Implementation depends on consent system
      },
    };

    return stats;
  }

  /**
   * Delete logs based on retention policy
   */
  cleanupExpiredLogs(): number {
    const toDelete = this.getLogsToBeDeleted();
    const deletedCount = toDelete.length;

    this.logs = this.logs.filter(log => {
      const retentionExpiry = new Date(log.timestamp);
      retentionExpiry.setDate(retentionExpiry.getDate() + log.retentionPeriod);
      return retentionExpiry > new Date();
    });

    this.saveLogs();
    return deletedCount;
  }

  /**
   * Export audit logs for user download
   */
  exportAuditLogs(format: 'json' | 'csv' = 'json'): string {
    this.logDataExport('partial_export', ['audit_logs'], 'user_download', format);

    if (format === 'json') {
      return JSON.stringify(this.logs, null, 2);
    } else {
      return this.convertToCSV(this.logs);
    }
  }

  /**
   * Handle user consent revocation
   */
  handleConsentRevocation(dataTypes: string[]): void {
    // Mark relevant logs
    this.logs.forEach(log => {
      if (dataTypes.includes(log.dataType)) {
        log.userConsent = false;
        log.metadata.consentRevoked = new Date().toISOString();
      }
    });

    this.logPrivacySensitiveAction(
      'consent_revocation',
      'privacy_controls',
      dataTypes,
      'User revoked consent for data processing',
      true
    );

    this.saveLogs();
  }

  // Private methods
  private loadLogs(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        this.logs = parsed.map((log: any) => ({
          ...log,
          timestamp: new Date(log.timestamp),
        }));
      }
    } catch (error) {
      console.error('Failed to load audit logs:', error);
      this.logs = [];
    }
  }

  private saveLogs(): void {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.logs));
    } catch (error) {
      console.error('Failed to save audit logs:', error);
    }
  }

  private getCurrentUserId(): string | null {
    // Get from auth store
    const authStore = useAppStore.getState();
    return 'user_placeholder'; // Replace with actual user ID logic
  }

  private hasUserConsent(dataType: AuditLogEntry['dataType']): boolean {
    // Check user's privacy settings
    return true; // Implement based on privacy consent system
  }

  private getRetentionPeriod(privacyLevel: AuditLogEntry['privacyLevel']): number {
    const periods = {
      low: 30,      // 30 days
      medium: 90,   // 3 months
      high: 180,    // 6 months
      critical: 365, // 1 year
    };
    return periods[privacyLevel] || 90;
  }

  private generateId(): string {
    return `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private enforceLogLimits(): void {
    if (this.logs.length > this.maxLogEntries) {
      // Remove oldest logs first
      this.logs.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
      this.logs = this.logs.slice(-this.maxLogEntries);
    }
  }

  private getLogsToBeDeleted(): AuditLogEntry[] {
    return this.logs.filter(log => {
      const retentionExpiry = new Date(log.timestamp);
      retentionExpiry.setDate(retentionExpiry.getDate() + log.retentionPeriod);
      return retentionExpiry <= new Date();
    });
  }

  private setupAutoCleanup(): void {
    // Clean up expired logs daily
    setInterval(() => {
      this.cleanupExpiredLogs();
    }, 24 * 60 * 60 * 1000); // 24 hours
  }

  private emitAuditEvent(entry: AuditLogEntry): void {
    window.dispatchEvent(new CustomEvent('auditLogEntry', { detail: entry }));
  }

  private convertToCSV(logs: AuditLogEntry[]): string {
    const headers = ['ID', 'Timestamp', 'Action', 'Component', 'Data Type', 'Description', 'Privacy Level', 'User Consent', 'Purpose'];
    const csvRows = [headers.join(',')];

    logs.forEach(log => {
      const row = [
        log.id,
        log.timestamp.toISOString(),
        log.action,
        log.component,
        log.dataType,
        `"${log.description.replace(/"/g, '""')}"`,
        log.privacyLevel,
        log.userConsent.toString(),
        `"${log.purpose.replace(/"/g, '""')}"`,
      ];
      csvRows.push(row.join(','));
    });

    return csvRows.join('\n');
  }
}

// Create singleton instance
export const auditLogger = new AuditLoggingService();

// Convenience methods for common logging patterns
export const logAIInteraction = auditLogger.logAIInteraction.bind(auditLogger);
export const logPrivacyAction = auditLogger.logPrivacySensitiveAction.bind(auditLogger);
export const logDataExport = auditLogger.logDataExport.bind(auditLogger);

export default auditLogger;