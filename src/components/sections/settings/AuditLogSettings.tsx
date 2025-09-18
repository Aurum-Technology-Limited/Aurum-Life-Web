import React, { useState, useEffect } from 'react';
import { Download, Eye, EyeOff, Shield, Clock, Database, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Separator } from '../../ui/separator';
import { Switch } from '../../ui/switch';
import { Label } from '../../ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../ui/table';
import { ScrollArea } from '../../ui/scroll-area';
import { toast } from 'sonner@2.0.3';
import auditLogger, { AuditLogEntry, DataUsageStats } from '../../../services/auditLoggingService';

const AuditLogSettings: React.FC = () => {
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [dataStats, setDataStats] = useState<DataUsageStats | null>(null);
  const [showSensitiveData, setShowSensitiveData] = useState(false);
  const [timeRange, setTimeRange] = useState('7'); // days
  const [componentFilter, setComponentFilter] = useState('all');
  const [privacyFilter, setPrivacyFilter] = useState('all');
  const [autoCleanupEnabled, setAutoCleanupEnabled] = useState(true);

  useEffect(() => {
    loadAuditData();
  }, [timeRange, componentFilter, privacyFilter]);

  const loadAuditData = () => {
    const days = parseInt(timeRange);
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const logs = auditLogger.getAuditLogs(
      startDate,
      undefined,
      componentFilter === 'all' ? undefined : componentFilter,
      privacyFilter === 'all' ? undefined : (privacyFilter as any)
    );

    setAuditLogs(logs);
    setDataStats(auditLogger.getDataUsageStats(days));
  };

  const handleExportLogs = (format: 'json' | 'csv') => {
    try {
      const exportData = auditLogger.exportAuditLogs(format);
      const blob = new Blob([exportData], { 
        type: format === 'json' ? 'application/json' : 'text/csv' 
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `aurum-audit-logs-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success(`Audit logs exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Failed to export audit logs');
    }
  };

  const handleCleanupExpiredLogs = () => {
    const deletedCount = auditLogger.cleanupExpiredLogs();
    toast.success(`Cleaned up ${deletedCount} expired log entries`);
    loadAuditData();
  };

  const getPrivacyLevelColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-green-500/20 text-green-400';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400';
      case 'high': return 'bg-orange-500/20 text-orange-400';
      case 'critical': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getDataTypeIcon = (dataType: string) => {
    switch (dataType) {
      case 'personal': return <Shield className="w-4 h-4" />;
      case 'sensitive': return <AlertTriangle className="w-4 h-4" />;
      case 'ai_generated': return <Database className="w-4 h-4" />;
      default: return <Eye className="w-4 h-4" />;
    }
  };

  const formatMetadata = (metadata: Record<string, any>) => {
    const filtered = { ...metadata };
    if (!showSensitiveData) {
      delete filtered.userAgent;
      delete filtered.url;
    }
    return JSON.stringify(filtered, null, 2);
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">AI Data Usage & Audit Logs</h3>
        <p className="text-sm text-muted-foreground mt-1">
          Track all AI interactions and data processing for complete transparency
        </p>
      </div>

      {/* Data Usage Statistics */}
      {dataStats && (
        <Card className="glassmorphism-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              Data Usage Summary
            </CardTitle>
            <CardDescription>
              Last {timeRange} days of AI and data processing activity
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">{dataStats.totalAIInteractions}</div>
                <div className="text-sm text-muted-foreground">AI Interactions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">{dataStats.dataProcessed.personal}</div>
                <div className="text-sm text-muted-foreground">Personal Data</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-400">{dataStats.dataProcessed.sensitive}</div>
                <div className="text-sm text-muted-foreground">Sensitive Data</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">{dataStats.retentionSummary.activeRetention}</div>
                <div className="text-sm text-muted-foreground">Active Logs</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="logs" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="logs">Audit Logs</TabsTrigger>
          <TabsTrigger value="settings">Log Settings</TabsTrigger>
          <TabsTrigger value="export">Export & Cleanup</TabsTrigger>
        </TabsList>

        <TabsContent value="logs" className="space-y-4">
          {/* Filters */}
          <Card className="glassmorphism-card">
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <Label htmlFor="timeRange">Time Range</Label>
                  <Select value={timeRange} onValueChange={setTimeRange}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Last 24 hours</SelectItem>
                      <SelectItem value="7">Last 7 days</SelectItem>
                      <SelectItem value="30">Last 30 days</SelectItem>
                      <SelectItem value="90">Last 3 months</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="componentFilter">Component</Label>
                  <Select value={componentFilter} onValueChange={setComponentFilter}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Components</SelectItem>
                      <SelectItem value="ai_service_openai">OpenAI Service</SelectItem>
                      <SelectItem value="ai_service_gemini">Gemini Service</SelectItem>
                      <SelectItem value="quick_capture">Quick Capture</SelectItem>
                      <SelectItem value="privacy_controls">Privacy Controls</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="privacyFilter">Privacy Level</Label>
                  <Select value={privacyFilter} onValueChange={setPrivacyFilter}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Levels</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-end">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="showSensitive"
                      checked={showSensitiveData}
                      onCheckedChange={setShowSensitiveData}
                    />
                    <Label htmlFor="showSensitive">Show Sensitive Data</Label>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Logs Table */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle>Audit Log Entries ({auditLogs.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead>Component</TableHead>
                      <TableHead>Data Type</TableHead>
                      <TableHead>Privacy Level</TableHead>
                      <TableHead>Consent</TableHead>
                      <TableHead>Details</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {auditLogs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell className="font-mono text-xs">
                          {log.timestamp.toLocaleString()}
                        </TableCell>
                        <TableCell className="font-medium">
                          {log.action.replace(/_/g, ' ')}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getDataTypeIcon(log.dataType)}
                            {log.component}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className={getDataTypeIcon(log.dataType) ? 'bg-blue-500/20' : ''}>
                            {log.dataType}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={getPrivacyLevelColor(log.privacyLevel)}>
                            {log.privacyLevel}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {log.userConsent ? (
                            <Badge className="bg-green-500/20 text-green-400">Granted</Badge>
                          ) : (
                            <Badge className="bg-red-500/20 text-red-400">Revoked</Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="max-w-xs">
                            <div className="text-sm font-medium">{log.description}</div>
                            <div className="text-xs text-muted-foreground mt-1">{log.purpose}</div>
                            {showSensitiveData && (
                              <details className="mt-2">
                                <summary className="text-xs cursor-pointer text-primary">Metadata</summary>
                                <pre className="text-xs mt-1 p-2 bg-card rounded overflow-x-auto">
                                  {formatMetadata(log.metadata)}
                                </pre>
                              </details>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {auditLogs.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No audit logs found for the selected criteria
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle>Audit Log Configuration</CardTitle>
              <CardDescription>
                Configure how audit logs are collected and retained
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="autoCleanup">Automatic Cleanup</Label>
                  <p className="text-sm text-muted-foreground">
                    Automatically delete expired logs based on retention policy
                  </p>
                </div>
                <Switch
                  id="autoCleanup"
                  checked={autoCleanupEnabled}
                  onCheckedChange={setAutoCleanupEnabled}
                />
              </div>

              <Separator />

              <div>
                <h4 className="font-medium mb-3">Retention Periods</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Low Privacy Level</span>
                    <Badge>30 days</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Medium Privacy Level</span>
                    <Badge>90 days</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">High Privacy Level</span>
                    <Badge>180 days</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Critical Privacy Level</span>
                    <Badge>365 days</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="export" className="space-y-4">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle>Export & Data Management</CardTitle>
              <CardDescription>
                Export your audit logs or clean up old entries
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="font-medium mb-3">Export Audit Logs</h4>
                <p className="text-sm text-muted-foreground mb-4">
                  Download your complete audit log history for review or backup
                </p>
                <div className="flex gap-4">
                  <Button 
                    onClick={() => handleExportLogs('json')}
                    className="flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Export as JSON
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => handleExportLogs('csv')}
                    className="flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Export as CSV
                  </Button>
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="font-medium mb-3">Cleanup Operations</h4>
                <p className="text-sm text-muted-foreground mb-4">
                  Remove expired log entries to free up storage space
                </p>
                <Button 
                  variant="destructive" 
                  onClick={handleCleanupExpiredLogs}
                  className="flex items-center gap-2"
                >
                  <Clock className="w-4 h-4" />
                  Clean Up Expired Logs
                </Button>
              </div>

              {dataStats && (
                <>
                  <Separator />
                  <div>
                    <h4 className="font-medium mb-3">Storage Summary</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-card rounded-lg">
                        <div className="text-lg font-bold">{dataStats.retentionSummary.activeRetention}</div>
                        <div className="text-sm text-muted-foreground">Active Log Entries</div>
                      </div>
                      <div className="text-center p-4 bg-card rounded-lg">
                        <div className="text-lg font-bold text-orange-400">{dataStats.retentionSummary.toBeDeleted}</div>
                        <div className="text-sm text-muted-foreground">Ready for Cleanup</div>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AuditLogSettings;