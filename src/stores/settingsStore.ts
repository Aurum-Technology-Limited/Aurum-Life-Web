import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { 
  AccountSettingsData, 
  NotificationSettingsData, 
  AISettingsData, 
  SyncSettingsData, 
  PrivacySettingsData 
} from '../schemas/settings';

interface SettingsStore {
  // Account Settings
  accountSettings: AccountSettingsData;
  setAccountSettings: (settings: Partial<AccountSettingsData>) => void;
  
  // Notification Settings
  notificationSettings: NotificationSettingsData;
  setNotificationSettings: (settings: Partial<NotificationSettingsData>) => void;
  
  // AI Settings
  aiSettings: AISettingsData;
  setAISettings: (settings: Partial<AISettingsData>) => void;
  
  // Sync Settings
  syncSettings: SyncSettingsData;
  setSyncSettings: (settings: Partial<SyncSettingsData>) => void;
  
  // Privacy Settings
  privacySettings: PrivacySettingsData;
  setPrivacySettings: (settings: Partial<PrivacySettingsData>) => void;
  
  // Loading states for backend operations
  isLoading: {
    account: boolean;
    notifications: boolean;
    ai: boolean;
    sync: boolean;
    privacy: boolean;
  };
  setLoading: (section: keyof SettingsStore['isLoading'], loading: boolean) => void;
  
  // Error states
  errors: {
    account: string | null;
    notifications: string | null;
    ai: string | null;
    sync: string | null;
    privacy: string | null;
  };
  setError: (section: keyof SettingsStore['errors'], error: string | null) => void;
  
  // Last saved timestamps for optimistic updates
  lastSaved: {
    account: Date | null;
    notifications: Date | null;
    ai: Date | null;
    sync: Date | null;
    privacy: Date | null;
  };
  setLastSaved: (section: keyof SettingsStore['lastSaved'], date: Date) => void;
  
  // Reset functions
  resetAccountSettings: () => void;
  resetNotificationSettings: () => void;
  resetAISettings: () => void;
  resetSyncSettings: () => void;
  resetPrivacySettings: () => void;
  resetAllSettings: () => void;
}

// Default settings values
const defaultAccountSettings: AccountSettingsData = {
  fullName: '',
  email: '',
  phone: '',
  timezone: 'America/New_York',
  bio: '',
  website: '',
  location: '',
};

const defaultNotificationSettings: NotificationSettingsData = {
  emailNotifications: {
    taskReminders: true,
    projectUpdates: true,
    weeklySummary: true,
    systemUpdates: true,
    marketingEmails: false,
  },
  pushNotifications: {
    taskReminders: true,
    immediateAlerts: true,
    dailyDigest: true,
    weekendMode: false,
  },
  inAppNotifications: {
    sounds: true,
    desktopNotifications: true,
    badges: true,
  },
  schedule: {
    quietHoursEnabled: true,
    quietHoursStart: '22:00',
    quietHoursEnd: '08:00',
    timezone: 'America/New_York',
  },
};

const defaultAISettings: AISettingsData = {
  aiFeatures: {
    smartSuggestions: true,
    autoTagging: true,
    priorityPrediction: true,
    insightGeneration: true,
    naturalLanguageProcessing: true,
  },
  automation: {
    autoScheduling: false,
    smartDeadlines: true,
    progressTracking: true,
    contextualReminders: true,
  },
  privacy: {
    dataUsageConsent: false,
    improvementProgram: false,
    anonymousAnalytics: true,
  },
  preferences: {
    suggestionFrequency: 'medium',
    automationLevel: 'balanced',
    insightStyle: 'detailed',
  },
};

const defaultSyncSettings: SyncSettingsData = {
  synchronization: {
    autoSync: true,
    syncFrequency: 'realtime',
    conflictResolution: 'prompt',
    offlineMode: true,
  },
  backup: {
    autoBackup: true,
    backupFrequency: 'daily',
    retentionPeriod: '90',
    includeAttachments: true,
  },
  devices: {
    syncAcrossDevices: true,
    deviceLimit: 5,
    compressionEnabled: true,
  },
  exportOptions: {
    autoExport: false,
    exportFormat: 'json',
    exportFrequency: 'monthly',
    includeMedia: false,
  },
};

const defaultPrivacySettings: PrivacySettingsData = {
  account: {
    profileVisibility: 'private',
    activityStatus: false,
    lastSeenVisibility: false,
    searchableByEmail: false,
  },
  data: {
    analyticsOptIn: false,
    crashReporting: true,
    usageStatistics: false,
    personalizedAds: false,
  },
  security: {
    twoFactorAuth: false,
    sessionTimeout: '60',
    loginNotifications: true,
    suspiciousActivityAlerts: true,
  },
  sharing: {
    allowDataSharing: false,
    thirdPartyIntegrations: false,
    publicAPI: false,
    dataExportRequests: true,
  },
};

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set, get) => ({
      // Initial state
      accountSettings: defaultAccountSettings,
      notificationSettings: defaultNotificationSettings,
      aiSettings: defaultAISettings,
      syncSettings: defaultSyncSettings,
      privacySettings: defaultPrivacySettings,
      
      isLoading: {
        account: false,
        notifications: false,
        ai: false,
        sync: false,
        privacy: false,
      },
      
      errors: {
        account: null,
        notifications: null,
        ai: null,
        sync: null,
        privacy: null,
      },
      
      lastSaved: {
        account: null,
        notifications: null,
        ai: null,
        sync: null,
        privacy: null,
      },
      
      // Setters
      setAccountSettings: (settings) => {
        set((state) => ({
          accountSettings: { ...state.accountSettings, ...settings }
        }));
      },
      
      setNotificationSettings: (settings) => {
        set((state) => ({
          notificationSettings: { ...state.notificationSettings, ...settings }
        }));
      },
      
      setAISettings: (settings) => {
        set((state) => ({
          aiSettings: { ...state.aiSettings, ...settings }
        }));
      },
      
      setSyncSettings: (settings) => {
        set((state) => ({
          syncSettings: { ...state.syncSettings, ...settings }
        }));
      },
      
      setPrivacySettings: (settings) => {
        set((state) => ({
          privacySettings: { ...state.privacySettings, ...settings }
        }));
      },
      
      setLoading: (section, loading) => {
        set((state) => ({
          isLoading: { ...state.isLoading, [section]: loading }
        }));
      },
      
      setError: (section, error) => {
        set((state) => ({
          errors: { ...state.errors, [section]: error }
        }));
      },
      
      setLastSaved: (section, date) => {
        set((state) => ({
          lastSaved: { ...state.lastSaved, [section]: date }
        }));
      },
      
      // Reset functions
      resetAccountSettings: () => {
        set({ accountSettings: defaultAccountSettings });
      },
      
      resetNotificationSettings: () => {
        set({ notificationSettings: defaultNotificationSettings });
      },
      
      resetAISettings: () => {
        set({ aiSettings: defaultAISettings });
      },
      
      resetSyncSettings: () => {
        set({ syncSettings: defaultSyncSettings });
      },
      
      resetPrivacySettings: () => {
        set({ privacySettings: defaultPrivacySettings });
      },
      
      resetAllSettings: () => {
        set({
          accountSettings: defaultAccountSettings,
          notificationSettings: defaultNotificationSettings,
          aiSettings: defaultAISettings,
          syncSettings: defaultSyncSettings,
          privacySettings: defaultPrivacySettings,
          errors: {
            account: null,
            notifications: null,
            ai: null,
            sync: null,
            privacy: null,
          },
          lastSaved: {
            account: null,
            notifications: null,
            ai: null,
            sync: null,
            privacy: null,
          },
        });
      },
    }),
    {
      name: 'aurum-life-settings-store',
      partialize: (state) => ({
        accountSettings: state.accountSettings,
        notificationSettings: state.notificationSettings,
        aiSettings: state.aiSettings,
        syncSettings: state.syncSettings,
        privacySettings: state.privacySettings,
        lastSaved: state.lastSaved,
      }),
    }
  )
);