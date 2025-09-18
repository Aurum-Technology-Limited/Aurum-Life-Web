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
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { 
  Users,
  UserPlus,
  Target,
  CheckCircle2,
  Clock,
  MessageCircle,
  Share2,
  Award,
  TrendingUp,
  Calendar,
  Bell,
  Settings,
  Crown,
  Shield,
  Eye,
  Edit,
  Trash2,
  Plus,
  Send,
  Heart,
  Star,
  Activity,
  BarChart3,
  Zap,
  BookOpen,
  Handshake
} from 'lucide-react';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  joinedAt: Date;
  lastActive: Date;
  contributionScore: number;
  pillars: string[];
  status: 'active' | 'away' | 'busy' | 'offline';
}

interface SharedGoal {
  id: string;
  title: string;
  description: string;
  category: 'team' | 'individual' | 'organization';
  progress: number;
  targetDate?: Date;
  participants: string[];
  createdBy: string;
  milestones: Milestone[];
  updates: GoalUpdate[];
  accountability: AccountabilityPartner[];
}

interface Milestone {
  id: string;
  title: string;
  completed: boolean;
  completedBy?: string;
  completedAt?: Date;
  assignedTo?: string[];
}

interface GoalUpdate {
  id: string;
  message: string;
  author: string;
  timestamp: Date;
  type: 'progress' | 'milestone' | 'comment' | 'celebration';
  attachments?: string[];
}

interface AccountabilityPartner {
  id: string;
  partnerId: string;
  goalId: string;
  type: 'check_in' | 'support' | 'challenge';
  frequency: 'daily' | 'weekly' | 'monthly';
  lastInteraction: Date;
  effectiveness: number; // 0-100
}

interface TeamInsight {
  id: string;
  type: 'performance' | 'collaboration' | 'motivation' | 'productivity';
  title: string;
  description: string;
  metrics: Record<string, number>;
  recommendations: string[];
}

export default function TeamCollaborationHub() {
  const [activeTab, setActiveTab] = useState('overview');
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [sharedGoals, setSharedGoals] = useState<SharedGoal[]>([]);
  const [teamInsights, setTeamInsights] = useState<TeamInsight[]>([]);
  const [inviteEmail, setInviteEmail] = useState('');
  const [newGoalTitle, setNewGoalTitle] = useState('');
  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null);

  // Sample data initialization
  useEffect(() => {
    const sampleMembers: TeamMember[] = [
      {
        id: '1',
        name: 'Sarah Chen',
        email: 'sarah@example.com',
        avatar: '/avatars/sarah.jpg',
        role: 'admin',
        joinedAt: new Date('2024-01-15'),
        lastActive: new Date(),
        contributionScore: 92,
        pillars: ['Career & Growth', 'Health & Wellness'],
        status: 'active'
      },
      {
        id: '2',
        name: 'Mike Rodriguez',
        email: 'mike@example.com',
        role: 'member',
        joinedAt: new Date('2024-01-20'),
        lastActive: new Date(Date.now() - 2 * 60 * 60 * 1000),
        contributionScore: 78,
        pillars: ['Financial Security', 'Relationships'],
        status: 'away'
      },
      {
        id: '3',
        name: 'Emma Thompson',
        email: 'emma@example.com',
        role: 'member',
        joinedAt: new Date('2024-02-01'),
        lastActive: new Date(Date.now() - 30 * 60 * 1000),
        contributionScore: 85,
        pillars: ['Personal Growth', 'Health & Wellness'],
        status: 'active'
      }
    ];

    const sampleGoals: SharedGoal[] = [
      {
        id: '1',
        title: 'Team Fitness Challenge',
        description: 'Complete 10,000 steps daily for 30 days as a team',
        category: 'team',
        progress: 67,
        targetDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
        participants: ['1', '2', '3'],
        createdBy: '1',
        milestones: [
          { id: 'm1', title: 'Week 1: Establish routine', completed: true, completedBy: '1', completedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) },
          { id: 'm2', title: 'Week 2: Increase consistency', completed: true, completedBy: '2', completedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) },
          { id: 'm3', title: 'Week 3: Support each other', completed: false, assignedTo: ['1', '2', '3'] },
          { id: 'm4', title: 'Week 4: Celebrate success', completed: false, assignedTo: ['1', '2', '3'] }
        ],
        updates: [
          {
            id: 'u1',
            message: 'Great job everyone! We\'re ahead of our target pace.',
            author: '1',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
            type: 'progress'
          },
          {
            id: 'u2',
            message: 'Completed my 12,000 steps today! 💪',
            author: '2',
            timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
            type: 'milestone'
          }
        ],
        accountability: [
          {
            id: 'a1',
            partnerId: '2',
            goalId: '1',
            type: 'check_in',
            frequency: 'daily',
            lastInteraction: new Date(),
            effectiveness: 89
          }
        ]
      },
      {
        id: '2',
        title: 'Learning & Development Goals',
        description: 'Each member completes one professional development course this quarter',
        category: 'individual',
        progress: 34,
        targetDate: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
        participants: ['1', '2', '3'],
        createdBy: '1',
        milestones: [
          { id: 'm5', title: 'Select courses', completed: true, completedBy: '1' },
          { id: 'm6', title: 'Complete 25% of content', completed: false, assignedTo: ['1', '2', '3'] },
          { id: 'm7', title: 'Mid-point check-in', completed: false },
          { id: 'm8', title: 'Complete and share learnings', completed: false }
        ],
        updates: [
          {
            id: 'u3',
            message: 'Started my UX Design course on Coursera!',
            author: '3',
            timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
            type: 'progress'
          }
        ],
        accountability: []
      }
    ];

    const sampleInsights: TeamInsight[] = [
      {
        id: '1',
        type: 'collaboration',
        title: 'Strong Team Momentum',
        description: 'Team collaboration has increased 45% this month with consistent daily check-ins',
        metrics: { collaboration_score: 87, check_in_frequency: 4.2, goal_completion: 78 },
        recommendations: [
          'Continue daily check-ins',
          'Consider adding peer recognition system',
          'Schedule team celebration for milestones'
        ]
      },
      {
        id: '2',
        type: 'performance',
        title: 'Individual vs Team Goals Balance',
        description: 'Team shows optimal balance between individual growth and collective achievements',
        metrics: { individual_progress: 76, team_progress: 82, satisfaction: 89 },
        recommendations: [
          'Introduce cross-pillar collaboration opportunities',
          'Create mentorship pairs within team',
          'Share individual wins more frequently'
        ]
      }
    ];

    setTeamMembers(sampleMembers);
    setSharedGoals(sampleGoals);
    setTeamInsights(sampleInsights);
  }, []);

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner': return <Crown className="h-4 w-4 text-yellow-400" />;
      case 'admin': return <Shield className="h-4 w-4 text-blue-400" />;
      case 'member': return <Users className="h-4 w-4 text-green-400" />;
      case 'viewer': return <Eye className="h-4 w-4 text-gray-400" />;
      default: return <Users className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'away': return 'bg-yellow-500';
      case 'busy': return 'bg-red-500';
      case 'offline': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const handleInviteMember = () => {
    if (!inviteEmail) return;
    // Implementation would send invitation
    console.log('Inviting:', inviteEmail);
    setInviteEmail('');
  };

  const handleCreateGoal = () => {
    if (!newGoalTitle) return;
    // Implementation would create new shared goal
    console.log('Creating goal:', newGoalTitle);
    setNewGoalTitle('');
  };

  const activeMembers = teamMembers.filter(m => m.status === 'active').length;
  const averageContribution = Math.round(teamMembers.reduce((sum, m) => sum + m.contributionScore, 0) / teamMembers.length);
  const completedGoals = sharedGoals.filter(g => g.progress === 100).length;
  const totalGoals = sharedGoals.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center space-x-3">
              <Users className="h-8 w-8 text-primary" />
              <span>Team Collaboration</span>
            </h1>
            <p className="text-muted-foreground mt-1">
              Shared goals, accountability, and team analytics for collective growth
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline">
              <Settings className="h-4 w-4 mr-2" />
              Team Settings
            </Button>
            <Button>
              <UserPlus className="h-4 w-4 mr-2" />
              Invite Member
            </Button>
          </div>
        </div>

        {/* Team Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Members</p>
                  <p className="text-2xl font-bold">{activeMembers}/{teamMembers.length}</p>
                </div>
                <Users className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Team Goals</p>
                  <p className="text-2xl font-bold">{completedGoals}/{totalGoals}</p>
                </div>
                <Target className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg Contribution</p>
                  <p className="text-2xl font-bold">{averageContribution}%</p>
                </div>
                <Award className="h-8 w-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Team Insights</p>
                  <p className="text-2xl font-bold">{teamInsights.length}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="members">Members</TabsTrigger>
          <TabsTrigger value="goals">Shared Goals</TabsTrigger>
          <TabsTrigger value="accountability">Accountability</TabsTrigger>
          <TabsTrigger value="insights">Team Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Recent Activity */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Recent Team Activity</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {sharedGoals.flatMap(goal => goal.updates).slice(0, 5).map((update) => {
                const author = teamMembers.find(m => m.id === update.author);
                return (
                  <div key={update.id} className="flex items-start space-x-3 glassmorphism-panel p-4">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={author?.avatar} />
                      <AvatarFallback>{author?.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <p className="text-sm">
                        <span className="font-medium">{author?.name}</span> {update.message}
                      </p>
                      <p className="text-xs text-muted-foreground">{update.timestamp.toLocaleString()}</p>
                    </div>
                    <Badge variant="outline" className="capitalize">
                      {update.type.replace('_', ' ')}
                    </Badge>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="glassmorphism-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <UserPlus className="h-5 w-5" />
                  <span>Invite Team Member</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex space-x-2">
                  <Input
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="Enter email address"
                    type="email"
                  />
                  <Button onClick={handleInviteMember}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="glassmorphism-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="h-5 w-5" />
                  <span>Create Shared Goal</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex space-x-2">
                  <Input
                    value={newGoalTitle}
                    onChange={(e) => setNewGoalTitle(e.target.value)}
                    placeholder="Goal title"
                  />
                  <Button onClick={handleCreateGoal}>
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="members" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {teamMembers.map((member) => (
              <Card key={member.id} className="glassmorphism-card">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="relative">
                      <Avatar className="h-12 w-12">
                        <AvatarImage src={member.avatar} />
                        <AvatarFallback>{member.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                      </Avatar>
                      <div className={`absolute -bottom-1 -right-1 h-4 w-4 rounded-full ${getStatusColor(member.status)} border-2 border-background`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold">{member.name}</h3>
                        {getRoleIcon(member.role)}
                      </div>
                      <p className="text-sm text-muted-foreground">{member.email}</p>
                      <div className="mt-2">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span>Contribution Score</span>
                          <span className="font-medium">{member.contributionScore}%</span>
                        </div>
                        <Progress value={member.contributionScore} className="h-2" />
                      </div>
                      <div className="mt-3">
                        <p className="text-xs text-muted-foreground mb-1">Focus Pillars:</p>
                        <div className="flex flex-wrap gap-1">
                          {member.pillars.map((pillar, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {pillar}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        Last active: {member.lastActive.toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="goals" className="space-y-6">
          <div className="space-y-4">
            {sharedGoals.map((goal) => (
              <Card key={goal.id} className="glassmorphism-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{goal.title}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge className={
                        goal.category === 'team' ? 'bg-blue-500/20 text-blue-300' :
                        goal.category === 'individual' ? 'bg-green-500/20 text-green-300' :
                        'bg-purple-500/20 text-purple-300'
                      }>
                        {goal.category}
                      </Badge>
                      <Button size="sm" variant="ghost">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <CardDescription>{goal.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Progress</span>
                      <span className="text-sm font-bold">{goal.progress}%</span>
                    </div>
                    <Progress value={goal.progress} className="h-3" />
                  </div>

                  {/* Participants */}
                  <div className="space-y-2">
                    <span className="text-sm font-medium">Participants</span>
                    <div className="flex -space-x-2">
                      {goal.participants.map((participantId) => {
                        const participant = teamMembers.find(m => m.id === participantId);
                        return (
                          <Avatar key={participantId} className="h-8 w-8 border-2 border-background">
                            <AvatarImage src={participant?.avatar} />
                            <AvatarFallback className="text-xs">
                              {participant?.name.split(' ').map(n => n[0]).join('')}
                            </AvatarFallback>
                          </Avatar>
                        );
                      })}
                    </div>
                  </div>

                  {/* Milestones */}
                  <div className="space-y-2">
                    <span className="text-sm font-medium">Milestones</span>
                    <div className="space-y-1">
                      {goal.milestones.map((milestone) => (
                        <div key={milestone.id} className="flex items-center space-x-3 text-sm glassmorphism-panel p-2">
                          {milestone.completed ? (
                            <CheckCircle2 className="h-4 w-4 text-green-400" />
                          ) : (
                            <div className="h-4 w-4 border-2 border-muted-foreground rounded-full" />
                          )}
                          <span className={milestone.completed ? 'line-through text-muted-foreground' : ''}>
                            {milestone.title}
                          </span>
                          {milestone.completedBy && (
                            <span className="text-xs text-muted-foreground ml-auto">
                              by {teamMembers.find(m => m.id === milestone.completedBy)?.name}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recent Updates */}
                  <div className="space-y-2">
                    <span className="text-sm font-medium">Recent Updates</span>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {goal.updates.slice(0, 3).map((update) => {
                        const author = teamMembers.find(m => m.id === update.author);
                        return (
                          <div key={update.id} className="text-sm glassmorphism-panel p-2">
                            <div className="flex items-center space-x-2">
                              <Avatar className="h-5 w-5">
                                <AvatarImage src={author?.avatar} />
                                <AvatarFallback className="text-xs">
                                  {author?.name.split(' ').map(n => n[0]).join('')}
                                </AvatarFallback>
                              </Avatar>
                              <span className="font-medium">{author?.name}</span>
                              <span className="text-xs text-muted-foreground">
                                {update.timestamp.toLocaleDateString()}
                              </span>
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">{update.message}</p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="accountability" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Handshake className="h-5 w-5" />
                <span>Accountability Partnerships</span>
              </CardTitle>
              <CardDescription>
                Peer support and check-ins to keep everyone motivated and on track
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="glassmorphism-panel p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold">Daily Check-ins</h4>
                    <Badge className="bg-green-500/20 text-green-300">Active</Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Avatar className="h-6 w-6">
                        <AvatarFallback className="text-xs">SC</AvatarFallback>
                      </Avatar>
                      <span className="text-sm">Sarah & Mike</span>
                      <span className="text-xs text-muted-foreground ml-auto">89% effective</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Daily fitness goal check-ins and mutual encouragement
                    </p>
                  </div>
                </div>

                <div className="glassmorphism-panel p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold">Weekly Reviews</h4>
                    <Badge className="bg-blue-500/20 text-blue-300">Scheduled</Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Avatar className="h-6 w-6">
                        <AvatarFallback className="text-xs">ET</AvatarFallback>
                      </Avatar>
                      <span className="text-sm">Emma & Sarah</span>
                      <span className="text-xs text-muted-foreground ml-auto">76% effective</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Professional development goals and learning accountability
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="font-semibold">Partnership Effectiveness</h4>
                <div className="space-y-2">
                  {[
                    { partners: 'Sarah & Mike', effectiveness: 89, type: 'Daily Fitness' },
                    { partners: 'Emma & Sarah', effectiveness: 76, type: 'Learning Goals' },
                    { partners: 'Mike & Emma', effectiveness: 82, type: 'Career Growth' }
                  ].map((partnership, index) => (
                    <div key={index} className="glassmorphism-panel p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">{partnership.partners}</span>
                        <span className="text-sm font-bold">{partnership.effectiveness}%</span>
                      </div>
                      <Progress value={partnership.effectiveness} className="h-2 mb-1" />
                      <p className="text-xs text-muted-foreground">{partnership.type}</p>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="space-y-4">
            {teamInsights.map((insight) => (
              <Card key={insight.id} className="glassmorphism-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5" />
                      <span>{insight.title}</span>
                    </CardTitle>
                    <Badge className={
                      insight.type === 'performance' ? 'bg-blue-500/20 text-blue-300' :
                      insight.type === 'collaboration' ? 'bg-green-500/20 text-green-300' :
                      insight.type === 'motivation' ? 'bg-yellow-500/20 text-yellow-300' :
                      'bg-purple-500/20 text-purple-300'
                    }>
                      {insight.type}
                    </Badge>
                  </div>
                  <CardDescription>{insight.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(insight.metrics).map(([key, value]) => (
                      <div key={key} className="glassmorphism-panel p-3 text-center">
                        <div className="text-2xl font-bold text-primary">{value}%</div>
                        <div className="text-sm text-muted-foreground capitalize">
                          {key.replace('_', ' ')}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-semibold">Recommendations</h4>
                    <div className="space-y-1">
                      {insight.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-center space-x-2 text-sm glassmorphism-panel p-2">
                          <Zap className="h-4 w-4 text-primary" />
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}