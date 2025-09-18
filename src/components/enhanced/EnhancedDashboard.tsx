import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Target, 
  Calendar, 
  CheckSquare, 
  TrendingUp, 
  Lightbulb,
  Plus,
  ArrowRight,
  Clock,
  Star,
  Zap,
  Brain,
  Heart
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { cn } from '../../lib/utils';
import { useAppStore } from '../../stores/basicAppStore';
import { TouchOptimizedButton } from './MobileEnhancements';

interface TodaysFocusProps {
  className?: string;
}

export function TodaysFocus({ className }: TodaysFocusProps) {
  const [focusTasks, setFocusTasks] = useState([
    {
      id: '1',
      title: 'Complete quarterly review',
      pillar: 'Career Growth',
      priority: 'high',
      timeEstimate: '2 hours',
      completed: false
    },
    {
      id: '2',
      title: 'Exercise session',
      pillar: 'Health & Wellness',
      priority: 'medium',
      timeEstimate: '45 minutes',
      completed: true
    },
    {
      id: '3',
      title: 'Family dinner planning',
      pillar: 'Relationships',
      priority: 'medium',
      timeEstimate: '30 minutes',
      completed: false
    }
  ]);

  const completedCount = focusTasks.filter(task => task.completed).length;
  const progressPercentage = (completedCount / focusTasks.length) * 100;

  const toggleTask = (taskId: string) => {
    setFocusTasks(prev => 
      prev.map(task => 
        task.id === taskId ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-400/10';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10';
      case 'low': return 'text-green-400 bg-green-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  return (
    <Card className={cn("glassmorphism-card", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-primary" />
            <CardTitle className="text-lg">Today's Focus</CardTitle>
          </div>
          <Badge variant="outline" className="text-xs">
            {completedCount}/{focusTasks.length} completed
          </Badge>
        </div>
        <Progress value={progressPercentage} className="h-2" />
      </CardHeader>

      <CardContent className="space-y-3">
        <AnimatePresence>
          {focusTasks.map((task, index) => (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                "p-3 rounded-lg border border-border/50 transition-all cursor-pointer",
                task.completed 
                  ? "bg-green-500/10 border-green-500/20" 
                  : "bg-muted/30 hover:bg-muted/50"
              )}
              onClick={() => toggleTask(task.id)}
            >
              <div className="flex items-start gap-3">
                <div className={cn(
                  "w-5 h-5 rounded-full border-2 flex items-center justify-center mt-0.5",
                  task.completed 
                    ? "bg-green-500 border-green-500" 
                    : "border-muted-foreground hover:border-primary"
                )}>
                  {task.completed && <CheckSquare className="w-3 h-3 text-white" />}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className={cn(
                      "font-medium text-sm",
                      task.completed && "line-through text-muted-foreground"
                    )}>
                      {task.title}
                    </h4>
                    <Badge className={getPriorityColor(task.priority)} variant="secondary">
                      {task.priority}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Target className="w-3 h-3" />
                      {task.pillar}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {task.timeEstimate}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        <TouchOptimizedButton
          variant="ghost"
          className="w-full justify-center text-primary hover:bg-primary/10"
          onClick={() => {/* Open quick capture */}}
        >
          <Plus className="w-4 h-4 mr-2" />
          Add to today's focus
        </TouchOptimizedButton>
      </CardContent>
    </Card>
  );
}

interface QuickCaptureProps {
  onCapture?: (content: string, type: 'task' | 'note' | 'idea') => void;
  className?: string;
}

export function QuickCapture({ onCapture, className }: QuickCaptureProps) {
  const [input, setInput] = useState('');
  const [selectedType, setSelectedType] = useState<'task' | 'note' | 'idea'>('task');

  const handleCapture = () => {
    if (input.trim() && onCapture) {
      onCapture(input.trim(), selectedType);
      setInput('');
    }
  };

  const captureTypes = [
    { type: 'task' as const, icon: CheckSquare, label: 'Task', color: 'text-blue-400' },
    { type: 'note' as const, icon: Heart, label: 'Note', color: 'text-green-400' },
    { type: 'idea' as const, icon: Lightbulb, label: 'Idea', color: 'text-yellow-400' }
  ];

  return (
    <Card className={cn("glassmorphism-card", className)}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Zap className="w-5 h-5 text-primary" />
          Quick Capture
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex gap-1 p-1 bg-muted/50 rounded-lg">
          {captureTypes.map(({ type, icon: Icon, label, color }) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={cn(
                "flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md transition-all text-sm",
                selectedType === type
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-muted/70"
              )}
            >
              <Icon className={cn("w-4 h-4", selectedType === type ? "" : color)} />
              {label}
            </button>
          ))}
        </div>

        <div className="space-y-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`What's on your mind? (${selectedType})`}
            className="w-full h-20 p-3 bg-muted/50 border border-border/50 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                handleCapture();
              }
            }}
          />
          
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground">
              ⌘+Enter to capture
            </span>
            <TouchOptimizedButton
              onClick={handleCapture}
              disabled={!input.trim()}
              size="sm"
              variant="primary"
            >
              Capture
            </TouchOptimizedButton>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface ProgressVisualizationProps {
  className?: string;
}

export function ProgressVisualization({ className }: ProgressVisualizationProps) {
  const pillars = [
    { name: 'Health & Wellness', progress: 85, color: 'bg-green-500', trend: '+12%' },
    { name: 'Career Growth', progress: 72, color: 'bg-blue-500', trend: '+8%' },
    { name: 'Relationships', progress: 90, color: 'bg-purple-500', trend: '+5%' },
    { name: 'Financial Freedom', progress: 65, color: 'bg-yellow-500', trend: '+15%' }
  ];

  return (
    <Card className={cn("glassmorphism-card", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            Pillar Progress
          </CardTitle>
          <Button variant="ghost" size="sm">
            View Details
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {pillars.map((pillar, index) => (
          <motion.div
            key={pillar.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="space-y-2"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{pillar.name}</span>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs text-green-400">
                  {pillar.trend}
                </Badge>
                <span className="text-sm text-muted-foreground">{pillar.progress}%</span>
              </div>
            </div>
            
            <div className="relative">
              <div className="h-2 bg-muted/50 rounded-full overflow-hidden">
                <motion.div
                  className={cn("h-full rounded-full", pillar.color)}
                  initial={{ width: 0 }}
                  animate={{ width: `${pillar.progress}%` }}
                  transition={{ duration: 1, delay: index * 0.2 }}
                />
              </div>
            </div>
          </motion.div>
        ))}
      </CardContent>
    </Card>
  );
}

interface SmartRecommendationsProps {
  className?: string;
}

export function SmartRecommendations({ className }: SmartRecommendationsProps) {
  const recommendations = [
    {
      type: 'suggestion',
      title: 'Consider blocking time for Health & Wellness',
      description: 'You haven\'t scheduled any wellness activities this week.',
      action: 'Schedule Now',
      priority: 'medium'
    },
    {
      type: 'insight',
      title: 'Great momentum on Career Growth!',
      description: 'You\'ve completed 5 career-related tasks this week.',
      action: 'View Progress',
      priority: 'low'
    },
    {
      type: 'reminder',
      title: 'Weekly review is due',
      description: 'Reflect on your progress and plan for next week.',
      action: 'Start Review',
      priority: 'high'
    }
  ];

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'suggestion': return Lightbulb;
      case 'insight': return TrendingUp;
      case 'reminder': return Calendar;
      default: return Brain;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-400/20 bg-red-400/10';
      case 'medium': return 'border-yellow-400/20 bg-yellow-400/10';
      case 'low': return 'border-green-400/20 bg-green-400/10';
      default: return 'border-blue-400/20 bg-blue-400/10';
    }
  };

  return (
    <Card className={cn("glassmorphism-card", className)}>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Brain className="w-5 h-5 text-primary" />
          Smart Recommendations
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {recommendations.map((recommendation, index) => {
          const Icon = getRecommendationIcon(recommendation.type);
          
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                "p-3 rounded-lg border",
                getPriorityColor(recommendation.priority)
              )}
            >
              <div className="flex items-start gap-3">
                <Icon className="w-5 h-5 text-primary mt-0.5" />
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm mb-1">{recommendation.title}</h4>
                  <p className="text-xs text-muted-foreground mb-2">
                    {recommendation.description}
                  </p>
                  <TouchOptimizedButton
                    size="sm"
                    variant="ghost"
                    className="h-7 px-3 text-xs"
                  >
                    {recommendation.action}
                  </TouchOptimizedButton>
                </div>
              </div>
            </motion.div>
          );
        })}

        <Separator />
        
        <div className="flex items-center justify-center">
          <Button variant="link" size="sm" className="text-xs">
            <Star className="w-3 h-3 mr-1" />
            Powered by AI insights
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}