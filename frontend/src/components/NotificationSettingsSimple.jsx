/**
 * Simple Notification Settings Component for Testing
 */

import React, { useState } from 'react';

const NotificationSettingsSimple = () => {
  const [formData, setFormData] = useState({
    email_notifications: true,
    browser_notifications: true,
    task_due_notifications: true,
    task_overdue_notifications: true,
    task_reminder_notifications: true,
    project_deadline_notifications: true,
    recurring_task_notifications: true,
    reminder_advance_time: 30,
    quiet_hours_start: '22:00',
    quiet_hours_end: '08:00',
    daily_digest: false,
    weekly_digest: true
  });

  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleInputChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setSaved(false);
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Error saving preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTestNotification = async () => {
    alert('Test notification sent!');
  };

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#F4B400' }}>
            Notification Settings
          </h1>
          <p className="text-gray-400">
            Configure how and when you receive notifications about your tasks and projects.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Notification Channels */}
          <div className="space-y-6">
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-white">
                Notification Channels
              </h2>

              <div className="space-y-4">
                {/* Browser Notifications */}
                <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="h-5 w-5 bg-blue-400 rounded"></div>
                    <div>
                      <h3 className="font-medium text-white">Browser Notifications</h3>
                      <p className="text-sm text-gray-400">
                        Show desktop notifications in your browser
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.browser_notifications}
                        onChange={(e) => handleInputChange('browser_notifications', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>

                {/* Email Notifications */}
                <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="h-5 w-5 bg-green-400 rounded"></div>
                    <div>
                      <h3 className="font-medium text-white">Email Notifications</h3>
                      <p className="text-sm text-gray-400">
                        Receive notifications via email
                      </p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.email_notifications}
                      onChange={(e) => handleInputChange('email_notifications', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                  </label>
                </div>
              </div>
            </div>

            {/* Notification Types */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-white">
                Notification Types
              </h2>

              <div className="space-y-3">
                {[
                  { key: 'task_due_notifications', label: 'Task Due', desc: 'When tasks are due now' },
                  { key: 'task_overdue_notifications', label: 'Task Overdue', desc: 'When tasks become overdue' },
                  { key: 'task_reminder_notifications', label: 'Task Reminders', desc: 'Advance reminders before due time' },
                  { key: 'project_deadline_notifications', label: 'Project Deadlines', desc: 'When project deadlines approach' },
                  { key: 'recurring_task_notifications', label: 'Recurring Tasks', desc: 'New recurring task instances' }
                ].map(({ key, label, desc }) => (
                  <div key={key} className="flex items-center justify-between p-3 hover:bg-gray-800/30 rounded-lg">
                    <div>
                      <h4 className="font-medium text-white">{label}</h4>
                      <p className="text-sm text-gray-400">{desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData[key]}
                        onChange={(e) => handleInputChange(key, e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-500"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Timing & Preferences */}
          <div className="space-y-6">
            {/* Timing Settings */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-white">
                Timing Settings
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Reminder Advance Time (minutes)
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="1440"
                    value={formData.reminder_advance_time}
                    onChange={(e) => handleInputChange('reminder_advance_time', parseInt(e.target.value))}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-yellow-500"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    How early to remind you before tasks are due
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Quiet Hours Start
                    </label>
                    <input
                      type="time"
                      value={formData.quiet_hours_start}
                      onChange={(e) => handleInputChange('quiet_hours_start', e.target.value)}
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-yellow-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Quiet Hours End
                    </label>
                    <input
                      type="time"
                      value={formData.quiet_hours_end}
                      onChange={(e) => handleInputChange('quiet_hours_end', e.target.value)}
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-yellow-500"
                    />
                  </div>
                </div>
                <p className="text-xs text-gray-400">
                  No notifications will be sent during quiet hours
                </p>
              </div>
            </div>

            {/* Digest Settings */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-white">
                Email Digests
              </h2>

              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 hover:bg-gray-800/30 rounded-lg">
                  <div>
                    <h4 className="font-medium text-white">Daily Digest</h4>
                    <p className="text-sm text-gray-400">Summary of daily tasks and progress</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.daily_digest}
                      onChange={(e) => handleInputChange('daily_digest', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between p-3 hover:bg-gray-800/30 rounded-lg">
                  <div>
                    <h4 className="font-medium text-white">Weekly Digest</h4>
                    <p className="text-sm text-gray-400">Weekly progress summary and insights</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.weekly_digest}
                      onChange={(e) => handleInputChange('weekly_digest', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                  </label>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-white">
                Actions
              </h2>

              <div className="space-y-3">
                <button
                  onClick={handleSave}
                  disabled={loading}
                  className={`w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors ${
                    saved 
                      ? 'bg-green-600 text-white' 
                      : 'bg-yellow-500 hover:bg-yellow-600 text-black'
                  } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <span>{saved ? 'Saved!' : (loading ? 'Saving...' : 'Save Settings')}</span>
                </button>

                <button
                  onClick={handleTestNotification}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors"
                >
                  <span>Send Test Notification</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationSettingsSimple;