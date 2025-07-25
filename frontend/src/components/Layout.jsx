import React, { useState } from 'react';
import { 
  Brain, 
  BookOpen, 
  CheckSquare, 
  MessageCircle, 
  Trophy, 
  Settings,
  Menu,
  X,
  Calendar,
  Layers,
  FolderOpen,
  User,
  BarChart3,
  FileText,
  Repeat,
  Mountain
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import NotificationManager from './NotificationManager';

const Layout = ({ children, activeSection, onSectionChange }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user } = useAuth();

  const navigation = [
    { id: 'dashboard', name: 'Dashboard', icon: Brain, description: 'Overview & insights' },
    { id: 'today', name: 'Today', icon: Calendar, description: 'Today\'s tasks & focus' },
    { id: 'insights', name: 'Insights', icon: BarChart3, description: 'Data & analytics' },
    { id: 'pillars', name: 'Pillars', icon: Mountain, description: 'Life domains hierarchy' },
    { id: 'areas', name: 'Areas', icon: Layers, description: 'Life domains' },
    { id: 'projects', name: 'Projects', icon: FolderOpen, description: 'Active projects' },
    { id: 'project-templates', name: 'Templates', icon: FileText, description: 'Project templates' },
    { id: 'tasks', name: 'Tasks', icon: CheckSquare, description: 'Goals & productivity' },
    { id: 'recurring-tasks', name: 'Recurring', icon: Repeat, description: 'Automated tasks' },
    { id: 'journal', name: 'Journal', icon: BookOpen, description: 'Reflection & writing' },
    { id: 'feedback', name: 'Feedback', icon: MessageCircle, description: 'Share suggestions & get support' },
    { id: 'ai-coach', name: 'AI Coach', icon: MessageCircle, description: 'Personal guidance' },
    { id: 'achievements', name: 'Achievements', icon: Trophy, description: 'Badges & rewards' },
    { id: 'notification-settings', name: 'Notifications', icon: Settings, description: 'Notification preferences' },
    { id: 'profile', name: 'Profile', icon: User, description: 'Account settings' }
  ];

  const handleNavigation = (sectionId) => {
    console.log('🖱️ Layout: Navigation clicked for section:', sectionId);
    console.log('🔄 Layout: Calling onSectionChange with:', sectionId);
    onSectionChange(sectionId);
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#0B0D14' }}>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-lg transition-all duration-200"
          style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
        >
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-40 w-80 transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        border-r border-gray-800
      `}
      style={{ backgroundColor: 'rgba(11, 13, 20, 0.95)' }}
      >
        {/* Logo */}
        <div className="flex items-center h-20 px-6 border-b border-gray-800">
          <div className="flex items-center space-x-3">
            <div 
              className="w-10 h-10 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: '#F4B400' }}
            >
              <Brain size={24} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: '#F4B400' }}>
                Aurum Life
              </h1>
              <p className="text-xs text-gray-400">Personal Growth Platform</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="mt-8 px-4">
          {navigation.map((item) => {
            const isActive = activeSection === item.id;
            
            // Debug logging for insights button specifically
            if (item.id === 'insights') {
              console.log('🔍 Debug: Rendering insights button with id:', item.id);
            }
            
            return (
              <button
                key={item.id}
                onClick={() => {
                  console.log('🖱️ Button clicked with item.id:', item.id);
                  handleNavigation(item.id);
                }}
                className={`
                  w-full flex items-center px-4 py-3 mb-2 rounded-lg text-left
                  transition-all duration-200 group hover:scale-105
                  ${isActive 
                    ? 'shadow-lg transform' 
                    : 'hover:bg-gray-800/50'
                  }
                `}
                style={{
                  backgroundColor: isActive ? '#F4B400' : 'transparent',
                  color: isActive ? '#0B0D14' : '#ffffff'
                }}
              >
                <item.icon 
                  size={20} 
                  className={`mr-3 ${isActive ? '' : 'group-hover:scale-110 transition-transform'}`}
                />
                <div>
                  <div className={`font-medium ${isActive ? 'text-gray-900' : ''}`}>
                    {item.name}
                  </div>
                  <div className={`text-xs ${isActive ? 'text-gray-700' : 'text-gray-400'}`}>
                    {item.description}
                  </div>
                </div>
              </button>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="p-4 rounded-lg bg-gray-800/30 border border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-yellow-400 to-yellow-600 flex items-center justify-center">
                <span className="text-sm font-bold text-gray-900">
                  {user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                </span>
              </div>
              <div>
                <p className="text-sm font-medium text-white">
                  {user?.first_name ? `${user.first_name} ${user.last_name}` : user?.username || 'User'}
                </p>
                <p className="text-xs text-gray-400">
                  Level {user?.level || 1} • {user?.total_points || 0} points
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="lg:ml-80 min-h-screen">
        {/* Top header with level display */}
        <div className="sticky top-0 z-20 bg-[#0B0D14]/95 backdrop-blur-sm border-b border-gray-800/50 p-4 lg:p-6">
          <div className="flex items-center justify-between">
            <div className="lg:hidden">
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/50"
              >
                <Menu size={24} />
              </button>
            </div>
            
            {/* Header actions */}
            <div className="ml-auto flex items-center space-x-4">
              {/* Notification Manager */}
              <NotificationManager />
              
              {/* Level display */}
              {user && (
                <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-yellow-400/10 border border-yellow-400/20">
                  <span className="text-yellow-400 font-medium">Level {user.level}</span>
                  <span className="text-gray-400">•</span>
                  <span className="text-gray-300">{user.total_points} points</span>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <main className="p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;