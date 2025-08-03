import React, { useState } from 'react';
import { CogIcon, BellIcon, ShieldCheckIcon } from '@heroicons/react/outline';
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
      case 'privacy':
        return (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <div className="space-y-8">
              {/* Privacy & Security Header */}
              <div className="border-b border-gray-700 pb-4">
                <div className="flex items-center mb-2">
                  <ShieldCheckIcon className="h-6 w-6 text-yellow-400 mr-2" />
                  <h2 className="text-xl font-semibold text-white">Privacy & Security</h2>
                </div>
                <p className="text-gray-400">
                  Manage your account security and privacy settings.
                </p>
              </div>

              {/* Account Data Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-white">Account Data</h3>
                <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="text-white font-medium mb-1">Export Data</h4>
                      <p className="text-gray-400 text-sm mb-3">
                        Download a copy of your personal data including tasks, projects, journal entries, and preferences.
                      </p>
                      <button className="bg-gray-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors text-sm">
                        Request Data Export
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Danger Zone */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-red-400">Danger Zone</h3>
                <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="text-red-400 font-medium mb-1">Delete Account</h4>
                      <p className="text-gray-400 text-sm mb-3">
                        Permanently delete your account and all associated data. This action cannot be undone.
                      </p>
                      <p className="text-red-300 text-xs mb-4 font-medium">
                        ⚠️ This will delete: All tasks, projects, areas, pillars, journal entries, AI interactions, and personal data.
                      </p>
                      <button 
                        onClick={() => setActiveSubSection('delete-account')}
                        className="bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors text-sm"
                      >
                        Delete Account
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case 'delete-account':
        return <DeleteAccountSection onBack={() => setActiveSubSection('privacy')} />;
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