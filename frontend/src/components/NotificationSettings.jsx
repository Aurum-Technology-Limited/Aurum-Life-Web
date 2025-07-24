/**
 * Notification Settings Component for Aurum Life
 * Allows users to configure their notification preferences
 */

import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  Mail, 
  Monitor, 
  Clock, 
  Volume2, 
  VolumeX,
  CheckCircle2,
  Save,
  Test as TestIcon,
  Settings
} from 'lucide-react';
// import { useNotifications } from '../contexts/NotificationContext';

const NotificationSettings = () => {
  // Temporarily disable context usage for testing
  // const { 
  //   preferences, 
  //   updatePreferences, 
  //   browserPermission, 
  //   requestBrowserPermission,
  //   sendTestNotification 
  // } = useNotifications();

  const [formData, setFormData] = useState({
    email_notifications: true,
    browser_notifications: true,
    task_due_notifications: true,
    task_overdue_notifications: true,
    task_reminder_notifications: true,
    project_deadline_notifications: true,
    recurring_task_notifications: true,
    reminder_advance_time: 30,
    overdue_check_interval: 60,
    quiet_hours_start: '22:00',
    quiet_hours_end: '08:00',
    daily_digest: false,
    weekly_digest: true
  });

  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const browserPermission = 'default'; // Mock for testing

  // Load preferences when component mounts
  useEffect(() => {
    // Temporarily disabled for testing
    // if (preferences) {
    //   setFormData({
    //     email_notifications: preferences.email_notifications ?? true,
    //     browser_notifications: preferences.browser_notifications ?? true,
    //     task_due_notifications: preferences.task_due_notifications ?? true,
    //     task_overdue_notifications: preferences.task_overdue_notifications ?? true,
    //     task_reminder_notifications: preferences.task_reminder_notifications ?? true,
    //     project_deadline_notifications: preferences.project_deadline_notifications ?? true,
    //     recurring_task_notifications: preferences.recurring_task_notifications ?? true,
    //     reminder_advance_time: preferences.reminder_advance_time ?? 30,
    //     overdue_check_interval: preferences.overdue_check_interval ?? 60,
    //     quiet_hours_start: preferences.quiet_hours_start ?? '22:00',
    //     quiet_hours_end: preferences.quiet_hours_end ?? '08:00',
    //     daily_digest: preferences.daily_digest ?? false,
    //     weekly_digest: preferences.weekly_digest ?? true
    //   });
    // }
  }, []);

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
      // await updatePreferences(formData);
      // Mock save for testing
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
    setTestLoading(true);
    try {
      // await sendTestNotification();
      // Mock test notification for testing
      await new Promise(resolve => setTimeout(resolve, 1000));
      alert('Test notification sent!');
    } catch (error) {
      console.error('Error sending test notification:', error);
    } finally {
      setTestLoading(false);
    }
  };

  const handleRequestBrowserPermission = async () => {
    // const permission = await requestBrowserPermission();
    // if (permission === 'granted') {
    //   handleInputChange('browser_notifications', true);
    // }
    // Mock for testing
    alert('Browser permission requested!');
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
              <h2 className="text-xl font-semibold mb-4 text-white flex items-center">
                <Settings className="h-5 w-5 mr-2" style={{ color: '#F4B400' }} />
                Notification Channels
              </h2>

              <div className="space-y-4">
                {/* Browser Notifications */}
                <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Monitor className="h-5 w-5 text-blue-400" />
                    <div>
                      <h3 className="font-medium text-white">Browser Notifications</h3>
                      <p className="text-sm text-gray-400">
                        Show desktop notifications in your browser
                      </p>
                      {browserPermission !== 'granted' && (
                        <p className="text-xs text-orange-400 mt-1">
                          Permission required - click to enable
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {browserPermission !== 'granted' && (
                      <button
                        onClick={handleRequestBrowserPermission}
                        className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded transition-colors"
                      >
                        Enable
                      </button>
                    )}
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.browser_notifications && browserPermission === 'granted'}
                        onChange={(e) => handleInputChange('browser_notifications', e.target.checked)}
                        disabled={browserPermission !== 'granted'}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>

                {/* Email Notifications */}
                <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Mail className="h-5 w-5 text-green-400" />
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
              <h2 className="text-xl font-semibold mb-4 text-white flex items-center">
                <Bell className="h-5 w-5 mr-2" style={{ color: '#F4B400' }} />
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
              <h2 className="text-xl font-semibold mb-4 text-white flex items-center">
                <Clock className="h-5 w-5 mr-2" style={{ color: '#F4B400' }} />
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
              <h2 className="text-xl font-semibold mb-4 text-white flex items-center">
                <Mail className="h-5 w-5 mr-2" style={{ color: '#F4B400' }} />
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
                  {saved ? (
                    <>
                      <CheckCircle2 className="h-5 w-5" />
                      <span>Saved!</span>
                    </>
                  ) : (
                    <>
                      <Save className="h-5 w-5" />
                      <span>{loading ? 'Saving...' : 'Save Settings'}</span>
                    </>
                  )}
                </button>

                <button
                  onClick={handleTestNotification}
                  disabled={testLoading}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <TestIcon className="h-5 w-5" />
                  <span>{testLoading ? 'Sending...' : 'Send Test Notification'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationSettings;