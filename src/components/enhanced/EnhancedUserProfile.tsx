/**
 * Enhanced User Profile Component
 * Comprehensive user profile with extended metadata and AI preferences
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  User, Settings, Brain, BarChart3, Trophy, 
  Calendar, Clock, Target, Zap, Eye, 
  Shield, Edit2, Save, X, Camera,
  Activity, TrendingUp, Award, Star,
  Globe, Smartphone, Bell, Lock
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { usePhase2Store } from '../../stores/phase2IntegrationStore';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Switch } from '../ui/switch';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { Avatar, AvatarContent, AvatarImage, AvatarFallback } from '../ui/avatar';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Separator } from '../ui/separator';
import toast from '../../utils/toast';

interface UserStats {
  totalTasks: number;
  completedTasks: number;
  activeProjects: number;
  totalPillars: number;
  journalEntries: number;
  daysSinceJoined: number;
  currentStreak: number;
  longestStreak: number;
  productivityScore: number;
  lastActiveDate: string;
}

interface AIPreferences {
  enableSmartSuggestions: boolean;
  enableProductivityInsights: boolean;
  enableGoalRecommendations: boolean;
  enableTimeBlocking: boolean;
  enableHabitTracking: boolean;
  dataProcessingLevel: 'minimal' | 'standard' | 'comprehensive';
  insightFrequency: 'realtime' | 'daily' | 'weekly';
  privacyMode: 'open' | 'balanced' | 'strict';
}

interface EnhancedProfile {
  bio: string;
  timezone: string;
  workingHours: { start: string; end: string };
  focusAreas: string[];
  personalityType: string;
  workStyle: string;
  communicationPreference: string;
  goals: string[];
  achievements: string[];
  customFields: Record<string, string>;
}

interface EnhancedUserProfileProps {
  className?: string;
  onClose?: () => void;
}

const EnhancedUserProfile: React.FC<EnhancedUserProfileProps> = React.memo(({
  className = '',
  onClose
}) => {
  const { user, updateUserProfile } = useAuthStore();
  
  // Use individual selectors to prevent infinite re-renders
  const productivityMetrics = usePhase2Store(state => state.productivityMetrics);
  const aiInsights = usePhase2Store(state => state.aiInsights);
  
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [showAvatarModal, setShowAvatarModal] = useState(false);

  // Profile state
  const [profile, setProfile] = useState<EnhancedProfile>({
    bio: '',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    workingHours: { start: '09:00', end: '17:00' },
    focusAreas: [],
    personalityType: '',
    workStyle: 'balanced',
    communicationPreference: 'email',
    goals: [],
    achievements: [],
    customFields: {}
  });

  // AI Preferences state
  const [aiPreferences, setAIPreferences] = useState<AIPreferences>({
    enableSmartSuggestions: true,
    enableProductivityInsights: true,
    enableGoalRecommendations: true,
    enableTimeBlocking: false,
    enableHabitTracking: false,
    dataProcessingLevel: 'standard',
    insightFrequency: 'daily',
    privacyMode: 'balanced'
  });

  // User statistics - initialize with static values first
  const [userStats, setUserStats] = useState<UserStats>(() => ({
    totalTasks: 0,
    completedTasks: 0,
    activeProjects: 0,
    totalPillars: 0,
    journalEntries: 0,
    daysSinceJoined: 0,
    currentStreak: 0,
    longestStreak: 0,
    productivityScore: 0,
    lastActiveDate: new Date().toISOString()
  }));

  // Define loadProfileData before using it in useEffect
  const loadProfileData = React.useCallback(async () => {
    if (!user?.id) return;
    
    try {
      // Load from localStorage for now (would be from API in production)
      const storedProfile = localStorage.getItem(`aurum-profile-${user.id}`);
      const storedAIPrefs = localStorage.getItem(`aurum-ai-preferences-${user.id}`);
      const storedStats = localStorage.getItem(`aurum-user-stats-${user.id}`);

      if (storedProfile) {
        setProfile(JSON.parse(storedProfile));
      }

      if (storedAIPrefs) {
        setAIPreferences(JSON.parse(storedAIPrefs));
      }

      if (storedStats) {
        setUserStats(JSON.parse(storedStats));
      } else {
        // Calculate stats from stored data inline to avoid circular dependency
        try {
          const pillars = JSON.parse(localStorage.getItem('aurum-pillars') || '[]');
          const projects = JSON.parse(localStorage.getItem('aurum-projects') || '[]');
          const tasks = JSON.parse(localStorage.getItem('aurum-tasks') || '[]');
          const journalEntries = JSON.parse(localStorage.getItem('aurum-journal-entries') || '[]');

          const completedTasks = tasks.filter((t: any) => t?.status === 'completed').length;
          const activeProjects = projects.filter((p: any) => p?.status === 'active').length;
          
          const joinDate = new Date(user.created_at || Date.now());
          const daysSinceJoined = Math.floor((Date.now() - joinDate.getTime()) / (1000 * 60 * 60 * 24));

          const newStats: UserStats = {
            totalTasks: tasks.length,
            completedTasks,
            activeProjects,
            totalPillars: pillars.length,
            journalEntries: journalEntries.length,
            daysSinceJoined,
            currentStreak: 7, // Placeholder
            longestStreak: 21, // Placeholder
            productivityScore: 75, // Will be updated by useEffect when metrics load
            lastActiveDate: new Date().toISOString()
          };

          setUserStats(newStats);
        } catch (error) {
          console.error('Failed to calculate initial user stats:', error);
        }
      }
    } catch (error) {
      console.error('Failed to load profile data:', error);
    }
  }, [user?.id, user?.created_at]);

  // Load profile data - now loadProfileData is defined above
  useEffect(() => {
    loadProfileData();
  }, [loadProfileData]);

  // Update productivity score when metrics change - prevent setState during render
  useEffect(() => {
    if (productivityMetrics?.productivityScore !== undefined) {
      setUserStats(prevStats => ({
        ...prevStats,
        productivityScore: productivityMetrics.productivityScore
      }));
    }
  }, [productivityMetrics?.productivityScore]);

  const handleSaveProfile = async () => {
    setLoading(true);
    try {
      // Save to localStorage (would be API call in production)
      localStorage.setItem(`aurum-profile-${user?.id}`, JSON.stringify(profile));
      localStorage.setItem(`aurum-ai-preferences-${user?.id}`, JSON.stringify(aiPreferences));
      
      // Update auth store with basic info
      if (updateUserProfile) {
        await updateUserProfile({
          name: user?.name || '',
          bio: profile.bio,
          timezone: profile.timezone
        });
      }

      setIsEditing(false);
      toast.success('Profile updated successfully');
    } catch (error) {
      console.error('Failed to save profile:', error);
      toast.error('Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  const getProfileCompletionScore = (): number => {
    const fields = [
      profile.bio,
      profile.personalityType,
      profile.workStyle,
      profile.focusAreas.length > 0,
      profile.goals.length > 0,
      aiPreferences.dataProcessingLevel !== 'minimal'
    ];
    
    const completedFields = fields.filter(Boolean).length;
    return Math.round((completedFields / fields.length) * 100);
  };

  const getAchievementLevel = (): string => {
    const score = userStats.productivityScore;
    if (score >= 90) return 'Master';
    if (score >= 80) return 'Expert';
    if (score >= 70) return 'Advanced';
    if (score >= 60) return 'Intermediate';
    return 'Beginner';
  };

  if (!user) {
    return (
      <div className="glassmorphism-card p-6">
        <div className="text-center">
          <p className="text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`${className}`}
    >
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="glassmorphism-card border-0 grid w-full grid-cols-3">
          <TabsTrigger value="overview" className="text-foreground">Overview</TabsTrigger>
          <TabsTrigger value="ai-preferences" className="text-foreground">AI Settings</TabsTrigger>
          <TabsTrigger value="insights" className="text-foreground">Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Profile Header */}
          <div className="flex flex-col sm:flex-row items-start gap-6">
            <div className="relative">
              <Avatar className="w-24 h-24">
                <AvatarImage src={user?.avatar_url} />
                <AvatarFallback className="text-2xl bg-primary/20 text-primary">
                  {user?.name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <Button
                size="sm"
                variant="outline"
                className="absolute -bottom-2 -right-2 h-8 w-8 rounded-full p-0"
                onClick={() => setShowAvatarModal(true)}
              >
                <Camera className="w-4 h-4" />
              </Button>
            </div>

            <div className="flex-1 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-foreground">{user?.name}</h2>
                  <p className="text-muted-foreground">{user?.email}</p>
                </div>
                <Button
                  onClick={() => setIsEditing(!isEditing)}
                  variant="outline"
                  size="sm"
                >
                  {isEditing ? <X className="w-4 h-4 mr-2" /> : <Edit2 className="w-4 h-4 mr-2" />}
                  {isEditing ? 'Cancel' : 'Edit Profile'}
                </Button>
              </div>

              {isEditing ? (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="bio">Bio</Label>
                    <Textarea
                      id="bio"
                      value={profile.bio}
                      onChange={(e) => setProfile(prev => ({ ...prev, bio: e.target.value }))}
                      placeholder="Tell us about yourself..."
                      className="resize-none"
                    />
                  </div>
                  <div className="flex gap-4">
                    <div className="flex-1">
                      <Label htmlFor="timezone">Timezone</Label>
                      <Input
                        id="timezone"
                        value={profile.timezone}
                        onChange={(e) => setProfile(prev => ({ ...prev, timezone: e.target.value }))}
                      />
                    </div>
                    <div className="flex-1">
                      <Label htmlFor="workStyle">Work Style</Label>
                      <Input
                        id="workStyle"
                        value={profile.workStyle}
                        onChange={(e) => setProfile(prev => ({ ...prev, workStyle: e.target.value }))}
                        placeholder="e.g., focused, collaborative"
                      />
                    </div>
                  </div>
                  <Button onClick={handleSaveProfile} disabled={loading} className="w-full">
                    {loading ? (
                      <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full mr-2" />
                    ) : (
                      <Save className="w-4 h-4 mr-2" />
                    )}
                    Save Changes
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <p className="text-foreground">{profile.bio || 'No bio added yet.'}</p>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Globe className="w-3 h-3" />
                      {profile.timezone}
                    </Badge>
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Activity className="w-3 h-3" />
                      {getAchievementLevel()}
                    </Badge>
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {userStats.daysSinceJoined} days
                    </Badge>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Profile Completion */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Profile Completion
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">
                    Complete your profile to unlock more features
                  </span>
                  <span className="font-medium text-primary">
                    {getProfileCompletionScore()}%
                  </span>
                </div>
                <Progress value={getProfileCompletionScore()} className="h-2" />
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="glassmorphism-card text-center">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-green-400">
                  {userStats.completedTasks}
                </div>
                <div className="text-xs text-muted-foreground">Tasks Done</div>
              </CardContent>
            </Card>

            <Card className="glassmorphism-card text-center">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-blue-400">
                  {userStats.activeProjects}
                </div>
                <div className="text-xs text-muted-foreground">Active Projects</div>
              </CardContent>
            </Card>

            <Card className="glassmorphism-card text-center">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-primary">
                  {userStats.currentStreak}
                </div>
                <div className="text-xs text-muted-foreground">Day Streak</div>
              </CardContent>
            </Card>

            <Card className="glassmorphism-card text-center">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-purple-400">
                  {userStats.productivityScore}%
                </div>
                <div className="text-xs text-muted-foreground">Productivity</div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="ai-preferences" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-primary" />
                AI Intelligence Features
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label htmlFor="smart-suggestions">Smart Suggestions</Label>
                  <p className="text-sm text-muted-foreground">
                    Get intelligent recommendations for tasks and goals
                  </p>
                </div>
                <Switch
                  id="smart-suggestions"
                  checked={aiPreferences.enableSmartSuggestions}
                  onCheckedChange={(checked) => 
                    setAIPreferences(prev => ({ ...prev, enableSmartSuggestions: checked }))
                  }
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label htmlFor="productivity-insights">Productivity Insights</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive AI-powered analysis of your productivity patterns
                  </p>
                </div>
                <Switch
                  id="productivity-insights"
                  checked={aiPreferences.enableProductivityInsights}
                  onCheckedChange={(checked) => 
                    setAIPreferences(prev => ({ ...prev, enableProductivityInsights: checked }))
                  }
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label htmlFor="goal-recommendations">Goal Recommendations</Label>
                  <p className="text-sm text-muted-foreground">
                    Get personalized goal suggestions based on your activities
                  </p>
                </div>
                <Switch
                  id="goal-recommendations"
                  checked={aiPreferences.enableGoalRecommendations}
                  onCheckedChange={(checked) => 
                    setAIPreferences(prev => ({ ...prev, enableGoalRecommendations: checked }))
                  }
                />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                Privacy & Data Processing
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Data Processing Level</Label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  {(['minimal', 'standard', 'comprehensive'] as const).map(level => (
                    <button
                      key={level}
                      onClick={() => setAIPreferences(prev => ({ ...prev, dataProcessingLevel: level }))}
                      className={`p-3 rounded-lg border transition-all ${
                        aiPreferences.dataProcessingLevel === level
                          ? 'border-primary bg-primary/20 text-primary'
                          : 'border-border bg-card hover:bg-accent'
                      }`}
                    >
                      <div className="font-medium capitalize">{level}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {level === 'minimal' && 'Basic features only'}
                        {level === 'standard' && 'Balanced experience'}
                        {level === 'comprehensive' && 'Full AI capabilities'}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Button onClick={handleSaveProfile} disabled={loading} className="w-full">
            {loading ? (
              <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full mr-2" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Save AI Preferences
          </Button>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          {/* AI Insights */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-primary" />
                AI Insights ({aiInsights?.length || 0})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {aiInsights && aiInsights.length > 0 ? (
                <div className="space-y-3">
                  {aiInsights.slice(0, 3).map((insight, index) => (
                    <div key={insight.id || index} className="p-3 glassmorphism-panel rounded-lg">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1">
                          <h4 className="font-medium text-foreground">{insight.title}</h4>
                          <p className="text-sm text-muted-foreground mt-1">
                            {insight.description}
                          </p>
                        </div>
                        <Badge
                          variant="secondary"
                          className={
                            insight.priority === 'high' ? 'bg-red-500/20 text-red-300' :
                            insight.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                            'bg-green-500/20 text-green-300'
                          }
                        >
                          {insight.priority}
                        </Badge>
                      </div>
                    </div>
                  ))}
                  {aiInsights.length > 3 && (
                    <Button variant="outline" size="sm" className="w-full">
                      View All {aiInsights.length} Insights
                    </Button>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No insights yet</h3>
                  <p className="text-muted-foreground text-sm">
                    Use Aurum Life more to generate personalized insights
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Achievements */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="w-5 h-5 text-primary" />
                Achievements
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="flex items-center gap-3 p-3 glassmorphism-panel rounded-lg">
                  <Award className="w-8 h-8 text-yellow-400" />
                  <div>
                    <h4 className="font-medium">Getting Started</h4>
                    <p className="text-sm text-muted-foreground">Created your profile</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 glassmorphism-panel rounded-lg">
                  <Star className="w-8 h-8 text-blue-400" />
                  <div>
                    <h4 className="font-medium">Consistent User</h4>
                    <p className="text-sm text-muted-foreground">{userStats.daysSinceJoined} days active</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Avatar Modal */}
      {showAvatarModal && (
        <Dialog open={showAvatarModal} onOpenChange={setShowAvatarModal}>
          <DialogContent className="glassmorphism-card border-0">
            <DialogHeader>
              <DialogTitle>Update Profile Picture</DialogTitle>
            </DialogHeader>
            <div className="text-center py-8">
              <p className="text-muted-foreground">
                Avatar upload functionality would be implemented here.
              </p>
              <Button 
                onClick={() => setShowAvatarModal(false)} 
                className="mt-4"
              >
                Close
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </motion.div>
  );
});

EnhancedUserProfile.displayName = 'EnhancedUserProfile';

export default EnhancedUserProfile;