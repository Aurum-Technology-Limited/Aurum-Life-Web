import { useEffect } from 'react';
import { Settings as SettingsIcon, Search, User, Bell, Shield, Palette, Cloud, Brain, HelpCircle } from 'lucide-react';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { motion, AnimatePresence } from 'motion/react';
import { useAppStore } from '../../stores/basicAppStore';

// Import individual settings components
import AccountSettings from './settings/AccountSettings';
import PreferencesSettings from './settings/PreferencesSettings';
import NotificationSettings from './settings/NotificationSettings';
import AISettings from './settings/AISettings';
import SyncSettings from './settings/SyncSettings';
import PrivacySettings from './settings/PrivacySettings';
import HelpSettings from './settings/HelpSettings';

export default function NavigationSettings() {
  const activeSettingsSection = useAppStore(state => state.activeSettingsSection);
  const setActiveSettingsSection = useAppStore(state => state.setActiveSettingsSection);

  const settingsCategories = [
    { 
      id: 'account', 
      label: 'Account & Profile', 
      icon: <User className="w-4 h-4" />, 
      description: 'Personal information and account settings',
      component: AccountSettings
    },
    { 
      id: 'preferences', 
      label: 'App Preferences', 
      icon: <Palette className="w-4 h-4" />, 
      description: 'Adjust display and behavior settings',
      component: PreferencesSettings
    },
    { 
      id: 'notifications', 
      label: 'Notifications', 
      icon: <Bell className="w-4 h-4" />, 
      description: 'Manage your notification preferences',
      component: NotificationSettings
    },
    { 
      id: 'ai', 
      label: 'AI & Automation', 
      icon: <Brain className="w-4 h-4" />, 
      description: 'Configure AI features and automation',
      component: AISettings
    },
    { 
      id: 'sync', 
      label: 'Sync & Backup', 
      icon: <Cloud className="w-4 h-4" />, 
      description: 'Data synchronization and backup settings',
      component: SyncSettings
    },
    { 
      id: 'privacy', 
      label: 'Privacy & Security', 
      icon: <Shield className="w-4 h-4" />, 
      description: 'Security settings and privacy controls',
      component: PrivacySettings
    },
    { 
      id: 'help', 
      label: 'Help & Support', 
      icon: <HelpCircle className="w-4 h-4" />, 
      description: 'Get help and contact support',
      component: HelpSettings
    }
  ];

  // Get current active section
  const activeSection = settingsCategories.find(cat => cat.id === activeSettingsSection);
  const ActiveComponent = activeSection?.component || AccountSettings;

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="aurum-gradient w-10 h-10 rounded-lg flex items-center justify-center">
            <SettingsIcon className="w-6 h-6 text-[#0B0D14]" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">{activeSection?.label || 'Settings'}</h1>
            <p className="text-[#B8BCC8]">{activeSection?.description || 'Configure your Aurum Life experience'}</p>
          </div>
        </div>
        
        <div className="hidden sm:flex items-center space-x-4">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#B8BCC8]" />
            <Input
              placeholder="Search settings..."
              className="pl-10 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
            />
          </div>
        </div>
      </div>

      {/* User Profile Card */}
      <Card className="glassmorphism-card border-0">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <Avatar className="w-16 h-16">
              <AvatarImage src="/api/placeholder/64/64" alt="Profile" />
              <AvatarFallback className="bg-[#F4D03F] text-[#0B0D14] text-xl font-bold">JD</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <h3 className="text-xl font-medium text-white">John Doe</h3>
              <p className="text-[#B8BCC8]">john.doe@example.com</p>
              <Badge className="mt-2 bg-[#F4D03F] text-[#0B0D14]">Premium Member</Badge>
            </div>
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
              Edit Profile
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Settings Content */}
      <div>
        <AnimatePresence mode="wait">
          <motion.div
            key={activeSettingsSection}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <ActiveComponent />
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}