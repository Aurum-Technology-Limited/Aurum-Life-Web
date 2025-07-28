import React, { useState, useEffect } from 'react';
import { 
  Home, 
  Calendar, 
  Target, 
  FolderOpen, 
  CheckSquare, 
  BookOpen, 
  MessageSquare, 
  Bot, 
  Trophy, 
  User, 
  BarChart3, 
  Settings,
  Bell,
  Menu,
  X,
  ChevronDown,
  LogOut,
  Mountain
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import NotificationManager from './NotificationManager';
import UserMenu from './UserMenu';

const Layout = ({ children, activeSection, onSectionChange }) => {
  const { user, logout } = useAuth();
  const { notifications } = useNotification();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Navigation items
  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'today', label: 'Today', icon: Calendar },
    { id: 'pillars', label: 'Pillars', icon: Mountain },
    { id: 'areas', label: 'Areas', icon: Target },
    { id: 'projects', label: 'Projects', icon: FolderOpen },
    { id: 'project-templates', label: 'Templates', icon: BookOpen },
    { id: 'tasks', label: 'Tasks', icon: CheckSquare },
    { id: 'journal', label: 'Journal', icon: BookOpen },
    { id: 'insights', label: 'Insights', icon: BarChart3 },
    { id: 'feedback', label: 'Feedback', icon: MessageSquare },
    { id: 'ai-coach', label: 'AI Coach', icon: Bot },
    { id: 'achievements', label: 'Achievements', icon: Trophy },
  ];

  const handleNavigation = (sectionId) => {
    console.log('🔄 Layout: Navigating to', sectionId);
    onSectionChange(sectionId);
    setSidebarOpen(false); // Close mobile sidebar
  };

  const handleLogout = async () => {
    try {
      await logout();
      setShowUserMenu(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showUserMenu && !event.target.closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

  // Close mobile sidebar when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (sidebarOpen && !event.target.closest('.sidebar-container') && !event.target.closest('.mobile-menu-button')) {
        setSidebarOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [sidebarOpen]);

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Mobile Header */}
      <div className="lg:hidden bg-gray-900 border-b border-gray-700 px-4 py-3 flex items-center justify-between relative z-50">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="mobile-menu-button text-gray-400 hover:text-white transition-colors p-1 rounded-md hover:bg-gray-800"
          >
            {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
          <h1 className="text-xl font-bold text-white">Aurum Life</h1>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <div className="relative">
            <button className="text-gray-400 hover:text-white relative transition-colors p-1 rounded-md hover:bg-gray-800">
              <Bell className="h-6 w-6" />
              {notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center animate-pulse">
                  {notifications.length}
                </span>
              )}
            </button>
          </div>
          
          {/* User Menu */}
          <div className="relative user-menu-container">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors p-1 rounded-md hover:bg-gray-800"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-gray-900 font-semibold text-sm">
                  {user?.first_name?.[0] || user?.username?.[0] || user?.email?.[0] || 'U'}
                </span>
              </div>
              <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${showUserMenu ? 'rotate-180' : ''}`} />
            </button>
            
            {showUserMenu && (
              <UserMenu 
                user={user} 
                onClose={() => setShowUserMenu(false)}
                onNavigate={handleNavigation}
                onLogout={handleLogout}
              />
            )}
          </div>
        </div>
      </div>

      <div className="flex min-h-screen">
        {/* Fixed Sidebar - Always positioned fixed for smooth experience */}
        <div className={`
          sidebar-container fixed top-0 left-0 h-full bg-gray-900 border-r border-gray-700 transition-all duration-300 ease-in-out z-40 w-64
          ${sidebarOpen ? 'translate-x-0' : 'lg:translate-x-0 -translate-x-full'}
          shadow-xl
        `}>
          {/* Logo */}
          <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-700 bg-gray-800/50">
            <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-gray-900 font-bold text-sm">AL</span>
            </div>
            <h1 className="text-xl font-bold text-white">Aurum Life</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavigation(item.id)}
                  className={`
                    group w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all duration-200
                    ${isActive 
                      ? 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-gray-900 font-medium shadow-lg transform scale-105' 
                      : 'text-gray-400 hover:text-white hover:bg-gray-800/50 hover:transform hover:scale-102'
                    }
                  `}
                >
                  <Icon className={`h-5 w-5 ${isActive ? 'text-gray-900' : 'text-gray-400 group-hover:text-white'} transition-colors`} />
                  <span className="truncate">{item.label}</span>
                  {isActive && (
                    <div className="ml-auto w-2 h-2 bg-gray-900 rounded-full"></div>
                  )}
                </button>
              );
            })}
          </nav>

          {/* User Section - Desktop */}
          <div className="border-t border-gray-700 p-4 bg-gray-800/30">
            <div className="relative user-menu-container">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all duration-200"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-gray-900 font-semibold text-sm">
                    {user?.first_name?.[0] || user?.username?.[0] || user?.email?.[0] || 'U'}
                  </span>
                </div>
                <div className="flex-1 text-left">
                  <div className="text-sm font-medium text-white truncate">
                    {user?.first_name && user?.last_name 
                      ? `${user.first_name} ${user.last_name}`
                      : user?.username || user?.email || 'User'
                    }
                  </div>
                  <div className="text-xs text-gray-500">
                    Level {user?.level || 1} • {user?.total_points || 0} pts
                  </div>
                </div>
                <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${showUserMenu ? 'rotate-180' : ''}`} />
              </button>
              
              {showUserMenu && (
                <UserMenu 
                  user={user} 
                  onClose={() => setShowUserMenu(false)}
                  onNavigate={handleNavigation}
                  onLogout={handleLogout}
                  isCollapsed={sidebarCollapsed}
                />
              )}
            </div>
          </div>
        </div>

        {/* Mobile Overlay */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content */}
        <div className={`
          flex-1 min-h-screen transition-all duration-300 ease-in-out
          ${sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-64'}
        `}>
          <main className="h-full">
            {children}
          </main>
        </div>
      </div>

      {/* Notification Manager */}
      <NotificationManager />
    </div>
  );
};

export default Layout;