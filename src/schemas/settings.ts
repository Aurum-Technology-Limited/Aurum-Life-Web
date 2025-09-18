import { z } from 'zod';

// Account Settings Schema
export const accountSettingsSchema = z.object({
  fullName: z.string().min(2, 'Full name must be at least 2 characters').max(50, 'Full name must be less than 50 characters'),
  email: z.string().email('Please enter a valid email address'),
  phone: z.string().optional(),
  timezone: z.string().min(1, 'Please select a timezone'),
  bio: z.string().max(500, 'Bio must be less than 500 characters').optional(),
  website: z.string().url('Please enter a valid URL').optional().or(z.literal('')),
  location: z.string().max(100, 'Location must be less than 100 characters').optional(),
});

export const passwordChangeSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

// Notification Settings Schema
export const notificationSettingsSchema = z.object({
  emailNotifications: z.object({
    taskReminders: z.boolean(),
    projectUpdates: z.boolean(),
    weeklySummary: z.boolean(),
    systemUpdates: z.boolean(),
    marketingEmails: z.boolean(),
  }),
  pushNotifications: z.object({
    taskReminders: z.boolean(),
    immediateAlerts: z.boolean(),
    dailyDigest: z.boolean(),
    weekendMode: z.boolean(),
  }),
  inAppNotifications: z.object({
    sounds: z.boolean(),
    desktopNotifications: z.boolean(),
    badges: z.boolean(),
  }),
  schedule: z.object({
    quietHoursEnabled: z.boolean(),
    quietHoursStart: z.string(),
    quietHoursEnd: z.string(),
    timezone: z.string(),
  }),
});

// AI Settings Schema
export const aiSettingsSchema = z.object({
  aiFeatures: z.object({
    smartSuggestions: z.boolean(),
    autoTagging: z.boolean(),
    priorityPrediction: z.boolean(),
    insightGeneration: z.boolean(),
    naturalLanguageProcessing: z.boolean(),
  }),
  automation: z.object({
    autoScheduling: z.boolean(),
    smartDeadlines: z.boolean(),
    progressTracking: z.boolean(),
    contextualReminders: z.boolean(),
  }),
  privacy: z.object({
    dataUsageConsent: z.boolean(),
    improvementProgram: z.boolean(),
    anonymousAnalytics: z.boolean(),
  }),
  preferences: z.object({
    suggestionFrequency: z.enum(['low', 'medium', 'high']),
    automationLevel: z.enum(['minimal', 'balanced', 'aggressive']),
    insightStyle: z.enum(['brief', 'detailed', 'comprehensive']),
  }),
});

// Sync Settings Schema
export const syncSettingsSchema = z.object({
  synchronization: z.object({
    autoSync: z.boolean(),
    syncFrequency: z.enum(['realtime', 'hourly', 'daily', 'manual']),
    conflictResolution: z.enum(['local', 'remote', 'prompt']),
    offlineMode: z.boolean(),
  }),
  backup: z.object({
    autoBackup: z.boolean(),
    backupFrequency: z.enum(['daily', 'weekly', 'monthly']),
    retentionPeriod: z.enum(['30', '90', '365', 'unlimited']),
    includeAttachments: z.boolean(),
  }),
  devices: z.object({
    syncAcrossDevices: z.boolean(),
    deviceLimit: z.number().min(1).max(10),
    compressionEnabled: z.boolean(),
  }),
  exportOptions: z.object({
    autoExport: z.boolean(),
    exportFormat: z.enum(['json', 'csv', 'pdf']),
    exportFrequency: z.enum(['weekly', 'monthly', 'quarterly']),
    includeMedia: z.boolean(),
  }),
});

// Privacy Settings Schema
export const privacySettingsSchema = z.object({
  account: z.object({
    profileVisibility: z.enum(['private', 'contacts', 'public']),
    activityStatus: z.boolean(),
    lastSeenVisibility: z.boolean(),
    searchableByEmail: z.boolean(),
  }),
  data: z.object({
    analyticsOptIn: z.boolean(),
    crashReporting: z.boolean(),
    usageStatistics: z.boolean(),
    personalizedAds: z.boolean(),
  }),
  security: z.object({
    twoFactorAuth: z.boolean(),
    sessionTimeout: z.enum(['15', '30', '60', '120', 'never']),
    loginNotifications: z.boolean(),
    suspiciousActivityAlerts: z.boolean(),
  }),
  sharing: z.object({
    allowDataSharing: z.boolean(),
    thirdPartyIntegrations: z.boolean(),
    publicAPI: z.boolean(),
    dataExportRequests: z.boolean(),
  }),
});

// Help Settings Schema
export const supportRequestSchema = z.object({
  category: z.enum(['bug', 'feature', 'account', 'billing', 'general']),
  priority: z.enum(['low', 'medium', 'high', 'urgent']),
  subject: z.string().min(5, 'Subject must be at least 5 characters').max(100, 'Subject must be less than 100 characters'),
  description: z.string().min(20, 'Please provide a detailed description (at least 20 characters)').max(2000, 'Description must be less than 2000 characters'),
  attachments: z.array(z.string()).optional(),
  contactPreference: z.enum(['email', 'phone', 'chat']),
});

export const feedbackSchema = z.object({
  type: z.enum(['praise', 'suggestion', 'complaint', 'question']),
  rating: z.number().min(1).max(5),
  feedback: z.string().min(10, 'Please provide detailed feedback (at least 10 characters)').max(1000, 'Feedback must be less than 1000 characters'),
  anonymous: z.boolean(),
  followUp: z.boolean(),
});

// Type exports
export type AccountSettingsData = z.infer<typeof accountSettingsSchema>;
export type PasswordChangeData = z.infer<typeof passwordChangeSchema>;
export type NotificationSettingsData = z.infer<typeof notificationSettingsSchema>;
export type AISettingsData = z.infer<typeof aiSettingsSchema>;
export type SyncSettingsData = z.infer<typeof syncSettingsSchema>;
export type PrivacySettingsData = z.infer<typeof privacySettingsSchema>;
export type SupportRequestData = z.infer<typeof supportRequestSchema>;
export type FeedbackData = z.infer<typeof feedbackSchema>;