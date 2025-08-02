import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/BackendAuthContext';
import { UserIcon, CogIcon, LogoutIcon } from '@heroicons/react/outline';

const UserMenu = ({ onSectionChange }) => {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleProfileClick = () => {
    setIsOpen(false);
    if (onSectionChange) {
      onSectionChange('profile');
    }
  };

  const handleSettingsClick = () => {
    setIsOpen(false);
    if (onSectionChange) {
      onSectionChange('settings', { subSection: 'notifications' });
    }
  };

  const handleLogout = async () => {
    await logout();
    setIsOpen(false);
  };

  if (!user) return null;

  const initials = user.first_name && user.last_name 
    ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
    : user.email?.[0]?.toUpperCase() || 'U';

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center p-2 text-left text-gray-300 rounded-lg hover:bg-gray-700 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            {user.profile_picture ? (
              <img
                className="h-8 w-8 rounded-full"
                src={user.profile_picture}
                alt="Profile"
              />
            ) : (
              <div className="h-8 w-8 bg-yellow-500 rounded-full flex items-center justify-center">
                <span className="text-black font-medium text-sm">{initials}</span>
              </div>
            )}
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-white">
              {user.first_name && user.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user.username || user.email
              }
            </p>
          </div>
        </div>
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 w-48 mt-2 bg-gray-800 rounded-md shadow-lg py-1 z-50 border border-gray-700">
          <div className="px-4 py-2 border-b border-gray-700">
            <p className="text-sm font-medium text-white">
              {user.first_name && user.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user.username || user.email
              }
            </p>
            <p className="text-xs text-gray-400">{user.email}</p>
          </div>
          
          <button
            onClick={handleProfileClick}
            className="flex items-center w-full px-4 py-2 text-sm text-gray-300 hover:bg-gray-700"
          >
            <UserIcon className="h-4 w-4 mr-2" />
            Profile
          </button>
          
          <button
            onClick={handleSettingsClick}
            className="flex items-center w-full px-4 py-2 text-sm text-gray-300 hover:bg-gray-700"
          >
            <CogIcon className="h-4 w-4 mr-2" />
            Settings
          </button>
          
          <div className="border-t border-gray-700 my-1"></div>
          
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-4 py-2 text-sm text-red-400 hover:bg-gray-700"
          >
            <LogoutIcon className="h-4 w-4 mr-2" />
            Sign out
          </button>
        </div>
      )}
    </div>
  );
};

export default UserMenu;