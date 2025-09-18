import { useState, useEffect } from 'react';
import { Bell, Volume2, VolumeX, Smartphone, Mail, Globe, Clock, Zap, Target, TrendingUp, Award, AlertTriangle, Shield, TestTube2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Switch } from '../../ui/switch';
import { Button } from '../../ui/button';
import { Label } from '../../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Slider } from '../../ui/slider';
import { Badge } from '../../ui/badge';
import { Separator } from '../../ui/separator';
import { Alert, AlertDescription } from '../../ui/alert';
import { useNotifications } from '../../../hooks/useNotifications';
import { NotificationPreferences } from '../../../services/realTimeNotificationService';

export default function NotificationSettings() {
  const {
    preferences,
    connectionStatus,
    updatePreferences,
    sendTestNotification,
    requestBrowserPermission,
    isLoading,
    error
  } = useNotifications();

  const [localPreferences, setLocalPreferences] = useState<NotificationPreferences>(preferences);
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setLocalPreferences(preferences);
  }, [preferences]);

  useEffect(() => {
    const hasChanged = JSON.stringify(localPreferences) !== JSON.stringify(preferences);
    setHasChanges(hasChanged);
  }, [localPreferences, preferences]);

  const handlePreferenceChange = (path: string[], value: any) => {
    setLocalPreferences(prev => {
      const updated = { ...prev };
      let current: any = updated;
      
      // Navigate to the parent of the target property
      for (let i = 0; i < path.length - 1; i++) {
        current[path[i]] = { ...current[path[i]] };
        current = current[path[i]];
      }
      
      // Set the final property
      current[path[path.length - 1]] = value;
      
      return updated;
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updatePreferences(localPreferences);
      setHasChanges(false);
    } catch (err) {
      console.error('Failed to save notification preferences:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    setLocalPreferences(preferences);
    setHasChanges(false);
  };

  const handleRequestBrowserPermission = async () => {
    try {
      const permission = await requestBrowserPermission();
      if (permission === 'granted') {
        await sendTestNotification();
      }
    } catch (err) {
      console.error('Failed to request browser permission:', err);
    }
  };

  const getTimeZoneOptions = () => {
    return Intl.supportedValuesOf('timeZone').slice(0, 50); // Limit for performance
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-white mb-2">Notification Settings</h2>
          <p className="text-[#B8BCC8]">
            Configure how and when you receive notifications from Aurum Life
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={connectionStatus.isConnected ? "default" : "secondary"}>
            {connectionStatus.isConnected ? 'Connected' : 'Offline'}
          </Badge>
          {hasChanges && (
            <Badge variant="outline" className="border-[#F59E0B] text-[#F59E0B]">
              Unsaved Changes
            </Badge>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Alert className="border-[#EF4444] bg-[rgba(239,68,68,0.1)]">
          <AlertTriangle className="h-4 w-4 text-[#EF4444]" />
          <AlertDescription className="text-[#EF4444]">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Master Toggle */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bell className="w-5 h-5 text-[#F4D03F]" />
              <div>
                <CardTitle className="text-white">Master Control</CardTitle>
                <CardDescription>Enable or disable all notifications</CardDescription>
              </div>
            </div>
            <Switch
              checked={localPreferences.enabled}
              onCheckedChange={(checked) => handlePreferenceChange(['enabled'], checked)}
            />
          </div>
        </CardHeader>
      </Card>

      {/* Delivery Methods */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Globe className="w-5 h-5 text-[#F4D03F]" />
            <span>Delivery Methods</span>
          </CardTitle>
          <CardDescription>Choose how you want to receive notifications</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Zap className="w-4 h-4 text-[#3B82F6]" />
              <div>
                <Label className="text-white">Real-time In-App</Label>
                <p className="text-xs text-[#B8BCC8]">Instant notifications within the app</p>
              </div>
            </div>
            <Switch
              checked={localPreferences.delivery.realTime}
              onCheckedChange={(checked) => handlePreferenceChange(['delivery', 'realTime'], checked)}
              disabled={!localPreferences.enabled}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Globe className="w-4 h-4 text-[#10B981]" />
              <div>
                <Label className="text-white">Browser Notifications</Label>
                <p className="text-xs text-[#B8BCC8]">System notifications even when app is closed</p>
                {connectionStatus.browserPermission === 'default' && (
                  <Button
                    variant="link"
                    size="sm"
                    onClick={handleRequestBrowserPermission}
                    className="text-[#F4D03F] hover:text-[#F7DC6F] p-0 h-auto text-xs"
                  >
                    Grant Permission
                  </Button>
                )}
                {connectionStatus.browserPermission === 'denied' && (
                  <p className="text-xs text-[#EF4444]">Permission denied. Enable in browser settings.</p>
                )}
              </div>
            </div>
            <Switch
              checked={localPreferences.delivery.browser}
              onCheckedChange={(checked) => handlePreferenceChange(['delivery', 'browser'], checked)}
              disabled={!localPreferences.enabled || connectionStatus.browserPermission !== 'granted'}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Mail className="w-4 h-4 text-[#8B5CF6]" />
              <div>
                <Label className="text-white">Email Notifications</Label>
                <p className="text-xs text-[#B8BCC8]">Weekly digest and important alerts</p>
              </div>
            </div>
            <Switch
              checked={localPreferences.delivery.email}
              onCheckedChange={(checked) => handlePreferenceChange(['delivery', 'email'], checked)}
              disabled={!localPreferences.enabled}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Smartphone className="w-4 h-4 text-[#F59E0B]" />
              <div>
                <Label className="text-white">Mobile Push</Label>
                <p className="text-xs text-[#B8BCC8]">Coming soon - mobile app notifications</p>
              </div>
            </div>
            <Switch
              checked={localPreferences.delivery.mobile}
              onCheckedChange={(checked) => handlePreferenceChange(['delivery', 'mobile'], checked)}
              disabled={true} // Coming soon
            />
          </div>
        </CardContent>
      </Card>

      {/* Categories */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Target className="w-5 h-5 text-[#F4D03F]" />
            <span>Notification Categories</span>
          </CardTitle>
          <CardDescription>Control which types of notifications you receive</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { key: 'productivity', icon: TrendingUp, label: 'Productivity', desc: 'Task reminders, project updates, deadlines' },
            { key: 'insights', icon: Zap, label: 'AI Insights', desc: 'Smart recommendations and analysis' },
            { key: 'achievements', icon: Award, label: 'Achievements', desc: 'Goal completions, streaks, milestones' },
            { key: 'reminders', icon: Clock, label: 'Reminders', desc: 'Scheduled tasks and calendar events' },
            { key: 'system', icon: Shield, label: 'System', desc: 'App updates, security alerts, maintenance' },
          ].map(({ key, icon: Icon, label, desc }) => (
            <div key={key} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Icon className="w-4 h-4 text-[#F4D03F]" />
                <div>
                  <Label className="text-white">{label}</Label>
                  <p className="text-xs text-[#B8BCC8]">{desc}</p>
                </div>
              </div>
              <Switch
                checked={localPreferences.categories[key as keyof typeof localPreferences.categories]}
                onCheckedChange={(checked) => handlePreferenceChange(['categories', key], checked)}
                disabled={!localPreferences.enabled}
              />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Priority Levels */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-[#F4D03F]" />
            <span>Priority Levels</span>
          </CardTitle>
          <CardDescription>Control notifications based on their priority</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { key: 'urgent', label: 'Urgent', color: '#EF4444', desc: 'Critical alerts that need immediate attention' },
            { key: 'high', label: 'High', color: '#F59E0B', desc: 'Important notifications that should be seen soon' },
            { key: 'medium', label: 'Medium', color: '#3B82F6', desc: 'Standard notifications and updates' },
            { key: 'low', label: 'Low', color: '#6B7280', desc: 'Optional information and tips' },
          ].map(({ key, label, color, desc }) => (
            <div key={key} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: color }} />
                <div>
                  <Label className="text-white">{label} Priority</Label>
                  <p className="text-xs text-[#B8BCC8]">{desc}</p>
                </div>
              </div>
              <Switch
                checked={localPreferences.priority[key as keyof typeof localPreferences.priority]}
                onCheckedChange={(checked) => handlePreferenceChange(['priority', key], checked)}
                disabled={!localPreferences.enabled}
              />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Frequency Controls */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Clock className="w-5 h-5 text-[#F4D03F]" />
            <span>Frequency & Timing</span>
          </CardTitle>
          <CardDescription>Control when and how often notifications are delivered</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Rate Limiting */}
          <div>
            <Label className="text-white mb-3 block">Maximum notifications per hour</Label>
            <div className="px-2">
              <Slider
                value={[localPreferences.frequency.maxPerHour]}
                onValueChange={([value]) => handlePreferenceChange(['frequency', 'maxPerHour'], value)}
                max={50}
                min={1}
                step={1}
                disabled={!localPreferences.enabled}
                className="mb-2"
              />
              <div className="flex justify-between text-xs text-[#B8BCC8]">
                <span>1</span>
                <span className="text-[#F4D03F]">{localPreferences.frequency.maxPerHour} per hour</span>
                <span>50</span>
              </div>
            </div>
          </div>

          <Separator className="bg-[rgba(244,208,63,0.1)]" />

          {/* Immediate vs Digest */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-white">Immediate Delivery</Label>
                <p className="text-xs text-[#B8BCC8]">Show notifications as they arrive</p>
              </div>
              <Switch
                checked={localPreferences.frequency.immediate}
                onCheckedChange={(checked) => handlePreferenceChange(['frequency', 'immediate'], checked)}
                disabled={!localPreferences.enabled}
              />
            </div>

            <div>
              <Label className="text-white mb-2 block">Email Digest Frequency</Label>
              <Select
                value={localPreferences.frequency.digest}
                onValueChange={(value) => handlePreferenceChange(['frequency', 'digest'], value)}
                disabled={!localPreferences.enabled || !localPreferences.delivery.email}
              >
                <SelectTrigger className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)]">
                  <SelectItem value="daily" className="text-white hover:bg-[rgba(244,208,63,0.1)]">Daily Summary</SelectItem>
                  <SelectItem value="weekly" className="text-white hover:bg-[rgba(244,208,63,0.1)]">Weekly Digest</SelectItem>
                  <SelectItem value="never" className="text-white hover:bg-[rgba(244,208,63,0.1)]">Never</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quiet Hours */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <VolumeX className="w-5 h-5 text-[#F4D03F]" />
            <span>Quiet Hours</span>
          </CardTitle>
          <CardDescription>Set times when you don't want to be disturbed (urgent notifications will still come through)</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label className="text-white">Enable Quiet Hours</Label>
            <Switch
              checked={localPreferences.quietHours.enabled}
              onCheckedChange={(checked) => handlePreferenceChange(['quietHours', 'enabled'], checked)}
              disabled={!localPreferences.enabled}
            />
          </div>

          {localPreferences.quietHours.enabled && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-white mb-2 block">Start Time</Label>
                  <Select
                    value={localPreferences.quietHours.start}
                    onValueChange={(value) => handlePreferenceChange(['quietHours', 'start'], value)}
                  >
                    <SelectTrigger className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)]">
                      {Array.from({ length: 24 }, (_, i) => {
                        const hour = i.toString().padStart(2, '0');
                        return (
                          <SelectItem key={`${hour}:00`} value={`${hour}:00`} className="text-white hover:bg-[rgba(244,208,63,0.1)]">
                            {hour}:00
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-white mb-2 block">End Time</Label>
                  <Select
                    value={localPreferences.quietHours.end}
                    onValueChange={(value) => handlePreferenceChange(['quietHours', 'end'], value)}
                  >
                    <SelectTrigger className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)]">
                      {Array.from({ length: 24 }, (_, i) => {
                        const hour = i.toString().padStart(2, '0');
                        return (
                          <SelectItem key={`${hour}:00`} value={`${hour}:00`} className="text-white hover:bg-[rgba(244,208,63,0.1)]">
                            {hour}:00
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label className="text-white mb-2 block">Time Zone</Label>
                <Select
                  value={localPreferences.quietHours.timezone}
                  onValueChange={(value) => handlePreferenceChange(['quietHours', 'timezone'], value)}
                >
                  <SelectTrigger className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] max-h-60">
                    {getTimeZoneOptions().map((tz) => (
                      <SelectItem key={tz} value={tz} className="text-white hover:bg-[rgba(244,208,63,0.1)]">
                        {tz}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Test & Debug */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <TestTube2 className="w-5 h-5 text-[#F4D03F]" />
            <span>Test & Debug</span>
          </CardTitle>
          <CardDescription>Test your notification settings and debug issues</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">Send Test Notification</Label>
              <p className="text-xs text-[#B8BCC8]">Send a sample notification to test your settings</p>
            </div>
            <Button
              onClick={sendTestNotification}
              disabled={!localPreferences.enabled || isLoading}
              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
            >
              <TestTube2 className="w-4 h-4 mr-2" />
              Send Test
            </Button>
          </div>

          <div className="bg-[rgba(26,29,41,0.4)] p-3 rounded-lg">
            <h4 className="text-white font-medium mb-2">Connection Status</h4>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-[#B8BCC8]">WebSocket:</span>
                <span className={connectionStatus.isConnected ? 'text-[#10B981]' : 'text-[#EF4444]'}>
                  {connectionStatus.isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#B8BCC8]">Browser Permission:</span>
                <span className={
                  connectionStatus.browserPermission === 'granted' ? 'text-[#10B981]' :
                  connectionStatus.browserPermission === 'denied' ? 'text-[#EF4444]' :
                  connectionStatus.browserPermission === 'default' ? 'text-[#F59E0B]' :
                  'text-[#6B7280]'
                }>
                  {connectionStatus.browserPermission || 'unsupported'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#B8BCC8]">Queue Length:</span>
                <span className="text-white">{connectionStatus.queueLength}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#B8BCC8]">Active Subscriptions:</span>
                <span className="text-white">{connectionStatus.subscriberCount}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-6 border-t border-[rgba(244,208,63,0.1)]">
        <Button
          variant="ghost"
          onClick={handleReset}
          disabled={!hasChanges || isSaving}
          className="text-[#B8BCC8] hover:text-white hover:bg-[rgba(244,208,63,0.1)]"
        >
          Reset Changes
        </Button>
        
        <Button
          onClick={handleSave}
          disabled={!hasChanges || isSaving}
          className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] disabled:opacity-50"
        >
          {isSaving ? 'Saving...' : 'Save Preferences'}
        </Button>
      </div>
    </div>
  );
}