import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { SectionType, User, Notification } from '../types/app';

interface AppState {
  // Authentication
  isAuthenticated: boolean;
  user: User | null;
  
  // UI State
  activeSection: SectionType;
  isNotificationsOpen: boolean;
  isSidebarCollapsed: boolean;
  
  // Loading & Error States
  isLoading: boolean;
  error: string | null;
  
  // Notifications
  notifications: Notification[];
  unreadCount: number;
  
  // Theme & Preferences
  theme: 'light' | 'dark';
  sidebarPreference: 'expanded' | 'collapsed' | 'auto';
}

interface AppActions {
  // Authentication Actions
  login: (user: User) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  
  // Navigation Actions
  setActiveSection: (section: SectionType) => void;
  goBack: () => void;
  
  // UI Actions
  openNotifications: () => void;
  closeNotifications: () => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // Loading & Error Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // Notification Actions
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  
  // Theme Actions
  setTheme: (theme: 'light' | 'dark') => void;
  toggleTheme: () => void;
}

type AppStore = AppState & AppActions;

const initialState: AppState = {
  isAuthenticated: false,
  user: null,
  activeSection: 'dashboard',
  isNotificationsOpen: false,
  isSidebarCollapsed: false,
  isLoading: false,
  error: null,
  notifications: [],
  unreadCount: 0,
  theme: 'dark',
  sidebarPreference: 'expanded',
};

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      // Authentication Actions
      login: (user: User) => {
        set({ 
          isAuthenticated: true, 
          user, 
          error: null,
          activeSection: user.preferences?.defaultView || 'dashboard'
        });
        
        // Add welcome notification
        get().addNotification({
          type: 'success',
          title: 'Welcome back!',
          message: `Welcome back, ${user.name}. Ready to align your actions with your vision?`,
          timestamp: new Date().toISOString(),
          isRead: false,
        });
      },
      
      logout: () => {
        set({
          isAuthenticated: false,
          user: null,
          activeSection: 'dashboard',
          isNotificationsOpen: false,
          notifications: [],
          unreadCount: 0,
          error: null,
        });
      },
      
      updateUser: (updates: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...updates } });
        }
      },
      
      // Navigation Actions
      setActiveSection: (section: SectionType) => {
        set({ activeSection: section });
      },
      
      goBack: () => {
        // Implementation would depend on navigation history
        set({ activeSection: 'dashboard' });
      },
      
      // UI Actions
      openNotifications: () => {
        set({ isNotificationsOpen: true });
      },
      
      closeNotifications: () => {
        set({ isNotificationsOpen: false });
      },
      
      toggleSidebar: () => {
        set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed }));
      },
      
      setSidebarCollapsed: (collapsed: boolean) => {
        set({ isSidebarCollapsed: collapsed });
      },
      
      // Loading & Error Actions
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
        if (loading) {
          set({ error: null });
        }
      },
      
      setError: (error: string | null) => {
        set({ error, isLoading: false });
      },
      
      clearError: () => {
        set({ error: null });
      },
      
      // Notification Actions
      addNotification: (notification: Omit<Notification, 'id'>) => {
        const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const newNotification: Notification = { ...notification, id };
        
        set((state) => ({
          notifications: [newNotification, ...state.notifications],
          unreadCount: state.unreadCount + 1,
        }));
        
        // Auto-remove info notifications after 5 seconds
        if (notification.type === 'info') {
          setTimeout(() => {
            get().removeNotification(id);
          }, 5000);
        }
      },
      
      markNotificationRead: (id: string) => {
        set((state) => {
          const notification = state.notifications.find(n => n.id === id);
          if (notification && !notification.isRead) {
            return {
              notifications: state.notifications.map(n => 
                n.id === id ? { ...n, isRead: true } : n
              ),
              unreadCount: Math.max(0, state.unreadCount - 1),
            };
          }
          return state;
        });
      },
      
      markAllNotificationsRead: () => {
        set((state) => ({
          notifications: state.notifications.map(n => ({ ...n, isRead: true })),
          unreadCount: 0,
        }));
      },
      
      removeNotification: (id: string) => {
        set((state) => {
          const notification = state.notifications.find(n => n.id === id);
          const wasUnread = notification && !notification.isRead;
          
          return {
            notifications: state.notifications.filter(n => n.id !== id),
            unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
          };
        });
      },
      
      clearNotifications: () => {
        set({ notifications: [], unreadCount: 0 });
      },
      
      // Theme Actions
      setTheme: (theme: 'light' | 'dark') => {
        set({ theme });
        document.documentElement.classList.toggle('dark', theme === 'dark');
      },
      
      toggleTheme: () => {
        const currentTheme = get().theme;
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        get().setTheme(newTheme);
      },
    }),
    {
      name: 'aurum-life-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        activeSection: state.activeSection,
        theme: state.theme,
        sidebarPreference: state.sidebarPreference,
        isSidebarCollapsed: state.isSidebarCollapsed,
      }),
    }
  )
);

// Selectors for optimized subscriptions
export const useAuth = () => useAppStore((state) => ({
  isAuthenticated: state.isAuthenticated,
  user: state.user,
  login: state.login,
  logout: state.logout,
  updateUser: state.updateUser,
}));

export const useNavigation = () => useAppStore((state) => ({
  activeSection: state.activeSection,
  setActiveSection: state.setActiveSection,
  goBack: state.goBack,
}));

export const useNotifications = () => useAppStore((state) => ({
  notifications: state.notifications,
  unreadCount: state.unreadCount,
  isNotificationsOpen: state.isNotificationsOpen,
  openNotifications: state.openNotifications,
  closeNotifications: state.closeNotifications,
  addNotification: state.addNotification,
  markNotificationRead: state.markNotificationRead,
  markAllNotificationsRead: state.markAllNotificationsRead,
  removeNotification: state.removeNotification,
  clearNotifications: state.clearNotifications,
}));

export const useUI = () => useAppStore((state) => ({
  isSidebarCollapsed: state.isSidebarCollapsed,
  toggleSidebar: state.toggleSidebar,
  setSidebarCollapsed: state.setSidebarCollapsed,
  theme: state.theme,
  setTheme: state.setTheme,
  toggleTheme: state.toggleTheme,
}));

export const useLoadingError = () => useAppStore((state) => ({
  isLoading: state.isLoading,
  error: state.error,
  setLoading: state.setLoading,
  setError: state.setError,
  clearError: state.clearError,
}));