import React, { useEffect, useState } from 'react';
import { Bell, Zap, TrendingUp, Target, Activity, Wifi, WifiOff, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { useAppStore } from '../../stores/basicAppStore';
import { useRealTimeData } from '../../hooks/useRealTimeData';
import { useNotifications } from '../../hooks/useNotifications';
import { usePrivacyConsent } from '../../hooks/usePrivacyConsent';
import { realTimeNotificationService } from '../../services/realTimeNotificationService';
import { motion } from 'motion/react';

export default function EnhancedDashboard() {
  const { 
    quickCaptureItems, 
    openQuickCapture, 
    getUnprocessedQuickCapture,  
    processQuickCaptureItem,
    pillars,
    getAllTasks,
    getAllProjects
  } = useEnhancedFeaturesStore();
  
  const { setActiveSection } = useAppStore();
  
  // Real-time data hooks
  const { 
    data: realTimeData, 
    isConnected: isBackendConnected, 
    isLoading: isRealTimeLoading,
    error: realTimeError,
    lastUpdated
  } = useRealTimeData();

  const {
    notifications,
    unreadCount,
    connectionStatus,
    preferences,
    markAsRead,
    sendTestNotification
  } = useNotifications();

  const {
    hasConsent,
    canUseAIFor,
    aiConsent,
    complianceStatus
  } = usePrivacyConsent();

  const [showConnectionStatus, setShowConnectionStatus] = useState(true);
  
  const unprocessedItems = getUnprocessedQuickCapture();
  const recentItems = quickCaptureItems.slice(0, 3);
  
  // Calculate metrics from both local and real-time data
  const allTasks = getAllTasks();
  const allProjects = getAllProjects();
  const completedTasks = allTasks.filter(task => task.status === 'completed');
  
  // Use real-time data if available and AI consent is granted
  const stats = {
    activePillars: realTimeData?.userStats?.active_pillars || pillars.length,
    totalTasks: realTimeData?.userStats?.total_tasks || allTasks.length,
    completedTasksToday: realTimeData?.userStats?.completed_tasks_today || completedTasks.length,
    weeklyProgress: realTimeData?.userStats?.weekly_progress || 
      (allTasks.length > 0 ? Math.round((completedTasks.length / allTasks.length) * 100) : 0),
    urgentTasks: realTimeData?.userStats?.urgent_tasks_count || 
      allTasks.filter(task => task.priority === 'urgent').length,
    averageHealth: realTimeData?.pillarHealth?.length > 0 ? 
      Math.round(realTimeData.pillarHealth.reduce((sum: number, p: any) => sum + p.health_score, 0) / realTimeData.pillarHealth.length) :
      (pillars.length > 0 ? Math.round(pillars.reduce((sum, pillar) => sum + pillar.healthScore, 0) / pillars.length) : 0)
  };

  // Handle navigation to different sections
  const handleNavigateToSection = (section: string) => {
    try {
      setActiveSection(section as any);
    } catch (error) {
      console.error('Navigation error:', error);
    }
  };

  // Generate smart recommendations based on real-time data and AI consent
  const getSmartRecommendations = () => {
    const recommendations = [];

    if (!canUseAIFor('taskAnalysis')) {
      recommendations.push({
        id: 'ai-consent',
        type: 'info',
        title: 'Enable AI Insights',
        message: 'Grant AI consent to receive personalized productivity recommendations.',
        action: () => setActiveSection('settings')
      });
    }

    if (stats.urgentTasks > 0) {
      recommendations.push({
        id: 'urgent-tasks',
        type: 'urgent',
        title: `${stats.urgentTasks} Urgent Task${stats.urgentTasks > 1 ? 's' : ''}`,
        message: 'You have urgent tasks requiring immediate attention.',
        action: () => setActiveSection('tasks')
      });
    }

    if (stats.weeklyProgress > 80) {
      recommendations.push({
        id: 'great-progress',
        type: 'achievement',
        title: 'Excellent Progress!',
        message: `You're at ${stats.weeklyProgress}% completion this week. Keep it up!`,
        action: () => setActiveSection('analytics')
      });
    }

    if (realTimeData?.recommendations) {
      realTimeData.recommendations.slice(0, 2).forEach((rec: any) => {
        recommendations.push({
          id: rec.id,
          type: rec.type,
          title: rec.title,
          message: rec.description,
          action: rec.action_text ? () => setActiveSection('analytics') : undefined
        });
      });
    }

    return recommendations.slice(0, 3);
  };

  const smartRecommendations = getSmartRecommendations();

  // Test notification function
  const handleTestNotification = async () => {
    try {
      await sendTestNotification();
    } catch (error) {
      console.error('Failed to send test notification:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Connection Status */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Enhanced Dashboard</h1>
            <p className="text-[#B8BCC8]">Real-time insights for your personal operating system</p>
          </div>
          <div className="flex items-center space-x-3">
            {/* Backend Connection Status */}
            <div className="flex items-center space-x-2">
              {isBackendConnected ? (
                <Wifi className="w-4 h-4 text-[#10B981]" />
              ) : (
                <WifiOff className="w-4 h-4 text-[#6B7280]" />
              )}
              <span className="text-sm text-[#B8BCC8]">
                {isBackendConnected ? 'Connected' : 'Offline Mode'}
              </span>
            </div>

            {/* Notifications Status */}
            <div className="flex items-center space-x-2">
              <Bell className="w-4 h-4 text-[#F4D03F]" />
              {unreadCount > 0 && (
                <Badge className="bg-[#F4D03F] text-[#0B0D14]">
                  {unreadCount}
                </Badge>
              )}
            </div>

            {/* Real-time Data Status */}
            {connectionStatus.isConnected && (
              <Badge variant="outline" className="text-[#10B981] border-[#10B981]">
                Real-time
              </Badge>
            )}
          </div>
        </div>

        {/* Data Freshness Indicator */}
        {lastUpdated && (
          <div className="mt-2 text-xs text-[#6B7280]">
            Last updated: {new Date(lastUpdated).toLocaleTimeString()}
          </div>
        )}
      </div>

      {/* Privacy Compliance Alert */}
      {complianceStatus && !complianceStatus.compliant && (
        <Alert className="border-[#F59E0B] bg-[rgba(245,158,11,0.1)]">
          <AlertCircle className="w-4 h-4 text-[#F59E0B]" />
          <AlertDescription>
            <div className="flex items-center justify-between">
              <span>Privacy settings need attention for full AI features</span>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setActiveSection('settings')}
                className="border-[#F59E0B] text-[#F59E0B]"
              >
                Review Settings
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Enhanced Stats Grid with Real-time Data */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.button
          onClick={() => handleNavigateToSection('pillars')}
          className="glassmorphism-card p-6 text-left hover:scale-105 transition-all duration-200 cursor-pointer touch-target"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-[rgba(244,208,63,0.2)] flex items-center justify-center">
              <Target className="w-4 h-4 text-[#F4D03F]" />
            </div>
            <div>
              <p className="text-sm text-[#B8BCC8]">Active Pillars</p>
              <div className="flex items-center space-x-2">
                <p className="text-2xl font-semibold text-white">{stats.activePillars}</p>
                {isBackendConnected && (
                  <Badge variant="outline" className="text-xs text-[#10B981] border-[#10B981]">
                    Live
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </motion.button>

        <motion.button
          onClick={() => handleNavigateToSection('tasks')}
          className="glassmorphism-card p-6 text-left hover:scale-105 transition-all duration-200 cursor-pointer touch-target"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-[rgba(16,185,129,0.2)] flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
            </div>
            <div>
              <p className="text-sm text-[#B8BCC8]">Tasks Today</p>
              <div className="flex items-center space-x-2">
                <p className="text-2xl font-semibold text-white">
                  {stats.completedTasksToday}
                  <span className="text-lg text-[#B8BCC8]">/{stats.totalTasks}</span>
                </p>
                {stats.urgentTasks > 0 && (
                  <Badge className="bg-[#EF4444] text-white text-xs">
                    {stats.urgentTasks} urgent
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </motion.button>

        <motion.button
          onClick={() => handleNavigateToSection('analytics')}
          className="glassmorphism-card p-6 text-left hover:scale-105 transition-all duration-200 cursor-pointer touch-target"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-[rgba(59,130,246,0.2)] flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-[#3B82F6]" />
            </div>
            <div>
              <p className="text-sm text-[#B8BCC8]">Weekly Progress</p>
              <div className="flex items-center space-x-2">
                <p className="text-2xl font-semibold text-white">{stats.weeklyProgress}%</p>
                <Progress value={stats.weeklyProgress} className="w-16 h-2" />
              </div>
            </div>
          </div>
        </motion.button>

        <motion.button
          onClick={() => handleNavigateToSection('analytics')}
          className="glassmorphism-card p-6 text-left hover:scale-105 transition-all duration-200 cursor-pointer touch-target"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-[rgba(139,92,246,0.2)] flex items-center justify-center">
              <Activity className="w-4 h-4 text-[#8B5CF6]" />
            </div>
            <div>
              <p className="text-sm text-[#B8BCC8]">Health Score</p>
              <div className="flex items-center space-x-2">
                <p className="text-2xl font-semibold text-white">{stats.averageHealth}%</p>
                {isRealTimeLoading && (
                  <div className="w-4 h-4 animate-spin rounded-full border-2 border-[#F4D03F] border-t-transparent"></div>
                )}
              </div>
            </div>
          </div>
        </motion.button>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Smart Recommendations with AI Integration */}
        <div className="lg:col-span-1">
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Zap className="w-5 h-5 text-[#F4D03F]" />
                <span>Smart Recommendations</span>
                {canUseAIFor('goalRecommendations') && (
                  <Badge variant="outline" className="text-[#8B5CF6] border-[#8B5CF6]">
                    AI Powered
                  </Badge>
                )}
              </CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                {canUseAIFor('goalRecommendations') 
                  ? 'Personalized insights based on your activity patterns'
                  : 'Enable AI features in Settings for personalized recommendations'
                }
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {smartRecommendations.map((rec) => (
                <motion.div
                  key={rec.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`p-4 rounded-lg border transition-all hover:scale-[1.02] cursor-pointer ${
                    rec.type === 'urgent' ? 'border-[#EF4444] bg-[rgba(239,68,68,0.1)]' :
                    rec.type === 'achievement' ? 'border-[#10B981] bg-[rgba(16,185,129,0.1)]' :
                    rec.type === 'info' ? 'border-[#3B82F6] bg-[rgba(59,130,246,0.1)]' :
                    'border-[rgba(244,208,63,0.2)] bg-[rgba(244,208,63,0.05)]'
                  }`}
                  onClick={rec.action}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      rec.type === 'urgent' ? 'bg-[rgba(239,68,68,0.2)]' :
                      rec.type === 'achievement' ? 'bg-[rgba(16,185,129,0.2)]' :
                      rec.type === 'info' ? 'bg-[rgba(59,130,246,0.2)]' :
                      'bg-[rgba(244,208,63,0.2)]'
                    }`}>
                      {rec.type === 'urgent' && <AlertCircle className="w-4 h-4 text-[#EF4444]" />}
                      {rec.type === 'achievement' && <CheckCircle2 className="w-4 h-4 text-[#10B981]" />}
                      {rec.type === 'info' && <Zap className="w-4 h-4 text-[#3B82F6]" />}
                      {rec.type === 'tip' && <Zap className="w-4 h-4 text-[#F4D03F]" />}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-white mb-1">{rec.title}</h4>
                      <p className="text-sm text-[#B8BCC8]">{rec.message}</p>
                    </div>
                  </div>
                </motion.div>
              ))}

              {smartRecommendations.length === 0 && (
                <div className="text-center py-8">
                  <Zap className="w-12 h-12 text-[#6B7280] mx-auto mb-4" />
                  <h3 className="text-white font-medium mb-2">No recommendations yet</h3>
                  <p className="text-[#B8BCC8] text-sm mb-4">
                    {canUseAIFor('goalRecommendations') 
                      ? 'Complete more tasks to receive AI-powered insights'
                      : 'Enable AI features to receive personalized recommendations'
                    }
                  </p>
                  {!canUseAIFor('goalRecommendations') && (
                    <Button
                      onClick={() => setActiveSection('settings')}
                      variant="outline"
                      className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                    >
                      Enable AI Features
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Real-time Notifications Panel */}
        <div className="lg:col-span-1">
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Bell className="w-5 h-5 text-[#F4D03F]" />
                <span>Live Updates</span>
                {connectionStatus.isConnected && (
                  <div className="w-2 h-2 bg-[#10B981] rounded-full animate-pulse"></div>
                )}
              </CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                Recent notifications and system updates
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {notifications.slice(0, 5).map((notification) => (
                <motion.div
                  key={notification.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`p-3 rounded-lg border cursor-pointer transition-all hover:scale-[1.02] ${
                    notification.isRead 
                      ? 'border-[rgba(244,208,63,0.1)] bg-[rgba(26,29,41,0.3)]'
                      : 'border-[rgba(244,208,63,0.2)] bg-[rgba(244,208,63,0.05)]'
                  }`}
                  onClick={() => !notification.isRead && markAsRead([notification.id])}
                >
                  <div className="flex items-start space-x-2">
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      notification.isRead ? 'bg-[#6B7280]' : 'bg-[#F4D03F]'
                    }`}></div>
                    <div className="flex-1 min-w-0">
                      <h5 className={`text-sm font-medium ${
                        notification.isRead ? 'text-[#B8BCC8]' : 'text-white'
                      }`}>
                        {notification.title}
                      </h5>
                      <p className="text-xs text-[#6B7280] line-clamp-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-[#6B7280] mt-1">
                        {new Date(notification.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}

              {notifications.length === 0 && (
                <div className="text-center py-6">
                  <Bell className="w-8 h-8 text-[#6B7280] mx-auto mb-2" />
                  <p className="text-sm text-[#B8BCC8]">No notifications yet</p>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleTestNotification}
                    className="mt-2 border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                  >
                    Send Test
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Quick Capture with AI Suggestions */}
        <div className="lg:col-span-2">
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Zap className="w-5 h-5 text-[#F4D03F]" />
                <span>Quick Capture</span>
                {unprocessedItems.length > 0 && (
                  <Badge className="bg-[#F4D03F] text-[#0B0D14]">
                    {unprocessedItems.length} new
                  </Badge>
                )}
              </CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                Capture ideas instantly with AI-powered categorization
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button 
                onClick={openQuickCapture}
                className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              >
                <Zap className="w-4 h-4 mr-2" />
                Open Quick Capture
              </Button>

              {recentItems.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-[#B8BCC8]">Recent Captures:</h4>
                  {recentItems.map((item) => (
                    <div 
                      key={item.id} 
                      className={`p-3 rounded-lg border transition-all ${
                        item.processed 
                          ? 'border-[#10B981] bg-[rgba(16,185,129,0.1)]' 
                          : 'border-[rgba(244,208,63,0.2)] bg-[rgba(244,208,63,0.05)]'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <Badge variant="outline" className="text-xs">
                              {item.type}
                            </Badge>
                            {item.processed && (
                              <Badge className="bg-[#10B981] text-white text-xs">
                                Processed
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-white line-clamp-2 mb-2">
                            {item.content}
                          </p>
                          {item.suggestedPillar && (
                            <div className="flex items-center space-x-1 text-xs text-[#B8BCC8]">
                              <Target className="w-3 h-3" />
                              <span>{item.suggestedPillar}</span>
                              {item.suggestedArea && (
                                <>
                                  <span>→</span>
                                  <span>{item.suggestedArea}</span>
                                </>
                              )}
                            </div>
                          )}
                        </div>
                        {!item.processed && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => processQuickCaptureItem(
                              item.id, 
                              item.suggestedPillar || 'Personal Development',
                              item.suggestedArea || 'Learning & Growth'
                            )}
                            className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                          >
                            Process
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>


      </div>
    </div>
  );
}