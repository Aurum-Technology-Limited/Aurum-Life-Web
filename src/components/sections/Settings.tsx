import { User, Bell, Shield, Palette, Cloud, Brain, HelpCircle, FileText } from 'lucide-react';
import { motion } from 'motion/react';
import { useAppStore } from '../../stores/basicAppStore';

// Import individual settings components
import AccountSettings from './settings/AccountSettings';
import PreferencesSettings from './settings/PreferencesSettings';
import NotificationSettings from './settings/NotificationSettings';
import AISettings from './settings/AISettings';
import SyncSettings from './settings/SyncSettings';
import PrivacySettings from './settings/PrivacySettings';
import AuditLogSettings from './settings/AuditLogSettings';
import HelpSettings from './settings/HelpSettings';

export default function Settings() {
  const activeSettingsSection = useAppStore(state => state.activeSettingsSection);

  const settingsCategories = {
    account: { 
      label: 'Account & Profile', 
      icon: User, 
      description: 'Personal information and account settings',
      component: AccountSettings
    },
    preferences: { 
      label: 'App Preferences', 
      icon: Palette, 
      description: 'Customize appearance and behavior',
      component: PreferencesSettings
    },
    notifications: { 
      label: 'Notifications', 
      icon: Bell, 
      description: 'Manage your notification preferences',
      component: NotificationSettings
    },
    ai: { 
      label: 'AI & Automation', 
      icon: Brain, 
      description: 'Configure AI features and automation',
      component: AISettings
    },
    sync: { 
      label: 'Sync & Backup', 
      icon: Cloud, 
      description: 'Data synchronization and backup settings',
      component: SyncSettings
    },
    privacy: { 
      label: 'Privacy & Security', 
      icon: Shield, 
      description: 'Security settings and privacy controls',
      component: PrivacySettings
    },
    audit: { 
      label: 'Audit & Transparency', 
      icon: FileText, 
      description: 'AI data usage transparency and audit logs',
      component: AuditLogSettings
    },
    help: { 
      label: 'Help & Support', 
      icon: HelpCircle, 
      description: 'Get help and contact support',
      component: HelpSettings
    }
  };

  // Get current active section
  const activeSection = settingsCategories[activeSettingsSection as keyof typeof settingsCategories];
  const ActiveComponent = activeSection?.component || AccountSettings;
  const Icon = activeSection?.icon || User;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Header for the specific settings section */}
      <div className="flex items-center space-x-3 mb-6">
        <div className="aurum-gradient w-10 h-10 rounded-lg flex items-center justify-center">
          <Icon className="w-6 h-6 text-[#0B0D14]" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white">{activeSection?.label || 'Settings'}</h1>
          <p className="text-[#B8BCC8]">{activeSection?.description || 'Customize your Aurum Life experience'}</p>
        </div>
      </div>

      {/* Settings Content in its own container */}
      <motion.div
        key={activeSettingsSection}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.3 }}
      >
        <ActiveComponent />
      </motion.div>
    </motion.div>
  );
}