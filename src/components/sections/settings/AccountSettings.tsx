import { useState } from 'react';
import { User, Bell, Shield, Download, Trash2, Lock, Upload, Eye, EyeOff, AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import { Button } from '../../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Separator } from '../../ui/separator';
import { Badge } from '../../ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../../ui/avatar';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Textarea } from '../../ui/textarea';
import { Alert, AlertDescription } from '../../ui/alert';
import { Progress } from '../../ui/progress';
import { motion } from 'motion/react';
import { useForm } from 'react-hook-form@7.55.0';
import { zodResolver } from '@hookform/resolvers/zod';
import { accountSettingsSchema, passwordChangeSchema, type AccountSettingsData, type PasswordChangeData } from '../../../schemas/settings';
import { useSettingsStore } from '../../../stores/settingsStore';
import { useAppStore } from '../../../stores/basicAppStore';
import { toast } from 'sonner@2.0.3';

export default function AccountSettings() {
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  const [uploadProgress, setUploadProgress] = useState(0);

  // Store integration
  const { accountSettings, setAccountSettings, isLoading, errors, setLoading, setError, setLastSaved } = useSettingsStore();
  const addNotification = useAppStore(state => state.addNotification);

  // Account form
  const accountForm = useForm<AccountSettingsData>({
    resolver: zodResolver(accountSettingsSchema),
    defaultValues: accountSettings,
    mode: 'onChange',
  });

  // Password form
  const passwordForm = useForm<PasswordChangeData>({
    resolver: zodResolver(passwordChangeSchema),
    mode: 'onChange',
  });

  // Handle account settings save
  const handleAccountSave = async (data: AccountSettingsData) => {
    setLoading('account', true);
    setError('account', null);

    try {
      // Simulate API call - replace with actual backend call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Update store
      setAccountSettings(data);
      setLastSaved('account', new Date());
      
      toast.success('Account settings saved successfully');
      addNotification({
        type: 'success',
        title: 'Settings Updated',
        message: 'Your account settings have been saved.',
        isRead: false,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save account settings';
      setError('account', errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading('account', false);
    }
  };

  // Handle password change
  const handlePasswordChange = async (data: PasswordChangeData) => {
    setLoading('account', true);
    setError('account', null);

    try {
      // Simulate API call - replace with actual backend call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      passwordForm.reset();
      setIsChangingPassword(false);
      
      toast.success('Password changed successfully');
      addNotification({
        type: 'success',
        title: 'Password Updated',
        message: 'Your password has been changed successfully.',
        isRead: false,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to change password';
      setError('account', errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading('account', false);
    }
  };

  // Handle avatar upload
  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadProgress(0);
    
    try {
      // Simulate upload progress
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 200);

      // Simulate API call - replace with actual backend call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success('Profile photo updated successfully');
    } catch (error) {
      toast.error('Failed to upload profile photo');
    } finally {
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  // Handle account deletion
  const handleAccountDeletion = async () => {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    setLoading('account', true);
    
    try {
      // Simulate API call - replace with actual backend call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success('Account deletion request submitted');
      addNotification({
        type: 'info',
        title: 'Account Deletion',
        message: 'Your account deletion request has been submitted. You will receive a confirmation email within 24 hours.',
        isRead: false,
      });
    } catch (error) {
      toast.error('Failed to submit account deletion request');
    } finally {
      setLoading('account', false);
    }
  };

  const timezones = [
    { value: 'America/New_York', label: 'Eastern Time (EST)' },
    { value: 'America/Chicago', label: 'Central Time (CST)' },
    { value: 'America/Denver', label: 'Mountain Time (MST)' },
    { value: 'America/Los_Angeles', label: 'Pacific Time (PST)' },
    { value: 'UTC', label: 'UTC' },
    { value: 'Europe/London', label: 'GMT' },
    { value: 'Europe/Paris', label: 'CET' },
    { value: 'Asia/Tokyo', label: 'JST' },
  ];
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Error Alert */}
      {errors.account && (
        <Alert className="border-[#EF4444] bg-[rgba(239,68,68,0.1)]">
          <AlertCircle className="w-4 h-4 text-[#EF4444]" />
          <AlertDescription className="text-[#EF4444]">
            {errors.account}
          </AlertDescription>
        </Alert>
      )}

      {/* Last Saved Indicator */}
      {useSettingsStore.getState().lastSaved.account && (
        <div className="flex items-center space-x-2 text-sm text-[#10B981]">
          <CheckCircle2 className="w-4 h-4" />
          <span>Last saved: {new Date(useSettingsStore.getState().lastSaved.account!).toLocaleString()}</span>
        </div>
      )}

      {/* Profile Overview */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <User className="w-5 h-5 text-[#F4D03F]" />
            <span>Profile Information</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Manage your personal information and account settings
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Avatar className="w-20 h-20">
                <AvatarImage src="/api/placeholder/80/80" alt="Profile" />
                <AvatarFallback className="bg-[#F4D03F] text-[#0B0D14] text-2xl font-bold">
                  {accountSettings.fullName.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              {uploadProgress > 0 && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-full">
                  <Progress value={uploadProgress} className="w-16" />
                </div>
              )}
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-medium text-white">{accountSettings.fullName || 'Unknown User'}</h3>
              <p className="text-[#B8BCC8]">{accountSettings.email}</p>
              <p className="text-[#B8BCC8] text-sm">Member since January 2024</p>
              <Badge className="mt-2 bg-[#F4D03F] text-[#0B0D14]">Premium Member</Badge>
            </div>
            <div className="space-y-2">
              <input
                type="file"
                accept="image/*"
                onChange={handleAvatarUpload}
                className="hidden"
                id="avatar-upload"
              />
              <Button 
                variant="outline" 
                className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                onClick={() => document.getElementById('avatar-upload')?.click()}
                disabled={uploadProgress > 0}
              >
                <Upload className="w-4 h-4 mr-2" />
                Change Photo
              </Button>
            </div>
          </div>

          <Separator className="bg-[rgba(244,208,63,0.1)]" />

          <form onSubmit={accountForm.handleSubmit(handleAccountSave)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="fullName" className="text-white">Full Name</Label>
                <Input
                  id="fullName"
                  {...accountForm.register('fullName')}
                  className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
                {accountForm.formState.errors.fullName && (
                  <p className="text-[#EF4444] text-sm mt-1">{accountForm.formState.errors.fullName.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="email" className="text-white">Email</Label>
                <Input
                  id="email"
                  type="email"
                  {...accountForm.register('email')}
                  className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                />
                {accountForm.formState.errors.email && (
                  <p className="text-[#EF4444] text-sm mt-1">{accountForm.formState.errors.email.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="phone" className="text-white">Phone</Label>
                <Input
                  id="phone"
                  type="tel"
                  {...accountForm.register('phone')}
                  className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                  placeholder="+1 (555) 123-4567"
                />
                {accountForm.formState.errors.phone && (
                  <p className="text-[#EF4444] text-sm mt-1">{accountForm.formState.errors.phone.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="timezone" className="text-white">Time Zone</Label>
                <Select 
                  value={accountForm.watch('timezone')} 
                  onValueChange={(value) => accountForm.setValue('timezone', value)}
                >
                  <SelectTrigger className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                    <SelectValue placeholder="Select timezone" />
                  </SelectTrigger>
                  <SelectContent>
                    {timezones.map((tz) => (
                      <SelectItem key={tz.value} value={tz.value}>
                        {tz.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {accountForm.formState.errors.timezone && (
                  <p className="text-[#EF4444] text-sm mt-1">{accountForm.formState.errors.timezone.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="location" className="text-white">Location</Label>
                <Input
                  id="location"
                  {...accountForm.register('location')}
                  className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                  placeholder="New York, NY"
                />
                {accountForm.formState.errors.location && (
                  <p className="text-[#EF4444] text-sm mt-1">{accountForm.formState.errors.location.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="website" className="text-white">Website</Label>
                <Input
                  id="website"
                  type="url"
                  {...accountForm.register('website')}
                  className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                  placeholder="https://example.com"
                />
                {accountForm.formState.errors.website && (
                  <p className="text-[#EF4444] text-sm mt-1">{accountForm.formState.errors.website.message}</p>
                )}
              </div>
            </div>
            
            <div>
              <Label htmlFor="bio" className="text-white">Bio</Label>
              <Textarea
                id="bio"
                {...accountForm.register('bio')}
                className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white min-h-20"
                placeholder="Tell us about yourself..."
                rows={3}
              />
              <div className="flex justify-between items-center mt-1">
                {accountForm.formState.errors.bio && (
                  <p className="text-[#EF4444] text-sm">{accountForm.formState.errors.bio.message}</p>
                )}
                <p className="text-[#B8BCC8] text-sm ml-auto">
                  {accountForm.watch('bio')?.length || 0}/500
                </p>
              </div>
            </div>

            <div className="flex space-x-4">
              <Button 
                type="submit"
                className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                disabled={isLoading.account || !accountForm.formState.isDirty}
              >
                {isLoading.account && <Clock className="w-4 h-4 mr-2 animate-spin" />}
                Save Changes
              </Button>
              <Button 
                type="button"
                variant="outline" 
                className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                onClick={() => accountForm.reset()}
                disabled={isLoading.account}
              >
                Reset
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Password Change */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Lock className="w-5 h-5 text-[#F4D03F]" />
            <span>Change Password</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Update your account password for better security
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!isChangingPassword ? (
            <Button 
              onClick={() => setIsChangingPassword(true)}
              variant="outline" 
              className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
            >
              <Lock className="w-4 h-4 mr-2" />
              Change Password
            </Button>
          ) : (
            <form onSubmit={passwordForm.handleSubmit(handlePasswordChange)} className="space-y-4">
              <div>
                <Label htmlFor="currentPassword" className="text-white">Current Password</Label>
                <div className="relative">
                  <Input
                    id="currentPassword"
                    type={showPasswords.current ? 'text' : 'password'}
                    {...passwordForm.register('currentPassword')}
                    className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full px-3 text-[#B8BCC8] hover:text-[#F4D03F]"
                    onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                  >
                    {showPasswords.current ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                </div>
                {passwordForm.formState.errors.currentPassword && (
                  <p className="text-[#EF4444] text-sm mt-1">{passwordForm.formState.errors.currentPassword.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="newPassword" className="text-white">New Password</Label>
                <div className="relative">
                  <Input
                    id="newPassword"
                    type={showPasswords.new ? 'text' : 'password'}
                    {...passwordForm.register('newPassword')}
                    className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full px-3 text-[#B8BCC8] hover:text-[#F4D03F]"
                    onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                  >
                    {showPasswords.new ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                </div>
                {passwordForm.formState.errors.newPassword && (
                  <p className="text-[#EF4444] text-sm mt-1">{passwordForm.formState.errors.newPassword.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="confirmPassword" className="text-white">Confirm New Password</Label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    type={showPasswords.confirm ? 'text' : 'password'}
                    {...passwordForm.register('confirmPassword')}
                    className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full px-3 text-[#B8BCC8] hover:text-[#F4D03F]"
                    onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                  >
                    {showPasswords.confirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                </div>
                {passwordForm.formState.errors.confirmPassword && (
                  <p className="text-[#EF4444] text-sm mt-1">{passwordForm.formState.errors.confirmPassword.message}</p>
                )}
              </div>
              
              <div className="flex space-x-4">
                <Button 
                  type="submit"
                  className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                  disabled={isLoading.account}
                >
                  {isLoading.account && <Clock className="w-4 h-4 mr-2 animate-spin" />}
                  Update Password
                </Button>
                <Button 
                  type="button"
                  variant="outline" 
                  className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                  onClick={() => {
                    setIsChangingPassword(false);
                    passwordForm.reset();
                  }}
                  disabled={isLoading.account}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white">Quick Actions</CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Common account management tasks
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] h-12 justify-start">
              <Bell className="w-4 h-4 mr-3" />
              Notification Preferences
            </Button>
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] h-12 justify-start">
              <Shield className="w-4 h-4 mr-3" />
              Privacy Settings
            </Button>
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] h-12 justify-start">
              <Download className="w-4 h-4 mr-3" />
              Download My Data
            </Button>
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] h-12 justify-start">
              <User className="w-4 h-4 mr-3" />
              Account Activity
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Subscription Info */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white">Subscription</CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Manage your subscription and billing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-[rgba(244,208,63,0.1)] rounded-lg border border-[rgba(244,208,63,0.2)]">
            <div>
              <h4 className="text-white font-medium">Premium Plan</h4>
              <p className="text-[#B8BCC8] text-sm">Next billing: March 15, 2024</p>
            </div>
            <Badge className="bg-[#10B981] text-white">Active</Badge>
          </div>
          
          <div className="flex space-x-4">
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
              Manage Billing
            </Button>
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
              View Invoice History
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="glassmorphism-card border-0 border-[rgba(239,68,68,0.3)]">
        <CardHeader>
          <CardTitle className="text-[#EF4444]">Danger Zone</CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Irreversible and destructive actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-[rgba(239,68,68,0.1)] rounded-lg border border-[rgba(239,68,68,0.2)]">
              <div>
                <h4 className="text-white font-medium">Delete Account</h4>
                <p className="text-[#B8BCC8] text-sm">Permanently delete your account and all data</p>
              </div>
              <Button 
                variant="destructive" 
                className="bg-[#EF4444] hover:bg-[#DC2626]"
                onClick={handleAccountDeletion}
                disabled={isLoading.account}
              >
                {isLoading.account ? (
                  <Clock className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Trash2 className="w-4 h-4 mr-2" />
                )}
                Delete Account
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}