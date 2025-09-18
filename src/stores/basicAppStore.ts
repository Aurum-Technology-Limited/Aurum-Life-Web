import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { SectionType, Notification } from '../types/app';

interface AppearanceSettings {
  glassEffect: boolean;
  reducedMotion: boolean;
  highContrast: boolean;
  fontSize: number;
  compactMode: boolean;
}

interface HierarchyContext {
  pillarId?: string;
  areaId?: string;
  projectId?: string;
  pillarName?: string;
  areaName?: string;
  projectName?: string;
}

interface AppStore {
  // UI State
  activeSection: SectionType;
  activeSettingsSection: string;
  isNotificationsOpen: boolean;
  isSidebarCollapsed: boolean;
  isMobileMenuOpen: boolean;
  
  // Hierarchical Navigation
  hierarchyContext: HierarchyContext;
  
  // Notifications
  notifications: Notification[];
  unreadCount: number;
  
  // Preferences (dark mode only)
  appearanceSettings: AppearanceSettings;
  
  // Actions
  setActiveSection: (section: SectionType, settingsSection?: string) => void;
  setActiveSettingsSection: (settingsSection: string) => void;
  openNotifications: () => void;
  closeNotifications: () => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  openMobileMenu: () => void;
  closeMobileMenu: () => void;
  toggleMobileMenu: () => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  // Theme functions removed - dark mode only
  updateAppearanceSettings: (settings: Partial<AppearanceSettings>) => void;
  resetAppearanceSettings: () => void;
  
  // Hierarchical Navigation Actions
  navigateToPillar: (pillarId: string, pillarName: string) => void;
  navigateToArea: (areaId: string, areaName: string) => void;
  navigateToAreaFromPillar: (pillarId: string, pillarName: string, areaId: string, areaName: string) => void;
  navigateToProject: (projectId: string, projectName: string) => void;
  navigateToProjectWithFullContext: (pillarId: string, pillarName: string, areaId: string, areaName: string, projectId: string, projectName: string) => void;
  navigateToTasks: () => void;
  navigateUp: () => void;
  resetHierarchy: () => void;
  navigateToBreadcrumb: (section: SectionType, context?: Partial<HierarchyContext>) => void;
}

const defaultAppearanceSettings: AppearanceSettings = {
  glassEffect: true,
  reducedMotion: false,
  highContrast: false,
  fontSize: 16,
  compactMode: false
};

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
  // Initial state
  activeSection: 'dashboard',
  activeSettingsSection: 'account',
  isNotificationsOpen: false,
  isSidebarCollapsed: false,
  isMobileMenuOpen: false,
  hierarchyContext: {},
  notifications: [],
  unreadCount: 0,
  appearanceSettings: defaultAppearanceSettings,
  
  // Actions
  
  setActiveSection: (section: SectionType, settingsSection?: string) => {
    const update: any = { activeSection: section };
    if (settingsSection) {
      update.activeSettingsSection = settingsSection;
    }
    set(update);
  },

  setActiveSettingsSection: (settingsSection: string) => {
    set({ activeSettingsSection: settingsSection });
  },
  
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
  
  openMobileMenu: () => {
    set({ isMobileMenuOpen: true });
  },
  
  closeMobileMenu: () => {
    set({ isMobileMenuOpen: false });
  },
  
  toggleMobileMenu: () => {
    set((state) => ({ isMobileMenuOpen: !state.isMobileMenuOpen }));
  },
  
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
  
  // Theme functions removed - application is dark mode only

  updateAppearanceSettings: (settings: Partial<AppearanceSettings>) => {
    set(state => ({
      appearanceSettings: { ...state.appearanceSettings, ...settings }
    }));
  },

  resetAppearanceSettings: () => {
    set({ appearanceSettings: defaultAppearanceSettings });
  },

  // Hierarchical Navigation Actions
  navigateToPillar: (pillarId: string, pillarName: string) => {
    console.log('🔗 [STORE] Navigating to pillar:', pillarName, 'ID:', pillarId);
    
    const newContext = {
      pillarId,
      pillarName,
      areaId: undefined,
      areaName: undefined,
      projectId: undefined,
      projectName: undefined,
    };
    
    console.log('🔗 [STORE] Setting new context and active section:', newContext);
    
    // Update state immediately
    set({
      activeSection: 'areas',
      hierarchyContext: newContext
    });
    
    // Immediate verification
    const updatedState = get();
    console.log('🔗 [STORE] State immediately after update:', {
      activeSection: updatedState.activeSection,
      hierarchyContext: updatedState.hierarchyContext,
      success: updatedState.hierarchyContext.pillarId === pillarId && updatedState.activeSection === 'areas'
    });
    
    // Notify other parts of the app about the navigation
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('aurumHierarchyChanged', {
        detail: { type: 'pillar', pillarId, pillarName }
      }));
    }
  },

  navigateToArea: (areaId: string, areaName: string) => {
    console.log('🔗 Navigating to area:', areaName, 'ID:', areaId);
    set(state => ({
      activeSection: 'projects',
      hierarchyContext: {
        ...state.hierarchyContext,
        areaId,
        areaName,
        projectId: undefined,
        projectName: undefined,
      }
    }));
  },

  navigateToAreaFromPillar: (pillarId: string, pillarName: string, areaId: string, areaName: string) => {
    console.log('🔗 Navigating to area from pillar:', areaName, 'from pillar:', pillarName);
    set({
      activeSection: 'projects',
      hierarchyContext: {
        pillarId,
        pillarName,
        areaId,
        areaName,
        projectId: undefined,
        projectName: undefined,
      }
    });
  },

  navigateToProject: (projectId: string, projectName: string) => {
    console.log('🔗 Navigating to project:', projectName, 'ID:', projectId);
    set(state => ({
      activeSection: 'tasks',
      hierarchyContext: {
        ...state.hierarchyContext,
        projectId,
        projectName,
      }
    }));
  },

  navigateToProjectWithFullContext: (pillarId: string, pillarName: string, areaId: string, areaName: string, projectId: string, projectName: string) => {
    console.log('🔗 Navigating to project with full context:', projectName, 'Area:', areaName, 'Pillar:', pillarName);
    set({
      activeSection: 'tasks',
      hierarchyContext: {
        pillarId,
        pillarName,
        areaId,
        areaName,
        projectId,
        projectName,
      }
    });
  },

  navigateToTasks: () => {
    set({ activeSection: 'tasks' });
  },

  navigateUp: () => {
    set(state => {
      const { hierarchyContext } = state;
      
      if (hierarchyContext.projectId) {
        // Go from tasks back to projects
        return {
          activeSection: 'projects',
          hierarchyContext: {
            ...hierarchyContext,
            projectId: undefined,
            projectName: undefined,
          }
        };
      } else if (hierarchyContext.areaId) {
        // Go from projects back to areas
        return {
          activeSection: 'areas',
          hierarchyContext: {
            ...hierarchyContext,
            areaId: undefined,
            areaName: undefined,
          }
        };
      } else if (hierarchyContext.pillarId) {
        // Go from areas back to pillars
        return {
          activeSection: 'pillars',
          hierarchyContext: {}
        };
      }
      
      return state;
    });
  },

  resetHierarchy: () => {
    set({
      hierarchyContext: {},
      activeSection: 'dashboard'
    });
  },

  navigateToBreadcrumb: (section: SectionType, context?: Partial<HierarchyContext>) => {
    if (context) {
      set({
        activeSection: section,
        hierarchyContext: {
          pillarId: context.pillarId,
          pillarName: context.pillarName,
          areaId: context.areaId,
          areaName: context.areaName,
          projectId: context.projectId,
          projectName: context.projectName,
        }
      });
    } else {
      set({ activeSection: section });
    }
  },
    }),
    {
      name: 'aurum-life-app-store',
      partialize: (state) => ({
        appearanceSettings: state.appearanceSettings,
        activeSection: state.activeSection,
        activeSettingsSection: state.activeSettingsSection,
        isSidebarCollapsed: state.isSidebarCollapsed,
        hierarchyContext: state.hierarchyContext,
      }),
    }
  )
);