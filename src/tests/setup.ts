/**
 * Test Setup Configuration for Aurum Life
 * Comprehensive testing setup with Jest, React Testing Library, and MSW
 */

import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { server } from './mocks/server';

// Configure React Testing Library
configure({
  testIdAttribute: 'data-testid',
});

// Mock modules that are not available in test environment
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation((callback) => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
  root: null,
  rootMargin: '',
  thresholds: [],
}));

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock performance.mark and performance.measure
Object.defineProperty(performance, 'mark', {
  writable: true,
  value: jest.fn(),
});

Object.defineProperty(performance, 'measure', {
  writable: true,
  value: jest.fn(),
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock as any;

// Mock URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'mocked-url');
global.URL.revokeObjectURL = jest.fn();

// Mock crypto.randomUUID
Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: () => 'mocked-uuid',
    getRandomValues: (arr: any) => arr.map(() => Math.random() * 256),
  },
});

// Mock fetch
global.fetch = jest.fn();

// Mock Supabase client
jest.mock('../utils/supabase/client', () => ({
  createClient: jest.fn(() => ({
    auth: {
      getSession: jest.fn(),
      signInWithPassword: jest.fn(),
      signUp: jest.fn(),
      signOut: jest.fn(),
      onAuthStateChange: jest.fn(),
    },
    from: jest.fn(() => ({
      select: jest.fn(),
      insert: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
      upsert: jest.fn(),
    })),
  })),
}));

// Mock Zustand stores
jest.mock('../stores/basicAppStore', () => ({
  useAppStore: jest.fn(() => ({
    activeSection: 'dashboard',
    setActiveSection: jest.fn(),
    isNotificationsOpen: false,
    openNotifications: jest.fn(),
    closeNotifications: jest.fn(),
  })),
}));

jest.mock('../stores/authStore', () => ({
  useAuthStore: jest.fn(() => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    signIn: jest.fn(),
    signUp: jest.fn(),
    signOut: jest.fn(),
  })),
}));

// Mock motion/react
jest.mock('motion/react', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock sonner toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
    warning: jest.fn(),
  },
}));

// Setup MSW server
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Clear all mocks after each test
afterEach(() => {
  jest.clearAllMocks();
  localStorageMock.clear();
  sessionStorageMock.clear();
});

// Global test utilities
export const createMockUser = (overrides = {}) => ({
  id: 'test-user-id',
  email: 'test@aurumlife.com',
  name: 'Test User',
  created_at: new Date().toISOString(),
  ...overrides,
});

export const createMockPillar = (overrides = {}) => ({
  id: 'test-pillar-id',
  title: 'Health & Wellness',
  description: 'Physical and mental well-being',
  color: '#10B981',
  icon: 'heart',
  progress: 75,
  created_at: new Date().toISOString(),
  ...overrides,
});

export const createMockArea = (overrides = {}) => ({
  id: 'test-area-id',
  pillar_id: 'test-pillar-id',
  title: 'Fitness',
  description: 'Regular exercise and activity',
  color: '#3B82F6',
  progress: 80,
  created_at: new Date().toISOString(),
  ...overrides,
});

export const createMockProject = (overrides = {}) => ({
  id: 'test-project-id',
  area_id: 'test-area-id',
  title: 'Morning Workout Routine',
  description: 'Establish a consistent morning exercise habit',
  status: 'in_progress',
  priority: 'high',
  due_date: new Date().toISOString(),
  progress: 60,
  created_at: new Date().toISOString(),
  ...overrides,
});

export const createMockTask = (overrides = {}) => ({
  id: 'test-task-id',
  project_id: 'test-project-id',
  title: 'Go for a 30-minute run',
  description: 'Complete a 30-minute outdoor run',
  status: 'pending',
  priority: 'medium',
  due_date: new Date().toISOString(),
  estimated_duration: 30,
  created_at: new Date().toISOString(),
  ...overrides,
});

export const createMockJournalEntry = (overrides = {}) => ({
  id: 'test-journal-id',
  title: 'Daily Reflection',
  content: 'Today was a productive day...',
  mood: 'positive',
  energy_level: 8,
  template_id: 'daily-reflection',
  tags: ['productivity', 'wellness'],
  created_at: new Date().toISOString(),
  ...overrides,
});

// Test environment setup
console.log('🧪 Test environment initialized');