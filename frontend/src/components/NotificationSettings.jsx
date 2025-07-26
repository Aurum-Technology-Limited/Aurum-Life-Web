import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  Mail, 
  Monitor, 
  Clock, 
  CheckCircle2,
  Save,
  Send,
  Settings,
  Loader,
  AlertCircle
} from 'lucide-react';
import { notificationsAPI } from '../services/api';

const NotificationSettings = () => {
  const [preferences, setPreferences] = useState(null);
  const [formData, setFormData] = useState({
    email_notifications: true,
    browser_notifications: true,
    task_due_notifications: true,
    task_overdue_notifications: true,
    task_reminder_notifications: true,
    project_deadline_notifications: true,
    recurring_task_notifications: true,
    achievement_notifications: true,
    unblocked_task_notifications: true,
    reminder_advance_time: 30,
    overdue_check_interval: 60,
    quiet_hours_start: '22:00',
    quiet_hours_end: '08:00',
    daily_digest: false,
    weekly_digest: true
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'

  // Load preferences when component mounts
  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const response = await notificationsAPI.getPreferences();
      const prefs = response.data;
      setPreferences(prefs);
      
      if (prefs) {
        setFormData({
          email_notifications: prefs.email_notifications ?? true,
          browser_notifications: prefs.browser_notifications ?? true,
          task_due_notifications: prefs.task_due_notifications ?? true,
          task_overdue_notifications: prefs.task_overdue_notifications ?? true,
          task_reminder_notifications: prefs.task_reminder_notifications ?? true,
          project_deadline_notifications: prefs.project_deadline_notifications ?? true,
          recurring_task_notifications: prefs.recurring_task_notifications ?? true,
          achievement_notifications: prefs.achievement_notifications ?? true,
          unblocked_task_notifications: prefs.unblocked_task_notifications ?? true,
          reminder_advance_time: prefs.reminder_advance_time ?? 30,
          overdue_check_interval: prefs.overdue_check_interval ?? 60,
          quiet_hours_start: prefs.quiet_hours_start ?? '22:00',
          quiet_hours_end: prefs.quiet_hours_end ?? '08:00',
          daily_digest: prefs.daily_digest ?? false,
          weekly_digest: prefs.weekly_digest ?? true
        });
      }
    } catch (error) {
      console.error('Error loading notification preferences:', error);
      setMessage('Failed to load notification preferences');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setSaved(false);
    setMessage('');
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    try {
      await notificationsAPI.updatePreferences(formData);
      setSaved(true);
      setMessage('Notification settings saved successfully!');
      setMessageType('success');
      setTimeout(() => {
        setSaved(false);
        setMessage('');
      }, 3000);
    } catch (error) {
      console.error('Error saving preferences:', error);
      setMessage('Failed to save notification settings');
      setMessageType('error');
    } finally {
      setSaving(false);
    }
  };

  const handleTestNotification = async () => {
    setTestLoading(true);
    setMessage('');
    try {
      await notificationsAPI.sendTest();
      setMessage('Test notification sent successfully!');
      setMessageType('success');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error sending test notification:', error);
      setMessage('Failed to send test notification');
      setMessageType('error');
    } finally {
      setTestLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <Loader className="h-8 w-8 animate-spin text-yellow-400" />
          <span className="ml-3 text-gray-400">Loading notification settings...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2" style={{ color: '#F4B400' }}>
          Notification Settings
        </h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Configure how and when you receive notifications about your tasks and projects.
        </p>
      </div>

      {/* Message Display */}
      {message && (
        <div className={`p-4 rounded-lg flex items-center ${
          messageType === 'success' 
            ? 'bg-green-900/20 border border-green-600 text-green-400'
            : 'bg-red-900/20 border border-red-600 text-red-400'
        }`}>
          {messageType === 'success' ? (
            <CheckCircle2 className="h-5 w-5 mr-3" />
          ) : (
            <AlertCircle className="h-5 w-5 mr-3" />
          )}
          <span>{message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                  </div>
                </div>
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
                { key: 'unblocked_task_notifications', label: 'Unblocked Tasks', desc: 'When task dependencies are complete' },
                { key: 'project_deadline_notifications', label: 'Project Deadlines', desc: 'When project deadlines approach' },
                { key: 'recurring_task_notifications', label: 'Recurring Tasks', desc: 'New recurring task instances' },
                { key: 'achievement_notifications', label: 'Achievement Unlocks', desc: 'New badges and achievements' }
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
                disabled={saving}
                className={`w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors ${
                  saved 
                    ? 'bg-green-600 text-white' 
                    : 'bg-yellow-500 hover:bg-yellow-600 text-black'
                } ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {saved ? (
                  <>
                    <CheckCircle2 className="h-5 w-5" />
                    <span>Saved!</span>
                  </>
                ) : (
                  <>
                    <Save className="h-5 w-5" />
                    <span>{saving ? 'Saving...' : 'Save Settings'}</span>
                  </>
                )}
              </button>

              <button
                onClick={handleTestNotification}
                disabled={testLoading}
                className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="h-5 w-5" />
                <span>{testLoading ? 'Sending...' : 'Send Test Notification'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationSettings;