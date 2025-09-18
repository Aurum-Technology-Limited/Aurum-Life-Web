import { useState } from 'react';
import { Settings as SettingsIcon, Code, Database, Zap, Bug, Globe, Terminal, FileText, AlertTriangle, RotateCcw, TestTube, RefreshCw } from 'lucide-react';
import { Button } from '../../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Label } from '../../ui/label';
import { Switch } from '../../ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Separator } from '../../ui/separator';
import { Input } from '../../ui/input';
import { Textarea } from '../../ui/textarea';
import { Badge } from '../../ui/badge';
import { motion } from 'motion/react';
import { useAuthStore } from '../../../stores/authStore';
import { useOnboardingStore } from '../../../stores/onboardingStore';
import { showSuccess, showError } from '../../../utils/toast';

export default function AdvancedSettings() {
  const { user, resetDemoOnboarding } = useAuthStore();
  const { resetOnboarding } = useOnboardingStore();
  const isDemoUser = user?.email === 'demo@aurumlife.com';
  
  const [advancedSettings, setAdvancedSettings] = useState({
    debugMode: false,
    betaFeatures: false,
    developerMode: false,
    verboseLogging: false,
    performanceMode: 'balanced',
    cacheEnabled: true,
    preloadData: true
  });

  const handleResetDemoOnboarding = () => {
    try {
      // Reset onboarding store
      resetOnboarding();
      
      // Reset auth state for demo user
      resetDemoOnboarding();
      
      showSuccess('Demo onboarding reset successfully! Please refresh the page to see the onboarding flow.');
    } catch (error) {
      console.error('Failed to reset demo onboarding:', error);
      showError('Failed to reset demo onboarding. Please try again.');
    }
  };

  const [systemInfo] = useState({
    version: '2.1.0',
    buildNumber: '2024.02.15.1',
    platform: 'Web',
    nodeVersion: '18.17.0',
    databaseVersion: 'PostgreSQL 15.4',
    lastUpdate: '2024-02-15'
  });

  const [logs] = useState([
    { id: 1, level: 'info', message: 'Application started successfully', timestamp: '2024-02-15 10:30:25' },
    { id: 2, level: 'warn', message: 'Slow query detected in dashboard metrics', timestamp: '2024-02-15 10:29:12' },
    { id: 3, level: 'error', message: 'Failed to sync with external calendar', timestamp: '2024-02-15 10:25:45' },
    { id: 4, level: 'info', message: 'Background sync completed', timestamp: '2024-02-15 10:20:10' }
  ]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* System Information */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <SettingsIcon className="w-5 h-5 text-[#F4D03F]" />
            <span>System Information</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Current system status and version information
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-4 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
              <Label className="text-[#F4D03F]">App Version</Label>
              <p className="text-white font-mono">{systemInfo.version}</p>
            </div>
            <div className="p-4 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
              <Label className="text-[#F4D03F]">Build Number</Label>
              <p className="text-white font-mono">{systemInfo.buildNumber}</p>
            </div>
            <div className="p-4 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
              <Label className="text-[#F4D03F]">Platform</Label>
              <p className="text-white font-mono">{systemInfo.platform}</p>
            </div>
            <div className="p-4 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
              <Label className="text-[#F4D03F]">Runtime</Label>
              <p className="text-white font-mono">Node {systemInfo.nodeVersion}</p>
            </div>
            <div className="p-4 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
              <Label className="text-[#F4D03F]">Database</Label>
              <p className="text-white font-mono">{systemInfo.databaseVersion}</p>
            </div>
            <div className="p-4 bg-[rgba(244,208,63,0.05)] rounded-lg border border-[rgba(244,208,63,0.1)]">
              <Label className="text-[#F4D03F]">Last Update</Label>
              <p className="text-white font-mono">{systemInfo.lastUpdate}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Demo Testing Section - Only for demo users */}
      {isDemoUser && (
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <TestTube className="w-5 h-5 text-[#F4D03F]" />
              <span>Demo Testing Tools</span>
              <Badge className="bg-[#F4D03F] text-[#0B0D14] text-xs">DEMO ONLY</Badge>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Special testing tools available for the demo account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="p-4 bg-[rgba(244,208,63,0.1)] rounded-lg border border-[rgba(244,208,63,0.2)]">
              <div className="flex items-center space-x-2 text-[#F4D03F] mb-3">
                <RotateCcw className="w-4 h-4" />
                <span className="font-medium">Reset Onboarding Flow</span>
              </div>
              <p className="text-[#B8BCC8] text-sm mb-4">
                Reset the demo account to trigger the complete onboarding experience from the beginning. 
                This will clear all onboarding progress and mark you as a first-time user.
              </p>
              <Button 
                onClick={handleResetDemoOnboarding}
                className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset Demo Onboarding
              </Button>
            </div>

            <div className="p-4 bg-[rgba(59,130,246,0.1)] rounded-lg border border-[rgba(59,130,246,0.2)]">
              <div className="flex items-center space-x-2 text-[#3B82F6] mb-3">
                <RefreshCw className="w-4 h-4" />
                <span className="font-medium">Quick Reset Options</span>
              </div>
              <p className="text-[#B8BCC8] text-sm mb-4">
                Additional reset options for testing different scenarios.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Button 
                  variant="outline" 
                  className="border-[rgba(59,130,246,0.3)] text-[#3B82F6] hover:bg-[rgba(59,130,246,0.1)]"
                  onClick={() => {
                    localStorage.removeItem('aurum-onboarding');
                    showSuccess('Onboarding data cleared');
                  }}
                >
                  Clear Onboarding Data
                </Button>
                <Button 
                  variant="outline" 
                  className="border-[rgba(59,130,246,0.3)] text-[#3B82F6] hover:bg-[rgba(59,130,246,0.1)]"
                  onClick={() => {
                    localStorage.removeItem('aurum-auth');
                    showSuccess('Auth state cleared');
                  }}
                >
                  Clear Auth State
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Developer Settings */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Code className="w-5 h-5 text-[#F4D03F]" />
            <span>Developer Settings</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Advanced options for developers and power users
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">Developer Mode</Label>
              <p className="text-[#B8BCC8] text-sm">Enable advanced developer features and tools</p>
            </div>
            <Switch 
              checked={advancedSettings.developerMode} 
              onCheckedChange={(checked) => setAdvancedSettings(prev => ({ ...prev, developerMode: checked }))}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">Debug Mode</Label>
              <p className="text-[#B8BCC8] text-sm">Show detailed debugging information</p>
            </div>
            <Switch 
              checked={advancedSettings.debugMode} 
              onCheckedChange={(checked) => setAdvancedSettings(prev => ({ ...prev, debugMode: checked }))}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">Verbose Logging</Label>
              <p className="text-[#B8BCC8] text-sm">Enable detailed application logging</p>
            </div>
            <Switch 
              checked={advancedSettings.verboseLogging} 
              onCheckedChange={(checked) => setAdvancedSettings(prev => ({ ...prev, verboseLogging: checked }))}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">Beta Features</Label>
              <p className="text-[#B8BCC8] text-sm">Access experimental features (may be unstable)</p>
            </div>
            <Switch 
              checked={advancedSettings.betaFeatures} 
              onCheckedChange={(checked) => setAdvancedSettings(prev => ({ ...prev, betaFeatures: checked }))}
            />
          </div>

          {advancedSettings.betaFeatures && (
            <div className="p-4 bg-[rgba(239,68,68,0.1)] rounded-lg border border-[rgba(239,68,68,0.2)]">
              <div className="flex items-center space-x-2 text-[#EF4444] mb-2">
                <AlertTriangle className="w-4 h-4" />
                <span className="font-medium">Warning</span>
              </div>
              <p className="text-[#B8BCC8] text-sm">Beta features may be unstable and could cause data loss or app crashes. Use with caution.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Performance Settings */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Zap className="w-5 h-5 text-[#F4D03F]" />
            <span>Performance Settings</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Optimize app performance for your device
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label className="text-white">Performance Mode</Label>
            <Select 
              value={advancedSettings.performanceMode} 
              onValueChange={(value) => setAdvancedSettings(prev => ({ ...prev, performanceMode: value }))}
            >
              <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                <SelectItem value="power-saver">Power Saver - Minimal resource usage</SelectItem>
                <SelectItem value="balanced">Balanced - Good performance and efficiency</SelectItem>
                <SelectItem value="performance">Performance - Maximum speed and responsiveness</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">Enable Caching</Label>
              <p className="text-[#B8BCC8] text-sm">Cache data locally for faster loading</p>
            </div>
            <Switch 
              checked={advancedSettings.cacheEnabled} 
              onCheckedChange={(checked) => setAdvancedSettings(prev => ({ ...prev, cacheEnabled: checked }))}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="text-white">Preload Data</Label>
              <p className="text-[#B8BCC8] text-sm">Load data in background for smoother experience</p>
            </div>
            <Switch 
              checked={advancedSettings.preloadData} 
              onCheckedChange={(checked) => setAdvancedSettings(prev => ({ ...prev, preloadData: checked }))}
            />
          </div>
        </CardContent>
      </Card>

      {/* API Configuration */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Globe className="w-5 h-5 text-[#F4D03F]" />
            <span>API Configuration</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Configure API endpoints and external integrations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-white">API Base URL</Label>
            <Input
              value="https://api.aurumlife.com/v1"
              className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white font-mono"
              readOnly
            />
          </div>

          <div>
            <Label className="text-white">Webhook URL</Label>
            <Input
              placeholder="https://your-domain.com/webhook"
              className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
            />
          </div>

          <div>
            <Label className="text-white">Request Timeout (seconds)</Label>
            <Select defaultValue="30">
              <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                <SelectItem value="10">10 seconds</SelectItem>
                <SelectItem value="30">30 seconds</SelectItem>
                <SelectItem value="60">60 seconds</SelectItem>
                <SelectItem value="120">120 seconds</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Database Tools */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Database className="w-5 h-5 text-[#F4D03F]" />
            <span>Database Tools</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Advanced database management and maintenance
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] h-12 justify-start">
              <Database className="w-4 h-4 mr-3" />
              Vacuum Database
            </Button>
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] h-12 justify-start">
              <Zap className="w-4 h-4 mr-3" />
              Rebuild Indexes
            </Button>
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] h-12 justify-start">
              <FileText className="w-4 h-4 mr-3" />
              Export Schema
            </Button>
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] h-12 justify-start">
              <Terminal className="w-4 h-4 mr-3" />
              SQL Console
            </Button>
          </div>

          <div className="p-4 bg-[rgba(239,68,68,0.1)] rounded-lg border border-[rgba(239,68,68,0.2)]">
            <div className="flex items-center space-x-2 text-[#EF4444] mb-2">
              <AlertTriangle className="w-4 h-4" />
              <span className="font-medium">Danger Zone</span>
            </div>
            <p className="text-[#B8BCC8] text-sm mb-3">These operations can affect your data. Use with extreme caution.</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button variant="destructive" className="bg-[#EF4444] hover:bg-[#DC2626] h-12 justify-start">
                <Database className="w-4 h-4 mr-3" />
                Reset Cache
              </Button>
              <Button variant="destructive" className="bg-[#EF4444] hover:bg-[#DC2626] h-12 justify-start">
                <Terminal className="w-4 h-4 mr-3" />
                Reset Settings
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Debug Logs */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Bug className="w-5 h-5 text-[#F4D03F]" />
            <span>Debug Logs</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            View recent application logs and debug information
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
            {logs.map((log) => (
              <div key={log.id} className="p-3 bg-[rgba(244,208,63,0.05)] rounded border border-[rgba(244,208,63,0.1)] font-mono text-sm">
                <div className="flex items-center justify-between mb-1">
                  <Badge className={`text-xs ${
                    log.level === 'error' ? 'bg-[#EF4444]' : 
                    log.level === 'warn' ? 'bg-[#F59E0B]' : 
                    'bg-[#10B981]'
                  } text-white`}>
                    {log.level.toUpperCase()}
                  </Badge>
                  <span className="text-[#B8BCC8] text-xs">{log.timestamp}</span>
                </div>
                <p className="text-white text-sm">{log.message}</p>
              </div>
            ))}
          </div>

          <div className="flex space-x-4">
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
              <FileText className="w-4 h-4 mr-2" />
              Export Logs
            </Button>
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
              <Bug className="w-4 h-4 mr-2" />
              Clear Logs
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Custom Scripts */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Terminal className="w-5 h-5 text-[#F4D03F]" />
            <span>Custom Scripts</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Execute custom scripts and automation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-white">Script Console</Label>
            <Textarea
              placeholder="// Enter your custom JavaScript here
console.log('Hello Aurum Life!');"
              rows={6}
              className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white font-mono"
            />
          </div>

          <div className="flex space-x-4">
            <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
              <Terminal className="w-4 h-4 mr-2" />
              Execute Script
            </Button>
            <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
              <FileText className="w-4 h-4 mr-2" />
              Save Script
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex space-x-4">
        <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
          Save Advanced Settings
        </Button>
        <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
          Export Configuration
        </Button>
      </div>
    </motion.div>
  );
}