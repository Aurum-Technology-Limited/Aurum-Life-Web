import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Input } from '../ui/input';
import { Switch } from '../ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Separator } from '../ui/separator';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  Calendar,
  Mail,
  Smartphone,
  CheckCircle2,
  AlertTriangle,
  Settings,
  Plus,
  Link,
  Unlink,
  Clock,
  RefreshCw,
  Download,
  Upload,
  Cloud,
  Wifi,
  WifiOff,
  Shield,
  Bell,
  Eye,
  EyeOff,
  ArrowRight,
  Sync,
  Globe,
  Zap,
  Users,
  FileText,
  Info,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

interface CalendarIntegration {
  id: string;
  name: string;
  provider: 'google' | 'apple' | 'outlook' | 'gmail';
  type: 'calendar' | 'email';
  description: string;
  icon: string;
  status: 'connected' | 'disconnected' | 'syncing' | 'error' | 'setup_required';
  lastSync?: Date;
  syncFrequency: 'realtime' | 'every_15min' | 'hourly' | 'daily';
  dataTypes: string[];
  permissions: string[];
  settings: {
    syncDirection: 'import' | 'export' | 'bidirectional';
    autoSync: boolean;
    notifications: boolean;
    privateEvents: boolean;
    selectedCalendars?: string[];
    selectedLabels?: string[];
  };
  metrics: {
    eventsSynced: number;
    emailsProcessed: number;
    lastSyncDuration: number;
    successRate: number;
  };
  setupSteps: string[];
}

interface SyncActivity {
  id: string;
  integrationId: string;
  type: 'sync' | 'import' | 'export' | 'error';
  message: string;
  timestamp: Date;
  status: 'success' | 'warning' | 'error';
  details?: string;
}

export default function Integrations() {
  const [activeTab, setActiveTab] = useState('overview');
  const [integrations, setIntegrations] = useState<CalendarIntegration[]>([]);
  const [syncActivity, setSyncActivity] = useState<SyncActivity[]>([]);
  const [autoSyncEnabled, setAutoSyncEnabled] = useState(true);
  const [selectedIntegration, setSelectedIntegration] = useState<string | null>(null);

  // Initialize sample data
  useEffect(() => {
    const sampleIntegrations: CalendarIntegration[] = [
      {
        id: 'google-calendar',
        name: 'Google Calendar',
        provider: 'google',
        type: 'calendar',
        description: 'Sync your Google Calendar events with Aurum Life to automatically time-block your schedule and integrate tasks with your calendar',
        icon: '📅',
        status: 'connected',
        lastSync: new Date(Date.now() - 5 * 60 * 1000),
        syncFrequency: 'realtime',
        dataTypes: ['events', 'meetings', 'time_blocks', 'reminders', 'attendees'],
        permissions: ['read_calendar', 'write_calendar', 'manage_events'],
        settings: {
          syncDirection: 'bidirectional',
          autoSync: true,
          notifications: true,
          privateEvents: false,
          selectedCalendars: ['primary', 'work@company.com', 'personal@gmail.com']
        },
        metrics: {
          eventsSynced: 1247,
          emailsProcessed: 0,
          lastSyncDuration: 2.3,
          successRate: 99.8
        },
        setupSteps: [
          'Sign in to your Google account',
          'Grant calendar permissions',
          'Select calendars to sync',
          'Configure sync preferences',
          'Test connection'
        ]
      },
      {
        id: 'gmail',
        name: 'Gmail',
        provider: 'gmail',
        type: 'email',
        description: 'Connect Gmail to automatically create tasks from emails, track important conversations, and sync meeting invites',
        icon: '✉️',
        status: 'connected',
        lastSync: new Date(Date.now() - 10 * 60 * 1000),
        syncFrequency: 'every_15min',
        dataTypes: ['emails', 'labels', 'attachments', 'contacts', 'calendar_invites'],
        permissions: ['read_email', 'modify_labels', 'read_contacts'],
        settings: {
          syncDirection: 'import',
          autoSync: true,
          notifications: true,
          privateEvents: true,
          selectedLabels: ['Important', 'Work', 'Projects', 'Follow-up']
        },
        metrics: {
          eventsSynced: 0,
          emailsProcessed: 3847,
          lastSyncDuration: 4.1,
          successRate: 97.2
        },
        setupSteps: [
          'Authenticate with Gmail',
          'Select email labels to monitor',
          'Configure auto-task creation rules',
          'Set up notification preferences',
          'Verify email processing'
        ]
      },
      {
        id: 'apple-calendar',
        name: 'Apple Calendar (iCloud)',
        provider: 'apple',
        type: 'calendar',
        description: 'Sync your Apple Calendar and iCloud events seamlessly with your Aurum Life workflow and task management',
        icon: '🍎',
        status: 'setup_required',
        syncFrequency: 'hourly',
        dataTypes: ['events', 'reminders', 'time_blocks'],
        permissions: ['read_calendar', 'write_calendar'],
        settings: {
          syncDirection: 'bidirectional',
          autoSync: true,
          notifications: true,
          privateEvents: false
        },
        metrics: {
          eventsSynced: 0,
          emailsProcessed: 0,
          lastSyncDuration: 0,
          successRate: 0
        },
        setupSteps: [
          'Generate app-specific password in iCloud',
          'Enter iCloud credentials',
          'Select calendars to sync',
          'Configure sync settings',
          'Test connection'
        ]
      },
      {
        id: 'outlook-calendar',
        name: 'Outlook Calendar',
        provider: 'outlook',
        type: 'calendar', 
        description: 'Connect Microsoft Outlook Calendar to sync work events, meetings, and business schedule with your personal productivity system',
        icon: '📧',
        status: 'disconnected',
        syncFrequency: 'every_15min',
        dataTypes: ['events', 'meetings', 'attendees', 'rooms'],
        permissions: ['read_calendar', 'write_calendar', 'read_contacts'],
        settings: {
          syncDirection: 'bidirectional',
          autoSync: false,
          notifications: false,
          privateEvents: true
        },
        metrics: {
          eventsSynced: 0,
          emailsProcessed: 0,
          lastSyncDuration: 0,
          successRate: 0
        },
        setupSteps: [
          'Sign in with Microsoft account',
          'Grant calendar permissions',
          'Select Outlook calendars',
          'Configure meeting preferences',
          'Enable synchronization'
        ]
      }
    ];

    const sampleActivity: SyncActivity[] = [
      {
        id: '1',
        integrationId: 'google-calendar',
        type: 'sync',
        message: 'Successfully synced 12 new calendar events',
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
        status: 'success'
      },
      {
        id: '2', 
        integrationId: 'gmail',
        type: 'import',
        message: 'Processed 23 emails and created 4 new tasks',
        timestamp: new Date(Date.now() - 10 * 60 * 1000),
        status: 'success'
      },
      {
        id: '3',
        integrationId: 'apple-calendar',
        type: 'error',
        message: 'Connection failed - app-specific password required',
        timestamp: new Date(Date.now() - 30 * 60 * 1000),
        status: 'error',
        details: 'Please generate a new app-specific password in your iCloud settings'
      },
      {
        id: '4',
        integrationId: 'google-calendar',
        type: 'export',
        message: 'Created 3 calendar events from Aurum Life tasks',
        timestamp: new Date(Date.now() - 45 * 60 * 1000),
        status: 'success'
      }
    ];

    setIntegrations(sampleIntegrations);
    setSyncActivity(sampleActivity);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircle2 className="h-4 w-4 text-green-400" />;
      case 'disconnected': return <Unlink className="h-4 w-4 text-gray-400" />;
      case 'syncing': return <RefreshCw className="h-4 w-4 text-blue-400 animate-spin" />;
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-400" />;
      case 'setup_required': return <Settings className="h-4 w-4 text-yellow-400" />;
      default: return <Globe className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'disconnected': return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
      case 'syncing': return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'error': return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'setup_required': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'google': return <Calendar className="h-5 w-5 text-blue-400" />;
      case 'gmail': return <Mail className="h-5 w-5 text-red-400" />;
      case 'apple': return <Smartphone className="h-5 w-5 text-gray-300" />;
      case 'outlook': return <Mail className="h-5 w-5 text-blue-500" />;
      default: return <Calendar className="h-5 w-5" />;
    }
  };

  const connectedCount = integrations.filter(i => i.status === 'connected').length;
  const totalEvents = integrations.reduce((sum, i) => sum + i.metrics.eventsSynced, 0);
  const totalEmails = integrations.reduce((sum, i) => sum + i.metrics.emailsProcessed, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center space-x-3">
              <Calendar className="h-8 w-8 text-primary" />
              <span>Calendar & Email Integrations</span>
            </h1>
            <p className="text-muted-foreground mt-1">
              Connect your calendars and email to seamlessly integrate with your Personal Operating System
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <span className="text-sm">Auto Sync</span>
              <Switch checked={autoSyncEnabled} onCheckedChange={setAutoSyncEnabled} />
            </div>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => {
                // Navigate to the broader integration hub
                window.dispatchEvent(new CustomEvent('aurumNavigate', { 
                  detail: { section: 'integration-hub' } 
                }));
              }}
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Browse All Integrations
            </Button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Connected</p>
                  <p className="text-2xl font-bold text-primary">{connectedCount}/{integrations.length}</p>
                </div>
                <Link className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Events Synced</p>
                  <p className="text-2xl font-bold">{totalEvents.toLocaleString()}</p>
                </div>
                <Calendar className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Emails Processed</p>
                  <p className="text-2xl font-bold">{totalEmails.toLocaleString()}</p>
                </div>
                <Mail className="h-8 w-8 text-red-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Last Sync</p>
                  <p className="text-lg font-bold">5m ago</p>
                </div>
                <RefreshCw className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="calendar">Calendar</TabsTrigger>
          <TabsTrigger value="email">Email</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Quick Setup Section */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5 text-primary" />
                <span>Quick Setup Recommendations</span>
              </CardTitle>
              <CardDescription>
                Get the most out of Aurum Life by connecting your most-used services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {integrations
                  .filter(i => i.status !== 'connected')
                  .slice(0, 2)
                  .map((integration) => (
                  <div key={integration.id} className="glassmorphism-panel p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <span className="text-xl">{integration.icon}</span>
                        <div>
                          <h4 className="font-medium">{integration.name}</h4>
                          <Badge className={getStatusColor(integration.status)} variant="secondary">
                            {integration.status === 'setup_required' ? 'Setup Required' : 'Not Connected'}
                          </Badge>
                        </div>
                      </div>
                      <Button size="sm">
                        {integration.status === 'setup_required' ? 'Setup' : 'Connect'}
                      </Button>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{integration.description}</p>
                    <div className="text-xs text-muted-foreground">
                      Benefits: Automatic time blocking • Task creation • Schedule optimization
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Connected Services */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle2 className="h-5 w-5 text-green-400" />
                <span>Connected Services</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {integrations.filter(i => i.status === 'connected').length === 0 ? (
                <div className="text-center py-8">
                  <Cloud className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No Connected Services</h3>
                  <p className="text-muted-foreground mb-4">
                    Connect your calendar and email to unlock the full power of Aurum Life
                  </p>
                  <Button>Get Started</Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {integrations
                    .filter(i => i.status === 'connected')
                    .map((integration) => (
                    <div key={integration.id} className="glassmorphism-panel p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <span className="text-lg">{integration.icon}</span>
                          <div>
                            <h4 className="font-medium">{integration.name}</h4>
                            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                              <span>Last sync: {integration.lastSync?.toLocaleTimeString()}</span>
                              <span>•</span>
                              <span className="capitalize">{integration.syncFrequency.replace('_', ' ')}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(integration.status)}
                          <Button size="sm" variant="ghost">
                            <Settings className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mb-3">
                        <div className="text-center">
                          <p className="text-lg font-bold text-primary">
                            {integration.type === 'calendar' 
                              ? integration.metrics.eventsSynced.toLocaleString()
                              : integration.metrics.emailsProcessed.toLocaleString()}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {integration.type === 'calendar' ? 'Events' : 'Emails'}
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-green-400">
                            {integration.metrics.successRate}%
                          </p>
                          <p className="text-xs text-muted-foreground">Success Rate</p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <Button size="sm" variant="outline">
                          <RefreshCw className="h-3 w-3 mr-2" />
                          Sync Now
                        </Button>
                        <Button size="sm" variant="ghost">
                          Configure
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* PAPT Integration Benefits */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5 text-primary" />
                <span>How Integrations Enhance Your PAPT Framework</span>
              </CardTitle>
              <CardDescription>
                See how calendar and email integrations align with your Personal Operating System
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="glassmorphism-panel p-4 hierarchy-pillar">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                      <Calendar className="h-4 w-4 text-primary" />
                    </div>
                    <h4 className="font-medium">Calendar Integration</h4>
                  </div>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-primary"></div>
                      <span>Auto-creates time blocks for Projects</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                      <span>Schedules Tasks based on Areas</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-green-400"></div>
                      <span>Aligns meetings with Pillar goals</span>
                    </div>
                  </div>
                </div>

                <div className="glassmorphism-panel p-4 hierarchy-area">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                      <Mail className="h-4 w-4 text-blue-400" />
                    </div>
                    <h4 className="font-medium">Email Integration</h4>
                  </div>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                      <span>Converts emails to actionable Tasks</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-green-400"></div>
                      <span>Links conversations to Projects</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-purple-400"></div>
                      <span>Tracks follow-ups by Area</span>
                    </div>
                  </div>
                </div>
              </div>

              <Alert className="border-primary/20 bg-primary/10">
                <Info className="h-4 w-4" />
                <AlertDescription className="text-primary-foreground">
                  <strong>Pro Tip:</strong> Connected integrations automatically organize your external commitments 
                  into your PAPT hierarchy, ensuring nothing falls through the cracks while maintaining focus on your life goals.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Clock className="h-5 w-5" />
                <span>Recent Sync Activity</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {syncActivity.slice(0, 5).map((activity) => {
                const integration = integrations.find(i => i.id === activity.integrationId);
                return (
                  <div key={activity.id} className="flex items-start space-x-3 glassmorphism-panel p-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{integration?.icon}</span>
                      {activity.status === 'success' && <CheckCircle2 className="h-4 w-4 text-green-400" />}
                      {activity.status === 'error' && <AlertTriangle className="h-4 w-4 text-red-400" />}
                      {activity.status === 'warning' && <AlertTriangle className="h-4 w-4 text-yellow-400" />}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.message}</p>
                      <p className="text-xs text-muted-foreground">
                        {integration?.name} • {activity.timestamp.toLocaleString()}
                      </p>
                      {activity.details && (
                        <p className="text-xs text-red-300 mt-1">{activity.details}</p>
                      )}
                    </div>
                    <Badge className={getStatusColor(activity.status)} variant="secondary">
                      {activity.type}
                    </Badge>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="calendar" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {integrations
              .filter(i => i.type === 'calendar')
              .map((integration) => (
              <Card key={integration.id} className="glassmorphism-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{integration.icon}</span>
                      <div>
                        <CardTitle className="text-lg">{integration.name}</CardTitle>
                        <div className="flex items-center space-x-2 mt-1">
                          {getProviderIcon(integration.provider)}
                          <span className="text-sm text-muted-foreground capitalize">
                            {integration.provider} Calendar
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(integration.status)}
                    </div>
                  </div>
                  <CardDescription>{integration.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Badge className={getStatusColor(integration.status)} variant="secondary">
                      {integration.status.replace('_', ' ')}
                    </Badge>
                    {integration.status === 'connected' && (
                      <div className="text-sm text-muted-foreground">
                        Next sync: {integration.syncFrequency.replace('_', ' ')}
                      </div>
                    )}
                  </div>

                  {integration.status === 'connected' && (
                    <>
                      <Separator />
                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                          <span>Events Synced:</span>
                          <span className="font-medium">{integration.metrics.eventsSynced.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span>Success Rate:</span>
                          <span className="font-medium text-green-400">{integration.metrics.successRate}%</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span>Last Sync Duration:</span>
                          <span className="font-medium">{integration.metrics.lastSyncDuration}s</span>
                        </div>
                      </div>

                      <Separator />
                      <div className="space-y-3">
                        <h4 className="text-sm font-medium">Sync Settings</h4>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Auto Sync</span>
                            <Switch 
                              checked={integration.settings.autoSync} 
                              onCheckedChange={() => {}} 
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Notifications</span>
                            <Switch 
                              checked={integration.settings.notifications} 
                              onCheckedChange={() => {}} 
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Private Events</span>
                            <Switch 
                              checked={integration.settings.privateEvents} 
                              onCheckedChange={() => {}} 
                            />
                          </div>
                        </div>
                      </div>
                    </>
                  )}

                  {integration.status === 'setup_required' && (
                    <>
                      <Separator />
                      <div className="space-y-3">
                        <h4 className="text-sm font-medium">Setup Steps</h4>
                        <div className="space-y-2">
                          {integration.setupSteps.map((step, index) => (
                            <div key={index} className="flex items-center space-x-2">
                              <div className="w-5 h-5 rounded-full bg-primary/20 text-primary text-xs flex items-center justify-center">
                                {index + 1}
                              </div>
                              <span className="text-sm">{step}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  )}

                  <div className="flex items-center space-x-2 pt-2">
                    {integration.status === 'connected' ? (
                      <>
                        <Button size="sm" variant="outline">
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Sync Now
                        </Button>
                        <Button size="sm" variant="outline">
                          <Settings className="h-4 w-4 mr-2" />
                          Configure
                        </Button>
                        <Button size="sm" variant="destructive">
                          <Unlink className="h-4 w-4 mr-2" />
                          Disconnect
                        </Button>
                      </>
                    ) : integration.status === 'setup_required' ? (
                      <Button size="sm" className="w-full">
                        <Settings className="h-4 w-4 mr-2" />
                        Complete Setup
                      </Button>
                    ) : (
                      <Button size="sm" className="w-full">
                        <Link className="h-4 w-4 mr-2" />
                        Connect Calendar
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="email" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {integrations
              .filter(i => i.type === 'email')
              .map((integration) => (
              <Card key={integration.id} className="glassmorphism-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{integration.icon}</span>
                      <div>
                        <CardTitle className="text-lg">{integration.name}</CardTitle>
                        <div className="flex items-center space-x-2 mt-1">
                          {getProviderIcon(integration.provider)}
                          <span className="text-sm text-muted-foreground capitalize">
                            Email Integration
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(integration.status)}
                    </div>
                  </div>
                  <CardDescription>{integration.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Badge className={getStatusColor(integration.status)} variant="secondary">
                      {integration.status.replace('_', ' ')}
                    </Badge>
                    {integration.status === 'connected' && (
                      <div className="text-sm text-muted-foreground">
                        Checking every {integration.syncFrequency.replace('_', ' ')}
                      </div>
                    )}
                  </div>

                  {integration.status === 'connected' && (
                    <>
                      <Separator />
                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                          <span>Emails Processed:</span>
                          <span className="font-medium">{integration.metrics.emailsProcessed.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span>Success Rate:</span>
                          <span className="font-medium text-green-400">{integration.metrics.successRate}%</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span>Last Check Duration:</span>
                          <span className="font-medium">{integration.metrics.lastSyncDuration}s</span>
                        </div>
                      </div>

                      <Separator />
                      <div className="space-y-3">
                        <h4 className="text-sm font-medium">Email Settings</h4>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Auto Task Creation</span>
                            <Switch 
                              checked={integration.settings.autoSync} 
                              onCheckedChange={() => {}} 
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Email Notifications</span>
                            <Switch 
                              checked={integration.settings.notifications} 
                              onCheckedChange={() => {}} 
                            />
                          </div>
                        </div>
                        
                        {integration.settings.selectedLabels && (
                          <div className="space-y-2">
                            <span className="text-sm font-medium">Monitored Labels</span>
                            <div className="flex flex-wrap gap-1">
                              {integration.settings.selectedLabels.map((label) => (
                                <Badge key={label} variant="secondary" className="text-xs">
                                  {label}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </>
                  )}

                  <div className="flex items-center space-x-2 pt-2">
                    {integration.status === 'connected' ? (
                      <>
                        <Button size="sm" variant="outline">
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Check Now
                        </Button>
                        <Button size="sm" variant="outline">
                          <Settings className="h-4 w-4 mr-2" />
                          Configure
                        </Button>
                        <Button size="sm" variant="destructive">
                          <Unlink className="h-4 w-4 mr-2" />
                          Disconnect
                        </Button>
                      </>
                    ) : (
                      <Button size="sm" className="w-full">
                        <Link className="h-4 w-4 mr-2" />
                        Connect Email
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Add Email Integration Card */}
          <Card className="glassmorphism-card border-dashed border-primary/30">
            <CardContent className="p-6 text-center">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mx-auto">
                  <Plus className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-lg font-medium mb-2">Add Email Integration</h3>
                  <p className="text-muted-foreground text-sm">
                    Connect additional email accounts to create tasks, track conversations, and manage your inbox productivity
                  </p>
                </div>
                <Button
                  onClick={() => {
                    // Navigate to the broader integration hub
                    window.dispatchEvent(new CustomEvent('aurumNavigate', { 
                      detail: { section: 'integration-hub' } 
                    }));
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Browse Email Providers
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="space-y-6">
          <div className="space-y-4">
            {syncActivity.map((activity) => {
              const integration = integrations.find(i => i.id === activity.integrationId);
              return (
                <Card key={activity.id} className="glassmorphism-card">
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-xl">{integration?.icon}</span>
                        {activity.status === 'success' && <CheckCircle2 className="h-5 w-5 text-green-400" />}
                        {activity.status === 'error' && <AlertTriangle className="h-5 w-5 text-red-400" />}
                        {activity.status === 'warning' && <AlertTriangle className="h-5 w-5 text-yellow-400" />}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-semibold">{activity.message}</h3>
                          <Badge className={getStatusColor(activity.status)} variant="secondary">
                            {activity.type}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <span>{integration?.name}</span>
                          <span>•</span>
                          <span>{activity.timestamp.toLocaleString()}</span>
                        </div>
                        {activity.details && (
                          <Alert className="mt-3 border-red-500/20 bg-red-500/10">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription className="text-red-300">
                              {activity.details}
                            </AlertDescription>
                          </Alert>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}