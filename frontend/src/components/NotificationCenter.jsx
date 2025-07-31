import React, { useState, useEffect } from 'react';
import {Bell, Check, CheckCheck, Trash2, X, AlertCircle, Clock, Calendar, FolderOpen, CheckSquare, Trophy, Loader} from 'lucide-react';
import { notificationsAPI } from '../services/api';

const NotificationCenter = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState({});
  const [filter, setFilter] = useState('all'); // 'all', 'unread'
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadNotifications();
  }, [filter]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await notificationsAPI.getNotifications(filter === 'unread');
      setNotifications(response.data || []);
    } catch (error) {
      console.error('Error loading notifications:', error);
      setMessage('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    if (actionLoading[notificationId]) return;
    
    try {
      setActionLoading(prev => ({ ...prev, [notificationId]: true }));
      await notificationsAPI.markAsRead(notificationId);
      
      // Update the notification in the local state
      setNotifications(prev => prev.map(notification => 
        notification.id === notificationId 
          ? { ...notification, is_read: true, read_at: new Date().toISOString() }
          : notification
      ));
    } catch (error) {
      console.error('Error marking notification as read:', error);
      setMessage('Failed to mark notification as read');
    } finally {
      setActionLoading(prev => ({ ...prev, [notificationId]: false }));
    }
  };

  const handleMarkAllRead = async () => {
    try {
      const response = await notificationsAPI.markAllRead();
      setMessage(`${response.data.count} notifications marked as read`);
      await loadNotifications(); // Reload to get updated state
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      setMessage('Failed to mark all notifications as read');
    }
  };

  const handleDelete = async (notificationId) => {
    if (actionLoading[notificationId]) return;
    
    try {
      setActionLoading(prev => ({ ...prev, [notificationId]: true }));
      await notificationsAPI.deleteNotification(notificationId);
      
      // Remove the notification from local state
      setNotifications(prev => prev.filter(notification => notification.id !== notificationId));
    } catch (error) {
      console.error('Error deleting notification:', error);
      setMessage('Failed to delete notification');
    } finally {
      setActionLoading(prev => ({ ...prev, [notificationId]: false }));
    }
  };

  const handleClearAll = async () => {
    if (window.confirm('Are you sure you want to clear all notifications? This action cannot be undone.')) {
      try {
        const response = await notificationsAPI.clearAllNotifications();
        setMessage(`${response.data.count} notifications cleared`);
        setNotifications([]);
      } catch (error) {
        console.error('Error clearing all notifications:', error);
        setMessage('Failed to clear all notifications');
      }
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'task_due':
      case 'task_overdue':
      case 'task_reminder':
      case 'unblocked_task':
        return <CheckSquare className="h-5 w-5" />;
      case 'project_deadline':
        return <FolderOpen className="h-5 w-5" />;
      case 'recurring_task':
        return <Clock className="h-5 w-5" />;
      case 'achievement_unlocked':
        return <Trophy className="h-5 w-5" />;
      default:
        return <Bell className="h-5 w-5" />;
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'task_due':
        return 'text-orange-400 bg-orange-400/10 border-orange-400/20';
      case 'task_overdue':
        return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'task_reminder':
        return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'unblocked_task':
        return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'project_deadline':
        return 'text-purple-400 bg-purple-400/10 border-purple-400/20';
      case 'recurring_task':
        return 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20';
      case 'achievement_unlocked':
        return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      default:
        return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const formatTimeAgo = (dateString) => {
    if (!dateString) return 'Unknown time';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    
    return date.toLocaleDateString();
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;
  const filteredNotifications = notifications.filter(notification => 
    filter === 'all' || !notification.is_read
  );

  if (loading) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <Loader className="h-8 w-8 animate-spin text-yellow-400" />
            <span className="ml-3 text-gray-400">Loading notifications...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold flex items-center" style={{ color: '#F4B400' }}>
                <Bell className="h-8 w-8 mr-3" />
                Notifications
              </h1>
              {unreadCount > 0 && (
                <span className="ml-3 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                  {unreadCount}
                </span>
              )}
            </div>
          </div>
          <p className="text-gray-400 mt-2">
            Stay updated with your tasks, achievements, and important events
          </p>
        </div>

        {/* Message Display */}
        {message && (
          <div className="mb-6 p-4 rounded-lg bg-blue-900/20 border border-blue-600 text-blue-400 flex items-center">
            <AlertCircle className="h-5 w-5 mr-3" />
            <span>{message}</span>
            <button 
              onClick={() => setMessage('')}
              className="ml-auto text-blue-400 hover:text-blue-300"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Controls */}
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-yellow-400 text-gray-900'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              All ({notifications.length})
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'unread'
                  ? 'bg-yellow-400 text-gray-900'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              Unread ({unreadCount})
            </button>
          </div>

          <div className="flex items-center space-x-2">
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="flex items-center space-x-2 px-4 py-2 bg-green-800 hover:bg-green-700 text-green-400 rounded-lg font-medium transition-colors"
              >
                <CheckCheck className="h-4 w-4" />
                <span>Mark All Read</span>
              </button>
            )}
            
            {notifications.length > 0 && (
              <button
                onClick={handleClearAll}
                className="flex items-center space-x-2 px-4 py-2 bg-red-800 hover:bg-red-700 text-red-400 rounded-lg font-medium transition-colors"
              >
                <Trash2 className="h-4 w-4" />
                <span>Clear All</span>
              </button>
            )}
          </div>
        </div>

        {/* Notifications List */}
        <div className="space-y-4">
          {filteredNotifications.length === 0 ? (
            <div className="text-center py-12">
              <Bell className="h-12 w-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">
                {filter === 'unread' ? 'No unread notifications' : 'No notifications yet'}
              </p>
              <p className="text-gray-500 text-sm mt-2">
                You'll see notifications here when you have task updates, achievements, and more
              </p>
            </div>
          ) : (
            filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-4 rounded-lg border transition-all duration-200 ${
                  notification.is_read
                    ? 'bg-gray-900/30 border-gray-800'
                    : 'bg-gray-900/50 border-gray-700 shadow-lg'
                }`}
              >
                <div className="flex items-start space-x-4">
                  {/* Icon */}
                  <div className={`p-2 rounded-lg border ${getNotificationColor(notification.type)}`}>
                    {getNotificationIcon(notification.type)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className={`font-semibold ${notification.is_read ? 'text-gray-300' : 'text-white'}`}>
                          {notification.title}
                        </h3>
                        <p className={`text-sm mt-1 ${notification.is_read ? 'text-gray-400' : 'text-gray-300'}`}>
                          {notification.message}
                        </p>
                        
                        {/* Metadata */}
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                          <span className="flex items-center">
                            <Calendar className="h-3 w-3 mr-1" />
                            {formatTimeAgo(notification.created_at)}
                          </span>
                          
                          {notification.project_name && (
                            <span className="flex items-center">
                              <FolderOpen className="h-3 w-3 mr-1" />
                              {notification.project_name}
                            </span>
                          )}
                          
                          {notification.priority && (
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              notification.priority === 'high' 
                                ? 'bg-red-900/30 text-red-400'
                                : notification.priority === 'medium'
                                ? 'bg-yellow-900/30 text-yellow-400'
                                : 'bg-green-900/30 text-green-400'
                            }`}>
                              {notification.priority}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center space-x-2 ml-4">
                        {!notification.is_read && (
                          <button
                            onClick={() => handleMarkAsRead(notification.id)}
                            disabled={actionLoading[notification.id]}
                            className="p-1 text-gray-400 hover:text-green-400 transition-colors"
                            title="Mark as read"
                          >
                            {actionLoading[notification.id] ? (
                              <Loader className="h-4 w-4 animate-spin" />
                            ) : (
                              <Check className="h-4 w-4" />
                            )}
                          </button>
                        )}
                        
                        <button
                          onClick={() => handleDelete(notification.id)}
                          disabled={actionLoading[notification.id]}
                          className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                          title="Delete notification"
                        >
                          {actionLoading[notification.id] ? (
                            <Loader className="h-4 w-4 animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default NotificationCenter;