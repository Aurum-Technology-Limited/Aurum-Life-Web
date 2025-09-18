/**
 * Granular Privacy Controls Component
 * Comprehensive privacy settings with granular control over AI features and data usage
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Shield, Eye, EyeOff, Brain, Server, Download, 
  Trash2, Lock, Unlock, Settings, AlertTriangle,
  CheckCircle, Info, Clock, FileText, Users,
  Database, Cloud, Smartphone, Globe, History,
  ChevronDown, ChevronRight, Save, X, RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Alert, AlertDescription } from '../ui/alert';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Separator } from '../ui/separator';
import { useAuthStore } from '../../stores/authStore';
import { privacyConsentService } from '../../services/privacyConsentService';
import toast from '../../utils/toast';

interface PrivacySettings {
  dataCollection: {
    analytics: boolean;
    usage: boolean;
    performance: boolean;
    errors: boolean;
    interactions: boolean;
  };
  aiFeatures: {
    smartSuggestions: boolean;
    productivityInsights: boolean;
    goalRecommendations: boolean;
    habitTracking: boolean;
    timeBlocking: boolean;
    semanticSearch: boolean;
    autoTagging: boolean;
    contentAnalysis: boolean;
  };
  dataSharing: {
    anonymizedUsage: boolean;
    productImprovement: boolean;
    researchParticipation: boolean;
    marketingCommunications: boolean;
    thirdPartyIntegrations: boolean;
  };
  dataRetention: {
    activityLogs: 'forever' | '1year' | '6months' | '3months';
    analyticsData: 'forever' | '1year' | '6months' | '3months';
    aiInsights: 'forever' | '1year' | '6months' | '3months';
    deletedItems: 'forever' | '1year' | '6months' | '3months' | '30days';
  };
  visibility: {
    profileVisibility: 'private' | 'limited' | 'public';
    activitySharing: boolean;
    achievementSharing: boolean;
    progressSharing: boolean;
  };
  security: {
    twoFactorAuth: boolean;
    sessionTimeout: '15min' | '30min' | '1hour' | '4hours' | 'never';
    deviceTracking: boolean;
    loginNotifications: boolean;
  };
}

interface ConsentRecord {
  id: string;
  category: string;
  granted: boolean;
  timestamp: string;
  version: string;
  details: string;
}

interface AuditLogEntry {
  id: string;
  timestamp: string;
  action: string;
  category: 'data_access' | 'ai_processing' | 'data_export' | 'privacy_change' | 'consent_update';
  details: string;
  dataTypes: string[];
  purpose: string;
  automated: boolean;
}

interface GranularPrivacyControlsProps {
  className?: string;
}

const GranularPrivacyControls: React.FC<GranularPrivacyControlsProps> = ({
  className = ''
}) => {
  const { user } = useAuthStore();
  
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('permissions');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showAuditLog, setShowAuditLog] = useState(false);
  
  // Privacy settings state
  const [privacySettings, setPrivacySettings] = useState<PrivacySettings>({
    dataCollection: {
      analytics: true,
      usage: true,
      performance: true,
      errors: true,
      interactions: false
    },
    aiFeatures: {
      smartSuggestions: true,
      productivityInsights: true,
      goalRecommendations: true,
      habitTracking: false,
      timeBlocking: false,
      semanticSearch: true,
      autoTagging: true,
      contentAnalysis: false
    },
    dataSharing: {
      anonymizedUsage: false,
      productImprovement: false,
      researchParticipation: false,
      marketingCommunications: false,
      thirdPartyIntegrations: false
    },
    dataRetention: {
      activityLogs: '1year',
      analyticsData: '6months',
      aiInsights: '1year',
      deletedItems: '30days'
    },
    visibility: {
      profileVisibility: 'private',
      activitySharing: false,
      achievementSharing: false,
      progressSharing: false
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: '1hour',
      deviceTracking: true,
      loginNotifications: true
    }
  });

  // Consent and audit data
  const [consentHistory, setConsentHistory] = useState<ConsentRecord[]>([]);
  const [auditLog, setAuditLog] = useState<AuditLogEntry[]>([]);
  const [expandedSections, setExpandedSections] = useState<string[]>(['dataCollection']);

  // Load privacy settings
  useEffect(() => {
    loadPrivacySettings();
    loadConsentHistory();
    loadAuditLog();
  }, [user]);

  const loadPrivacySettings = async () => {
    try {
      const settings = await privacyConsentService.getPrivacySettings();
      if (settings) {
        setPrivacySettings(settings);
      }
    } catch (error) {
      console.error('Failed to load privacy settings:', error);
    }
  };

  const loadConsentHistory = async () => {
    try {
      const history = await privacyConsentService.getConsentHistory();
      setConsentHistory(history);
    } catch (error) {
      console.error('Failed to load consent history:', error);
    }
  };

  const loadAuditLog = async () => {
    try {
      const log = await privacyConsentService.getAuditLog();
      setAuditLog(log);
    } catch (error) {
      console.error('Failed to load audit log:', error);
    }
  };

  const savePrivacySettings = async () => {
    setLoading(true);
    try {
      await privacyConsentService.updatePrivacySettings(privacySettings);
      
      // Log the privacy settings change
      await privacyConsentService.logPrivacyAction({
        action: 'privacy_settings_updated',
        category: 'privacy_change',
        details: 'User updated privacy settings',
        dataTypes: Object.keys(privacySettings),
        purpose: 'privacy_control'
      });
      
      toast.success('Privacy settings updated successfully');
    } catch (error) {
      console.error('Failed to save privacy settings:', error);
      toast.error('Failed to save privacy settings');
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  const updateNestedSetting = (
    category: keyof PrivacySettings,
    setting: string,
    value: boolean | string
  ) => {
    setPrivacySettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value
      }
    }));
  };

  const getPrivacyScore = (): number => {
    let score = 0;
    let total = 0;

    // Calculate privacy score based on restrictive settings
    Object.entries(privacySettings.dataCollection).forEach(([_, enabled]) => {
      total++;
      if (!enabled) score++; // More privacy = higher score
    });

    Object.entries(privacySettings.aiFeatures).forEach(([_, enabled]) => {
      total++;
      if (!enabled) score++; // Fewer AI features = higher privacy
    });

    Object.entries(privacySettings.dataSharing).forEach(([_, enabled]) => {
      total++;
      if (!enabled) score++; // No sharing = higher privacy
    });

    return Math.round((score / total) * 100);
  };

  const exportUserData = async () => {
    try {
      setLoading(true);
      const data = await privacyConsentService.exportUserData();
      
      // Create and download the file
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `aurum-life-data-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      // Log the export action
      await privacyConsentService.logPrivacyAction({
        action: 'data_exported',
        category: 'data_export',
        details: 'User exported their data',
        dataTypes: ['all'],
        purpose: 'data_portability'
      });
      
      setShowExportModal(false);
      toast.success('Data export completed successfully');
    } catch (error) {
      console.error('Failed to export data:', error);
      toast.error('Failed to export data');
    } finally {
      setLoading(false);
    }
  };

  const deleteAccount = async () => {
    try {
      setLoading(true);
      await privacyConsentService.deleteAccount();
      toast.success('Account deletion initiated. You will receive confirmation shortly.');
      setShowDeleteConfirm(false);
      
      // Redirect to goodbye page
      window.location.href = '/';
    } catch (error) {
      console.error('Failed to delete account:', error);
      toast.error('Failed to initiate account deletion');
    } finally {
      setLoading(false);
    }
  };

  const renderDataCollectionSettings = () => (
    <Collapsible 
      open={expandedSections.includes('dataCollection')}
      onOpenChange={() => toggleSection('dataCollection')}
    >
      <CollapsibleTrigger asChild>
        <div className="flex items-center justify-between p-4 glassmorphism-panel rounded-lg cursor-pointer hover:bg-primary/5">
          <div className="flex items-center gap-3">
            <Database className="w-5 h-5 text-primary" />
            <div>
              <h3 className="font-medium">Data Collection</h3>
              <p className="text-sm text-muted-foreground">Control what data we collect</p>
            </div>
          </div>
          {expandedSections.includes('dataCollection') ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
        </div>
      </CollapsibleTrigger>
      <CollapsibleContent className="space-y-4 mt-4">
        {Object.entries(privacySettings.dataCollection).map(([key, enabled]) => (
          <div key={key} className="flex items-center justify-between p-3 glassmorphism-panel rounded-lg">
            <div>
              <Label htmlFor={`data-${key}`} className="font-medium capitalize">
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </Label>
              <p className="text-sm text-muted-foreground">
                {getDataCollectionDescription(key)}
              </p>
            </div>
            <Switch
              id={`data-${key}`}
              checked={enabled}
              onCheckedChange={(checked) => updateNestedSetting('dataCollection', key, checked)}
            />
          </div>
        ))}
      </CollapsibleContent>
    </Collapsible>
  );

  const renderAIFeaturesSettings = () => (
    <Collapsible 
      open={expandedSections.includes('aiFeatures')}
      onOpenChange={() => toggleSection('aiFeatures')}
    >
      <CollapsibleTrigger asChild>
        <div className="flex items-center justify-between p-4 glassmorphism-panel rounded-lg cursor-pointer hover:bg-primary/5">
          <div className="flex items-center gap-3">
            <Brain className="w-5 h-5 text-primary" />
            <div>
              <h3 className="font-medium">AI Features</h3>
              <p className="text-sm text-muted-foreground">Control AI-powered functionality</p>
            </div>
          </div>
          {expandedSections.includes('aiFeatures') ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
        </div>
      </CollapsibleTrigger>
      <CollapsibleContent className="space-y-4 mt-4">
        {Object.entries(privacySettings.aiFeatures).map(([key, enabled]) => (
          <div key={key} className="flex items-center justify-between p-3 glassmorphism-panel rounded-lg">
            <div>
              <Label htmlFor={`ai-${key}`} className="font-medium capitalize">
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </Label>
              <p className="text-sm text-muted-foreground">
                {getAIFeatureDescription(key)}
              </p>
            </div>
            <Switch
              id={`ai-${key}`}
              checked={enabled}
              onCheckedChange={(checked) => updateNestedSetting('aiFeatures', key, checked)}
            />
          </div>
        ))}
      </CollapsibleContent>
    </Collapsible>
  );

  const renderDataSharingSettings = () => (
    <Collapsible 
      open={expandedSections.includes('dataSharing')}
      onOpenChange={() => toggleSection('dataSharing')}
    >
      <CollapsibleTrigger asChild>
        <div className="flex items-center justify-between p-4 glassmorphism-panel rounded-lg cursor-pointer hover:bg-primary/5">
          <div className="flex items-center gap-3">
            <Users className="w-5 h-5 text-primary" />
            <div>
              <h3 className="font-medium">Data Sharing</h3>
              <p className="text-sm text-muted-foreground">Control how your data is shared</p>
            </div>
          </div>
          {expandedSections.includes('dataSharing') ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
        </div>
      </CollapsibleTrigger>
      <CollapsibleContent className="space-y-4 mt-4">
        {Object.entries(privacySettings.dataSharing).map(([key, enabled]) => (
          <div key={key} className="flex items-center justify-between p-3 glassmorphism-panel rounded-lg">
            <div>
              <Label htmlFor={`sharing-${key}`} className="font-medium capitalize">
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </Label>
              <p className="text-sm text-muted-foreground">
                {getDataSharingDescription(key)}
              </p>
            </div>
            <Switch
              id={`sharing-${key}`}
              checked={enabled}
              onCheckedChange={(checked) => updateNestedSetting('dataSharing', key, checked)}
            />
          </div>
        ))}
      </CollapsibleContent>
    </Collapsible>
  );

  const renderDataRetentionSettings = () => (
    <Collapsible 
      open={expandedSections.includes('dataRetention')}
      onOpenChange={() => toggleSection('dataRetention')}
    >
      <CollapsibleTrigger asChild>
        <div className="flex items-center justify-between p-4 glassmorphism-panel rounded-lg cursor-pointer hover:bg-primary/5">
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-primary" />
            <div>
              <h3 className="font-medium">Data Retention</h3>
              <p className="text-sm text-muted-foreground">Control how long data is kept</p>
            </div>
          </div>
          {expandedSections.includes('dataRetention') ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
        </div>
      </CollapsibleTrigger>
      <CollapsibleContent className="space-y-4 mt-4">
        {Object.entries(privacySettings.dataRetention).map(([key, value]) => (
          <div key={key} className="flex items-center justify-between p-3 glassmorphism-panel rounded-lg">
            <div className="flex-1">
              <Label htmlFor={`retention-${key}`} className="font-medium capitalize">
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </Label>
              <p className="text-sm text-muted-foreground">
                {getDataRetentionDescription(key)}
              </p>
            </div>
            <Select
              value={value}
              onValueChange={(newValue) => updateNestedSetting('dataRetention', key, newValue)}
            >
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="forever">Forever</SelectItem>
                <SelectItem value="1year">1 Year</SelectItem>
                <SelectItem value="6months">6 Months</SelectItem>
                <SelectItem value="3months">3 Months</SelectItem>
                {key === 'deletedItems' && <SelectItem value="30days">30 Days</SelectItem>}
              </SelectContent>
            </Select>
          </div>
        ))}
      </CollapsibleContent>
    </Collapsible>
  );

  const renderConsentHistory = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Consent History</h3>
        <Badge variant="secondary">{consentHistory.length} records</Badge>
      </div>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {consentHistory.map((record) => (
          <div key={record.id} className="p-4 glassmorphism-panel rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium capitalize">{record.category.replace('_', ' ')}</h4>
              <div className="flex items-center gap-2">
                {record.granted ? (
                  <CheckCircle className="w-4 h-4 text-green-400" />
                ) : (
                  <X className="w-4 h-4 text-red-400" />
                )}
                <span className="text-sm text-muted-foreground">
                  {record.granted ? 'Granted' : 'Denied'}
                </span>
              </div>
            </div>
            <p className="text-sm text-muted-foreground mb-2">{record.details}</p>
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Version {record.version}</span>
              <span>{new Date(record.timestamp).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAuditLog = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Privacy Audit Log</h3>
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{auditLog.length} entries</Badge>
          <Button variant="outline" size="sm" onClick={loadAuditLog}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {auditLog.map((entry) => (
          <div key={entry.id} className="p-4 glassmorphism-panel rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                {getCategoryIcon(entry.category)}
                <h4 className="font-medium">{entry.action.replace('_', ' ')}</h4>
                {entry.automated && (
                  <Badge variant="outline" className="text-xs">Auto</Badge>
                )}
              </div>
              <span className="text-sm text-muted-foreground">
                {new Date(entry.timestamp).toLocaleString()}
              </span>
            </div>
            <p className="text-sm text-muted-foreground mb-2">{entry.details}</p>
            <div className="flex items-center justify-between text-xs">
              <div className="flex gap-1">
                {entry.dataTypes.map((type) => (
                  <Badge key={type} variant="secondary" className="text-xs">
                    {type}
                  </Badge>
                ))}
              </div>
              <span className="text-muted-foreground">Purpose: {entry.purpose}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className={`w-full max-w-4xl mx-auto space-y-6 ${className}`}>
      {/* Privacy Score Header */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-6 h-6 text-primary" />
              <div>
                <CardTitle>Privacy Controls</CardTitle>
                <p className="text-muted-foreground text-sm">
                  Manage your data privacy and AI feature permissions
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-primary">{getPrivacyScore()}%</div>
              <div className="text-sm text-muted-foreground">Privacy Score</div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Progress value={getPrivacyScore()} className="h-2" />
          <p className="text-sm text-muted-foreground mt-2">
            Higher scores indicate more restrictive privacy settings
          </p>
        </CardContent>
      </Card>

      {/* Privacy Controls Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4 glassmorphism-panel">
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
          <TabsTrigger value="retention">Retention</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
          <TabsTrigger value="account">Account</TabsTrigger>
        </TabsList>

        {/* Permissions Tab */}
        <TabsContent value="permissions" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardContent className="p-6 space-y-6">
              {renderDataCollectionSettings()}
              {renderAIFeaturesSettings()}
              {renderDataSharingSettings()}
              
              <div className="flex justify-end">
                <Button onClick={savePrivacySettings} disabled={loading}>
                  {loading ? (
                    <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full mr-2" />
                  ) : (
                    <Save className="w-4 h-4 mr-2" />
                  )}
                  Save Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Retention Tab */}
        <TabsContent value="retention" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardContent className="p-6 space-y-6">
              {renderDataRetentionSettings()}
              
              <Alert>
                <Info className="w-4 h-4" />
                <AlertDescription>
                  Data retention settings determine how long different types of data are stored. 
                  Shorter retention periods enhance privacy but may limit some features.
                </AlertDescription>
              </Alert>
              
              <div className="flex justify-end">
                <Button onClick={savePrivacySettings} disabled={loading}>
                  {loading ? (
                    <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full mr-2" />
                  ) : (
                    <Save className="w-4 h-4 mr-2" />
                  )}
                  Save Retention Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="glassmorphism-card">
              <CardContent className="p-6">
                {renderConsentHistory()}
              </CardContent>
            </Card>
            
            <Card className="glassmorphism-card">
              <CardContent className="p-6">
                <Button 
                  variant="outline" 
                  onClick={() => setShowAuditLog(true)}
                  className="w-full"
                >
                  <History className="w-4 h-4 mr-2" />
                  View Full Audit Log
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Account Tab */}
        <TabsContent value="account" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Data Export */}
            <Card className="glassmorphism-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Download className="w-5 h-5" />
                  Export Data
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground text-sm">
                  Download all your data in a portable format. This includes your profile, 
                  tasks, projects, and all associated data.
                </p>
                <Button 
                  onClick={() => setShowExportModal(true)}
                  className="w-full"
                  variant="outline"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export My Data
                </Button>
              </CardContent>
            </Card>

            {/* Account Deletion */}
            <Card className="glassmorphism-card border-red-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-400">
                  <Trash2 className="w-5 h-5" />
                  Delete Account
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert>
                  <AlertTriangle className="w-4 h-4" />
                  <AlertDescription>
                    This action cannot be undone. All your data will be permanently deleted.
                  </AlertDescription>
                </Alert>
                <Button 
                  onClick={() => setShowDeleteConfirm(true)}
                  variant="destructive"
                  className="w-full"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete My Account
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Modals */}
      
      {/* Data Export Confirmation */}
      <Dialog open={showExportModal} onOpenChange={setShowExportModal}>
        <DialogContent className="glassmorphism-card">
          <DialogHeader>
            <DialogTitle>Export Your Data</DialogTitle>
            <DialogDescription>
              This will create a comprehensive export of all your Aurum Life data.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Alert>
              <Info className="w-4 h-4" />
              <AlertDescription>
                The export will include your profile, pillars, areas, projects, tasks, 
                journal entries, and privacy settings. This may take a few moments.
              </AlertDescription>
            </Alert>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowExportModal(false)}>
                Cancel
              </Button>
              <Button onClick={exportUserData} disabled={loading}>
                {loading ? (
                  <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full mr-2" />
                ) : (
                  <Download className="w-4 h-4 mr-2" />
                )}
                Export Data
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Account Deletion Confirmation */}
      <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <DialogContent className="glassmorphism-card">
          <DialogHeader>
            <DialogTitle className="text-red-400">Delete Account</DialogTitle>
            <DialogDescription>
              This action cannot be undone. Are you absolutely sure?
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Alert>
              <AlertTriangle className="w-4 h-4" />
              <AlertDescription>
                Deleting your account will permanently remove all your data, including:
                pillars, areas, projects, tasks, journal entries, and settings.
              </AlertDescription>
            </Alert>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowDeleteConfirm(false)}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={deleteAccount} disabled={loading}>
                {loading ? (
                  <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full mr-2" />
                ) : (
                  <Trash2 className="w-4 h-4 mr-2" />
                )}
                Yes, Delete My Account
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Audit Log Modal */}
      <Dialog open={showAuditLog} onOpenChange={setShowAuditLog}>
        <DialogContent className="glassmorphism-card max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Privacy Audit Log</DialogTitle>
            <DialogDescription>
              Complete log of all privacy-related actions and data processing
            </DialogDescription>
          </DialogHeader>
          <div className="overflow-y-auto">
            {renderAuditLog()}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Helper functions
const getDataCollectionDescription = (key: string): string => {
  const descriptions: Record<string, string> = {
    analytics: 'Usage patterns and feature interactions',
    usage: 'How you use different features and sections',
    performance: 'App performance and loading times',
    errors: 'Error reports to improve stability',
    interactions: 'Detailed click and interaction tracking'
  };
  return descriptions[key] || 'Data collection setting';
};

const getAIFeatureDescription = (key: string): string => {
  const descriptions: Record<string, string> = {
    smartSuggestions: 'AI-powered recommendations for tasks and goals',
    productivityInsights: 'Analysis of your productivity patterns',
    goalRecommendations: 'Personalized goal suggestions',
    habitTracking: 'AI learns and suggests habit improvements',
    timeBlocking: 'Automatic schedule optimization',
    semanticSearch: 'AI-enhanced search across your content',
    autoTagging: 'Automatic categorization of tasks and notes',
    contentAnalysis: 'AI analysis of journal entries and notes'
  };
  return descriptions[key] || 'AI feature setting';
};

const getDataSharingDescription = (key: string): string => {
  const descriptions: Record<string, string> = {
    anonymizedUsage: 'Share anonymous usage statistics',
    productImprovement: 'Use your data to improve Aurum Life',
    researchParticipation: 'Participate in privacy-preserving research',
    marketingCommunications: 'Receive product updates and tips',
    thirdPartyIntegrations: 'Share data with connected third-party services'
  };
  return descriptions[key] || 'Data sharing setting';
};

const getDataRetentionDescription = (key: string): string => {
  const descriptions: Record<string, string> = {
    activityLogs: 'How long to keep logs of your actions',
    analyticsData: 'Retention period for usage analytics',
    aiInsights: 'How long to store AI-generated insights',
    deletedItems: 'How long deleted items remain recoverable'
  };
  return descriptions[key] || 'Data retention setting';
};

const getCategoryIcon = (category: string) => {
  const icons: Record<string, React.ReactNode> = {
    data_access: <Eye className="w-4 h-4 text-blue-400" />,
    ai_processing: <Brain className="w-4 h-4 text-purple-400" />,
    data_export: <Download className="w-4 h-4 text-green-400" />,
    privacy_change: <Shield className="w-4 h-4 text-yellow-400" />,
    consent_update: <FileText className="w-4 h-4 text-orange-400" />
  };
  return icons[category] || <Info className="w-4 h-4 text-gray-400" />;
};

export default GranularPrivacyControls;