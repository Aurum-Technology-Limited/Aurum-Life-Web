/**
 * Simplified Notification Manager for Aurum Life
 * Shows only immediate, actionable notifications
 */

import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  X, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Calendar
} from 'lucide-react';
import { tasksAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

// Simple notification component for actionable items
const ActionableNotification = ({ notification, onDismiss }) => {
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'overdue':
        return <AlertCircle className="h-5 w-5 text-red-400" />;
      case 'due_today':
        return <Clock className="h-5 w-5 text-orange-400" />;
      case 'due_soon':
        return <Calendar className="h-5 w-5 text-yellow-400" />;
      default:
        return <Bell className="h-5 w-5 text-blue-400" />;
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'overdue':
        return 'border-red-400/30 bg-red-900/20';
      case 'due_today':
        return 'border-orange-400/30 bg-orange-900/20';
      case 'due_soon':
        return 'border-yellow-400/30 bg-yellow-900/20';
      default:
        return 'border-blue-400/30 bg-blue-900/20';
    }
  };

  return (
    <div className={`p-4 rounded-lg border ${getNotificationColor(notification.type)} mb-3`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          {getNotificationIcon(notification.type)}
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-medium text-white mb-1">
            {notification.title}
          </h4>
          <p className="text-sm text-gray-300 mb-2">
            {notification.message}
          </p>
          {notification.action && (
            <button
              onClick={notification.action}
              className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded transition-colors"
            >
              {notification.actionText || 'View Task'}
            </button>
          )}
        </div>
        <button
          onClick={() => onDismiss(notification.id)}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

// Main simplified notification manager
const NotificationManager = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dismissedIds, setDismissedIds] = useState(new Set());

  // Load actionable notifications (tasks due today, overdue, etc.)
  const loadActionableNotifications = async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      const response = await tasksAPI.getTasks();
      const tasks = response.data;
      
      const actionableNotifications = [];
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      tasks.forEach(task => {
        if (task.completed || dismissedIds.has(task.id)) return;
        
        const dueDate = task.due_date ? new Date(task.due_date) : null;
        if (!dueDate) return;
        
        // Overdue tasks
        if (dueDate < today) {
          const daysOverdue = Math.ceil((today - dueDate) / (1000 * 60 * 60 * 24));
          actionableNotifications.push({
            id: `overdue-${task.id}`,
            type: 'overdue',
            title: `Task Overdue: ${task.name}`,
            message: `This task was due ${daysOverdue} day${daysOverdue > 1 ? 's' : ''} ago`,
            taskId: task.id,
            action: () => navigateToTask(task.id),
            actionText: 'View Task'
          });
        }
        // Due today
        else if (dueDate.toDateString() === today.toDateString()) {
          actionableNotifications.push({
            id: `due-today-${task.id}`,
            type: 'due_today',
            title: `Due Today: ${task.name}`,
            message: `This task is due today`,
            taskId: task.id,
            action: () => navigateToTask(task.id),
            actionText: 'View Task'
          });
        }
        // Due tomorrow
        else if (dueDate.toDateString() === tomorrow.toDateString()) {
          actionableNotifications.push({
            id: `due-tomorrow-${task.id}`,
            type: 'due_soon',
            title: `Due Tomorrow: ${task.name}`,
            message: `This task is due tomorrow`,
            taskId: task.id,
            action: () => navigateToTask(task.id),
            actionText: 'View Task'
          });
        }
      });
      
      setNotifications(actionableNotifications);
    } catch (error) {
      console.error('Error loading actionable notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  // Navigate to task (placeholder - would integrate with routing)
  const navigateToTask = (taskId) => {
    // This would integrate with your routing system
    window.location.href = `/tasks?focus=${taskId}`;
  };

  // Dismiss notification
  const dismissNotification = (notificationId) => {
    const taskId = notificationId.split('-').pop();
    setDismissedIds(prev => new Set([...prev, taskId]));
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  // Load notifications on mount and when user changes
  useEffect(() => {
    loadActionableNotifications();
  }, [user]);

  // Refresh notifications periodically (every 5 minutes)
  useEffect(() => {
    const interval = setInterval(loadActionableNotifications, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [user]);

  const unreadCount = notifications.length;

  return (
    <div className="relative">
      {/* Notification bell */}
      <button
        onClick={() => setShowNotifications(!showNotifications)}
        className="relative p-2 text-gray-400 hover:text-white transition-colors"
        title={unreadCount > 0 ? `${unreadCount} actionable items` : 'No urgent items'}
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification dropdown */}
      {showNotifications && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-gray-800 border border-gray-700 rounded-lg shadow-lg max-h-96 overflow-hidden z-50">
          <div className="p-3 sm:p-4 border-b border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-base sm:text-lg font-medium text-white">Action Items</h3>
              <button
                onClick={() => setShowNotifications(false)}
                className="text-gray-400 hover:text-white p-1"
              >
                <X className="h-4 w-4 sm:h-5 sm:w-5" />
              </button>
            </div>
            <p className="text-xs sm:text-sm text-gray-400">
              Tasks that need your attention
            </p>
          </div>

          <div className="max-h-80 overflow-y-auto p-3 sm:p-4">
            {loading ? (
              <div className="text-center py-6 text-gray-400">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto mb-2"></div>
                <p className="text-sm">Loading...</p>
              </div>
            ) : notifications.length === 0 ? (
              <div className="text-center py-6 text-gray-400">
                <CheckCircle2 className="h-8 w-8 mx-auto mb-2 text-green-400" />
                <p className="text-sm">All caught up!</p>
                <p className="text-xs mt-1">No overdue or urgent tasks</p>
              </div>
            ) : (
              <div>
                {notifications.map(notification => (
                  <ActionableNotification
                    key={notification.id}
                    notification={notification}
                    onDismiss={dismissNotification}
                  />
                ))}
              </div>
            )}
          </div>

          <div className="p-2 sm:p-3 border-t border-gray-700 bg-gray-900">
            <button
              onClick={loadActionableNotifications}
              disabled={loading}
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors disabled:opacity-50"
            >
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationManager;