/**
 * Notification Toast Component for Aurum Life
 * Displays in-app notifications with actions
 */

import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  X, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Target,
  Settings
} from 'lucide-react';
import { useNotifications } from '../contexts/NotificationContext';

// Individual notification toast
const NotificationToast = ({ notification, onClose, onMarkRead }) => {
  const [isVisible, setIsVisible] = useState(true);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'task_due':
        return <Clock className="h-5 w-5 text-orange-400" />;
      case 'task_overdue':
        return <AlertCircle className="h-5 w-5 text-red-400" />;
      case 'task_reminder':
        return <Bell className="h-5 w-5 text-blue-400" />;
      case 'project_deadline':
        return <Target className="h-5 w-5 text-purple-400" />;
      default:
        return <Bell className="h-5 w-5 text-gray-400" />;
    }
  };

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => {
      onClose(notification.id);
    }, 300);
  };

  const handleMarkRead = async () => {
    await onMarkRead(notification.id);
    handleClose();
  };

  if (!isVisible) return null;

  return (
    <div className={`
      transform transition-all duration-300 ease-in-out
      ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
      bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-4 mb-3 max-w-sm
    `}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          {getNotificationIcon(notification.type)}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="text-sm font-medium text-white mb-1">
                {notification.title}
              </h4>
              <p className="text-sm text-gray-300 leading-relaxed">
                {notification.message}
              </p>
              
              {notification.task_name && (
                <div className="mt-2 text-xs text-gray-400">
                  Task: <span className="text-gray-300">{notification.task_name}</span>
                  {notification.project_name && (
                    <span> • Project: <span className="text-gray-300">{notification.project_name}</span></span>
                  )}
                </div>
              )}
              
              <div className="mt-2 text-xs text-gray-500">
                {new Date(notification.created_at).toLocaleString()}
              </div>
            </div>
            
            <button
              onClick={handleClose}
              className="ml-2 text-gray-400 hover:text-white transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          
          {!notification.read && (
            <div className="mt-3 flex space-x-2">
              <button
                onClick={handleMarkRead}
                className="text-xs bg-yellow-500 hover:bg-yellow-600 text-black px-2 py-1 rounded transition-colors"
              >
                Mark as Read
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Main notification manager component
const NotificationManager = () => {
  const { 
    notifications, 
    unreadCount, 
    markAsRead, 
    fetchNotifications 
  } = useNotifications();
  
  const [visibleNotifications, setVisibleNotifications] = useState([]);
  const [showAllNotifications, setShowAllNotifications] = useState(false);

  // Show only recent unread notifications as toasts
  useEffect(() => {
    const recentUnread = notifications
      .filter(n => !n.read)
      .slice(0, 3) // Limit to 3 simultaneous toasts
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    setVisibleNotifications(recentUnread);
  }, [notifications]);

  const handleCloseToast = (notificationId) => {
    setVisibleNotifications(prev => 
      prev.filter(n => n.id !== notificationId)
    );
  };

  const handleMarkRead = async (notificationId) => {
    await markAsRead(notificationId);
  };

  return (
    <>
      {/* Toast notifications container */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {visibleNotifications.map(notification => (
          <NotificationToast
            key={notification.id}
            notification={notification}
            onClose={handleCloseToast}
            onMarkRead={handleMarkRead}
          />
        ))}
      </div>

      {/* Notification bell icon with count */}
      <div className="relative">
        <button
          onClick={() => setShowAllNotifications(!showAllNotifications)}
          className="relative p-2 text-gray-400 hover:text-white transition-colors"
          title={`${unreadCount} unread notifications`}
        >
          <Bell className="h-6 w-6" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>

        {/* Notification dropdown */}
        {showAllNotifications && (
          <div className="absolute right-0 mt-2 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-lg max-h-96 overflow-y-auto z-50">
            <div className="p-4 border-b border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-white">Notifications</h3>
                <button
                  onClick={() => setShowAllNotifications(false)}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-gray-500">
                  <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No notifications yet</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-700">
                  {notifications.slice(0, 10).map(notification => (
                    <div
                      key={notification.id}
                      className={`p-4 hover:bg-gray-700 transition-colors ${
                        !notification.read ? 'bg-gray-800' : 'bg-gray-900'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          {getNotificationIcon(notification.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className={`text-sm font-medium mb-1 ${
                                !notification.read ? 'text-white' : 'text-gray-300'
                              }`}>
                                {notification.title}
                              </h4>
                              <p className="text-sm text-gray-400 leading-relaxed">
                                {notification.message}
                              </p>
                              <div className="mt-1 text-xs text-gray-500">
                                {new Date(notification.created_at).toLocaleString()}
                              </div>
                            </div>
                            {!notification.read && (
                              <div className="ml-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                              </div>
                            )}
                          </div>
                          
                          {!notification.read && (
                            <button
                              onClick={() => handleMarkRead(notification.id)}
                              className="mt-2 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                            >
                              Mark as read
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-3 border-t border-gray-700 bg-gray-900">
              <button
                onClick={() => {
                  fetchNotifications();
                  setShowAllNotifications(false);
                }}
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Refresh notifications
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

// Helper function used in both components
const getNotificationIcon = (type) => {
  switch (type) {
    case 'task_due':
      return <Clock className="h-4 w-4 text-orange-400" />;
    case 'task_overdue':
      return <AlertCircle className="h-4 w-4 text-red-400" />;
    case 'task_reminder':
      return <Bell className="h-4 w-4 text-blue-400" />;
    case 'project_deadline':
      return <Target className="h-4 w-4 text-purple-400" />;
    default:
      return <Bell className="h-4 w-4 text-gray-400" />;
  }
};

export default NotificationManager;