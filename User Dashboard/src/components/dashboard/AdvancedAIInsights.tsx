import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  Target, 
  Zap, 
  MessageCircle,
  Lightbulb,
  BarChart3,
  Clock,
  Users,
  BookOpen,
  Briefcase
} from 'lucide-react';

interface AIInsight {
  id: string;
  type: 'recommendation' | 'prediction' | 'pattern' | 'optimization';
  title: string;
  description: string;
  pillar: string;
  priority: 'High' | 'Medium' | 'Low';
  confidence: number;
  actionLabel: string;
  impact: 'High' | 'Medium' | 'Low';
}

interface Prediction {
  id: string;
  goal: string;
  currentProgress: number;
  predictedCompletion: string;
  confidence: number;
  requiredActions: string[];
}

export function AdvancedAIInsights() {
  const [aiQuery, setAiQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const insights: AIInsight[] = [
    {
      id: '1',
      type: 'recommendation',
      title: 'Strategic Alignment Opportunity',
      description: 'Your Work pillar is strong (76%), but Relationships needs attention (54%). Consider adding 2x 30min family check-ins this week to improve balance.',
      pillar: 'Relationships',
      priority: 'High',
      confidence: 87,
      actionLabel: 'Schedule Family Time',
      impact: 'High'
    },
    {
      id: '2',
      type: 'optimization',
      title: 'Energy Optimization',
      description: 'Your peak focus time is 2-4 PM. Schedule high-impact Work tasks during this window for 40% better completion rates.',
      pillar: 'Work',
      priority: 'Medium',
      confidence: 92,
      actionLabel: 'Optimize Schedule',
      impact: 'Medium'
    },
    {
      id: '3',
      type: 'pattern',
      title: 'Productivity Pattern Detected',
      description: 'You complete 3x more tasks on Tuesdays and Thursdays. Consider scheduling your most important work on these days.',
      pillar: 'Work',
      priority: 'Medium',
      confidence: 78,
      actionLabel: 'Adjust Planning',
      impact: 'Medium'
    },
    {
      id: '4',
      type: 'recommendation',
      title: 'Health Investment Gap',
      description: 'Your Health pillar is under-invested at 30%. Adding 2 hours weekly could improve your overall energy and focus.',
      pillar: 'Health',
      priority: 'High',
      confidence: 85,
      actionLabel: 'Boost Health',
      impact: 'High'
    }
  ];

  const predictions: Prediction[] = [
    {
      id: '1',
      goal: 'Complete Alchemy Site',
      currentProgress: 62,
      predictedCompletion: '2 weeks',
      confidence: 89,
      requiredActions: ['2x 45min deep work blocks daily', 'Reduce context switching', 'Focus on high-impact features']
    },
    {
      id: '2',
      goal: 'Reach 80% Health pillar',
      currentProgress: 68,
      predictedCompletion: '3 weeks',
      confidence: 76,
      requiredActions: ['Add 2h weekly training', 'Improve sleep consistency', 'Track nutrition habits']
    },
    {
      id: '3',
      goal: 'Strengthen Relationships',
      currentProgress: 54,
      predictedCompletion: '4 weeks',
      confidence: 82,
      requiredActions: ['Schedule weekly family time', 'Plan 2 social activities', 'Improve communication habits']
    }
  ];

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'recommendation': return <Lightbulb className="w-5 h-5" style={{color: '#F4D03F'}} />;
      case 'prediction': return <TrendingUp className="w-5 h-5" style={{color: '#3B82F6'}} />;
      case 'pattern': return <BarChart3 className="w-5 h-5" style={{color: '#10B981'}} />;
      case 'optimization': return <Zap className="w-5 h-5" style={{color: '#F59E0B'}} />;
      default: return <Brain className="w-5 h-5" style={{color: '#F4D03F'}} />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'Medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'Low': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'High': return 'text-green-400';
      case 'Medium': return 'text-yellow-400';
      case 'Low': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const getPillarIcon = (pillar: string) => {
    switch (pillar) {
      case 'Work': return <Briefcase className="w-4 h-4" style={{color: '#F4D03F'}} />;
      case 'Health': return <Zap className="w-4 h-4" style={{color: '#F4D03F'}} />;
      case 'Relationships': return <Users className="w-4 h-4" style={{color: '#F4D03F'}} />;
      case 'Growth': return <BookOpen className="w-4 h-4" style={{color: '#F4D03F'}} />;
      default: return <Target className="w-4 h-4" style={{color: '#F4D03F'}} />;
    }
  };

  const handleAIQuery = async () => {
    if (!aiQuery.trim()) return;
    
    setIsLoading(true);
    // Simulate AI processing
    setTimeout(() => {
      setIsLoading(false);
      // In a real app, this would call an AI API
      console.log('AI Query:', aiQuery);
    }, 2000);
  };

  return (
    <div className="advanced-ai-insights space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-6 h-6" style={{color: '#F4D03F'}} />
          <h2 className="text-2xl font-semibold tracking-tight">Strategic AI Intelligence</h2>
        </div>
        <Badge variant="outline" className="text-xs" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>
          Auto-updated
        </Badge>
      </div>

      {/* AI Insights Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {insights.map((insight) => (
          <Card 
            key={insight.id} 
            className="transition-all hover:shadow-lg"
            style={{
              background: 'rgba(26,29,41,0.4)',
              backdropFilter: 'blur(12px)',
              borderColor: 'rgba(244,208,63,0.2)'
            }}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start gap-3">
                {getInsightIcon(insight.type)}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <CardTitle className="text-sm font-medium">{insight.title}</CardTitle>
                    <Badge className={`text-xs ${getPriorityColor(insight.priority)}`}>
                      {insight.priority}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-xs" style={{color: '#B8BCC8'}}>
                    {getPillarIcon(insight.pillar)}
                    <span>{insight.pillar}</span>
                    <span>•</span>
                    <span>{insight.confidence}% confidence</span>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-sm mb-3" style={{color: '#B8BCC8'}}>
                {insight.description}
              </p>
              <div className="flex items-center justify-between">
                <Button 
                  size="sm" 
                  variant="outline"
                  style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}
                >
                  {insight.actionLabel}
                </Button>
                <div className="flex items-center gap-1 text-xs">
                  <span style={{color: '#B8BCC8'}}>Impact:</span>
                  <span className={getImpactColor(insight.impact)}>{insight.impact}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Predictive Analytics */}
      <Card style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
        <CardHeader>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" style={{color: '#F4D03F'}} />
            <CardTitle>Goal Achievement Forecast</CardTitle>
          </div>
          <p className="text-sm" style={{color: '#B8BCC8'}}>AI-powered predictions for your strategic goals</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {predictions.map((prediction) => (
              <div key={prediction.id} className="p-4 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4" style={{color: '#F4D03F'}} />
                    <span className="font-medium">{prediction.goal}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold" style={{color: '#F4D03F'}}>
                      {prediction.predictedCompletion}
                    </div>
                    <div className="text-xs" style={{color: '#B8BCC8'}}>
                      {prediction.confidence}% confidence
                    </div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span>Current Progress</span>
                    <span className="font-medium">{prediction.currentProgress}%</span>
                  </div>
                  <div className="h-2 rounded-full overflow-hidden" style={{background: 'rgba(11,13,20,0.4)'}}>
                    <div 
                      className="h-full transition-all" 
                      style={{
                        width: `${prediction.currentProgress}%`,
                        background: 'linear-gradient(90deg, #F4D03F, #F7DC6F)'
                      }}
                    ></div>
                  </div>
                  
                  <div className="text-xs" style={{color: '#B8BCC8'}}>
                    Required actions: {prediction.requiredActions.join(', ')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Strategic AI Chat */}
      <Card style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
        <CardHeader>
          <div className="flex items-center gap-2">
            <MessageCircle className="w-5 h-5" style={{color: '#F4D03F'}} />
            <CardTitle>Ask Aurum AI</CardTitle>
          </div>
          <p className="text-sm" style={{color: '#B8BCC8'}}>Get strategic guidance and insights for your life management</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Input
                placeholder="Ask about strategic alignment, goal achievement, or life balance..."
                value={aiQuery}
                onChange={(e) => setAiQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAIQuery()}
                className="flex-1"
                style={{background: 'rgba(11,13,20,0.35)', borderColor: 'rgba(244,208,63,0.15)'}}
              />
              <Button 
                onClick={handleAIQuery}
                disabled={isLoading || !aiQuery.trim()}
                style={{backgroundColor: '#F4D03F', color: '#0B0D14'}}
              >
                {isLoading ? (
                  <Clock className="w-4 h-4 animate-spin" />
                ) : (
                  'Ask'
                )}
              </Button>
            </div>
            
            <div className="text-xs" style={{color: '#B8BCC8'}}>
              Try: "How can I better balance my Work and Relationships pillars?" or 
              "What's the optimal schedule for my high-impact tasks?"
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Performance Metrics */}
      <Card style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
        <CardContent className="p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold" style={{color: '#F4D03F'}}>87%</div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Prediction Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-green-400">12</div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Insights Generated</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-blue-400">3</div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Goals Tracked</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold" style={{color: '#F4D03F'}}>24h</div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Last Update</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
