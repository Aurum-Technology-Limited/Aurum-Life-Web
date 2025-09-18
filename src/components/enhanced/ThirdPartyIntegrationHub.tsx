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
import { 
  Puzzle,
  Calendar,
  Heart,
  DollarSign,
  Smartphone,
  Shield,
  CheckCircle2,
  AlertTriangle,

  Settings,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  Link,
  Unlink,
  Clock,
  Activity,
  TrendingUp,
  BarChart3,
  Globe,
  Zap,
  Bell,
  Lock,
  Unlock,
  RefreshCw,
  Download,
  Upload,
  Database,
  Cloud,
  Wifi,
  WifiOff
} from 'lucide-react';

interface Integration {
  id: string;
  name: string;
  category: 'productivity' | 'fitness' | 'finance' | 'calendar' | 'social' | 'health' | 'learning';
  description: string;
  icon: string;
  status: 'connected' | 'disconnected' | 'syncing' | 'error' | 'pending';
  connectedAt?: Date;
  lastSync?: Date;
  syncFrequency: 'realtime' | 'hourly' | 'daily' | 'weekly' | 'manual';
  dataTypes: string[];
  permissions: string[];
  settings: Record<string, any>;
  metrics: IntegrationMetric[];
  health: 'excellent' | 'good' | 'warning' | 'error';
}

interface IntegrationMetric {
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  lastUpdated: Date;
}

interface SyncActivity {
  id: string;
  integrationId: string;
  type: 'sync' | 'import' | 'export' | 'error' | 'connection';
  message: string;
  timestamp: Date;
  status: 'success' | 'warning' | 'error';
  details?: string;
}

interface DataFlow {
  source: string;
  target: string;
  dataType: string;
  frequency: string;
  lastTransfer: Date;
  volume: number;
  status: 'active' | 'paused' | 'error';
}

export default function ThirdPartyIntegrationHub() {
  const [activeTab, setActiveTab] = useState('overview');
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [syncActivity, setSyncActivity] = useState<SyncActivity[]>([]);
  const [dataFlows, setDataFlows] = useState<DataFlow[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [autoSync, setAutoSync] = useState(true);

  // Sample integrations data
  useEffect(() => {
    const sampleIntegrations: Integration[] = [
      {
        id: '1',
        name: 'Google Calendar',
        category: 'calendar',
        description: 'Sync events, meetings, and time blocks with your calendar',
        icon: '📅',
        status: 'connected',
        connectedAt: new Date('2024-01-15'),
        lastSync: new Date(Date.now() - 5 * 60 * 1000),
        syncFrequency: 'realtime',
        dataTypes: ['events', 'meetings', 'time_blocks', 'reminders'],
        permissions: ['read_calendar', 'write_calendar', 'manage_events'],
        settings: {
          calendar_selection: ['primary', 'work'],
          sync_direction: 'bidirectional',
          conflict_resolution: 'manual'
        },
        metrics: [
          { name: 'Events Synced', value: 1247, unit: 'events', trend: 'up', lastUpdated: new Date() },
          { name: 'Sync Success Rate', value: 99.8, unit: '%', trend: 'stable', lastUpdated: new Date() }
        ],
        health: 'excellent'
      },
      {
        id: '2',
        name: 'Apple Health',
        category: 'fitness',
        description: 'Track health metrics, workouts, and wellness data',
        icon: '❤️',
        status: 'connected',
        connectedAt: new Date('2024-01-20'),
        lastSync: new Date(Date.now() - 15 * 60 * 1000),
        syncFrequency: 'hourly',
        dataTypes: ['steps', 'heart_rate', 'sleep', 'workouts', 'nutrition'],
        permissions: ['read_health_data', 'read_workout_data'],
        settings: {
          data_types: ['steps', 'heart_rate', 'sleep'],
          aggregation: 'daily',
          privacy_level: 'high'
        },
        metrics: [
          { name: 'Daily Steps', value: 8432, unit: 'steps', trend: 'up', lastUpdated: new Date() },
          { name: 'Sleep Hours', value: 7.2, unit: 'hours', trend: 'stable', lastUpdated: new Date() }
        ],
        health: 'good'
      },
      {
        id: '3',
        name: 'Mint',
        category: 'finance',
        description: 'Monitor spending, budgets, and financial goals',
        icon: '💰',
        status: 'syncing',
        connectedAt: new Date('2024-02-01'),
        lastSync: new Date(Date.now() - 2 * 60 * 60 * 1000),
        syncFrequency: 'daily',
        dataTypes: ['transactions', 'budgets', 'accounts', 'investments'],
        permissions: ['read_transactions', 'read_accounts', 'read_budgets'],
        settings: {
          accounts: ['checking', 'savings', 'credit_cards'],
          categories: ['essential', 'discretionary'],
          budget_sync: true
        },
        metrics: [
          { name: 'Monthly Spending', value: 2847, unit: '$', trend: 'down', lastUpdated: new Date() },
          { name: 'Budget Adherence', value: 87, unit: '%', trend: 'up', lastUpdated: new Date() }
        ],
        health: 'good'
      },
      {
        id: '4',
        name: 'Spotify',
        category: 'social',
        description: 'Track music listening habits and productivity correlation',
        icon: '🎵',
        status: 'connected',
        connectedAt: new Date('2024-01-10'),
        lastSync: new Date(Date.now() - 30 * 60 * 1000),
        syncFrequency: 'daily',
        dataTypes: ['listening_history', 'playlists', 'preferences'],
        permissions: ['read_recently_played', 'read_playlists'],
        settings: {
          privacy_mode: true,
          productivity_analysis: true,
          mood_tracking: false
        },
        metrics: [
          { name: 'Daily Listening', value: 3.4, unit: 'hours', trend: 'stable', lastUpdated: new Date() },
          { name: 'Focus Music', value: 42, unit: '%', trend: 'up', lastUpdated: new Date() }
        ],
        health: 'excellent'
      },
      {
        id: '5',
        name: 'Notion',
        category: 'productivity',
        description: 'Sync notes, projects, and knowledge base',
        icon: '📝',
        status: 'error',
        connectedAt: new Date('2024-01-25'),
        lastSync: new Date(Date.now() - 6 * 60 * 60 * 1000),
        syncFrequency: 'hourly',
        dataTypes: ['pages', 'databases', 'tasks'],
        permissions: ['read_content', 'write_content'],
        settings: {
          sync_databases: ['tasks', 'projects'],
          conflict_resolution: 'notion_wins',
          auto_create_pages: false
        },
        metrics: [
          { name: 'Pages Synced', value: 156, unit: 'pages', trend: 'stable', lastUpdated: new Date() },
          { name: 'Sync Errors', value: 3, unit: 'errors', trend: 'up', lastUpdated: new Date() }
        ],
        health: 'error'
      },
      {
        id: '6',
        name: 'Strava',
        category: 'fitness',
        description: 'Track workouts, runs, and athletic performance',
        icon: '🏃',
        status: 'disconnected',
        dataTypes: ['activities', 'performance', 'goals'],
        permissions: ['read_activities', 'read_stats'],
        settings: {},
        metrics: [],
        health: 'warning'
      }
    ];

    const sampleActivity: SyncActivity[] = [
      {
        id: '1',
        integrationId: '1',
        type: 'sync',
        message: 'Successfully synced 12 new calendar events',
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
        status: 'success'
      },
      {
        id: '2',
        integrationId: '2',
        type: 'sync',
        message: 'Health data synchronized - 8,432 steps recorded',
        timestamp: new Date(Date.now() - 15 * 60 * 1000),
        status: 'success'
      },
      {
        id: '3',
        integrationId: '5',
        type: 'error',
        message: 'Failed to sync Notion database - authentication expired',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        status: 'error',
        details: 'Please reconnect your Notion account to continue syncing'
      },
      {
        id: '4',
        integrationId: '3',
        type: 'sync',
        message: 'Financial data updated - 15 new transactions imported',
        timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000),
        status: 'success'
      }
    ];

    const sampleDataFlows: DataFlow[] = [
      {
        source: 'Google Calendar',
        target: 'Aurum Life',
        dataType: 'Events & Time Blocks',
        frequency: 'Real-time',
        lastTransfer: new Date(Date.now() - 5 * 60 * 1000),
        volume: 1247,
        status: 'active'
      },
      {
        source: 'Apple Health',
        target: 'Aurum Life',
        dataType: 'Health Metrics',
        frequency: 'Hourly',
        lastTransfer: new Date(Date.now() - 15 * 60 * 1000),
        volume: 8432,
        status: 'active'
      },
      {
        source: 'Aurum Life',
        target: 'Google Calendar',
        dataType: 'Created Events',
        frequency: 'Real-time',
        lastTransfer: new Date(Date.now() - 30 * 60 * 1000),
        volume: 89,
        status: 'active'
      }
    ];

    setIntegrations(sampleIntegrations);
    setSyncActivity(sampleActivity);
    setDataFlows(sampleDataFlows);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircle2 className="h-4 w-4 text-green-400" />;
      case 'disconnected': return <Unlink className="h-4 w-4 text-gray-400" />;
      case 'syncing': return <RefreshCw className="h-4 w-4 text-blue-400 animate-spin" />;
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-400" />;
      case 'pending': return <Clock className="h-4 w-4 text-yellow-400" />;
      default: return <Globe className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-500/20 text-green-300';
      case 'disconnected': return 'bg-gray-500/20 text-gray-300';
      case 'syncing': return 'bg-blue-500/20 text-blue-300';
      case 'error': return 'bg-red-500/20 text-red-300';
      case 'pending': return 'bg-yellow-500/20 text-yellow-300';
      default: return 'bg-gray-500/20 text-gray-300';
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'excellent': return 'text-green-400';
      case 'good': return 'text-blue-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'calendar': return <Calendar className="h-5 w-5" />;
      case 'fitness': return <Heart className="h-5 w-5" />;
      case 'finance': return <DollarSign className="h-5 w-5" />;
      case 'productivity': return <Zap className="h-5 w-5" />;
      case 'social': return <Smartphone className="h-5 w-5" />;
      case 'health': return <Activity className="h-5 w-5" />;
      case 'learning': return <BarChart3 className="h-5 w-5" />;
      default: return <Puzzle className="h-5 w-5" />;
    }
  };

  const filteredIntegrations = selectedCategory === 'all' 
    ? integrations 
    : integrations.filter(i => i.category === selectedCategory);

  const connectedCount = integrations.filter(i => i.status === 'connected').length;
  const errorCount = integrations.filter(i => i.status === 'error').length;
  const totalDataPoints = integrations.reduce((sum, i) => sum + i.metrics.reduce((mSum, m) => mSum + m.value, 0), 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center space-x-3">
              <Puzzle className="h-8 w-8 text-primary" />
              <span>Integration Hub</span>
            </h1>
            <p className="text-muted-foreground mt-1">
              Connect and sync with your favorite apps and services
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-2">
              <span className="text-sm">Auto Sync</span>
              <Switch checked={autoSync} onCheckedChange={setAutoSync} />
            </div>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Integration
            </Button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Connected</p>
                  <p className="text-2xl font-bold">{connectedCount}/{integrations.length}</p>
                </div>
                <Link className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Errors</p>
                  <p className="text-2xl font-bold">{errorCount}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-red-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Data Points</p>
                  <p className="text-2xl font-bold">{totalDataPoints.toLocaleString()}</p>
                </div>
                <Database className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Last Sync</p>
                  <p className="text-lg font-bold">2m ago</p>
                </div>
                <RefreshCw className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="activity">Sync Activity</TabsTrigger>
          <TabsTrigger value="data-flows">Data Flows</TabsTrigger>
          <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Status Summary */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Integration Status</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {integrations.filter(i => i.status === 'connected' || i.status === 'error').map((integration) => (
                  <div key={integration.id} className="glassmorphism-panel p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{integration.icon}</span>
                        <span className="font-medium">{integration.name}</span>
                      </div>
                      {getStatusIcon(integration.status)}
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">{integration.description}</p>
                    <div className="flex items-center justify-between">
                      <Badge className={getStatusColor(integration.status)}>
                        {integration.status}
                      </Badge>
                      <span className={`text-xs ${getHealthColor(integration.health)}`}>
                        {integration.health}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
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
                    <Badge className={getStatusColor(activity.status)}>
                      {activity.type}
                    </Badge>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integrations" className="space-y-6">
          {/* Category Filter */}
          <div className="flex items-center space-x-4 glassmorphism-panel p-4">
            <span className="text-sm font-medium">Category:</span>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="calendar">Calendar</SelectItem>
                <SelectItem value="fitness">Fitness & Health</SelectItem>
                <SelectItem value="finance">Finance</SelectItem>
                <SelectItem value="productivity">Productivity</SelectItem>
                <SelectItem value="social">Social & Media</SelectItem>
                <SelectItem value="learning">Learning</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Integrations Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredIntegrations.map((integration) => (
              <Card key={integration.id} className="glassmorphism-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{integration.icon}</span>
                      <div>
                        <CardTitle className="text-lg">{integration.name}</CardTitle>
                        <div className="flex items-center space-x-2 mt-1">
                          {getCategoryIcon(integration.category)}
                          <span className="text-sm text-muted-foreground capitalize">{integration.category}</span>
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
                  <CardDescription>{integration.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Badge className={getStatusColor(integration.status)}>
                      {integration.status}
                    </Badge>
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <span>Health:</span>
                      <span className={getHealthColor(integration.health)}>{integration.health}</span>
                    </div>
                  </div>

                  {integration.status === 'connected' && (
                    <>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Last Sync:</span>
                          <span>{integration.lastSync?.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span>Frequency:</span>
                          <span className="capitalize">{integration.syncFrequency}</span>
                        </div>
                      </div>

                      {integration.metrics.length > 0 && (
                        <div className="space-y-2">
                          <span className="text-sm font-medium">Recent Metrics</span>
                          {integration.metrics.map((metric, index) => (
                            <div key={index} className="flex items-center justify-between glassmorphism-panel p-2">
                              <span className="text-sm">{metric.name}</span>
                              <div className="flex items-center space-x-2">
                                <span className="text-sm font-medium">
                                  {metric.value.toLocaleString()} {metric.unit}
                                </span>
                                {metric.trend === 'up' && <TrendingUp className="h-3 w-3 text-green-400" />}
                                {metric.trend === 'down' && <TrendingUp className="h-3 w-3 text-red-400 rotate-180" />}
                                {metric.trend === 'stable' && <Activity className="h-3 w-3 text-blue-400" />}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </>
                  )}

                  <div className="flex items-center space-x-2">
                    {integration.status === 'connected' ? (
                      <>
                        <Button size="sm" variant="outline">
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Sync Now
                        </Button>
                        <Button size="sm" variant="destructive">
                          <Unlink className="h-4 w-4 mr-2" />
                          Disconnect
                        </Button>
                      </>
                    ) : (
                      <Button size="sm">
                        <Link className="h-4 w-4 mr-2" />
                        Connect
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
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
                          <Badge className={getStatusColor(activity.status)}>
                            {activity.type}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <span>{integration?.name}</span>
                          <span>•</span>
                          <span>{activity.timestamp.toLocaleString()}</span>
                        </div>
                        {activity.details && (
                          <p className="text-sm text-red-300 mt-2">{activity.details}</p>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="data-flows" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5" />
                <span>Active Data Flows</span>
              </CardTitle>
              <CardDescription>
                Monitor how data moves between Aurum Life and your connected services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {dataFlows.map((flow, index) => (
                <div key={index} className="glassmorphism-panel p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-4">
                      <div className="text-center">
                        <div className="font-medium text-sm">{flow.source}</div>
                        <div className="text-xs text-muted-foreground">Source</div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="h-0.5 w-8 bg-primary"></div>
                        <Database className="h-4 w-4 text-primary" />
                        <div className="h-0.5 w-8 bg-primary"></div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-sm">{flow.target}</div>
                        <div className="text-xs text-muted-foreground">Target</div>
                      </div>
                    </div>
                    <Badge className={
                      flow.status === 'active' ? 'bg-green-500/20 text-green-300' :
                      flow.status === 'paused' ? 'bg-yellow-500/20 text-yellow-300' :
                      'bg-red-500/20 text-red-300'
                    }>
                      {flow.status}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Data Type:</span>
                      <div className="font-medium">{flow.dataType}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Frequency:</span>
                      <div className="font-medium">{flow.frequency}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Volume:</span>
                      <div className="font-medium">{flow.volume.toLocaleString()}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Last Transfer:</span>
                      <div className="font-medium">{flow.lastTransfer.toLocaleString()}</div>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="marketplace" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Globe className="h-5 w-5" />
                <span>Integration Marketplace</span>
              </CardTitle>
              <CardDescription>
                Discover and connect new apps and services to enhance your Aurum Life experience
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Globe className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Coming Soon</h3>
                <p className="text-muted-foreground">
                  The integration marketplace will feature dozens of popular apps and services.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}