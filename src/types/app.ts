// Application-wide TypeScript interfaces and types

export type SectionType = 
  | 'dashboard'
  | 'today'
  | 'pillars'
  | 'areas'
  | 'projects'
  | 'tasks'
  | 'journal'
  | 'ai-insights'
  | 'quick-actions'
  | 'goal-planner'
  | 'analytics'
  | 'feedback'
  | 'settings';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
  lastLoginAt: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  notifications: {
    email: boolean;
    push: boolean;
    desktop: boolean;
  };
  defaultView: SectionType;
  weekStartsOn: 0 | 1; // 0 = Sunday, 1 = Monday
}

export interface AppState {
  isAuthenticated: boolean;
  user: User | null;
  activeSection: SectionType;
  isNotificationsOpen: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface NavigationItem {
  id: SectionType;
  label: string;
  icon: string;
  badge?: number;
  disabled?: boolean;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Hierarchy Types for the strategic system
export interface Pillar {
  id: string;
  title: string;
  description: string;
  color: string;
  areas: Area[];
  progress: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Area {
  id: string;
  pillarId: string;
  title: string;
  description: string;
  projects: Project[];
  progress: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Project {
  id: string;
  areaId: string;
  title: string;
  description: string;
  status: 'not-started' | 'in-progress' | 'completed' | 'paused';
  priority: 'low' | 'medium' | 'high';
  dueDate?: Date;
  tasks: Task[];
  progress: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Task {
  id: string;
  projectId: string;
  title: string;
  description?: string;
  status: 'todo' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  dueDate?: Date;
  timeEstimate?: number; // in minutes
  actualTime?: number; // in minutes
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
}