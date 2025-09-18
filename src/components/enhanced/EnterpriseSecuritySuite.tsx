import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Switch } from '../ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { 
  Shield,
  Lock,
  Unlock,
  Key,
  Eye,
  EyeOff,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Settings,
  Download,
  Upload,
  Database,
  Network,
  Fingerprint,
  Smartphone,
  Globe,
  FileText,
  Users,
  Activity,
  BarChart3,
  Zap,
  Bell,
  RefreshCw,
  Search,
  Filter,
  Calendar,
  MapPin,
  Monitor,
  Wifi,
  Server,
  HardDrive,
  Cpu
} from 'lucide-react';

interface SecurityEvent {
  id: string;
  type: 'login' | 'data_access' | 'export' | 'permission_change' | 'security_scan' | 'breach_attempt';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  timestamp: Date;
  user?: string;
  location?: string;
  ipAddress?: string;
  device?: string;
  resolved: boolean;
  actions: SecurityAction[];
}

interface SecurityAction {
  id: string;
  type: 'block' | 'alert' | 'log' | 'escalate' | 'require_auth';
  description: string;
  automated: boolean;
  executed: boolean;
}

interface ComplianceStandard {
  id: string;
  name: string;
  description: string;
  compliance: number; // 0-100
  requirements: ComplianceRequirement[];
  lastAudit: Date;
  nextAudit: Date;
  status: 'compliant' | 'warning' | 'non_compliant';
}

interface ComplianceRequirement {
  id: string;
  title: string;
  description: string;
  status: 'met' | 'partial' | 'not_met';
  importance: 'low' | 'medium' | 'high' | 'critical';
  lastCheck: Date;
}

interface SecurityMetric {
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  status: 'good' | 'warning' | 'critical';
}

interface AccessControl {
  id: string;
  user: string;
  role: 'admin' | 'user' | 'viewer' | 'auditor';
  permissions: string[];
  lastAccess: Date;
  active: boolean;
  mfaEnabled: boolean;
  sessionTimeout: number; // minutes
}

export default function EnterpriseSecuritySuite() {
  const [activeTab, setActiveTab] = useState('overview');
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [complianceStandards, setComplianceStandards] = useState<ComplianceStandard[]>([]);
  const [securityMetrics, setSecurityMetrics] = useState<SecurityMetric[]>([]);
  const [accessControls, setAccessControls] = useState<AccessControl[]>([]);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [encryptionEnabled, setEncryptionEnabled] = useState(true);
  const [auditLoggingEnabled, setAuditLoggingEnabled] = useState(true);

  // Sample data initialization
  useEffect(() => {
    const sampleEvents: SecurityEvent[] = [
      {
        id: '1',
        type: 'login',
        severity: 'medium',
        title: 'Unusual Login Location',
        description: 'Login attempt from new geographical location detected',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        user: 'sarah.chen@company.com',
        location: 'San Francisco, CA',
        ipAddress: '192.168.1.100',
        device: 'MacBook Pro',
        resolved: false,
        actions: [
          { id: 'a1', type: 'require_auth', description: 'Require additional authentication', automated: true, executed: true },
          { id: 'a2', type: 'alert', description: 'Alert security team', automated: true, executed: true }
        ]
      },
      {
        id: '2',
        type: 'data_access',
        severity: 'high',
        title: 'Bulk Data Export',
        description: 'Large volume of sensitive data accessed and exported',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
        user: 'mike.rodriguez@company.com',
        location: 'New York, NY',
        ipAddress: '192.168.1.150',
        device: 'Windows PC',
        resolved: true,
        actions: [
          { id: 'a3', type: 'log', description: 'Log detailed access information', automated: true, executed: true },
          { id: 'a4', type: 'escalate', description: 'Escalate to security team', automated: false, executed: true }
        ]
      },
      {
        id: '3',
        type: 'security_scan',
        severity: 'low',
        title: 'Routine Security Scan',
        description: 'Automated security vulnerability scan completed successfully',
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
        resolved: true,
        actions: [
          { id: 'a5', type: 'log', description: 'Log scan results', automated: true, executed: true }
        ]
      },
      {
        id: '4',
        type: 'breach_attempt',
        severity: 'critical',
        title: 'Potential Breach Attempt',
        description: 'Multiple failed login attempts from suspicious IP addresses',
        timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000),
        location: 'Unknown',
        ipAddress: '203.0.113.0',
        device: 'Unknown',
        resolved: true,
        actions: [
          { id: 'a6', type: 'block', description: 'Block suspicious IP addresses', automated: true, executed: true },
          { id: 'a7', type: 'alert', description: 'Immediate security alert', automated: true, executed: true },
          { id: 'a8', type: 'escalate', description: 'Escalate to CISO', automated: false, executed: true }
        ]
      }
    ];

    const sampleCompliance: ComplianceStandard[] = [
      {
        id: '1',
        name: 'SOC 2 Type II',
        description: 'Service Organization Control 2 Type II compliance for security, availability, and confidentiality',
        compliance: 94,
        lastAudit: new Date('2024-01-15'),
        nextAudit: new Date('2024-07-15'),
        status: 'compliant',
        requirements: [
          { id: 'r1', title: 'Access Controls', description: 'Implement proper user access management', status: 'met', importance: 'critical', lastCheck: new Date() },
          { id: 'r2', title: 'Data Encryption', description: 'Encrypt data at rest and in transit', status: 'met', importance: 'critical', lastCheck: new Date() },
          { id: 'r3', title: 'Audit Logging', description: 'Maintain comprehensive audit logs', status: 'met', importance: 'high', lastCheck: new Date() },
          { id: 'r4', title: 'Incident Response', description: 'Document incident response procedures', status: 'partial', importance: 'high', lastCheck: new Date() }
        ]
      },
      {
        id: '2',
        name: 'GDPR',
        description: 'General Data Protection Regulation compliance for data privacy and protection',
        compliance: 89,
        lastAudit: new Date('2024-02-01'),
        nextAudit: new Date('2024-08-01'),
        status: 'compliant',
        requirements: [
          { id: 'r5', title: 'Data Subject Rights', description: 'Implement data subject access rights', status: 'met', importance: 'critical', lastCheck: new Date() },
          { id: 'r6', title: 'Consent Management', description: 'Proper consent collection and management', status: 'met', importance: 'critical', lastCheck: new Date() },
          { id: 'r7', title: 'Data Breach Notification', description: '72-hour breach notification process', status: 'met', importance: 'critical', lastCheck: new Date() },
          { id: 'r8', title: 'Privacy by Design', description: 'Implement privacy by design principles', status: 'partial', importance: 'medium', lastCheck: new Date() }
        ]
      },
      {
        id: '3',
        name: 'ISO 27001',
        description: 'International standard for information security management systems',
        compliance: 76,
        lastAudit: new Date('2024-01-01'),
        nextAudit: new Date('2024-12-31'),
        status: 'warning',
        requirements: [
          { id: 'r9', title: 'Risk Assessment', description: 'Regular security risk assessments', status: 'met', importance: 'critical', lastCheck: new Date() },
          { id: 'r10', title: 'Security Policies', description: 'Documented security policies and procedures', status: 'met', importance: 'high', lastCheck: new Date() },
          { id: 'r11', title: 'Employee Training', description: 'Security awareness training program', status: 'not_met', importance: 'medium', lastCheck: new Date() },
          { id: 'r12', title: 'Vendor Management', description: 'Third-party vendor security assessments', status: 'partial', importance: 'high', lastCheck: new Date() }
        ]
      }
    ];

    const sampleMetrics: SecurityMetric[] = [
      { name: 'Security Score', value: 87, unit: '%', trend: 'up', status: 'good' },
      { name: 'Failed Login Attempts', value: 23, unit: 'attempts', trend: 'down', status: 'good' },
      { name: 'Data Encryption Coverage', value: 99.8, unit: '%', trend: 'stable', status: 'good' },
      { name: 'Vulnerability Count', value: 2, unit: 'issues', trend: 'down', status: 'warning' },
      { name: 'Compliance Rating', value: 86, unit: '%', trend: 'up', status: 'good' },
      { name: 'Incident Response Time', value: 12, unit: 'minutes', trend: 'down', status: 'good' }
    ];

    const sampleAccessControls: AccessControl[] = [
      {
        id: '1',
        user: 'sarah.chen@company.com',
        role: 'admin',
        permissions: ['read', 'write', 'delete', 'admin', 'audit'],
        lastAccess: new Date(Date.now() - 30 * 60 * 1000),
        active: true,
        mfaEnabled: true,
        sessionTimeout: 480
      },
      {
        id: '2',
        user: 'mike.rodriguez@company.com',
        role: 'user',
        permissions: ['read', 'write'],
        lastAccess: new Date(Date.now() - 2 * 60 * 60 * 1000),
        active: true,
        mfaEnabled: true,
        sessionTimeout: 240
      },
      {
        id: '3',
        user: 'emma.thompson@company.com',
        role: 'viewer',
        permissions: ['read'],
        lastAccess: new Date(Date.now() - 24 * 60 * 60 * 1000),
        active: false,
        mfaEnabled: false,
        sessionTimeout: 120
      }
    ];

    setSecurityEvents(sampleEvents);
    setComplianceStandards(sampleCompliance);
    setSecurityMetrics(sampleMetrics);
    setAccessControls(sampleAccessControls);
  }, []);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <AlertTriangle className="h-4 w-4 text-red-400" />;
      case 'high': return <AlertTriangle className="h-4 w-4 text-orange-400" />;
      case 'medium': return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
      case 'low': return <CheckCircle2 className="h-4 w-4 text-green-400" />;
      default: return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/20 text-red-300';
      case 'high': return 'bg-orange-500/20 text-orange-300';
      case 'medium': return 'bg-yellow-500/20 text-yellow-300';
      case 'low': return 'bg-green-500/20 text-green-300';
      default: return 'bg-gray-500/20 text-gray-300';
    }
  };

  const getComplianceColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'non_compliant': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getRequirementStatusColor = (status: string) => {
    switch (status) {
      case 'met': return 'bg-green-500/20 text-green-300';
      case 'partial': return 'bg-yellow-500/20 text-yellow-300';
      case 'not_met': return 'bg-red-500/20 text-red-300';
      default: return 'bg-gray-500/20 text-gray-300';
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin': return <Shield className="h-4 w-4 text-red-400" />;
      case 'user': return <Users className="h-4 w-4 text-blue-400" />;
      case 'viewer': return <Eye className="h-4 w-4 text-green-400" />;
      case 'auditor': return <FileText className="h-4 w-4 text-purple-400" />;
      default: return <Users className="h-4 w-4" />;
    }
  };

  const criticalEvents = securityEvents.filter(e => e.severity === 'critical' || e.severity === 'high').length;
  const unresolvedEvents = securityEvents.filter(e => !e.resolved).length;
  const averageCompliance = Math.round(complianceStandards.reduce((sum, c) => sum + c.compliance, 0) / complianceStandards.length);
  const activeUsers = accessControls.filter(a => a.active).length;

  const filteredEvents = selectedSeverity === 'all' 
    ? securityEvents 
    : securityEvents.filter(e => e.severity === selectedSeverity);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center space-x-3">
              <Shield className="h-8 w-8 text-primary" />
              <span>Enterprise Security</span>
            </h1>
            <p className="text-muted-foreground mt-1">
              Advanced security, compliance, and access management for organizations
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
            <Button>
              <Settings className="h-4 w-4 mr-2" />
              Security Settings
            </Button>
          </div>
        </div>

        {/* Security Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Critical Events</p>
                  <p className="text-2xl font-bold">{criticalEvents}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-red-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Unresolved</p>
                  <p className="text-2xl font-bold">{unresolvedEvents}</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Compliance</p>
                  <p className="text-2xl font-bold">{averageCompliance}%</p>
                </div>
                <FileText className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Users</p>
                  <p className="text-2xl font-bold">{activeUsers}</p>
                </div>
                <Users className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="events">Security Events</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="access">Access Control</TabsTrigger>
          <TabsTrigger value="encryption">Encryption</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Security Health Dashboard */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Security Health Dashboard</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {securityMetrics.map((metric, index) => (
                  <div key={index} className="glassmorphism-panel p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">{metric.name}</span>
                      <div className="flex items-center space-x-1">
                        {metric.trend === 'up' && <Activity className="h-3 w-3 text-green-400" />}
                        {metric.trend === 'down' && <Activity className="h-3 w-3 text-red-400 rotate-180" />}
                        {metric.trend === 'stable' && <Activity className="h-3 w-3 text-blue-400" />}
                        <span className={`text-sm font-bold ${
                          metric.status === 'good' ? 'text-green-400' :
                          metric.status === 'warning' ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {metric.value}{metric.unit}
                        </span>
                      </div>
                    </div>
                    <Progress 
                      value={metric.unit === '%' ? metric.value : Math.min(metric.value / 100 * 100, 100)} 
                      className="h-2" 
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Critical Events */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5" />
                <span>Recent Critical Events</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {securityEvents.filter(e => e.severity === 'critical' || e.severity === 'high').slice(0, 3).map((event) => (
                <div key={event.id} className="glassmorphism-panel p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      {getSeverityIcon(event.severity)}
                      <div>
                        <h4 className="font-semibold">{event.title}</h4>
                        <p className="text-sm text-muted-foreground">{event.description}</p>
                        <div className="flex items-center space-x-4 text-xs text-muted-foreground mt-2">
                          {event.user && <span>User: {event.user}</span>}
                          {event.location && <span>Location: {event.location}</span>}
                          <span>{event.timestamp.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getSeverityColor(event.severity)}>
                        {event.severity}
                      </Badge>
                      {event.resolved ? (
                        <CheckCircle2 className="h-4 w-4 text-green-400" />
                      ) : (
                        <Clock className="h-4 w-4 text-yellow-400" />
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="glassmorphism-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Lock className="h-5 w-5" />
                  <span>Encryption Status</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span>Data at Rest Encryption</span>
                  <Switch checked={encryptionEnabled} onCheckedChange={setEncryptionEnabled} />
                </div>
                <div className="flex items-center justify-between">
                  <span>Transit Encryption</span>
                  <Switch checked={true} disabled />
                </div>
                <div className="glassmorphism-panel p-3">
                  <div className="text-lg font-bold text-green-400">256-bit AES</div>
                  <div className="text-sm text-muted-foreground">Encryption Standard</div>
                </div>
              </CardContent>
            </Card>

            <Card className="glassmorphism-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="h-5 w-5" />
                  <span>Audit Logging</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span>Comprehensive Logging</span>
                  <Switch checked={auditLoggingEnabled} onCheckedChange={setAuditLoggingEnabled} />
                </div>
                <div className="flex items-center justify-between">
                  <span>Real-time Monitoring</span>
                  <Switch checked={true} disabled />
                </div>
                <div className="glassmorphism-panel p-3">
                  <div className="text-lg font-bold text-blue-400">99.9%</div>
                  <div className="text-sm text-muted-foreground">Log Retention</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="events" className="space-y-6">
          {/* Event Filters */}
          <div className="flex items-center space-x-4 glassmorphism-panel p-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4" />
              <span className="text-sm font-medium">Filter by Severity:</span>
            </div>
            <Select value={selectedSeverity} onValueChange={setSelectedSeverity}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Security Events List */}
          <div className="space-y-4">
            {filteredEvents.map((event) => (
              <Card key={event.id} className="glassmorphism-card">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-3">
                      {getSeverityIcon(event.severity)}
                      <div>
                        <h3 className="text-lg font-semibold">{event.title}</h3>
                        <p className="text-muted-foreground">{event.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getSeverityColor(event.severity)}>
                        {event.severity}
                      </Badge>
                      {event.resolved ? (
                        <Badge className="bg-green-500/20 text-green-300">Resolved</Badge>
                      ) : (
                        <Badge className="bg-yellow-500/20 text-yellow-300">Open</Badge>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4 text-sm">
                    {event.user && (
                      <div>
                        <span className="text-muted-foreground">User:</span>
                        <div className="font-medium">{event.user}</div>
                      </div>
                    )}
                    {event.location && (
                      <div>
                        <span className="text-muted-foreground">Location:</span>
                        <div className="font-medium">{event.location}</div>
                      </div>
                    )}
                    {event.ipAddress && (
                      <div>
                        <span className="text-muted-foreground">IP Address:</span>
                        <div className="font-medium">{event.ipAddress}</div>
                      </div>
                    )}
                    <div>
                      <span className="text-muted-foreground">Timestamp:</span>
                      <div className="font-medium">{event.timestamp.toLocaleString()}</div>
                    </div>
                  </div>

                  {event.actions.length > 0 && (
                    <div className="space-y-2">
                      <span className="text-sm font-medium">Actions Taken:</span>
                      <div className="space-y-1">
                        {event.actions.map((action) => (
                          <div key={action.id} className="flex items-center justify-between glassmorphism-panel p-2">
                            <span className="text-sm">{action.description}</span>
                            <div className="flex items-center space-x-2">
                              {action.automated && (
                                <Badge variant="outline" className="text-xs">Automated</Badge>
                              )}
                              {action.executed ? (
                                <CheckCircle2 className="h-4 w-4 text-green-400" />
                              ) : (
                                <Clock className="h-4 w-4 text-yellow-400" />
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="compliance" className="space-y-6">
          <div className="space-y-6">
            {complianceStandards.map((standard) => (
              <Card key={standard.id} className="glassmorphism-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{standard.name}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge className={
                        standard.status === 'compliant' ? 'bg-green-500/20 text-green-300' :
                        standard.status === 'warning' ? 'bg-yellow-500/20 text-yellow-300' :
                        'bg-red-500/20 text-red-300'
                      }>
                        {standard.status}
                      </Badge>
                      <span className={`font-bold ${getComplianceColor(standard.status)}`}>
                        {standard.compliance}%
                      </span>
                    </div>
                  </div>
                  <CardDescription>{standard.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Compliance Progress</span>
                      <span>{standard.compliance}%</span>
                    </div>
                    <Progress value={standard.compliance} className="h-3" />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Last Audit:</span>
                      <div className="font-medium">{standard.lastAudit.toLocaleDateString()}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Next Audit:</span>
                      <div className="font-medium">{standard.nextAudit.toLocaleDateString()}</div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <span className="text-sm font-medium">Requirements Status</span>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {standard.requirements.map((req) => (
                        <div key={req.id} className="glassmorphism-panel p-3">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium">{req.title}</span>
                            <Badge className={getRequirementStatusColor(req.status)}>
                              {req.status.replace('_', ' ')}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground">{req.description}</p>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-muted-foreground capitalize">
                              {req.importance} importance
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {req.lastCheck.toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="access" className="space-y-6">
          <div className="space-y-4">
            {accessControls.map((access) => (
              <Card key={access.id} className="glassmorphism-card">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      {getRoleIcon(access.role)}
                      <div>
                        <h3 className="font-semibold">{access.user}</h3>
                        <p className="text-sm text-muted-foreground capitalize">{access.role}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {access.active ? (
                        <Badge className="bg-green-500/20 text-green-300">Active</Badge>
                      ) : (
                        <Badge className="bg-gray-500/20 text-gray-300">Inactive</Badge>
                      )}
                      {access.mfaEnabled ? (
                        <Fingerprint className="h-4 w-4 text-green-400" />
                      ) : (
                        <Fingerprint className="h-4 w-4 text-red-400" />
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Last Access:</span>
                      <div className="font-medium">{access.lastAccess.toLocaleString()}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Session Timeout:</span>
                      <div className="font-medium">{access.sessionTimeout} minutes</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">MFA Status:</span>
                      <div className={`font-medium ${access.mfaEnabled ? 'text-green-400' : 'text-red-400'}`}>
                        {access.mfaEnabled ? 'Enabled' : 'Disabled'}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <span className="text-sm font-medium">Permissions</span>
                    <div className="flex flex-wrap gap-2">
                      {access.permissions.map((permission) => (
                        <Badge key={permission} variant="outline" className="text-xs">
                          {permission}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="encryption" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Lock className="h-5 w-5" />
                <span>Encryption Configuration</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-semibold">Data at Rest</h4>
                  <div className="glassmorphism-panel p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span>AES-256 Encryption</span>
                      <CheckCircle2 className="h-4 w-4 text-green-400" />
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Key Rotation</span>
                      <CheckCircle2 className="h-4 w-4 text-green-400" />
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Hardware Security Module</span>
                      <CheckCircle2 className="h-4 w-4 text-green-400" />
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-semibold">Data in Transit</h4>
                  <div className="glassmorphism-panel p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span>TLS 1.3</span>
                      <CheckCircle2 className="h-4 w-4 text-green-400" />
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Certificate Pinning</span>
                      <CheckCircle2 className="h-4 w-4 text-green-400" />
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Perfect Forward Secrecy</span>
                      <CheckCircle2 className="h-4 w-4 text-green-400" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold">Key Management</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="glassmorphism-panel p-4 text-center">
                    <div className="text-2xl font-bold text-primary">256-bit</div>
                    <div className="text-sm text-muted-foreground">Encryption Strength</div>
                  </div>
                  <div className="glassmorphism-panel p-4 text-center">
                    <div className="text-2xl font-bold text-green-400">90 days</div>
                    <div className="text-sm text-muted-foreground">Key Rotation</div>
                  </div>
                  <div className="glassmorphism-panel p-4 text-center">
                    <div className="text-2xl font-bold text-blue-400">HSM</div>
                    <div className="text-sm text-muted-foreground">Key Storage</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="monitoring" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Monitor className="h-5 w-5" />
                <span>Security Monitoring</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="glassmorphism-panel p-4 text-center">
                  <Server className="h-8 w-8 text-primary mx-auto mb-2" />
                  <div className="text-lg font-bold">99.9%</div>
                  <div className="text-sm text-muted-foreground">Uptime</div>
                </div>
                <div className="glassmorphism-panel p-4 text-center">
                  <Network className="h-8 w-8 text-green-400 mx-auto mb-2" />
                  <div className="text-lg font-bold">24/7</div>
                  <div className="text-sm text-muted-foreground">Monitoring</div>
                </div>
                <div className="glassmorphism-panel p-4 text-center">
                  <Bell className="h-8 w-8 text-yellow-400 mx-auto mb-2" />
                  <div className="text-lg font-bold">12 min</div>
                  <div className="text-sm text-muted-foreground">Alert Response</div>
                </div>
                <div className="glassmorphism-panel p-4 text-center">
                  <Activity className="h-8 w-8 text-blue-400 mx-auto mb-2" />
                  <div className="text-lg font-bold">Real-time</div>
                  <div className="text-sm text-muted-foreground">Analysis</div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold">Monitoring Capabilities</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="glassmorphism-panel p-4">
                    <h5 className="font-medium mb-3">Infrastructure Monitoring</h5>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="h-4 w-4 text-green-400" />
                        <span>Server health and performance</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="h-4 w-4 text-green-400" />
                        <span>Network traffic analysis</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="h-4 w-4 text-green-400" />
                        <span>Database performance</span>
                      </div>
                    </div>
                  </div>

                  <div className="glassmorphism-panel p-4">
                    <h5 className="font-medium mb-3">Security Monitoring</h5>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="h-4 w-4 text-green-400" />
                        <span>Intrusion detection</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="h-4 w-4 text-green-400" />
                        <span>Anomaly detection</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="h-4 w-4 text-green-400" />
                        <span>Behavioral analysis</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}