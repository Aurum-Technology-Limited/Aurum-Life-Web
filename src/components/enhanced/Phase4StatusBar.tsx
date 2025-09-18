import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { 
  Zap, 
  Brain, 
  Users, 
  BarChart3, 
  Puzzle, 
  Shield,
  ChevronDown,
  ChevronUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  Star,
  Workflow
} from 'lucide-react';

interface Phase4Milestone {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  progress: number;
  status: 'completed' | 'in-progress' | 'planned' | 'blocked';
  estimatedCompletion: string;
  dependencies?: string[];
  keyDeliverables: string[];
}

const phase4Milestones: Phase4Milestone[] = [
  {
    id: 'ai-workflows',
    name: 'Advanced AI Workflows',
    description: 'Intelligent automation system with pattern learning',
    icon: <Workflow className="h-4 w-4" />,
    progress: 25,
    status: 'in-progress',
    estimatedCompletion: 'Q1 2025',
    keyDeliverables: [
      'Workflow Builder Interface ✓',
      'Pattern Recognition Engine',
      'Automated Task Scheduling',
      'Learning Algorithm Integration'
    ]
  },
  {
    id: 'ai-assistant',
    name: 'Intelligent Life Coach AI',
    description: 'Personal AI assistant for strategic guidance',
    icon: <Brain className="h-4 w-4" />,
    progress: 0,
    status: 'planned',
    estimatedCompletion: 'Q2 2025',
    dependencies: ['ai-workflows'],
    keyDeliverables: [
      'Natural Language Processing',
      'Context-Aware Recommendations',
      'Goal Achievement Coaching',
      'Decision Support System'
    ]
  },
  {
    id: 'team-features',
    name: 'Team & Organization Features',
    description: 'Multi-user collaboration and shared goals',
    icon: <Users className="h-4 w-4" />,
    progress: 0,
    status: 'planned',
    estimatedCompletion: 'Q2 2025',
    keyDeliverables: [
      'Multi-user Authentication',
      'Shared Project Management',
      'Team Goal Alignment',
      'Accountability Systems'
    ]
  },
  {
    id: 'predictive-analytics',
    name: 'Predictive Life Analytics',
    description: 'Advanced forecasting and trend analysis',
    icon: <BarChart3 className="h-4 w-4" />,
    progress: 0,
    status: 'planned',
    estimatedCompletion: 'Q1 2025',
    dependencies: ['ai-workflows'],
    keyDeliverables: [
      'Goal Achievement Modeling',
      'Burnout Risk Prediction',
      'Time Allocation Optimization',
      'Life Satisfaction Forecasting'
    ]
  },
  {
    id: 'integrations',
    name: 'Third-Party Integration Hub',
    description: 'Seamless connections with popular apps',
    icon: <Puzzle className="h-4 w-4" />,
    progress: 0,
    status: 'planned',
    estimatedCompletion: 'Q3 2025',
    keyDeliverables: [
      'Calendar Sync (Google, Outlook)',
      'Fitness Tracker Integration',
      'Financial App Connections',
      'Social Media Analytics'
    ]
  },
  {
    id: 'enterprise-security',
    name: 'Enterprise Security Suite',
    description: 'Advanced security for organizations',
    icon: <Shield className="h-4 w-4" />,
    progress: 0,
    status: 'planned',
    estimatedCompletion: 'Q3 2025',
    keyDeliverables: [
      'End-to-End Encryption',
      'Advanced Audit Logging',
      'SSO Integration',
      'Compliance Reporting'
    ]
  }
];

export default function Phase4StatusBar() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [currentMilestone, setCurrentMilestone] = useState(0);

  const totalProgress = Math.round(
    phase4Milestones.reduce((sum, milestone) => sum + milestone.progress, 0) / phase4Milestones.length
  );

  const completedMilestones = phase4Milestones.filter(m => m.status === 'completed').length;
  const inProgressMilestones = phase4Milestones.filter(m => m.status === 'in-progress').length;
  const plannedMilestones = phase4Milestones.filter(m => m.status === 'planned').length;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-300';
      case 'in-progress': return 'bg-blue-500/20 text-blue-300';
      case 'planned': return 'bg-gray-500/20 text-gray-300';
      case 'blocked': return 'bg-red-500/20 text-red-300';
      default: return 'bg-gray-500/20 text-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="h-4 w-4" />;
      case 'in-progress': return <Clock className="h-4 w-4" />;
      case 'planned': return <AlertCircle className="h-4 w-4" />;
      case 'blocked': return <AlertCircle className="h-4 w-4 text-red-400" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  // Auto-cycle through milestones when collapsed
  useEffect(() => {
    if (!isExpanded) {
      const interval = setInterval(() => {
        setCurrentMilestone((prev) => (prev + 1) % phase4Milestones.length);
      }, 4000);
      return () => clearInterval(interval);
    }
  }, [isExpanded]);

  return (
    <Card className="glassmorphism-card border-primary/20">
      <CardContent className="p-4">
        <motion.div layout>
          {/* Collapsed View */}
          <AnimatePresence mode="wait">
            {!isExpanded && (
              <motion.div
                key="collapsed"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-primary/20">
                      <Zap className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Phase 4: Advanced AI & Enterprise</h3>
                      <p className="text-sm text-muted-foreground">
                        {totalProgress}% Complete • {inProgressMilestones} Active • {plannedMilestones} Planned
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsExpanded(true)}
                  >
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Overall Progress</span>
                    <span className="font-semibold">{totalProgress}%</span>
                  </div>
                  <Progress value={totalProgress} className="h-2" />
                </div>

                {/* Current Milestone Spotlight */}
                <motion.div
                  key={currentMilestone}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="glassmorphism-panel p-3 rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-lg bg-background/50">
                        {phase4Milestones[currentMilestone].icon}
                      </div>
                      <div>
                        <h4 className="font-medium text-sm">
                          {phase4Milestones[currentMilestone].name}
                        </h4>
                        <p className="text-xs text-muted-foreground">
                          {phase4Milestones[currentMilestone].description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(phase4Milestones[currentMilestone].status)}>
                        {phase4Milestones[currentMilestone].status}
                      </Badge>
                      <span className="text-xs font-semibold">
                        {phase4Milestones[currentMilestone].progress}%
                      </span>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Expanded View */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                key="expanded"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-primary/20">
                      <Zap className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold">Phase 4: Advanced AI & Enterprise</h3>
                      <p className="text-sm text-muted-foreground">
                        Elevating Aurum Life with intelligent automation and enterprise features
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsExpanded(false)}
                  >
                    <ChevronUp className="h-4 w-4" />
                  </Button>
                </div>

                {/* Progress Overview */}
                <div className="grid grid-cols-4 gap-4">
                  <div className="glassmorphism-panel p-3 text-center">
                    <div className="text-lg font-bold text-primary">{totalProgress}%</div>
                    <div className="text-xs text-muted-foreground">Complete</div>
                  </div>
                  <div className="glassmorphism-panel p-3 text-center">
                    <div className="text-lg font-bold text-green-400">{completedMilestones}</div>
                    <div className="text-xs text-muted-foreground">Completed</div>
                  </div>
                  <div className="glassmorphism-panel p-3 text-center">
                    <div className="text-lg font-bold text-blue-400">{inProgressMilestones}</div>
                    <div className="text-xs text-muted-foreground">Active</div>
                  </div>
                  <div className="glassmorphism-panel p-3 text-center">
                    <div className="text-lg font-bold text-gray-400">{plannedMilestones}</div>
                    <div className="text-xs text-muted-foreground">Planned</div>
                  </div>
                </div>

                {/* Milestone Details */}
                <div className="space-y-4">
                  <h4 className="font-semibold flex items-center space-x-2">
                    <Star className="h-4 w-4" />
                    <span>Milestones</span>
                  </h4>
                  
                  <div className="space-y-3">
                    {phase4Milestones.map((milestone, index) => (
                      <motion.div
                        key={milestone.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="glassmorphism-panel p-4 rounded-lg"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className="p-2 rounded-lg bg-background/50">
                              {milestone.icon}
                            </div>
                            <div>
                              <h5 className="font-medium">{milestone.name}</h5>
                              <p className="text-sm text-muted-foreground">{milestone.description}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={getStatusColor(milestone.status)}>
                              {getStatusIcon(milestone.status)}
                              <span className="ml-1">{milestone.status}</span>
                            </Badge>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>Progress</span>
                            <span className="font-semibold">{milestone.progress}%</span>
                          </div>
                          <Progress value={milestone.progress} className="h-2" />
                        </div>

                        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                          <div>
                            <span className="text-muted-foreground">ETA:</span>
                            <span className="ml-2 font-medium">{milestone.estimatedCompletion}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Deliverables:</span>
                            <span className="ml-2 font-medium">{milestone.keyDeliverables.length} items</span>
                          </div>
                        </div>

                        {milestone.dependencies && (
                          <div className="mt-2 text-sm">
                            <span className="text-muted-foreground">Dependencies:</span>
                            <div className="mt-1 flex flex-wrap gap-1">
                              {milestone.dependencies.map((dep, i) => (
                                <Badge key={i} variant="outline" className="text-xs">
                                  {dep}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </CardContent>
    </Card>
  );
}