import { useState } from 'react';
import { Cloud, Download, Upload, RefreshCw, HardDrive, Smartphone, Monitor, CheckCircle2, AlertCircle, Wifi, Clock } from 'lucide-react';
import { Button } from '../../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Label } from '../../ui/label';
import { Switch } from '../../ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Separator } from '../../ui/separator';
import { Badge } from '../../ui/badge';
import { Progress } from '../../ui/progress';
import { Alert, AlertDescription } from '../../ui/alert';
import { motion } from 'motion/react';
import { useForm, Controller } from 'react-hook-form@7.55.0';
import { zodResolver } from '@hookform/resolvers/zod';
import { syncSettingsSchema, type SyncSettingsData } from '../../../schemas/settings';
import { useSettingsStore } from '../../../stores/settingsStore';
import { useAppStore } from '../../../stores/basicAppStore';
import { toast } from 'sonner@2.0.3';

export default function SyncSettings() {
  const [isManualSyncing, setIsManualSyncing] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);

  // Store integration
  const { syncSettings, setSyncSettings, isLoading, errors, setLoading, setError, setLastSaved } = useSettingsStore();
  const addNotification = useAppStore(state => state.addNotification);

  // Form setup
  const form = useForm<SyncSettingsData>({
    resolver: zodResolver(syncSettingsSchema),
    defaultValues: syncSettings,
    mode: 'onChange',
  });

  // Watch values for dynamic UI updates
  const watchedValues = form.watch();

  // Mock data for demo
  const [lastSync] = useState({
    timestamp: new Date(Date.now() - 2 * 60 * 1000), // 2 minutes ago
    status: 'success' as const,
    nextBackup: new Date(Date.now() + 4 * 60 * 60 * 1000), // 4 hours from now
  });

  const [devices] = useState([
    { id: 1, name: 'MacBook Pro', type: 'desktop', lastSync: new Date(Date.now() - 2 * 60 * 1000), status: 'synced' as const },
    { id: 2, name: 'iPhone 14', type: 'mobile', lastSync: new Date(Date.now() - 5 * 60 * 1000), status: 'synced' as const },
    { id: 3, name: 'iPad Air', type: 'tablet', lastSync: new Date(Date.now() - 2 * 60 * 60 * 1000), status: 'pending' as const }
  ]);

  const [storageUsage] = useState({
    used: 2.4,
    total: 5.0,
    percentage: 48
  });

  // Handle form submission
  const handleSave = async (data: SyncSettingsData) => {
    setLoading('sync', true);
    setError('sync', null);

    try {
      // Simulate API call - replace with actual backend call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Update store
      setSyncSettings(data);
      setLastSaved('sync', new Date());
      
      toast.success('Sync settings saved successfully');
      addNotification({
        type: 'success',
        title: 'Settings Updated',
        message: 'Your sync and backup preferences have been saved.',
        isRead: false,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save sync settings';
      setError('sync', errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading('sync', false);
    }
  };

  // Handle manual sync
  const handleManualSync = async () => {
    setIsManualSyncing(true);
    
    try {
      // Simulate sync process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success('Manual sync completed successfully');
      addNotification({
        type: 'success',
        title: 'Sync Complete',
        message: 'Your data has been synchronized across all devices.',
        isRead: false,
      });
    } catch (error) {
      toast.error('Manual sync failed');
    } finally {
      setIsManualSyncing(false);
    }
  };

  // Handle data export
  const handleDataExport = async () => {
    setIsExporting(true);
    setExportProgress(0);
    
    try {
      // Simulate export progress
      const interval = setInterval(() => {
        setExportProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 300);

      // Simulate export process
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      toast.success('Data export completed successfully');
      addNotification({
        type: 'success',
        title: 'Export Complete',
        message: 'Your data export is ready for download.',
        isRead: false,
      });
    } catch (error) {
      toast.error('Data export failed');
    } finally {
      setIsExporting(false);
      setTimeout(() => setExportProgress(0), 1000);
    }
  };

  // Format relative time
  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  // Get device icon
  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'mobile': return <Smartphone className="w-4 h-4" />;
      case 'tablet': return <Monitor className="w-4 h-4" />;
      default: return <Monitor className="w-4 h-4" />;
    }
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
      {errors.sync && (
        <Alert className="border-[#EF4444] bg-[rgba(239,68,68,0.1)]">
          <AlertCircle className="w-4 h-4 text-[#EF4444]" />
          <AlertDescription className="text-[#EF4444]">
            {errors.sync}
          </AlertDescription>
        </Alert>
      )}

      {/* Last Saved Indicator */}
      {useSettingsStore.getState().lastSaved.sync && (
        <div className="flex items-center space-x-2 text-sm text-[#10B981]">
          <CheckCircle2 className="w-4 h-4" />
          <span>Last saved: {new Date(useSettingsStore.getState().lastSaved.sync!).toLocaleString()}</span>
        </div>
      )}

      {/* Sync Status */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Cloud className="w-5 h-5 text-[#F4D03F]" />
            <span>Sync Status</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Current synchronization status and recent activity
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-[#10B981]" />
                <div>
                  <Label className="text-white">Last Sync</Label>
                  <p className="text-[#B8BCC8] text-sm">{formatRelativeTime(lastSync.timestamp)}</p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <Badge className="bg-[#10B981] text-white mb-2">Up to date</Badge>
              <p className="text-[#B8BCC8] text-sm">Next backup: {formatRelativeTime(lastSync.nextBackup)}</p>
            </div>
          </div>

          <div className="flex space-x-4">
            <Button 
              onClick={handleManualSync}
              disabled={isManualSyncing}
              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
            >
              {isManualSyncing ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              {isManualSyncing ? 'Syncing...' : 'Sync Now'}
            </Button>
            <Button 
              variant="outline" 
              className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
              onClick={handleDataExport}
              disabled={isExporting}
            >
              {isExporting ? (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  Exporting... ({exportProgress}%)
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  Export Data
                </>
              )}
            </Button>
          </div>

          {isExporting && exportProgress > 0 && (
            <div className="space-y-2">
              <Progress value={exportProgress} className="w-full" />
              <p className="text-[#B8BCC8] text-sm">Preparing your data export...</p>
            </div>
          )}
        </CardContent>
      </Card>

      <form onSubmit={form.handleSubmit(handleSave)} className="space-y-6">
        {/* Synchronization Settings */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <RefreshCw className="w-5 h-5 text-[#F4D03F]" />
              <span>Synchronization</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Configure how your data syncs across devices
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Auto Sync</Label>
                  <p className="text-[#B8BCC8] text-sm">Automatically sync data in the background</p>
                </div>
                <Controller
                  name="synchronization.autoSync"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              {watchedValues.synchronization?.autoSync && (
                <>
                  <div>
                    <Label htmlFor="syncFrequency" className="text-white">Sync Frequency</Label>
                    <Controller
                      name="synchronization.syncFrequency"
                      control={form.control}
                      render={({ field }) => (
                        <Select value={field.value} onValueChange={field.onChange}>
                          <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                            <SelectValue placeholder="Select frequency" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="realtime">Real-time</SelectItem>
                            <SelectItem value="hourly">Every hour</SelectItem>
                            <SelectItem value="daily">Daily</SelectItem>
                            <SelectItem value="manual">Manual only</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>

                  <div>
                    <Label htmlFor="conflictResolution" className="text-white">Conflict Resolution</Label>
                    <Controller
                      name="synchronization.conflictResolution"
                      control={form.control}
                      render={({ field }) => (
                        <Select value={field.value} onValueChange={field.onChange}>
                          <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                            <SelectValue placeholder="Select resolution method" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="local">Prefer local changes</SelectItem>
                            <SelectItem value="remote">Prefer cloud changes</SelectItem>
                            <SelectItem value="prompt">Ask me each time</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>
                </>
              )}

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Offline Mode</Label>
                  <p className="text-[#B8BCC8] text-sm">Work offline and sync when connected</p>
                </div>
                <Controller
                  name="synchronization.offlineMode"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Backup Settings */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <HardDrive className="w-5 h-5 text-[#F4D03F]" />
              <span>Backup</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Configure automatic backups and data retention
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Auto Backup</Label>
                  <p className="text-[#B8BCC8] text-sm">Automatically create data backups</p>
                </div>
                <Controller
                  name="backup.autoBackup"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              {watchedValues.backup?.autoBackup && (
                <>
                  <div>
                    <Label htmlFor="backupFrequency" className="text-white">Backup Frequency</Label>
                    <Controller
                      name="backup.backupFrequency"
                      control={form.control}
                      render={({ field }) => (
                        <Select value={field.value} onValueChange={field.onChange}>
                          <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                            <SelectValue placeholder="Select frequency" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="daily">Daily</SelectItem>
                            <SelectItem value="weekly">Weekly</SelectItem>
                            <SelectItem value="monthly">Monthly</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>

                  <div>
                    <Label htmlFor="retentionPeriod" className="text-white">Retention Period</Label>
                    <Controller
                      name="backup.retentionPeriod"
                      control={form.control}
                      render={({ field }) => (
                        <Select value={field.value} onValueChange={field.onChange}>
                          <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                            <SelectValue placeholder="Select retention period" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="30">30 days</SelectItem>
                            <SelectItem value="90">90 days</SelectItem>
                            <SelectItem value="365">1 year</SelectItem>
                            <SelectItem value="unlimited">Unlimited</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-white">Include Attachments</Label>
                      <p className="text-[#B8BCC8] text-sm">Include file attachments in backups</p>
                    </div>
                    <Controller
                      name="backup.includeAttachments"
                      control={form.control}
                      render={({ field }) => (
                        <Switch checked={field.value} onCheckedChange={field.onChange} />
                      )}
                    />
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Storage Usage */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white">Storage Usage</CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Monitor your cloud storage usage
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-[#B8BCC8]">
                <span>Used: {storageUsage.used} GB</span>
                <span>Available: {storageUsage.total - storageUsage.used} GB</span>
              </div>
              <Progress value={storageUsage.percentage} className="w-full" />
              <p className="text-xs text-[#B8BCC8]">
                {storageUsage.percentage}% of {storageUsage.total} GB used
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Connected Devices */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white">Connected Devices</CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Devices synced with your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {devices.map((device) => (
                <div key={device.id} className="flex items-center justify-between p-3 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
                  <div className="flex items-center space-x-3">
                    {getDeviceIcon(device.type)}
                    <div>
                      <Label className="text-white">{device.name}</Label>
                      <p className="text-[#B8BCC8] text-sm">Last sync: {formatRelativeTime(device.lastSync)}</p>
                    </div>
                  </div>
                  <Badge className={
                    device.status === 'synced' 
                      ? 'bg-[#10B981] text-white' 
                      : 'bg-[#F59E0B] text-white'
                  }>
                    {device.status === 'synced' ? 'Synced' : 'Pending'}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <Button 
            type="submit"
            className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
            disabled={isLoading.sync || !form.formState.isDirty}
          >
            {isLoading.sync && <CheckCircle2 className="w-4 h-4 mr-2 animate-spin" />}
            Save Settings
          </Button>
          <Button 
            type="button"
            variant="outline" 
            className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
            onClick={() => form.reset()}
            disabled={isLoading.sync}
          >
            Reset Changes
          </Button>
        </div>
      </form>
    </motion.div>
  );
}