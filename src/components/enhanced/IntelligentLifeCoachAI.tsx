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
import { Slider } from '../ui/slider';
import { 
  Bot,
  Brain,
  Lightbulb,
  TrendingUp,
  Target,
  Heart,
  Zap,
  Clock,
  Calendar,
  MessageCircle,
  Send,
  Mic,
  MicOff,
  Star,
  CheckCircle2,
  AlertTriangle,
  Info,
  BarChart3,
  Users,
  BookOpen,
  Settings,
  Sparkles,
  Award,
  Activity
} from 'lucide-react';

interface AICoachingInsight {
  id: string;
  type: 'daily' | 'strategic' | 'wellness' | 'productivity' | 'habit' | 'goal';
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  confidence: number;
  actionable: boolean;
  actions?: CoachingAction[];
  relatedPillar?: string;
  timestamp: Date;
  read: boolean;
}

interface CoachingAction {
  id: string;
  type: 'task' | 'habit' | 'reminder' | 'adjustment' | 'celebration';
  title: string;
  description: string;
  estimatedTime?: number;
  difficulty: 'easy' | 'medium' | 'hard';
  impact: 'low' | 'medium' | 'high';
}

interface CoachingConversation {
  id: string;
  type: 'user' | 'coach';
  message: string;
  timestamp: Date;
  insights?: string[];
  actions?: CoachingAction[];
}

interface CoachingGoal {
  id: string;
  title: string;
  description: string;
  category: 'habit' | 'achievement' | 'wellness' | 'learning' | 'relationship';
  targetDate?: Date;
  progress: number;
  milestones: {
    id: string;
    title: string;
    completed: boolean;
    date?: Date;
  }[];
  coachingNotes: string[];
}

export default function IntelligentLifeCoachAI() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [insights, setInsights] = useState<AICoachingInsight[]>([]);
  const [conversation, setConversation] = useState<CoachingConversation[]>([]);
  const [goals, setGoals] = useState<CoachingGoal[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [coachPersonality, setCoachPersonality] = useState({
    supportive: 8,
    challenging: 6,
    analytical: 7,
    encouraging: 9
  });

  // Sample data initialization
  useEffect(() => {
    const sampleInsights: AICoachingInsight[] = [
      {
        id: '1',
        type: 'daily',
        title: 'Optimal Energy Window Detected',
        message: 'Your energy levels are typically highest between 9-11 AM. Consider scheduling your most important creative work during this time.',
        priority: 'high',
        confidence: 0.87,
        actionable: true,
        actions: [
          {
            id: 'a1',
            type: 'adjustment',
            title: 'Reschedule Creative Tasks',
            description: 'Move your creative work to 9-11 AM time block',
            estimatedTime: 5,
            difficulty: 'easy',
            impact: 'high'
          }
        ],
        relatedPillar: 'Career & Growth',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        read: false
      },
      {
        id: '2',
        type: 'wellness',
        title: 'Stress Pattern Recognition',
        message: 'I notice your stress levels increase on days with more than 6 hours of meetings. Consider implementing buffer time between meetings.',
        priority: 'medium',
        confidence: 0.79,
        actionable: true,
        actions: [
          {
            id: 'a2',
            type: 'habit',
            title: 'Meeting Buffer Time',
            description: 'Add 15-minute buffers between back-to-back meetings',
            estimatedTime: 2,
            difficulty: 'easy',
            impact: 'medium'
          }
        ],
        relatedPillar: 'Health & Wellness',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
        read: false
      },
      {
        id: '3',
        type: 'goal',
        title: 'Fitness Goal Progress Alert',
        message: 'You\'re 23% ahead of your quarterly fitness goal! Your consistency is paying off. Consider setting a stretch goal.',
        priority: 'low',
        confidence: 0.95,
        actionable: true,
        actions: [
          {
            id: 'a3',
            type: 'celebration',
            title: 'Celebrate Progress',
            description: 'Acknowledge your fitness achievement and set a new challenge',
            estimatedTime: 10,
            difficulty: 'easy',
            impact: 'high'
          }
        ],
        relatedPillar: 'Health & Wellness',
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
        read: true
      }
    ];

    const sampleGoals: CoachingGoal[] = [
      {
        id: '1',
        title: 'Establish Morning Routine',
        description: 'Create a consistent 30-minute morning routine that energizes me for the day',
        category: 'habit',
        targetDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
        progress: 65,
        milestones: [
          { id: 'm1', title: 'Wake up at same time for 7 days', completed: true, date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000) },
          { id: 'm2', title: 'Include meditation in routine', completed: true },
          { id: 'm3', title: 'Add physical activity', completed: false },
          { id: 'm4', title: 'Maintain for 21 days consistently', completed: false }
        ],
        coachingNotes: [
          'Great progress on consistency! The early wake-up habit is sticking.',
          'Consider starting with just 5 minutes of movement to build the habit.',
          'Your meditation practice is showing positive effects on your stress levels.'
        ]
      },
      {
        id: '2',
        title: 'Learn Spanish Conversational Level',
        description: 'Achieve conversational fluency in Spanish for upcoming travels',
        category: 'learning',
        targetDate: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000),
        progress: 34,
        milestones: [
          { id: 'm5', title: 'Complete basic vocabulary (1000 words)', completed: true },
          { id: 'm6', title: 'Have first conversation with native speaker', completed: false },
          { id: 'm7', title: 'Watch a movie in Spanish without subtitles', completed: false },
          { id: 'm8', title: 'Plan trip using only Spanish', completed: false }
        ],
        coachingNotes: [
          'Vocabulary building is going well. Time to focus on speaking practice.',
          'Consider finding a conversation partner through language exchange apps.',
          'Your learning pace suggests you might achieve fluency earlier than planned.'
        ]
      }
    ];

    const sampleConversation: CoachingConversation[] = [
      {
        id: '1',
        type: 'coach',
        message: 'Good morning! I noticed you completed your morning routine 5 days in a row. How are you feeling about the changes?',
        timestamp: new Date(Date.now() - 10 * 60 * 1000),
        insights: ['Habit formation is showing positive momentum']
      },
      {
        id: '2',
        type: 'user',
        message: 'It feels great! I have more energy throughout the day. Though I still struggle with the meditation part.',
        timestamp: new Date(Date.now() - 8 * 60 * 1000)
      },
      {
        id: '3',
        type: 'coach',
        message: 'That\'s fantastic progress! For meditation, what if we start with just 3 minutes instead of 10? Sometimes smaller steps lead to bigger breakthroughs.',
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
        actions: [
          {
            id: 'conv-a1',
            type: 'adjustment',
            title: 'Reduce Meditation Time',
            description: 'Start with 3-minute meditation sessions',
            estimatedTime: 3,
            difficulty: 'easy',
            impact: 'medium'
          }
        ]
      }
    ];

    setInsights(sampleInsights);
    setGoals(sampleGoals);
    setConversation(sampleConversation);
  }, []);

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    // Add user message
    const userMessage: CoachingConversation = {
      id: Date.now().toString(),
      type: 'user',
      message: currentMessage,
      timestamp: new Date()
    };

    setConversation(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const coachResponse: CoachingConversation = {
        id: (Date.now() + 1).toString(),
        type: 'coach',
        message: generateCoachResponse(currentMessage),
        timestamp: new Date(),
        insights: ['Personalized response based on your patterns and goals']
      };
      
      setConversation(prev => [...prev, coachResponse]);
      setIsTyping(false);
    }, 2000);
  };

  const generateCoachResponse = (userMessage: string): string => {
    const responses = [
      "That's a great question! Based on your recent patterns, I'd suggest focusing on one small change at a time.",
      "I understand your concern. Let's break this down into manageable steps that align with your goals.",
      "Your progress has been remarkable! This challenge is actually a sign that you're pushing your boundaries.",
      "I've noticed similar patterns in your data. Here's what tends to work best for people in your situation...",
      "That's perfectly normal! Remember, growth happens outside our comfort zone. Let's find a gentle way forward."
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500/20 text-red-300';
      case 'high': return 'bg-orange-500/20 text-orange-300';
      case 'medium': return 'bg-yellow-500/20 text-yellow-300';
      case 'low': return 'bg-green-500/20 text-green-300';
      default: return 'bg-gray-500/20 text-gray-300';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'daily': return <Calendar className="h-4 w-4" />;
      case 'strategic': return <Target className="h-4 w-4" />;
      case 'wellness': return <Heart className="h-4 w-4" />;
      case 'productivity': return <Zap className="h-4 w-4" />;
      case 'habit': return <Clock className="h-4 w-4" />;
      case 'goal': return <Award className="h-4 w-4" />;
      default: return <Lightbulb className="h-4 w-4" />;
    }
  };

  const unreadInsights = insights.filter(i => !i.read).length;
  const highPriorityInsights = insights.filter(i => i.priority === 'high' || i.priority === 'urgent').length;
  const averageConfidence = Math.round(insights.reduce((sum, i) => sum + i.confidence, 0) / insights.length * 100);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center space-x-3">
              <Bot className="h-8 w-8 text-primary" />
              <span>AI Life Coach</span>
            </h1>
            <p className="text-muted-foreground mt-1">
              Your intelligent companion for personal growth and optimization
            </p>
          </div>
          <Button>
            <Settings className="h-4 w-4 mr-2" />
            Coach Settings
          </Button>
        </div>

        {/* Coach Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">New Insights</p>
                  <p className="text-2xl font-bold">{unreadInsights}</p>
                </div>
                <Sparkles className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">High Priority</p>
                  <p className="text-2xl font-bold">{highPriorityInsights}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-orange-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Confidence</p>
                  <p className="text-2xl font-bold">{averageConfidence}%</p>
                </div>
                <Brain className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Goals</p>
                  <p className="text-2xl font-bold">{goals.length}</p>
                </div>
                <Target className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="chat">Coach Chat</TabsTrigger>
          <TabsTrigger value="goals">Goal Coaching</TabsTrigger>
          <TabsTrigger value="personality">Personality</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6">
          {/* Today's Coaching Summary */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Today's Coaching Summary</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="glassmorphism-panel p-4">
                  <h4 className="font-semibold mb-2">Focus Area</h4>
                  <p className="text-sm text-muted-foreground">Energy Management & Productivity</p>
                  <Progress value={78} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-1">78% optimized</p>
                </div>
                <div className="glassmorphism-panel p-4">
                  <h4 className="font-semibold mb-2">Wellness Score</h4>
                  <p className="text-2xl font-bold text-green-400">8.2/10</p>
                  <p className="text-xs text-muted-foreground">+0.5 from yesterday</p>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="font-semibold">Recommended Actions</h4>
                {insights.slice(0, 3).map((insight) => (
                  <div key={insight.id} className="flex items-center justify-between glassmorphism-panel p-3">
                    <div className="flex items-center space-x-3">
                      {getTypeIcon(insight.type)}
                      <div>
                        <p className="text-sm font-medium">{insight.title}</p>
                        <p className="text-xs text-muted-foreground">{insight.confidence * 100}% confidence</p>
                      </div>
                    </div>
                    <Button size="sm" variant="outline">
                      Apply
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Progress */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5" />
                <span>Recent Progress</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {goals.map((goal) => (
                <div key={goal.id} className="glassmorphism-panel p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{goal.title}</h4>
                    <Badge className="bg-primary/20 text-primary">{goal.progress}%</Badge>
                  </div>
                  <Progress value={goal.progress} className="mb-2" />
                  <p className="text-sm text-muted-foreground">{goal.description}</p>
                  {goal.coachingNotes.length > 0 && (
                    <p className="text-xs text-primary mt-2">💡 {goal.coachingNotes[goal.coachingNotes.length - 1]}</p>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="space-y-4">
            {insights.map((insight) => (
              <Card key={insight.id} className={`glassmorphism-card ${!insight.read ? 'border-primary/30' : ''}`}>
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 rounded-lg bg-primary/20">
                      {getTypeIcon(insight.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-semibold">{insight.title}</h3>
                        <div className="flex items-center space-x-2">
                          <Badge className={getPriorityColor(insight.priority)}>
                            {insight.priority}
                          </Badge>
                          {!insight.read && (
                            <Badge className="bg-primary/20 text-primary">New</Badge>
                          )}
                        </div>
                      </div>
                      <p className="text-muted-foreground mb-4">{insight.message}</p>
                      
                      {insight.actions && insight.actions.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="font-medium">Recommended Actions:</h4>
                          {insight.actions.map((action) => (
                            <div key={action.id} className="flex items-center justify-between glassmorphism-panel p-3">
                              <div>
                                <p className="text-sm font-medium">{action.title}</p>
                                <p className="text-xs text-muted-foreground">{action.description}</p>
                                <div className="flex items-center space-x-2 mt-1">
                                  <Badge variant="outline" className="text-xs">{action.difficulty}</Badge>
                                  <Badge variant="outline" className="text-xs">{action.impact} impact</Badge>
                                  {action.estimatedTime && (
                                    <span className="text-xs text-muted-foreground">{action.estimatedTime} min</span>
                                  )}
                                </div>
                              </div>
                              <Button size="sm">
                                Apply
                              </Button>
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center justify-between mt-4">
                        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                          <span>Confidence: {Math.round(insight.confidence * 100)}%</span>
                          <span>•</span>
                          <span>{insight.timestamp.toLocaleDateString()}</span>
                          {insight.relatedPillar && (
                            <>
                              <span>•</span>
                              <span>{insight.relatedPillar}</span>
                            </>
                          )}
                        </div>
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={() => {
                            setInsights(prev => prev.map(i => 
                              i.id === insight.id ? { ...i, read: true } : i
                            ));
                          }}
                        >
                          {insight.read ? 'Read' : 'Mark as Read'}
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="chat" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <MessageCircle className="h-5 w-5" />
                <span>Chat with Your AI Coach</span>
              </CardTitle>
              <CardDescription>
                Ask questions, get guidance, or discuss your goals and challenges
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Chat Messages */}
              <div className="h-96 overflow-y-auto space-y-4 p-4 bg-background/50 rounded-lg">
                {conversation.map((message) => (
                  <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] p-3 rounded-lg ${
                      message.type === 'user' 
                        ? 'bg-primary text-primary-foreground' 
                        : 'glassmorphism-panel'
                    }`}>
                      <p className="text-sm">{message.message}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                      {message.insights && (
                        <div className="mt-2 text-xs opacity-80">
                          💡 {message.insights[0]}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {isTyping && (
                  <div className="flex justify-start">
                    <div className="glassmorphism-panel p-3 rounded-lg">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Message Input */}
              <div className="flex items-center space-x-2">
                <div className="flex-1 relative">
                  <Input
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    placeholder="Ask your AI coach anything..."
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="pr-12"
                  />
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2"
                    onClick={() => setIsListening(!isListening)}
                  >
                    {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  </Button>
                </div>
                <Button onClick={handleSendMessage} disabled={!currentMessage.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="goals" className="space-y-6">
          <div className="space-y-6">
            {goals.map((goal) => (
              <Card key={goal.id} className="glassmorphism-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{goal.title}</CardTitle>
                    <Badge className="bg-primary/20 text-primary">{goal.progress}% Complete</Badge>
                  </div>
                  <CardDescription>{goal.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Progress value={goal.progress} className="h-3" />
                  
                  {/* Milestones */}
                  <div className="space-y-2">
                    <h4 className="font-semibold">Milestones</h4>
                    {goal.milestones.map((milestone) => (
                      <div key={milestone.id} className="flex items-center space-x-3 glassmorphism-panel p-3">
                        {milestone.completed ? (
                          <CheckCircle2 className="h-5 w-5 text-green-400" />
                        ) : (
                          <div className="h-5 w-5 border-2 border-muted-foreground rounded-full" />
                        )}
                        <span className={milestone.completed ? 'text-muted-foreground line-through' : ''}>
                          {milestone.title}
                        </span>
                        {milestone.date && (
                          <span className="text-xs text-muted-foreground ml-auto">
                            {milestone.date.toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Coaching Notes */}
                  <div className="space-y-2">
                    <h4 className="font-semibold">AI Coaching Notes</h4>
                    {goal.coachingNotes.map((note, index) => (
                      <div key={index} className="flex items-start space-x-2 glassmorphism-panel p-3">
                        <Lightbulb className="h-4 w-4 text-primary mt-0.5" />
                        <p className="text-sm">{note}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="personality" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>Coach Personality Settings</span>
              </CardTitle>
              <CardDescription>
                Customize how your AI coach interacts with you
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {Object.entries(coachPersonality).map(([trait, value]) => (
                <div key={trait} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium capitalize">{trait}</label>
                    <span className="text-sm text-muted-foreground">{value}/10</span>
                  </div>
                  <Slider
                    value={[value]}
                    onValueChange={(newValue) => {
                      setCoachPersonality(prev => ({
                        ...prev,
                        [trait]: newValue[0]
                      }));
                    }}
                    max={10}
                    step={1}
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground">
                    {trait === 'supportive' && 'How encouraging and positive the coach should be'}
                    {trait === 'challenging' && 'How much the coach should push you out of your comfort zone'}
                    {trait === 'analytical' && 'How data-driven and detailed the insights should be'}
                    {trait === 'encouraging' && 'How much the coach should celebrate your wins'}
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}