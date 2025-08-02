import React, { useState } from 'react';
import { CogIcon, BellIcon, UserIcon, ShieldCheckIcon } from '@heroicons/react/outline';
import { Target } from 'lucide-react';
import NotificationSettings from './NotificationSettings';
import GoalSettings from './GoalSettings';

const Settings = ({ sectionParams }) => {
  // Get the active sub-section from sectionParams, default to 'goals'
  const [activeSubSection, setActiveSubSection] = useState(sectionParams?.subSection || 'goals');

  const menuItems = [
    {
      key: 'goals',
      label: 'Goals',
      icon: Target,
      description: 'Set and manage your alignment goals'
    },
    {
      key: 'notifications',
      label: 'Notifications',
      icon: BellIcon,
      description: 'Configure notification preferences'
    },
    {
      key: 'profile',
      label: 'Profile',
      icon: UserIcon,
      description: 'Manage your profile information'
    },
    {
      key: 'privacy',
      label: 'Privacy & Security',
      icon: ShieldCheckIcon,
      description: 'Privacy settings and account security'
    }
  ];

  const renderSubSection = () => {
    switch (activeSubSection) {
      case 'goals':
        return <GoalSettings />;
      case 'notifications':
        return <NotificationSettings />;
      case 'profile':
        return (
          <div className="text-center py-12">
            <div className="text-gray-400">
              <UserIcon className="h-16 w-16 mx-auto mb-4 text-gray-500" />
              <h3 className="text-lg font-medium mb-2 text-white">Profile Settings</h3>
              <p>Profile settings will be available here in a future update.</p>
            </div>
          </div>
        );
      case 'privacy':
        return (
          <div className="text-center py-12">
            <div className="text-gray-400">
              <ShieldCheckIcon className="h-16 w-16 mx-auto mb-4 text-gray-500" />
              <h3 className="text-lg font-medium mb-2 text-white">Privacy & Security</h3>
              <p>Privacy and security settings will be available here in a future update.</p>
            </div>
          </div>
        );
      default:
        return <GoalSettings />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">
          Manage your account settings and preferences.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Settings Navigation Menu */}
        <div className="lg:col-span-1">
          <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
              <CogIcon className="h-5 w-5 mr-2 text-yellow-400" />
              Settings Menu
            </h2>
            <nav className="space-y-2">
              {menuItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeSubSection === item.key;
                
                return (
                  <button
                    key={item.key}
                    onClick={() => setActiveSubSection(item.key)}
                    className={`w-full flex items-start p-3 rounded-lg text-left transition-colors ${
                      isActive
                        ? 'bg-yellow-500/10 border border-yellow-500/20 text-yellow-400'
                        : 'hover:bg-gray-800/50 text-gray-300 hover:text-white'
                    }`}
                  >
                    <Icon className={`h-5 w-5 mr-3 mt-0.5 flex-shrink-0 ${
                      isActive ? 'text-yellow-400' : 'text-gray-400'
                    }`} />
                    <div>
                      <h3 className={`font-medium ${
                        isActive ? 'text-yellow-400' : 'text-white'
                      }`}>
                        {item.label}
                      </h3>
                      <p className="text-xs text-gray-400 mt-1">
                        {item.description}
                      </p>
                    </div>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3">
          {renderSubSection()}
        </div>
      </div>
    </div>
  );
};

export default Settings;