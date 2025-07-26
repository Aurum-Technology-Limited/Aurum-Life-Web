import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const UserMenu = ({ onNavigate }) => {
  const { user } = useAuth();

  // Direct navigation to profile on avatar click
  const handleAvatarClick = () => {
    onNavigate('profile');
  };

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user) return 'U';
    
    const firstName = user.first_name || '';
    const lastName = user.last_name || '';
    
    if (firstName && lastName) {
      return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
    } else if (firstName) {
      return firstName.charAt(0).toUpperCase();
    } else if (user.username) {
      return user.username.charAt(0).toUpperCase();
    }
    
    return 'U';
  };

  const getUserDisplayName = () => {
    if (!user) return 'User';
    
    const firstName = user.first_name || '';
    const lastName = user.last_name || '';
    
    if (firstName && lastName) {
      return `${firstName} ${lastName}`;
    } else if (firstName) {
      return firstName;
    } else if (user.username) {
      return user.username;
    }
    
    return 'User';
  };

  return (
    <div className="relative">
      {/* User Avatar Button - Direct to Profile */}
      <button
        onClick={handleAvatarClick}
        className="w-full flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 hover:bg-gray-800/50 border border-transparent hover:border-gray-700 group"
        aria-label="Go to profile"
        title="Click to view your profile"
      >
        {/* Avatar Circle */}
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-500 to-yellow-600 flex items-center justify-center font-semibold text-sm text-white transition-transform duration-200 group-hover:scale-105">
          {getUserInitials()}
        </div>
        
        {/* User Info */}
        <div className="flex-1 text-left min-w-0">
          <p className="font-medium text-sm truncate text-white group-hover:text-yellow-400 transition-colors duration-200">
            {getUserDisplayName()}
          </p>
          <p className="text-xs text-gray-400 truncate">
            {user?.email || 'user@example.com'}
          </p>
        </div>

        {/* Profile Indicator Arrow */}
        <div className="w-4 h-4 text-gray-500 group-hover:text-yellow-400 transition-colors duration-200">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </button>
    </div>
  );
};

export default UserMenu;