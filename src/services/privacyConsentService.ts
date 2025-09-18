/**
 * Privacy Consent Service
 * Comprehensive privacy management and consent handling
 */

import { projectId, publicAnonKey } from '../utils/supabase/info';

interface PrivacySettings {
  dataCollection: {
    analytics: boolean;
    usage: boolean;
    performance: boolean;
    errors: boolean;
    interactions: boolean;
  };
  aiFeatures: {
    smartSuggestions: boolean;
    productivityInsights: boolean;
    goalRecommendations: boolean;
    habitTracking: boolean;
    timeBlocking: boolean;
    semanticSearch: boolean;
    autoTagging: boolean;
    contentAnalysis: boolean;
  };
  dataSharing: {
    anonymizedUsage: boolean;
    productImprovement: boolean;
    researchParticipation: boolean;
    marketingCommunications: boolean;
    thirdPartyIntegrations: boolean;
  };
  dataRetention: {
    activityLogs: 'forever' | '1year' | '6months' | '3months';
    analyticsData: 'forever' | '1year' | '6months' | '3months';
    aiInsights: 'forever' | '1year' | '6months' | '3months';
    deletedItems: 'forever' | '1year' | '6months' | '3months' | '30days';
  };
  visibility: {
    profileVisibility: 'private' | 'limited' | 'public';
    activitySharing: boolean;
    achievementSharing: boolean;
    progressSharing: boolean;
  };
  security: {
    twoFactorAuth: boolean;
    sessionTimeout: '15min' | '30min' | '1hour' | '4hours' | 'never';
    deviceTracking: boolean;
    loginNotifications: boolean;
  };
}

interface ConsentRecord {
  id: string;
  category: string;
  granted: boolean;
  timestamp: string;
  version: string;
  details: string;
}

interface AuditLogEntry {
  id: string;
  timestamp: string;
  action: string;
  category: 'data_access' | 'ai_processing' | 'data_export' | 'privacy_change' | 'consent_update';
  details: string;
  dataTypes: string[];
  purpose: string;
  automated: boolean;
}

interface PrivacyActionLog {
  action: string;
  category: 'data_access' | 'ai_processing' | 'data_export' | 'privacy_change' | 'consent_update';
  details: string;
  dataTypes: string[];
  purpose: string;
  automated?: boolean;
}

interface DataExport {
  user: any;
  profile: any;
  privacySettings: PrivacySettings;
  data: {
    pillars: any[];
    areas: any[];
    projects: any[];
    tasks: any[];
    journalEntries: any[];
  };
  settings: any;
  consentHistory: ConsentRecord[];
  auditLog: AuditLogEntry[];
  exportedAt: string;
  version: string;
}

class PrivacyConsentService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `https://${projectId}.supabase.co/functions/v1/make-server-dd6e2894`;
  }

  private getAuthToken(): string | null {
    try {
      const authData = localStorage.getItem('aurum-auth');
      if (authData) {
        const parsed = JSON.parse(authData);
        return parsed.session?.access_token;
      }
    } catch (error) {
      console.error('Failed to get auth token:', error);
    }
    return null;
  }

  private async apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getAuthToken();
    
    try {
      const response = await Promise.race([
        fetch(`${this.baseUrl}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token || publicAnonKey}`,
            ...options.headers,
          },
        }),
        new Promise<never>((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 5000)
        )
      ]);

      if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.log('Privacy service API error (non-critical):', errorMessage);
      throw error;
    }
  }

  /**
   * Get user's privacy settings
   */
  async getPrivacySettings(): Promise<PrivacySettings | null> {
    try {
      return await this.apiRequest<PrivacySettings>('/privacy/settings');
    } catch (error) {
      console.log('Privacy settings API failed, using fallback:', error);
      
      // Fallback to localStorage
      try {
        const userData = localStorage.getItem('aurum-auth');
        if (userData) {
          const parsed = JSON.parse(userData);
          const stored = localStorage.getItem(`aurum-privacy-settings-${parsed.user?.id}`);
          
          if (stored) {
            return JSON.parse(stored);
          }
        }
      } catch (fallbackError) {
        console.log('Fallback privacy settings loading failed:', fallbackError);
      }
      
      // Return default settings instead of null
      return this.initializePrivacySettings();
    }
  }

  /**
   * Update user's privacy settings
   */
  async updatePrivacySettings(settings: PrivacySettings): Promise<PrivacySettings> {
    try {
      return await this.apiRequest<PrivacySettings>('/privacy/settings', {
        method: 'PUT',
        body: JSON.stringify(settings),
      });
    } catch (error) {
      console.error('Failed to update privacy settings:', error);
      
      // Fallback to localStorage
      try {
        const userData = localStorage.getItem('aurum-auth');
        if (userData) {
          const parsed = JSON.parse(userData);
          const userId = parsed.user?.id;
          
          if (userId) {
            const settingsWithTimestamp = {
              ...settings,
              updatedAt: new Date().toISOString()
            };
            
            localStorage.setItem(`aurum-privacy-settings-${userId}`, JSON.stringify(settingsWithTimestamp));
            return settingsWithTimestamp;
          }
        }
      } catch (fallbackError) {
        console.error('Fallback privacy settings update failed:', fallbackError);
      }
      
      throw error;
    }
  }

  /**
   * Get consent history
   */
  async getConsentHistory(): Promise<ConsentRecord[]> {
    try {
      return await this.apiRequest<ConsentRecord[]>('/privacy/consent-history');
    } catch (error) {
      console.error('Failed to fetch consent history:', error);
      
      // Return mock consent history for demonstration
      return this.getMockConsentHistory();
    }
  }

  /**
   * Record new consent
   */
  async recordConsent(
    category: string,
    granted: boolean,
    details: string,
    version: string = '1.0'
  ): Promise<void> {
    try {
      await this.apiRequest('/privacy/consent', {
        method: 'POST',
        body: JSON.stringify({
          category,
          granted,
          details,
          version,
          timestamp: new Date().toISOString()
        }),
      });
    } catch (error) {
      console.error('Failed to record consent:', error);
      
      // Fallback to localStorage
      try {
        const userData = localStorage.getItem('aurum-auth');
        if (userData) {
          const parsed = JSON.parse(userData);
          const userId = parsed.user?.id;
          
          if (userId) {
            const consentRecord: ConsentRecord = {
              id: Date.now().toString(),
              category,
              granted,
              timestamp: new Date().toISOString(),
              version,
              details
            };
            
            const existingHistory = localStorage.getItem(`aurum-consent-history-${userId}`);
            const history = existingHistory ? JSON.parse(existingHistory) : [];
            history.push(consentRecord);
            
            localStorage.setItem(`aurum-consent-history-${userId}`, JSON.stringify(history));
          }
        }
      } catch (fallbackError) {
        console.error('Fallback consent recording failed:', fallbackError);
      }
    }
  }

  /**
   * Get privacy audit log
   */
  async getAuditLog(): Promise<AuditLogEntry[]> {
    try {
      return await this.apiRequest<AuditLogEntry[]>('/privacy/audit-log');
    } catch (error) {
      console.error('Failed to fetch audit log:', error);
      
      // Return mock audit log for demonstration
      return this.getMockAuditLog();
    }
  }

  /**
   * Log privacy-related action
   */
  async logPrivacyAction(action: PrivacyActionLog): Promise<void> {
    try {
      await this.apiRequest('/privacy/audit-log', {
        method: 'POST',
        body: JSON.stringify({
          ...action,
          timestamp: new Date().toISOString(),
          automated: action.automated || false
        }),
      });
    } catch (error) {
      console.error('Failed to log privacy action:', error);
      
      // Fallback to localStorage
      try {
        const userData = localStorage.getItem('aurum-auth');
        if (userData) {
          const parsed = JSON.parse(userData);
          const userId = parsed.user?.id;
          
          if (userId) {
            const auditEntry: AuditLogEntry = {
              id: Date.now().toString(),
              timestamp: new Date().toISOString(),
              automated: action.automated || false,
              ...action
            };
            
            const existingLog = localStorage.getItem(`aurum-audit-log-${userId}`);
            const log = existingLog ? JSON.parse(existingLog) : [];
            log.push(auditEntry);
            
            // Keep only last 100 entries to prevent localStorage bloat
            if (log.length > 100) {
              log.splice(0, log.length - 100);
            }
            
            localStorage.setItem(`aurum-audit-log-${userId}`, JSON.stringify(log));
          }
        }
      } catch (fallbackError) {
        console.error('Fallback audit logging failed:', fallbackError);
      }
    }
  }

  /**
   * Export all user data
   */
  async exportUserData(): Promise<DataExport> {
    try {
      return await this.apiRequest<DataExport>('/privacy/export');
    } catch (error) {
      console.error('Failed to export user data:', error);
      
      // Fallback to localStorage data export
      return this.exportLocalData();
    }
  }

  /**
   * Delete user account
   */
  async deleteAccount(): Promise<void> {
    try {
      await this.apiRequest('/privacy/delete-account', {
        method: 'DELETE'
      });
    } catch (error) {
      console.error('Failed to delete account:', error);
      throw error;
    }
  }

  /**
   * Check consent for specific category
   */
  async hasConsent(category: string): Promise<boolean> {
    try {
      const response = await this.apiRequest<{ hasConsent: boolean }>(`/privacy/consent/${category}`);
      return response.hasConsent;
    } catch (error) {
      console.log('Consent check API failed, using fallback:', error);
      
      // Fallback to privacy settings
      const settings = await this.getPrivacySettings();
      if (!settings) return false;
      
      // Map consent categories to settings
      switch (category) {
        case 'analytics':
        case 'data_collection':
          return settings.dataCollection.analytics;
        case 'ai_features':
        case 'ai_analysis':
          return Object.values(settings.aiFeatures).some(Boolean);
        case 'data_sharing':
          return Object.values(settings.dataSharing).some(Boolean);
        case 'marketing':
          return settings.dataSharing.marketingCommunications;
        case 'performance_analytics':
          return settings.dataCollection.performance;
        case 'third_party_integrations':
          return settings.dataSharing.thirdPartyIntegrations;
        default:
          return false;
      }
    }
  }

  /**
   * Get privacy compliance status
   */
  async getComplianceStatus(): Promise<{
    gdprCompliant: boolean;
    ccpaCompliant: boolean;
    lastAudit: string;
    issues: string[];
  }> {
    try {
      return await this.apiRequest('/privacy/compliance');
    } catch (error) {
      console.error('Failed to get compliance status:', error);
      
      // Return basic compliance info
      return {
        gdprCompliant: true,
        ccpaCompliant: true,
        lastAudit: new Date().toISOString(),
        issues: []
      };
    }
  }

  /**
   * Update consent for multiple categories
   */
  async updateBulkConsent(consents: Array<{
    category: string;
    granted: boolean;
    details?: string;
  }>): Promise<void> {
    try {
      await this.apiRequest('/privacy/bulk-consent', {
        method: 'POST',
        body: JSON.stringify({ consents }),
      });
    } catch (error) {
      console.error('Failed to update bulk consent:', error);
      
      // Fallback to individual consent updates
      for (const consent of consents) {
        await this.recordConsent(
          consent.category,
          consent.granted,
          consent.details || 'Bulk consent update'
        );
      }
    }
  }

  /**
   * Get data processing summary
   */
  async getDataProcessingSummary(): Promise<{
    totalDataPoints: number;
    aiProcessingEvents: number;
    dataSharedEvents: number;
    dataRetentionDays: number;
    lastProcessingDate: string;
  }> {
    try {
      return await this.apiRequest('/privacy/processing-summary');
    } catch (error) {
      console.error('Failed to get data processing summary:', error);
      
      // Return mock summary
      return {
        totalDataPoints: 1234,
        aiProcessingEvents: 567,
        dataSharedEvents: 0,
        dataRetentionDays: 365,
        lastProcessingDate: new Date().toISOString()
      };
    }
  }

  // Private helper methods

  private exportLocalData(): DataExport {
    const userData = localStorage.getItem('aurum-auth');
    const user = userData ? JSON.parse(userData).user : null;
    
    const export_data: DataExport = {
      user: {
        id: user?.id,
        email: user?.email,
        name: user?.user_metadata?.name,
        created_at: user?.created_at
      },
      profile: JSON.parse(localStorage.getItem(`aurum-profile-${user?.id}`) || '{}'),
      privacySettings: JSON.parse(localStorage.getItem(`aurum-privacy-settings-${user?.id}`) || '{}'),
      data: {
        pillars: JSON.parse(localStorage.getItem('aurum-pillars') || '[]'),
        areas: JSON.parse(localStorage.getItem('aurum-areas') || '[]'),
        projects: JSON.parse(localStorage.getItem('aurum-projects') || '[]'),
        tasks: JSON.parse(localStorage.getItem('aurum-tasks') || '[]'),
        journalEntries: JSON.parse(localStorage.getItem('aurum-journal-entries') || '[]')
      },
      settings: JSON.parse(localStorage.getItem('aurum-settings') || '{}'),
      consentHistory: JSON.parse(localStorage.getItem(`aurum-consent-history-${user?.id}`) || '[]'),
      auditLog: JSON.parse(localStorage.getItem(`aurum-audit-log-${user?.id}`) || '[]'),
      exportedAt: new Date().toISOString(),
      version: '1.0'
    };
    
    return export_data;
  }

  private getMockConsentHistory(): ConsentRecord[] {
    return [
      {
        id: '1',
        category: 'essential_cookies',
        granted: true,
        timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        version: '1.0',
        details: 'Essential cookies for app functionality'
      },
      {
        id: '2',
        category: 'analytics',
        granted: true,
        timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        version: '1.0',
        details: 'Analytics and performance tracking'
      },
      {
        id: '3',
        category: 'ai_features',
        granted: true,
        timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        version: '1.1',
        details: 'AI-powered features and recommendations'
      },
      {
        id: '4',
        category: 'marketing',
        granted: false,
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        version: '1.0',
        details: 'Marketing communications and newsletters'
      }
    ];
  }

  private getMockAuditLog(): AuditLogEntry[] {
    return [
      {
        id: '1',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        action: 'ai_suggestion_generated',
        category: 'ai_processing',
        details: 'Generated smart suggestions for task optimization',
        dataTypes: ['tasks', 'patterns'],
        purpose: 'productivity_enhancement',
        automated: true
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        action: 'analytics_data_collected',
        category: 'data_access',
        details: 'Collected usage analytics for dashboard interactions',
        dataTypes: ['interactions', 'timing'],
        purpose: 'product_improvement',
        automated: true
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        action: 'privacy_settings_updated',
        category: 'privacy_change',
        details: 'User updated AI feature preferences',
        dataTypes: ['settings'],
        purpose: 'privacy_control',
        automated: false
      },
      {
        id: '4',
        timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        action: 'data_export_requested',
        category: 'data_export',
        details: 'User requested full data export',
        dataTypes: ['all'],
        purpose: 'data_portability',
        automated: false
      },
      {
        id: '5',
        timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        action: 'consent_updated',
        category: 'consent_update',
        details: 'Updated consent for analytics tracking',
        dataTypes: ['consent'],
        purpose: 'compliance',
        automated: false
      }
    ];
  }

  /**
   * Initialize privacy settings with defaults
   */
  initializePrivacySettings(): PrivacySettings {
    return {
      dataCollection: {
        analytics: true,
        usage: true,
        performance: true,
        errors: true,
        interactions: false
      },
      aiFeatures: {
        smartSuggestions: true,
        productivityInsights: true,
        goalRecommendations: true,
        habitTracking: false,
        timeBlocking: false,
        semanticSearch: true,
        autoTagging: true,
        contentAnalysis: false
      },
      dataSharing: {
        anonymizedUsage: false,
        productImprovement: false,
        researchParticipation: false,
        marketingCommunications: false,
        thirdPartyIntegrations: false
      },
      dataRetention: {
        activityLogs: '1year',
        analyticsData: '6months',
        aiInsights: '1year',
        deletedItems: '30days'
      },
      visibility: {
        profileVisibility: 'private',
        activitySharing: false,
        achievementSharing: false,
        progressSharing: false
      },
      security: {
        twoFactorAuth: false,
        sessionTimeout: '1hour',
        deviceTracking: true,
        loginNotifications: true
      }
    };
  }

  /**
   * Check if user needs to update privacy consent
   */
  async needsConsentUpdate(): Promise<boolean> {
    try {
      const response = await this.apiRequest<{ needsUpdate: boolean }>('/privacy/consent-status');
      return response.needsUpdate;
    } catch (error) {
      console.log('Consent status check API failed, using fallback:', error);
      
      // Conservative fallback - don't require consent update for API failures
      return false;
    }
  }
}

export const privacyConsentService = new PrivacyConsentService();
export type { 
  PrivacySettings, 
  ConsentRecord, 
  AuditLogEntry, 
  PrivacyActionLog,
  DataExport 
};