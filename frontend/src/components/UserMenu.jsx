import React, { useState, useRef, useEffect } from 'react';
import { User, MessageCircle, LogOut, Settings } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const UserMenu = ({ onNavigate }) => {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);
  const buttonRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Close menu on escape key
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen]);

  const handleToggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleMenuItemClick = (action) => {
    setIsOpen(false); // Close menu first
    
    switch (action) {
      case 'profile':
        onNavigate('profile');
        break;
      case 'feedback':
        onNavigate('feedback');
        break;
      case 'logout':
        handleLogout();
        break;
      default:
        break;
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      // Logout function should handle redirect to login page
    } catch (error) {
      console.error('Logout failed:', error);
    }
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
      {/* User Avatar Button */}
      <button
        ref={buttonRef}
        onClick={handleToggleMenu}
        className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 ${
          isOpen
            ? 'bg-yellow-500/20 border border-yellow-500/30'
            : 'hover:bg-gray-800/50 border border-transparent'
        }`}
        aria-label="User menu"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        {/* Avatar Circle */}
        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all duration-200 ${
          isOpen
            ? 'bg-yellow-500 text-black'
            : 'bg-gradient-to-br from-yellow-500 to-yellow-600 text-white'
        }`}>
          {getUserInitials()}
        </div>
        
        {/* User Info */}
        <div className="flex-1 text-left min-w-0">
          <p className={`font-medium text-sm truncate transition-colors duration-200 ${
            isOpen ? 'text-yellow-500' : 'text-white'
          }`}>
            {getUserDisplayName()}
          </p>
          <p className="text-xs text-gray-400 truncate">
            {user?.email || 'user@example.com'}
          </p>
        </div>

        {/* Menu Indicator */}
        <div className={`w-2 h-2 rounded-full transition-all duration-200 ${
          isOpen ? 'bg-yellow-500' : 'bg-gray-600 group-hover:bg-gray-500'
        }`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop for mobile */}
          <div className="fixed inset-0 z-40 bg-black/20 md:hidden" />
          
          {/* Menu Panel */}
          <div
            ref={menuRef}
            className="absolute bottom-full left-0 w-full mb-2 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50 overflow-hidden"
            role="menu"
            aria-orientation="vertical"
          >
            {/* Menu Items */}
            <div className="py-2">
              {/* Profile & Settings */}
              <button
                onClick={() => handleMenuItemClick('profile')}
                className="w-full flex items-center space-x-3 px-4 py-3 text-left hover:bg-gray-800/50 transition-colors duration-200 group"
                role="menuitem"
              >
                <div className="p-2 rounded-lg bg-blue-500/20 group-hover:bg-blue-500/30 transition-colors duration-200">
                  <Settings className="h-4 w-4 text-blue-400" />
                </div>
                <div>
                  <p className="text-white font-medium text-sm">Profile & Settings</p>
                  <p className="text-gray-400 text-xs">Manage your account</p>
                </div>
              </button>

              {/* Send Feedback */}
              <button
                onClick={() => handleMenuItemClick('feedback')}
                className="w-full flex items-center space-x-3 px-4 py-3 text-left hover:bg-gray-800/50 transition-colors duration-200 group"
                role="menuitem"
              >
                <div className="p-2 rounded-lg bg-green-500/20 group-hover:bg-green-500/30 transition-colors duration-200">
                  <MessageCircle className="h-4 w-4 text-green-400" />
                </div>
                <div>
                  <p className="text-white font-medium text-sm">Send Feedback</p>
                  <p className="text-gray-400 text-xs">Share your thoughts</p>
                </div>
              </button>

              {/* Divider */}
              <div className="my-2 mx-4 border-t border-gray-700" />

              {/* Logout */}
              <button
                onClick={() => handleMenuItemClick('logout')}
                className="w-full flex items-center space-x-3 px-4 py-3 text-left hover:bg-red-500/10 transition-colors duration-200 group"
                role="menuitem"
              >
                <div className="p-2 rounded-lg bg-red-500/20 group-hover:bg-red-500/30 transition-colors duration-200">
                  <LogOut className="h-4 w-4 text-red-400" />
                </div>
                <div>
                  <p className="text-red-400 font-medium text-sm">Logout</p>
                  <p className="text-gray-400 text-xs">Sign out of your account</p>
                </div>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default UserMenu;