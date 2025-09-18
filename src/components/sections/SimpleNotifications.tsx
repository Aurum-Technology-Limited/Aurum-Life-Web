import { Bell, Check, X, Clock, AlertCircle, Info, CheckCircle, Settings, Wifi, WifiOff, Zap, Target, TrendingUp, Award } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { ScrollArea } from '../ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import { useNotifications } from '../../hooks/useNotifications';
import { RealTimeNotification } from '../../services/realTimeNotificationService';

interface NotificationsProps {
  onClose?: () => void;
}

export default function SimpleNotifications({ onClose }: NotificationsProps) {
  const {
    notifications,
    unreadCount,
    connectionStatus,
    isLoading,
    error,
    markAsRead,
    markAllAsRead,
    removeNotification,
    sendTestNotification
  } = useNotifications();

  const getNotificationIcon = (notification: RealTimeNotification) => {
    switch (notification.type) {
      case 'task_reminder':
        return <Clock className="w-4 h-4 text-[#3B82F6]" />;
      case 'project_update':
        return <TrendingUp className="w-4 h-4 text-[#10B981]" />;
      case 'pillar_milestone':
        return <Target className="w-4 h-4 text-[#8B5CF6]" />;
      case 'ai_insight':
        return <Zap className="w-4 h-4 text-[#F4D03F]" />;
      case 'goal_achievement':
        return <Award className="w-4 h-4 text-[#10B981]" />;
      case 'deadline_approaching':
        return <AlertCircle className="w-4 h-4 text-[#F59E0B]" />;
      case 'system_alert':
      default:
        return <Info className="w-4 h-4 text-[#3B82F6]" />;
    }
  };

  const getBorderColor = (notification: RealTimeNotification) => {
    const priorityColors = {
      urgent: 'border-l-[#EF4444]',
      high: 'border-l-[#F59E0B]',
      medium: 'border-l-[#3B82F6]',
      low: 'border-l-[#6B7280]',
    };
    return priorityColors[notification.priority] || priorityColors.medium;
  };

  const getCategoryColor = (category: string) => {
    const categoryColors = {
      productivity: '#3B82F6',
      insights: '#F4D03F',
      system: '#6B7280',
      achievements: '#10B981',
      reminders: '#8B5CF6',
    };
    return categoryColors[category as keyof typeof categoryColors] || categoryColors.system;
  };

  const handleNotificationClick = async (notification: RealTimeNotification) => {
    if (!notification.isRead) {
      await markAsRead([notification.id]);
    }

    // Execute primary action if available
    if (notification.actions?.[0]) {
      const action = notification.actions[0];
      if (action.action === 'navigate' && action.data?.section) {
        // This would integrate with your navigation system
        console.log('Navigate to:', action.data.section);
      }
    }
  };

  const handleRemoveNotification = (id: string, event: React.MouseEvent) => {
    event.stopPropagation();
    removeNotification(id);
  };

  const isRealTimeEnabled = connectionStatus.isConnected;

  return (
    <div className="max-w-5xl mx-auto">
      <Card className="glassmorphism-card border-0">
        <CardHeader className="flex flex-row items-center justify-between pb-4">
          <div className="flex items-center space-x-3">
            <Bell className="w-6 h-6 text-[#F4D03F]" />
            <div>
              <CardTitle className="text-white">Notifications</CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                Real-time updates and AI-powered insights
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {/* Connection Status */}
            <div className="flex items-center space-x-1">
              {isRealTimeEnabled ? (
                <Wifi className="w-4 h-4 text-[#10B981]" />
              ) : (
                <WifiOff className="w-4 h-4 text-[#6B7280]" />
              )}
              <span className={`text-xs ${isRealTimeEnabled ? 'text-[#10B981]' : 'text-[#6B7280]'}`}>
                {isRealTimeEnabled ? 'Live' : 'Offline'}
              </span>
            </div>

            {unreadCount > 0 && (
              <Badge className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                {unreadCount} new
              </Badge>
            )}
            
            {onClose && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
              >
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>
        </CardHeader>

        <CardContent className="p-0">
          {/* Error Display */}
          {error && (
            <div className="px-6 pb-4">
              <Alert className="border-[#F59E0B] bg-[rgba(245,158,11,0.1)]">
                <AlertCircle className="h-4 w-4 text-[#F59E0B]" />
                <AlertDescription className="text-[#F59E0B]">
                  {error}
                </AlertDescription>
              </Alert>
            </div>
          )}

          <Tabs defaultValue="all" className="w-full">
            <div className="px-6 pb-4">
              <div className="flex items-center justify-between mb-4">
                <TabsList className="bg-[rgba(26,29,41,0.6)] border border-[rgba(244,208,63,0.2)]">
                  <TabsTrigger value="all" className="data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14]">
                    All ({notifications.length})
                  </TabsTrigger>
                  <TabsTrigger value="unread" className="data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14]">
                    Unread ({unreadCount})
                  </TabsTrigger>
                  <TabsTrigger value="insights" className="data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14]">
                    AI Insights
                  </TabsTrigger>
                </TabsList>

                <div className="flex items-center space-x-2">
                  {unreadCount > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={markAllAsRead}
                      disabled={isLoading}
                      className="text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                    >
                      <Check className="w-4 h-4 mr-1" />
                      Mark all read
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={sendTestNotification}
                    className="text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                  >
                    <Zap className="w-4 h-4 mr-1" />
                    Test
                  </Button>
                </div>
              </div>
            </div>

            <TabsContent value="all" className="m-0">
              <ScrollArea className="h-[500px]">
                <div className="space-y-1 px-6 pb-6">
                  {notifications.length === 0 ? (
                    <div className="text-center py-12">
                      <Bell className="w-12 h-12 text-[#6B7280] mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-white mb-2">No notifications</h3>
                      <p className="text-[#B8BCC8] mb-4">
                        You're all caught up! Your real-time notifications will appear here.
                      </p>
                      {!isRealTimeEnabled && (
                        <p className="text-[#6B7280] text-sm">
                          Working offline - notifications will sync when connection is restored.
                        </p>
                      )}
                    </div>
                  ) : (
                    notifications.map((notification, index) => (
                      <NotificationItem
                        key={notification.id}
                        notification={notification}
                        onClick={() => handleNotificationClick(notification)}
                        onRemove={(e) => handleRemoveNotification(notification.id, e)}
                        getIcon={getNotificationIcon}
                        getBorderColor={getBorderColor}
                        getCategoryColor={getCategoryColor}
                        showSeparator={index < notifications.length - 1}
                      />
                    ))
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="unread" className="m-0">
              <ScrollArea className="h-[500px]">
                <div className="space-y-1 px-6 pb-6">
                  {notifications.filter(n => !n.isRead).length === 0 ? (
                    <div className="text-center py-12">
                      <CheckCircle className="w-12 h-12 text-[#10B981] mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-white mb-2">All caught up!</h3>
                      <p className="text-[#B8BCC8]">
                        No unread notifications. You're on top of everything!
                      </p>
                    </div>
                  ) : (
                    notifications
                      .filter(n => !n.isRead)
                      .map((notification, index, arr) => (
                        <NotificationItem
                          key={notification.id}
                          notification={notification}
                          onClick={() => handleNotificationClick(notification)}
                          onRemove={(e) => handleRemoveNotification(notification.id, e)}
                          getIcon={getNotificationIcon}
                          getBorderColor={getBorderColor}
                          getCategoryColor={getCategoryColor}
                          showSeparator={index < arr.length - 1}
                        />
                      ))
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="insights" className="m-0">
              <ScrollArea className="h-[500px]">
                <div className="space-y-1 px-6 pb-6">
                  {notifications.filter(n => n.type === 'ai_insight').length === 0 ? (
                    <div className="text-center py-12">
                      <Zap className="w-12 h-12 text-[#F4D03F] mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-white mb-2">No AI insights yet</h3>
                      <p className="text-[#B8BCC8]">
                        AI-powered recommendations and insights will appear here.
                      </p>
                    </div>
                  ) : (
                    notifications
                      .filter(n => n.type === 'ai_insight')
                      .map((notification, index, arr) => (
                        <NotificationItem
                          key={notification.id}
                          notification={notification}
                          onClick={() => handleNotificationClick(notification)}
                          onRemove={(e) => handleRemoveNotification(notification.id, e)}
                          getIcon={getNotificationIcon}
                          getBorderColor={getBorderColor}
                          getCategoryColor={getCategoryColor}
                          showSeparator={index < arr.length - 1}
                        />
                      ))
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}

interface NotificationItemProps {
  notification: RealTimeNotification;
  onClick: () => void;
  onRemove: (e: React.MouseEvent) => void;
  getIcon: (notification: RealTimeNotification) => React.ReactNode;
  getBorderColor: (notification: RealTimeNotification) => string;
  getCategoryColor: (category: string) => string;
  showSeparator: boolean;
}

function NotificationItem({
  notification,
  onClick,
  onRemove,
  getIcon,
  getBorderColor,
  getCategoryColor,
  showSeparator
}: NotificationItemProps) {
  // Simple time formatting without external dependencies
  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMinutes < 1) return 'just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return time.toLocaleDateString();
  };

  const timeAgo = getTimeAgo(notification.timestamp);

  return (
    <div>
      <div 
        className={`p-4 rounded-lg border-l-4 transition-all duration-200 ${
          getBorderColor(notification)
        } ${
          notification.isRead 
            ? 'bg-[rgba(26,29,41,0.3)]' 
            : 'bg-[rgba(244,208,63,0.05)] border-r border-t border-b border-[rgba(244,208,63,0.1)]'
        } hover:bg-[rgba(244,208,63,0.08)] cursor-pointer group`}
        onClick={onClick}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 flex-1 min-w-0">
            {getIcon(notification)}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <h4 className={`font-medium truncate ${
                  notification.isRead ? 'text-[#B8BCC8]' : 'text-white'
                }`}>
                  {notification.title}
                </h4>
                {!notification.isRead && (
                  <div className="w-2 h-2 bg-[#F4D03F] rounded-full flex-shrink-0"></div>
                )}
                <Badge 
                  variant="outline" 
                  className="text-xs px-2 py-0 border-0 flex-shrink-0"
                  style={{ 
                    backgroundColor: `${getCategoryColor(notification.category)}20`,
                    color: getCategoryColor(notification.category)
                  }}
                >
                  {notification.category}
                </Badge>
              </div>
              
              <p className={`text-sm mb-2 ${
                notification.isRead ? 'text-[#6B7280]' : 'text-[#B8BCC8]'
              }`}>
                {notification.message}
              </p>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-xs text-[#6B7280]">
                  <Clock className="w-3 h-3" />
                  <span>{timeAgo}</span>
                  <span>•</span>
                  <span className="capitalize">{notification.priority} priority</span>
                </div>
                
                {notification.actions && notification.actions.length > 0 && (
                  <div className="flex items-center space-x-1">
                    {notification.actions.slice(0, 2).map((action) => (
                      <Button
                        key={action.id}
                        variant="ghost"
                        size="sm"
                        className="text-xs h-6 px-2 text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)] opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Handle action
                        }}
                      >
                        {action.label}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={onRemove}
            className="text-[#6B7280] hover:text-[#EF4444] hover:bg-[rgba(239,68,68,0.1)] h-8 w-8 ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <X className="w-3 h-3" />
          </Button>
        </div>
      </div>
      
      {showSeparator && (
        <Separator className="bg-[rgba(244,208,63,0.1)] my-1" />
      )}
    </div>
  );
}