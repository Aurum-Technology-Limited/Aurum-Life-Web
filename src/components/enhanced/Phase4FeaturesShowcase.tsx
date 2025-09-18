import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  Zap, 
  Brain, 
  Users, 
  BarChart3, 
  Puzzle, 
  Shield, 
  Target, 
  Bell,
  Workflow,
  Bot,
  Network,
  TrendingUp,
  CheckCircle2,
  Clock,
  Star,
  FileText,
  Activity
} from 'lucide-react';

interface Phase4Feature {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: 'planned' | 'in-progress' | 'completed' | 'beta';
  progress: number;
  category: 'automation' | 'collaboration' | 'analytics' | 'integration' | 'security' | 'intelligence';
  estimatedCompletion: string;
  keyBenefits: string[];
  dependencies?: string[];
}

const phase4Features: Phase4Feature[] = [
  // Completed Phase 3 Features
  {
    id: 'audit-logging',
    name: 'Comprehensive Audit Logging',
    description: 'Complete transparency for AI data usage with detailed audit trails and privacy controls',
    icon: <FileText className="h-6 w-6" />,
    status: 'completed',
    progress: 100,
    category: 'security',
    estimatedCompletion: 'Completed',
    keyBenefits: [
      'Complete AI interaction transparency',
      'Privacy-focused data usage tracking',
      'Automated data retention policies',
      'User-controlled audit exports'
    ]
  },
  {
    id: 'performance-optimization',
    name: 'Advanced Performance Optimization',
    description: 'Intelligent caching, monitoring, and optimization for blazing-fast user experience',
    icon: <Activity className="h-6 w-6" />,
    status: 'completed',
    progress: 100,
    category: 'analytics',
    estimatedCompletion: 'Completed',
    keyBenefits: [
      'Real-time performance monitoring',
      'Intelligent caching strategies',
      'Automated optimization recommendations',
      'Memory usage optimization'
    ]
  },
  {
    id: 'automated-testing',
    name: 'Automated Testing Suite',
    description: 'Comprehensive testing framework ensuring reliability and quality across all features',
    icon: <CheckCircle2 className="h-6 w-6" />,
    status: 'completed',
    progress: 100,
    category: 'automation',
    estimatedCompletion: 'Completed',
    keyBenefits: [
      'Unit and integration test coverage',
      'Performance regression testing',
      'End-to-end user journey validation',
      'Continuous quality assurance'
    ]
  },
  // Phase 4 Features - NOW COMPLETED!
  {
    id: 'ai-workflows',
    name: 'Advanced AI Workflows',
    description: 'Intelligent automation that learns from your patterns and creates personalized workflows',
    icon: <Workflow className="h-6 w-6" />,
    status: 'completed',
    progress: 100,
    category: 'automation',
    estimatedCompletion: 'Completed',
    keyBenefits: [
      'Automated task scheduling based on energy levels',
      'Smart priority adjustment using AI insights',
      'Cross-pillar dependency management',
      'Predictive goal achievement modeling'
    ]
  },
  {
    id: 'ai-assistant',
    name: 'Intelligent Life Coach AI',
    description: 'Personal AI assistant that provides contextual guidance and strategic recommendations',
    icon: <Bot className="h-6 w-6" />,
    status: 'completed',
    progress: 100,
    category: 'intelligence',
    estimatedCompletion: 'Completed',
    keyBenefits: [
      'Personalized daily strategy recommendations',
      'Real-time decision support',
      'Goal achievement coaching',
      'Habit formation guidance'
    ]
  },
  {
    id: 'team-collaboration',
    name: 'Team & Organization Features',
    description: 'Multi-user capabilities with shared goals, projects, and accountability systems',
    icon: <Users className="h-6 w-6" />,
    status: 'completed',
    progress: 100,
    category: 'collaboration',
    estimatedCompletion: 'Completed',
    keyBenefits: [
      'Shared project management',
      'Team goal alignment',
      'Accountability partnerships',
      'Organization-wide analytics'
    ]
  },
  {
    id: 'predictive-analytics',
    name: 'Predictive Life Analytics',
    description: 'Advanced forecasting and trend analysis for life optimization',
    icon: <TrendingUp className="h-6 w-6" />,
    status: 'completed',
    progress: 100,
    category: 'analytics',
    estimatedCompletion: 'Completed',
    keyBenefits: [
      'Goal achievement probability modeling',
      'Burnout risk prediction',
      'Optimal time allocation suggestions',
      'Life satisfaction forecasting'
    ]
  },
  {
    id: 'integration-ecosystem',
    name: 'Third-Party Integration Hub',
    description: 'Seamless connections with popular productivity and wellness apps',
    icon: <Puzzle className="h-6 w-6" />,
    status: 'completed',
    progress: 100,
    category: 'integration',
    estimatedCompletion: 'Completed',
    keyBenefits: [
      'Calendar sync (Google, Outlook, Apple)',
      'Fitness tracker integration',
      'Financial app connections',
      'Social media wellness metrics'
    ]
  },
  {
    id: 'enterprise-security',
    name: 'Enterprise Security Suite',
    description: 'Advanced security features for organizations and privacy-conscious users',
    icon: <Shield className="h-6 w-6" />,
    status: 'completed',
    progress: 100,
    category: 'security',
    estimatedCompletion: 'Completed',
    keyBenefits: [
      'End-to-end encryption',
      'Advanced audit logging',
      'SSO integration',
      'Compliance reporting'
    ]
  }
];

const categoryColors = {
  automation: 'bg-yellow-500/20 text-yellow-300',
  collaboration: 'bg-blue-500/20 text-blue-300',
  analytics: 'bg-green-500/20 text-green-300',
  integration: 'bg-purple-500/20 text-purple-300',
  security: 'bg-red-500/20 text-red-300',
  intelligence: 'bg-orange-500/20 text-orange-300'
};

const statusColors = {
  planned: 'bg-gray-500/20 text-gray-300',
  'in-progress': 'bg-blue-500/20 text-blue-300',
  completed: 'bg-green-500/20 text-green-300',
  beta: 'bg-yellow-500/20 text-yellow-300'
};

export default function Phase4FeaturesShowcase() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedFeature, setSelectedFeature] = useState<Phase4Feature | null>(null);

  const filteredFeatures = selectedCategory === 'all' 
    ? phase4Features 
    : phase4Features.filter(feature => feature.category === selectedCategory);

  const overallProgress = Math.round(
    phase4Features.reduce((acc, feature) => acc + feature.progress, 0) / phase4Features.length
  );

  const completedFeatures = phase4Features.filter(f => f.status === 'completed').length;
  const inProgressFeatures = phase4Features.filter(f => f.status === 'in-progress').length;
  const plannedFeatures = phase4Features.filter(f => f.status === 'planned').length;

  return (
    <div className="space-y-8">
      {/* Phase 4 Header */}
      <div className="text-center space-y-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-2"
        >
          <h1 className="text-4xl font-bold aurum-text-gradient">Phase 4: COMPLETE! 🎉</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            All Phase 4 features successfully implemented! Aurum Life now features advanced AI, enterprise security, team collaboration, and comprehensive integrations
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="glassmorphism-card p-6 max-w-md mx-auto"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-medium">Overall Progress</span>
              <span className="text-2xl font-bold text-primary">{overallProgress}%</span>
            </div>
            <Progress value={overallProgress} className="h-3" />
            <div className="flex items-center justify-center space-x-2 text-sm text-muted-foreground">
              <CheckCircle2 className="h-4 w-4 text-green-400" />
              <span>{completedFeatures} Completed • {inProgressFeatures} In Progress • {plannedFeatures} Planned</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Completion Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glassmorphism-card p-6 bg-primary/10 border-primary/30"
      >
        <div className="text-center space-y-3">
          <div className="flex items-center justify-center space-x-2">
            <CheckCircle2 className="h-6 w-6 text-primary" />
            <h2 className="text-xl font-bold text-primary">🚀 Phase 4: FULLY COMPLETE! 🚀</h2>
          </div>
          <p className="text-muted-foreground">
            All advanced AI features, enterprise security, team collaboration, and third-party integrations are now live!
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm mt-4">
            <div className="flex items-center space-x-2">
              <Bot className="h-4 w-4 text-primary" />
              <span>AI Life Coach</span>
            </div>
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              <span>Predictive Analytics</span>
            </div>
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-primary" />
              <span>Team Features</span>
            </div>
            <div className="flex items-center space-x-2">
              <Puzzle className="h-4 w-4 text-primary" />
              <span>Integrations</span>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="h-4 w-4 text-primary" />
              <span>Enterprise Security</span>
            </div>
            <div className="flex items-center space-x-2">
              <Workflow className="h-4 w-4 text-primary" />
              <span>AI Workflows</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Category Filter */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="space-y-6">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="automation">Automation</TabsTrigger>
          <TabsTrigger value="intelligence">AI</TabsTrigger>
          <TabsTrigger value="collaboration">Teams</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="integration">Integrations</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        <TabsContent value={selectedCategory} className="space-y-6">
          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence mode="popLayout">
              {filteredFeatures.map((feature, index) => (
                <motion.div
                  key={feature.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card 
                    className={`glassmorphism-card cursor-pointer hover:scale-105 transition-all duration-300 ${
                      feature.status === 'completed' ? 'border-green-500/30' : ''
                    }`}
                    onClick={() => setSelectedFeature(feature)}
                  >
                    <CardHeader className="space-y-3">
                      <div className="flex items-start justify-between">
                        <div className={`p-3 rounded-lg ${
                          feature.status === 'completed' ? 'bg-green-500/20' : 'bg-primary/20'
                        }`}>
                          {feature.icon}
                        </div>
                        <div className="flex space-x-2">
                          <Badge className={categoryColors[feature.category]}>
                            {feature.category}
                          </Badge>
                          <Badge className={statusColors[feature.status]}>
                            {feature.status}
                          </Badge>
                        </div>
                      </div>
                      <div>
                        <CardTitle className="text-lg flex items-center gap-2">
                          {feature.name}
                          {feature.status === 'completed' && (
                            <CheckCircle2 className="h-5 w-5 text-green-400" />
                          )}
                        </CardTitle>
                        <CardDescription className="text-sm mt-1">
                          {feature.description}
                        </CardDescription>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Progress</span>
                          <span>{feature.progress}%</span>
                        </div>
                        <Progress value={feature.progress} className="h-2" />
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <div className="flex items-center space-x-1">
                          <Clock className="h-3 w-3" />
                          <span>ETA: {feature.estimatedCompletion}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <CheckCircle2 className="h-3 w-3" />
                          <span>{feature.keyBenefits.length} benefits</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </TabsContent>
      </Tabs>

      {/* Feature Detail Modal */}
      <AnimatePresence>
        {selectedFeature && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedFeature(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="glassmorphism-card max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 space-y-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`p-4 rounded-lg ${
                      selectedFeature.status === 'completed' ? 'bg-green-500/20' : 'bg-primary/20'
                    }`}>
                      {selectedFeature.icon}
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold flex items-center gap-2">
                        {selectedFeature.name}
                        {selectedFeature.status === 'completed' && (
                          <CheckCircle2 className="h-6 w-6 text-green-400" />
                        )}
                      </h3>
                      <p className="text-muted-foreground">{selectedFeature.description}</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedFeature(null)}
                  >
                    ✕
                  </Button>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="glassmorphism-panel p-4 text-center">
                    <div className={`text-2xl font-bold ${
                      selectedFeature.status === 'completed' ? 'text-green-400' : 'text-primary'
                    }`}>
                      {selectedFeature.progress}%
                    </div>
                    <div className="text-sm text-muted-foreground">Complete</div>
                  </div>
                  <div className="glassmorphism-panel p-4 text-center">
                    <div className="text-lg font-bold capitalize">{selectedFeature.status}</div>
                    <div className="text-sm text-muted-foreground">Status</div>
                  </div>
                  <div className="glassmorphism-panel p-4 text-center">
                    <div className="text-lg font-bold">{selectedFeature.estimatedCompletion}</div>
                    <div className="text-sm text-muted-foreground">ETA</div>
                  </div>
                </div>

                <div>
                  <h4 className="text-lg font-semibold mb-3">Key Benefits</h4>
                  <div className="space-y-2">
                    {selectedFeature.keyBenefits.map((benefit, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <CheckCircle2 className={`h-5 w-5 flex-shrink-0 ${
                          selectedFeature.status === 'completed' ? 'text-green-400' : 'text-primary'
                        }`} />
                        <span>{benefit}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {selectedFeature.dependencies && (
                  <div>
                    <h4 className="text-lg font-semibold mb-3">Dependencies</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedFeature.dependencies.map((dep, index) => (
                        <Badge key={index} variant="outline">{dep}</Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-end space-x-3">
                  <Button variant="outline" onClick={() => setSelectedFeature(null)}>
                    Close
                  </Button>
                  {selectedFeature.status === 'completed' && (
                    <Button className="bg-green-500 hover:bg-green-600">
                      View Implementation
                    </Button>
                  )}
                  {selectedFeature.status === 'in-progress' && (
                    <Button>
                      View Progress
                    </Button>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}