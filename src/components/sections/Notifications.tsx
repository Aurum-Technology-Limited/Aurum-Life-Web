import { useState } from 'react';
import { Bell, Check, X, Clock, AlertCircle, Info, CheckCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { ScrollArea } from '../ui/scroll-area';

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface NotificationsProps {
  onClose?: () => void;
}

export default function Notifications({ onClose }: NotificationsProps) {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      type: 'success',
      title: 'Goal Achievement',
      message: 'You completed "Complete Q4 Strategic Planning" project ahead of schedule!',
      timestamp: '2 minutes ago',
      isRead: false,
      action: {
        label: 'View Details',
        onClick: () => console.log('View goal details')
      }
    },
    {
      id: '2',
      type: 'info',
      title: 'AI Insight Available',
      message: 'New productivity patterns identified in your Health & Wellness pillar.',
      timestamp: '1 hour ago',
      isRead: false,
      action: {
        label: 'View Insights',
        onClick: () => console.log('View AI insights')
      }
    },
    {
      id: '3',
      type: 'warning',
      title: 'Task Due Soon',
      message: 'Review quarterly metrics is due in 2 hours.',
      timestamp: '3 hours ago',
      isRead: true
    },
    {
      id: '4',
      type: 'info',
      title: 'Weekly Journal Reminder',
      message: 'Time for your weekly reflection. Share your wins and learnings.',
      timestamp: '1 day ago',
      isRead: true
    },
    {
      id: '5',
      type: 'success',
      title: 'Streak Achievement',
      message: '🔥 7-day consistency streak in your Morning Routine!',
      timestamp: '2 days ago',
      isRead: true
    }
  ]);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-[#10B981]" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-[#F59E0B]" />;
      case 'error':
        return <X className="w-4 h-4 text-[#EF4444]" />;
      default:
        return <Info className="w-4 h-4 text-[#3B82F6]" />;
    }
  };

  const getBorderColor = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return 'border-l-[#10B981]';
      case 'warning':
        return 'border-l-[#F59E0B]';
      case 'error':
        return 'border-l-[#EF4444]';
      default:
        return 'border-l-[#3B82F6]';
    }
  };

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, isRead: true } : n)
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(n => ({ ...n, isRead: true }))
    );
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <div className="max-w-4xl mx-auto">
      <Card className="glassmorphism-card border-0">
        <CardHeader className="flex flex-row items-center justify-between pb-4">
          <div className="flex items-center space-x-3">
            <Bell className="w-6 h-6 text-[#F4D03F]" />
            <div>
              <CardTitle className="text-white">Notifications</CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                Stay updated with your progress and insights
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {unreadCount > 0 && (
              <Badge className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                {unreadCount} new
              </Badge>
            )}
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={markAllAsRead}
                className="text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
              >
                <Check className="w-4 h-4 mr-1" />
                Mark all read
              </Button>
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
          <ScrollArea className="h-[500px]">
            <div className="space-y-1 p-6 pt-0">
              {notifications.length === 0 ? (
                <div className="text-center py-12">
                  <Bell className="w-12 h-12 text-[#6B7280] mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-white mb-2">No notifications</h3>
                  <p className="text-[#B8BCC8]">
                    You're all caught up! Check back later for updates.
                  </p>
                </div>
              ) : (
                notifications.map((notification, index) => (
                  <div key={notification.id}>
                    <div 
                      className={`p-4 rounded-lg border-l-4 transition-all duration-200 ${
                        getBorderColor(notification.type)
                      } ${
                        notification.isRead 
                          ? 'bg-[rgba(26,29,41,0.3)]' 
                          : 'bg-[rgba(244,208,63,0.05)] border-[rgba(244,208,63,0.1)]'
                      } hover:bg-[rgba(244,208,63,0.08)] cursor-pointer`}
                      onClick={() => !notification.isRead && markAsRead(notification.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1">
                          {getIcon(notification.type)}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2 mb-1">
                              <h4 className={`font-medium ${
                                notification.isRead ? 'text-[#B8BCC8]' : 'text-white'
                              }`}>
                                {notification.title}
                              </h4>
                              {!notification.isRead && (
                                <div className="w-2 h-2 bg-[#F4D03F] rounded-full"></div>
                              )}
                            </div>
                            <p className={`text-sm ${
                              notification.isRead ? 'text-[#6B7280]' : 'text-[#B8BCC8]'
                            } mb-2`}>
                              {notification.message}
                            </p>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2 text-xs text-[#6B7280]">
                                <Clock className="w-3 h-3" />
                                <span>{notification.timestamp}</span>
                              </div>
                              {notification.action && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    notification.action!.onClick();
                                  }}
                                  className="text-[#F4D03F] hover:text-[#F7DC6F] hover:bg-[rgba(244,208,63,0.1)] h-6 px-2 text-xs"
                                >
                                  {notification.action.label}
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeNotification(notification.id);
                          }}
                          className="text-[#6B7280] hover:text-[#EF4444] hover:bg-[rgba(239,68,68,0.1)] h-8 w-8 ml-2"
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                    {index < notifications.length - 1 && (
                      <Separator className="bg-[rgba(244,208,63,0.1)] my-1" />
                    )}
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}