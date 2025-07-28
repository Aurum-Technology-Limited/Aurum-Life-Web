import React from 'react';
import { User, Settings, Bell, LogOut, Trophy, BarChart3 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const UserMenu = ({ user, onClose, onNavigate, onLogout }) => {
  const handleMenuClick = (action) => {
    if (action === 'logout') {
      onLogout();
    } else {
      onNavigate(action);
    }
    onClose();
  };

  return (
    <div className="absolute bottom-full mb-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 animate-in slide-in-from-bottom-2 duration-200 right-0 w-64">
      {/* User Info */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center shadow-lg">
            <span className="text-gray-900 font-semibold">
              {user?.first_name?.[0] || user?.username?.[0] || user?.email?.[0] || 'U'}
            </span>
          </div>
          <div className="flex-1">
            <div className="text-white font-medium truncate">
              {user?.first_name && user?.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user?.username || user?.email || 'User'
              }
            </div>
            <div className="text-gray-400 text-sm truncate">{user?.email}</div>
          </div>
        </div>
        
        <div className="mt-3 flex items-center justify-between text-sm">
          <span className="text-gray-400">Level {user?.level || 1}</span>
          <span className="text-yellow-500 font-medium">{user?.total_points || 0} points</span>
        </div>
        
        {user?.current_streak > 0 && (
          <div className="mt-1 text-sm text-gray-400">
            🔥 {user.current_streak} day streak
          </div>
        )}
      </div>

      {/* Menu Items */}
      <div className="py-2">
        <button
          onClick={() => handleMenuClick('profile')}
          className="w-full flex items-center gap-3 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-700 transition-colors"
        >
          <User className="h-4 w-4" />
          <span>Profile</span>
        </button>
        
        <button
          onClick={() => handleMenuClick('achievements')}
          className="w-full flex items-center gap-3 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-700 transition-colors"
        >
          <Trophy className="h-4 w-4" />
          <span>Achievements</span>
        </button>
        
        <button
          onClick={() => handleMenuClick('insights')}
          className="w-full flex items-center gap-3 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-700 transition-colors"
        >
          <BarChart3 className="h-4 w-4" />
          <span>Insights</span>
        </button>
        
        <button
          onClick={() => handleMenuClick('notification-settings')}
          className="w-full flex items-center gap-3 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-700 transition-colors"
        >
          <Bell className="h-4 w-4" />
          <span>Notifications</span>
        </button>
        
        <button
          onClick={() => handleMenuClick('profile')}
          className="w-full flex items-center gap-3 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-700 transition-colors"
        >
          <Settings className="h-4 w-4" />
          <span>Settings</span>
        </button>
      </div>

      {/* Logout */}
      <div className="border-t border-gray-700 py-2">
        <button
          onClick={() => handleMenuClick('logout')}
          className="w-full flex items-center gap-3 px-4 py-2 text-red-400 hover:text-red-300 hover:bg-gray-700 transition-colors"
        >
          <LogOut className="h-4 w-4" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );
};

export default UserMenu;