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
import { useAuth } from '../contexts/SupabaseAuthContext';
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

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#0B0D14' }}>
      {/* Mobile Header */}
      <div className="lg:hidden bg-gray-900 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-400 hover:text-white"
          >
            {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
          <h1 className="text-xl font-bold text-white">Aurum Life</h1>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <div className="relative">
            <button className="text-gray-400 hover:text-white relative">
              <Bell className="h-6 w-6" />
              {notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {notifications.length}
                </span>
              )}
            </button>
          </div>
          
          {/* User Menu */}
          <div className="relative user-menu-container">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 text-gray-400 hover:text-white"
            >
              <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                <span className="text-gray-900 font-semibold text-sm">
                  {user?.first_name?.[0] || user?.username?.[0] || user?.email?.[0] || 'U'}
                </span>
              </div>
              <ChevronDown className="h-4 w-4" />
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

      <div className="flex">
        {/* Sidebar */}
        <div className={`
          fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 border-r border-gray-700 transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:inset-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}>
          {/* Logo */}
          <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-700">
            <div className="w-8 h-8 bg-yellow-500 rounded-lg flex items-center justify-center">
              <span className="text-gray-900 font-bold text-sm">AL</span>
            </div>
            <h1 className="text-xl font-bold text-white">Aurum Life</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavigation(item.id)}
                  className={`
                    w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors
                    ${isActive 
                      ? 'bg-yellow-500 text-gray-900 font-medium' 
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                    }
                  `}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* User Section - Desktop */}
          <div className="hidden lg:block border-t border-gray-700 p-4">
            <div className="relative user-menu-container">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800"
              >
                <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                  <span className="text-gray-900 font-semibold text-sm">
                    {user?.first_name?.[0] || user?.username?.[0] || user?.email?.[0] || 'U'}
                  </span>
                </div>
                <div className="flex-1 text-left">
                  <div className="text-sm font-medium text-white">
                    {user?.first_name && user?.last_name 
                      ? `${user.first_name} ${user.last_name}`
                      : user?.username || user?.email || 'User'
                    }
                  </div>
                  <div className="text-xs text-gray-500">
                    Level {user?.level || 1} • {user?.total_points || 0} pts
                  </div>
                </div>
                <ChevronDown className="h-4 w-4" />
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

        {/* Mobile Sidebar Overlay */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content */}
        <div className="flex-1 lg:ml-0">
          {/* Desktop Header */}
          <div className="hidden lg:flex items-center justify-between bg-gray-900 border-b border-gray-700 px-6 py-4">
            <div>
              <h2 className="text-2xl font-bold text-white capitalize">
                {navigationItems.find(item => item.id === activeSection)?.label || 'Dashboard'}
              </h2>
              <p className="text-gray-400 text-sm mt-1">
                Welcome back, {user?.first_name || user?.username || 'User'}
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Notifications */}
              <div className="relative">
                <button 
                  onClick={() => handleNavigation('notifications')}
                  className="text-gray-400 hover:text-white relative"
                >
                  <Bell className="h-6 w-6" />
                  {notifications.length > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {notifications.length}
                    </span>
                  )}
                </button>
              </div>
              
              {/* Settings */}
              <button 
                onClick={() => handleNavigation('notification-settings')}
                className="text-gray-400 hover:text-white"
              >
                <Settings className="h-6 w-6" />
              </button>
            </div>
          </div>

          {/* Page Content */}
          <main className="p-6">
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