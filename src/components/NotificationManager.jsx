import React, { useEffect, useState } from 'react';
import {X, CheckCircle, AlertCircle, Info, AlertTriangle} from 'lucide-react';
import { useNotification } from '../contexts/NotificationContext';

// Notification types and their corresponding icons and colors
const notificationConfig = {
  success: {
    icon: CheckCircle,
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    iconColor: 'text-green-600',
    textColor: 'text-green-800'
  },
  error: {
    icon: AlertCircle,
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    iconColor: 'text-red-600',
    textColor: 'text-red-800'
  },
  warning: {
    icon: AlertTriangle,
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    iconColor: 'text-yellow-600',
    textColor: 'text-yellow-800'
  },
  info: {
    icon: Info,
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    iconColor: 'text-blue-600',
    textColor: 'text-blue-800'
  }
};

const NotificationManager = () => {
  const { notifications, removeNotification } = useNotification();
  const [visibleNotifications, setVisibleNotifications] = useState([]);

  useEffect(() => {
    setVisibleNotifications(notifications);
  }, [notifications]);

  const handleDismiss = (id) => {
    // Add fade-out animation class
    setVisibleNotifications(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, isRemoving: true } : notif
      )
    );
    
    // Remove after animation completes
    setTimeout(() => {
      removeNotification(id);
    }, 300);
  };

  if (visibleNotifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {visibleNotifications.map((notification) => {
        const config = notificationConfig[notification.type] || notificationConfig.info;
        const Icon = config.icon;
        
        return (
          <div
            key={notification.id}
            className={`
              ${config.bgColor} ${config.borderColor} ${config.textColor}
              border rounded-lg p-4 shadow-lg transition-all duration-300 ease-in-out
              ${notification.isRemoving ? 'opacity-0 transform translate-x-full' : 'opacity-100 transform translate-x-0'}
            `}
          >
            <div className="flex items-start">
              <Icon className={`${config.iconColor} h-5 w-5 mt-0.5 mr-3 flex-shrink-0`} />
              <div className="flex-1">
                {notification.title && (
                  <h4 className="font-medium text-sm mb-1">
                    {notification.title}
                  </h4>
                )}
                <p className="text-sm">
                  {notification.message}
                </p>
              </div>
              <button
                onClick={() => handleDismiss(notification.id)}
                className={`${config.iconColor} hover:opacity-70 ml-2 flex-shrink-0`}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default NotificationManager;