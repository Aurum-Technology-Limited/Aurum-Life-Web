import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Switch } from '../ui/switch';
import { Slider } from '../ui/slider';
import { 
  Brain,
  Zap,
  Play,
  Pause,
  Settings,
  Plus,
  Trash2,
  Edit,
  TrendingUp,
  Clock,
  Target,
  BarChart3,
  Workflow,
  Bot,
  Lightbulb,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
  Star,
  Activity
} from 'lucide-react';

interface WorkflowRule {
  id: string;
  name: string;
  description: string;
  trigger: {
    type: 'schedule' | 'completion' | 'deadline' | 'energy' | 'context';
    conditions: any;
  };
  actions: WorkflowAction[];
  enabled: boolean;
  priority: number;
  learningScore: number;
  executionCount: number;
  successRate: number;
}

interface WorkflowAction {
  id: string;
  type: 'create_task' | 'reschedule' | 'prioritize' | 'notify' | 'analyze' | 'suggest';
  parameters: any;
  confidence: number;
}

interface AIInsight {
  id: string;
  type: 'pattern' | 'optimization' | 'prediction' | 'recommendation';
  title: string;
  description: string;
  confidence: number;
  impact: 'low' | 'medium' | 'high';
  actionable: boolean;
  createdAt: Date;
}

export default function AdvancedAIWorkflows() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [workflows, setWorkflows] = useState<WorkflowRule[]>([]);
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [isCreatingWorkflow, setIsCreatingWorkflow] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowRule | null>(null);

  // Sample workflows for demonstration
  useEffect(() => {
    const sampleWorkflows: WorkflowRule[] = [
      {
        id: '1',
        name: 'Smart Morning Routine',
        description: 'Automatically adjusts morning tasks based on energy levels and calendar',
        trigger: {
          type: 'schedule',
          conditions: { time: '06:00', days: ['mon', 'tue', 'wed', 'thu', 'fri'] }
        },
        actions: [
          {
            id: 'a1',
            type: 'analyze',
            parameters: { 
              target: 'energy_level',
              timeframe: 'last_7_days'
            },
            confidence: 0.92
          },
          {
            id: 'a2',
            type: 'create_task',
            parameters: {
              pillar: 'Health & Wellness',
              priority: 'dynamic',
              adaptToEnergy: true
            },
            confidence: 0.87
          }
        ],
        enabled: true,
        priority: 5,
        learningScore: 8.4,
        executionCount: 24,
        successRate: 0.91
      },
      {
        id: '2',
        name: 'Deadline Pressure Response',
        description: 'Automatically reprioritizes tasks when deadlines approach',
        trigger: {
          type: 'deadline',
          conditions: { daysUntil: 3, priority: 'high' }
        },
        actions: [
          {
            id: 'b1',
            type: 'prioritize',
            parameters: {
              boost: 2,
              clearNonEssential: true
            },
            confidence: 0.95
          },
          {
            id: 'b2',
            type: 'reschedule',
            parameters: {
              timeBlocks: 'longer',
              distractions: 'minimize'
            },
            confidence: 0.89
          }
        ],
        enabled: true,
        priority: 4,
        learningScore: 9.1,
        executionCount: 12,
        successRate: 0.94
      },
      {
        id: '3',
        name: 'Context Switch Optimizer',
        description: 'Groups similar tasks and minimizes context switching',
        trigger: {
          type: 'context',
          conditions: { similar_tasks: 3, time_gap: '< 2h' }
        },
        actions: [
          {
            id: 'c1',
            type: 'suggest',
            parameters: {
              grouping: 'by_context',
              optimization: 'time_blocking'
            },
            confidence: 0.82
          }
        ],
        enabled: true,
        priority: 3,
        learningScore: 7.8,
        executionCount: 31,
        successRate: 0.76
      }
    ];

    const sampleInsights: AIInsight[] = [
      {
        id: '1',
        type: 'pattern',
        title: 'High Productivity Pattern Detected',
        description: 'You consistently achieve 40% more on Tuesdays when you start with creative tasks',
        confidence: 0.89,
        impact: 'high',
        actionable: true,
        createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
      },
      {
        id: '2',
        type: 'optimization',
        title: 'Time Block Optimization Opportunity',
        description: 'Combining similar administrative tasks could save 3.2 hours per week',
        confidence: 0.76,
        impact: 'medium',
        actionable: true,
        createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
      },
      {
        id: '3',
        type: 'prediction',
        title: 'Goal Achievement Risk',
        description: 'Current pace suggests 15% risk of missing Q1 fitness goals',
        confidence: 0.84,
        impact: 'high',
        actionable: true,
        createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000)
      }
    ];

    setWorkflows(sampleWorkflows);
    setInsights(sampleInsights);
  }, []);

  const getWorkflowStatusColor = (workflow: WorkflowRule) => {
    if (!workflow.enabled) return 'bg-gray-500/20 text-gray-300';
    if (workflow.successRate > 0.9) return 'bg-green-500/20 text-green-300';
    if (workflow.successRate > 0.7) return 'bg-yellow-500/20 text-yellow-300';
    return 'bg-red-500/20 text-red-300';
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'pattern': return <TrendingUp className="h-5 w-5" />;
      case 'optimization': return <Zap className="h-5 w-5" />;
      case 'prediction': return <Brain className="h-5 w-5" />;
      case 'recommendation': return <Lightbulb className="h-5 w-5" />;
      default: return <Activity className="h-5 w-5" />;
    }
  };

  const totalExecutions = workflows.reduce((sum, w) => sum + w.executionCount, 0);
  const avgSuccessRate = workflows.reduce((sum, w) => sum + w.successRate, 0) / workflows.length;
  const avgLearningScore = workflows.reduce((sum, w) => sum + w.learningScore, 0) / workflows.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center space-x-3">
              <Brain className="h-8 w-8 text-primary" />
              <span>Advanced AI Workflows</span>
            </h1>
            <p className="text-muted-foreground mt-1">
              Intelligent automation that learns from your patterns and optimizes your productivity
            </p>
          </div>
          <Button onClick={() => setIsCreatingWorkflow(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Workflow
          </Button>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Workflows</p>
                  <p className="text-2xl font-bold">{workflows.filter(w => w.enabled).length}</p>
                </div>
                <Workflow className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Executions</p>
                  <p className="text-2xl font-bold">{totalExecutions}</p>
                </div>
                <Play className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Success Rate</p>
                  <p className="text-2xl font-bold">{Math.round(avgSuccessRate * 100)}%</p>
                </div>
                <Target className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Learning Score</p>
                  <p className="text-2xl font-bold">{avgLearningScore.toFixed(1)}</p>
                </div>
                <Star className="h-8 w-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
          <TabsTrigger value="learning">Learning Hub</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6">
          {/* Recent Insights */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5" />
                <span>Recent AI Insights</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {insights.slice(0, 3).map((insight) => (
                <div key={insight.id} className="glassmorphism-panel p-4 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <div className="p-2 rounded-lg bg-primary/20">
                      {getInsightIcon(insight.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold">{insight.title}</h4>
                        <Badge className={
                          insight.impact === 'high' ? 'bg-red-500/20 text-red-300' :
                          insight.impact === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                          'bg-green-500/20 text-green-300'
                        }>
                          {insight.impact} impact
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{insight.description}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2 text-xs">
                          <span>Confidence: {Math.round(insight.confidence * 100)}%</span>
                          <span>•</span>
                          <span>{insight.createdAt.toLocaleDateString()}</span>
                        </div>
                        {insight.actionable && (
                          <Button size="sm" variant="outline">
                            Apply Suggestion
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Active Workflows Status */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Workflow className="h-5 w-5" />
                <span>Active Workflows</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {workflows.filter(w => w.enabled).map((workflow) => (
                <div key={workflow.id} className="glassmorphism-panel p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <h4 className="font-semibold">{workflow.name}</h4>
                      <Badge className={getWorkflowStatusColor(workflow)}>
                        {Math.round(workflow.successRate * 100)}% success
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-muted-foreground">
                        {workflow.executionCount} runs
                      </span>
                      <Button size="sm" variant="ghost">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{workflow.description}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 text-xs">
                      <span>Learning Score: {workflow.learningScore}/10</span>
                      <span>Priority: {workflow.priority}/5</span>
                    </div>
                    <Progress value={workflow.learningScore * 10} className="w-24 h-2" />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="workflows" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {workflows.map((workflow) => (
              <Card key={workflow.id} className="glassmorphism-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{workflow.name}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Switch 
                        checked={workflow.enabled}
                        onCheckedChange={(checked) => {
                          setWorkflows(prev => prev.map(w => 
                            w.id === workflow.id ? { ...w, enabled: checked } : w
                          ));
                        }}
                      />
                      <Button size="sm" variant="ghost">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <CardDescription>{workflow.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Executions:</span>
                      <span className="ml-2 font-semibold">{workflow.executionCount}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Success Rate:</span>
                      <span className="ml-2 font-semibold">{Math.round(workflow.successRate * 100)}%</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Learning Score:</span>
                      <span className="ml-2 font-semibold">{workflow.learningScore}/10</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Priority:</span>
                      <span className="ml-2 font-semibold">{workflow.priority}/5</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <span className="text-sm font-medium">Learning Progress</span>
                    <Progress value={workflow.learningScore * 10} className="h-2" />
                  </div>

                  <div className="space-y-2">
                    <span className="text-sm font-medium">Actions ({workflow.actions.length})</span>
                    <div className="space-y-1">
                      {workflow.actions.map((action, index) => (
                        <div key={action.id} className="flex items-center justify-between text-xs bg-background/50 p-2 rounded">
                          <span className="capitalize">{action.type.replace('_', ' ')}</span>
                          <span className="text-muted-foreground">{Math.round(action.confidence * 100)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="space-y-4">
            {insights.map((insight) => (
              <Card key={insight.id} className="glassmorphism-card">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 rounded-lg bg-primary/20">
                      {getInsightIcon(insight.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-semibold">{insight.title}</h3>
                        <div className="flex items-center space-x-2">
                          <Badge className={
                            insight.impact === 'high' ? 'bg-red-500/20 text-red-300' :
                            insight.impact === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                            'bg-green-500/20 text-green-300'
                          }>
                            {insight.impact} impact
                          </Badge>
                          <Badge variant="outline">{insight.type}</Badge>
                        </div>
                      </div>
                      <p className="text-muted-foreground mb-4">{insight.description}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm">
                          <span>Confidence: {Math.round(insight.confidence * 100)}%</span>
                          <span>•</span>
                          <span>{insight.createdAt.toLocaleDateString()}</span>
                        </div>
                        <div className="flex space-x-2">
                          {insight.actionable && (
                            <Button size="sm">Apply Suggestion</Button>
                          )}
                          <Button size="sm" variant="outline">View Details</Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="learning" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bot className="h-5 w-5" />
                <span>AI Learning Progress</span>
              </CardTitle>
              <CardDescription>
                Track how the AI is learning your patterns and improving automation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glassmorphism-panel p-4 text-center">
                  <div className="text-2xl font-bold text-primary">2,847</div>
                  <div className="text-sm text-muted-foreground">Data Points Collected</div>
                </div>
                <div className="glassmorphism-panel p-4 text-center">
                  <div className="text-2xl font-bold text-green-400">94%</div>
                  <div className="text-sm text-muted-foreground">Pattern Recognition</div>
                </div>
                <div className="glassmorphism-panel p-4 text-center">
                  <div className="text-2xl font-bold text-blue-400">8.7/10</div>
                  <div className="text-sm text-muted-foreground">Learning Score</div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold">Learning Categories</h4>
                {[
                  { name: 'Time Preferences', progress: 89, description: 'When you\'re most productive' },
                  { name: 'Task Patterns', progress: 76, description: 'How you approach different types of work' },
                  { name: 'Energy Cycles', progress: 92, description: 'Your natural energy rhythms' },
                  { name: 'Context Switching', progress: 67, description: 'How context changes affect you' },
                  { name: 'Goal Prioritization', progress: 84, description: 'What matters most to you' }
                ].map((category, index) => (
                  <div key={index} className="glassmorphism-panel p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{category.name}</span>
                      <span className="text-sm font-bold">{category.progress}%</span>
                    </div>
                    <Progress value={category.progress} className="h-2 mb-2" />
                    <p className="text-sm text-muted-foreground">{category.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}