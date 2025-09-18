import { useState } from 'react';
import { Shield, Key, Smartphone, Monitor, Eye, EyeOff, Lock, Unlock, CheckCircle2, AlertCircle, UserX, Globe } from 'lucide-react';
import { Button } from '../../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Label } from '../../ui/label';
import { Switch } from '../../ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Separator } from '../../ui/separator';
import { Badge } from '../../ui/badge';
import { Alert, AlertDescription } from '../../ui/alert';
import { motion } from 'motion/react';
import { useForm, Controller } from 'react-hook-form@7.55.0';
import { zodResolver } from '@hookform/resolvers/zod';
import { privacySettingsSchema, type PrivacySettingsData } from '../../../schemas/settings';
import { useSettingsStore } from '../../../stores/settingsStore';
import { useAppStore } from '../../../stores/basicAppStore';
import { toast } from 'sonner@2.0.3';

export default function PrivacySettings() {
  const [showTwoFactorSetup, setShowTwoFactorSetup] = useState(false);

  // Store integration
  const { privacySettings, setPrivacySettings, isLoading, errors, setLoading, setError, setLastSaved } = useSettingsStore();
  const addNotification = useAppStore(state => state.addNotification);

  // Form setup
  const form = useForm<PrivacySettingsData>({
    resolver: zodResolver(privacySettingsSchema),
    defaultValues: privacySettings,
    mode: 'onChange',
  });

  // Watch values for dynamic UI updates
  const watchedValues = form.watch();

  // Mock data for demo
  const [activeSessions] = useState([
    { id: 1, device: 'MacBook Pro', location: 'San Francisco, CA', lastActive: new Date(Date.now() - 2 * 60 * 1000), current: true },
    { id: 2, device: 'iPhone 14', location: 'San Francisco, CA', lastActive: new Date(Date.now() - 60 * 60 * 1000), current: false },
    { id: 3, device: 'iPad Air', location: 'New York, NY', lastActive: new Date(Date.now() - 24 * 60 * 60 * 1000), current: false },
  ]);

  // Handle form submission
  const handleSave = async (data: PrivacySettingsData) => {
    setLoading('privacy', true);
    setError('privacy', null);

    try {
      // Simulate API call - replace with actual backend call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Update store
      setPrivacySettings(data);
      setLastSaved('privacy', new Date());
      
      toast.success('Privacy settings saved successfully');
      addNotification({
        type: 'success',
        title: 'Settings Updated',
        message: 'Your privacy and security preferences have been saved.',
        isRead: false,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save privacy settings';
      setError('privacy', errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading('privacy', false);
    }
  };

  // Handle two-factor auth setup
  const handleTwoFactorSetup = async () => {
    setLoading('privacy', true);
    
    try {
      // Simulate 2FA setup API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setShowTwoFactorSetup(false);
      form.setValue('security.twoFactorAuth', true);
      
      toast.success('Two-factor authentication enabled');
      addNotification({
        type: 'success',
        title: 'Security Enhanced',
        message: 'Two-factor authentication has been enabled for your account.',
        isRead: false,
      });
    } catch (error) {
      toast.error('Failed to enable two-factor authentication');
    } finally {
      setLoading('privacy', false);
    }
  };

  // Handle session termination
  const handleTerminateSession = async (sessionId: number) => {
    try {
      // Simulate API call to terminate session
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('Session terminated successfully');
    } catch (error) {
      toast.error('Failed to terminate session');
    }
  };

  // Handle data download request
  const handleDataDownload = async () => {
    setLoading('privacy', true);
    
    try {
      // Simulate data preparation API call
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      toast.success('Data download request submitted');
      addNotification({
        type: 'info',
        title: 'Data Export',
        message: 'Your data export will be ready within 24 hours. You will receive an email with download instructions.',
        isRead: false,
      });
    } catch (error) {
      toast.error('Failed to request data download');
    } finally {
      setLoading('privacy', false);
    }
  };

  // Format relative time
  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Error Alert */}
      {errors.privacy && (
        <Alert className="border-[#EF4444] bg-[rgba(239,68,68,0.1)]">
          <AlertCircle className="w-4 h-4 text-[#EF4444]" />
          <AlertDescription className="text-[#EF4444]">
            {errors.privacy}
          </AlertDescription>
        </Alert>
      )}

      {/* Last Saved Indicator */}
      {useSettingsStore.getState().lastSaved.privacy && (
        <div className="flex items-center space-x-2 text-sm text-[#10B981]">
          <CheckCircle2 className="w-4 h-4" />
          <span>Last saved: {new Date(useSettingsStore.getState().lastSaved.privacy!).toLocaleString()}</span>
        </div>
      )}

      <form onSubmit={form.handleSubmit(handleSave)} className="space-y-6">
        {/* Account Privacy */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <UserX className="w-5 h-5 text-[#F4D03F]" />
              <span>Account Privacy</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Control who can see your profile and activity
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="profileVisibility" className="text-white">Profile Visibility</Label>
              <Controller
                name="account.profileVisibility"
                control={form.control}
                render={({ field }) => (
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue placeholder="Select visibility" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="private">Private - Only you</SelectItem>
                      <SelectItem value="contacts">Contacts - People you follow</SelectItem>
                      <SelectItem value="public">Public - Anyone can see</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Activity Status</Label>
                  <p className="text-[#B8BCC8] text-sm">Show when you're active or online</p>
                </div>
                <Controller
                  name="account.activityStatus"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Last Seen Visibility</Label>
                  <p className="text-[#B8BCC8] text-sm">Show when you were last active</p>
                </div>
                <Controller
                  name="account.lastSeenVisibility"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Searchable by Email</Label>
                  <p className="text-[#B8BCC8] text-sm">Allow others to find you by email address</p>
                </div>
                <Controller
                  name="account.searchableByEmail"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Data & Analytics */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Globe className="w-5 h-5 text-[#F4D03F]" />
              <span>Data & Analytics</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Control how your data is used for analytics and improvements
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Analytics Opt-in</Label>
                  <p className="text-[#B8BCC8] text-sm">Help improve the app with anonymous usage data</p>
                </div>
                <Controller
                  name="data.analyticsOptIn"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Crash Reporting</Label>
                  <p className="text-[#B8BCC8] text-sm">Send crash reports to help fix bugs</p>
                </div>
                <Controller
                  name="data.crashReporting"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Usage Statistics</Label>
                  <p className="text-[#B8BCC8] text-sm">Share feature usage statistics</p>
                </div>
                <Controller
                  name="data.usageStatistics"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Personalized Ads</Label>
                  <p className="text-[#B8BCC8] text-sm">Show ads based on your interests</p>
                </div>
                <Controller
                  name="data.personalizedAds"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Security */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Shield className="w-5 h-5 text-[#F4D03F]" />
              <span>Security</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Enhance your account security with additional protection
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between p-4 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
              <div className="flex items-center space-x-3">
                <Key className="w-5 h-5 text-[#F4D03F]" />
                <div>
                  <Label className="text-white">Two-Factor Authentication</Label>
                  <p className="text-[#B8BCC8] text-sm">Add an extra layer of security to your account</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Badge className={
                  watchedValues.security?.twoFactorAuth 
                    ? 'bg-[#10B981] text-white' 
                    : 'bg-[#F59E0B] text-white'
                }>
                  {watchedValues.security?.twoFactorAuth ? 'Enabled' : 'Disabled'}
                </Badge>
                <Controller
                  name="security.twoFactorAuth"
                  control={form.control}
                  render={({ field }) => (
                    <Switch 
                      checked={field.value} 
                      onCheckedChange={(checked) => {
                        if (checked && !field.value) {
                          setShowTwoFactorSetup(true);
                        } else {
                          field.onChange(checked);
                        }
                      }} 
                    />
                  )}
                />
              </div>
            </div>

            {showTwoFactorSetup && (
              <Alert className="border-[rgba(244,208,63,0.2)] bg-[rgba(244,208,63,0.05)]">
                <Key className="w-4 h-4 text-[#F4D03F]" />
                <AlertDescription className="text-[#B8BCC8]">
                  <div className="space-y-3">
                    <p className="text-white font-medium">Set up Two-Factor Authentication</p>
                    <p className="text-sm">
                      Two-factor authentication adds an extra layer of security to your account by requiring 
                      a verification code in addition to your password.
                    </p>
                    <div className="flex space-x-2">
                      <Button 
                        onClick={handleTwoFactorSetup}
                        disabled={isLoading.privacy}
                        size="sm"
                        className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                      >
                        Enable 2FA
                      </Button>
                      <Button 
                        onClick={() => setShowTwoFactorSetup(false)}
                        variant="outline"
                        size="sm"
                        className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                </AlertDescription>
              </Alert>
            )}

            <div>
              <Label htmlFor="sessionTimeout" className="text-white">Session Timeout</Label>
              <Controller
                name="security.sessionTimeout"
                control={form.control}
                render={({ field }) => (
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue placeholder="Select timeout" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="15">15 minutes</SelectItem>
                      <SelectItem value="30">30 minutes</SelectItem>
                      <SelectItem value="60">1 hour</SelectItem>
                      <SelectItem value="120">2 hours</SelectItem>
                      <SelectItem value="never">Never</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Login Notifications</Label>
                  <p className="text-[#B8BCC8] text-sm">Get notified when someone logs into your account</p>
                </div>
                <Controller
                  name="security.loginNotifications"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Suspicious Activity Alerts</Label>
                  <p className="text-[#B8BCC8] text-sm">Get alerts for unusual account activity</p>
                </div>
                <Controller
                  name="security.suspiciousActivityAlerts"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Active Sessions */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white">Active Sessions</CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Manage devices that are currently logged into your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {activeSessions.map((session) => (
                <div key={session.id} className="flex items-center justify-between p-3 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
                  <div className="flex items-center space-x-3">
                    {session.device.includes('iPhone') ? (
                      <Smartphone className="w-4 h-4 text-[#F4D03F]" />
                    ) : (
                      <Monitor className="w-4 h-4 text-[#F4D03F]" />
                    )}
                    <div>
                      <Label className="text-white">{session.device}</Label>
                      <p className="text-[#B8BCC8] text-sm">
                        {session.location} • Last active: {formatRelativeTime(session.lastActive)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {session.current && (
                      <Badge className="bg-[#10B981] text-white">Current</Badge>
                    )}
                    {!session.current && (
                      <Button 
                        variant="outline"
                        size="sm"
                        className="border-[#EF4444] text-[#EF4444] hover:bg-[rgba(239,68,68,0.1)]"
                        onClick={() => handleTerminateSession(session.id)}
                      >
                        Terminate
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Data Management */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white">Data Management</CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Download or delete your personal data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <div className="p-4 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
                <h4 className="text-white font-medium mb-2">Download Your Data</h4>
                <p className="text-[#B8BCC8] text-sm mb-3">
                  Request a copy of all your personal data stored in Aurum Life.
                </p>
                <Button 
                  onClick={handleDataDownload}
                  disabled={isLoading.privacy}
                  variant="outline"
                  className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                >
                  Request Data Download
                </Button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Data Export Requests</Label>
                  <p className="text-[#B8BCC8] text-sm">Allow automatic data export for compliance</p>
                </div>
                <Controller
                  name="sharing.dataExportRequests"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <Button 
            type="submit"
            className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
            disabled={isLoading.privacy || !form.formState.isDirty}
          >
            {isLoading.privacy && <CheckCircle2 className="w-4 h-4 mr-2 animate-spin" />}
            Save Settings
          </Button>
          <Button 
            type="button"
            variant="outline" 
            className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
            onClick={() => form.reset()}
            disabled={isLoading.privacy}
          >
            Reset Changes
          </Button>
        </div>
      </form>
    </motion.div>
  );
}