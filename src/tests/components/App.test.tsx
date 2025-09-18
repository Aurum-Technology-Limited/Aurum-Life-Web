/**
 * App Component Tests
 * Core application functionality and integration tests
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import App from '../../App';
import { useAuthStore } from '../../stores/authStore';
import { useOnboardingStore } from '../../stores/onboardingStore';

// Mock the stores
jest.mock('../../stores/authStore');
jest.mock('../../stores/onboardingStore');

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;
const mockUseOnboardingStore = useOnboardingStore as jest.MockedFunction<typeof useOnboardingStore>;

// Mock components that might cause issues in tests
jest.mock('../../components/onboarding/OnboardingFlow', () => {
  return function MockOnboardingFlow() {
    return <div data-testid="onboarding-flow">Onboarding Flow</div>;
  };
});

jest.mock('../../components/auth/TimeoutResistantLogin', () => {
  return function MockLogin({ onLogin }: { onLogin: () => void }) {
    return (
      <div data-testid="login-screen">
        <button onClick={onLogin}>Sign In</button>
      </div>
    );
  };
});

describe('App Component', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });
  });

  it('shows loading screen initially', () => {
    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,
      isFirstTimeUser: false,
      signIn: jest.fn(),
      signUp: jest.fn(),
      clearError: jest.fn(),
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: false,
      resetOnboarding: jest.fn(),
    });

    render(<App />);

    // Should show loading state initially
    expect(screen.getByText(/initializing aurum life/i)).toBeInTheDocument();
  });

  it('shows login screen when not authenticated', async () => {
    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      isFirstTimeUser: false,
      signIn: jest.fn(),
      signUp: jest.fn(),
      clearError: jest.fn(),
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: false,
      resetOnboarding: jest.fn(),
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    }, { timeout: 6000 });
  });

  it('shows onboarding for first-time users', async () => {
    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@example.com' },
      isAuthenticated: true,
      isLoading: false,
      error: null,
      isFirstTimeUser: true,
      signIn: jest.fn(),
      signUp: jest.fn(),
      clearError: jest.fn(),
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: false,
      resetOnboarding: jest.fn(),
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByTestId('onboarding-flow')).toBeInTheDocument();
    }, { timeout: 6000 });
  });

  it('shows main app for authenticated users who completed onboarding', async () => {
    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@example.com' },
      isAuthenticated: true,
      isLoading: false,
      error: null,
      isFirstTimeUser: false,
      signIn: jest.fn(),
      signUp: jest.fn(),
      clearError: jest.fn(),
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: true,
      resetOnboarding: jest.fn(),
    });

    render(<App />);

    await waitFor(() => {
      // Should show main app UI
      expect(screen.getByText(/welcome to your personal operating system/i)).toBeInTheDocument();
    }, { timeout: 6000 });
  });

  it('handles demo user correctly', async () => {
    const mockResetOnboarding = jest.fn();
    
    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'demo@aurumlife.com' },
      isAuthenticated: true,
      isLoading: false,
      error: null,
      isFirstTimeUser: false,
      signIn: jest.fn(),
      signUp: jest.fn(),
      clearError: jest.fn(),
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: true,
      resetOnboarding: mockResetOnboarding,
    });

    // Mock the store's getState method
    useOnboardingStore.getState = jest.fn().mockReturnValue({
      resetOnboarding: mockResetOnboarding,
    });

    render(<App />);

    await waitFor(() => {
      expect(mockResetOnboarding).toHaveBeenCalled();
    }, { timeout: 6000 });
  });

  it('handles authentication errors gracefully', async () => {
    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: 'Authentication failed',
      isFirstTimeUser: false,
      signIn: jest.fn(),
      signUp: jest.fn(),
      clearError: jest.fn(),
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: false,
      resetOnboarding: jest.fn(),
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    }, { timeout: 6000 });
  });

  it('handles app-level errors gracefully', async () => {
    // Mock console.error to avoid test noise
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@example.com' },
      isAuthenticated: true,
      isLoading: false,
      error: null,
      isFirstTimeUser: false,
      signIn: jest.fn(),
      signUp: jest.fn(),
      clearError: jest.fn(),
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: true,
      resetOnboarding: jest.fn(),
    });

    render(<App />);

    // Simulate an error
    const errorEvent = new ErrorEvent('error', {
      error: new Error('Test error'),
      message: 'Test error',
    });
    
    window.dispatchEvent(errorEvent);

    await waitFor(() => {
      // App should still be functional
      expect(screen.getByText(/welcome to your personal operating system/i)).toBeInTheDocument();
    }, { timeout: 6000 });

    consoleSpy.mockRestore();
  });

  it('respects timeout configurations', async () => {
    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,
      isFirstTimeUser: false,
      signIn: jest.fn(),
      signUp: jest.fn(),
      clearError: jest.fn(),
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: false,
      resetOnboarding: jest.fn(),
    });

    render(<App />);

    // Should timeout and show login after 6 seconds
    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    }, { timeout: 7000 });
  });

  it('initializes theme correctly', async () => {
    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@example.com' },
      isAuthenticated: true,
      isLoading: false,
      error: null,
      isFirstTimeUser: false,
      signIn: jest.fn(),
      signUp: jest.fn(),
      clearError: jest.fn(),
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: true,
      resetOnboarding: jest.fn(),
    });

    render(<App />);

    await waitFor(() => {
      // Check if dark theme is applied
      expect(document.body.classList.contains('dark')).toBe(true);
    }, { timeout: 6000 });
  });
});

describe('App Integration Tests', () => {
  it('handles complete authentication flow', async () => {
    const mockSignIn = jest.fn();
    const mockClearError = jest.fn();

    // Start with unauthenticated state
    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      isFirstTimeUser: false,
      signIn: mockSignIn,
      signUp: jest.fn(),
      clearError: mockClearError,
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: true,
      resetOnboarding: jest.fn(),
    });

    const { rerender } = render(<App />);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    }, { timeout: 6000 });

    // Simulate successful login
    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@example.com' },
      isAuthenticated: true,
      isLoading: false,
      error: null,
      isFirstTimeUser: false,
      signIn: mockSignIn,
      signUp: jest.fn(),
      clearError: mockClearError,
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    rerender(<App />);

    await waitFor(() => {
      expect(screen.getByText(/welcome to your personal operating system/i)).toBeInTheDocument();
    }, { timeout: 6000 });
  });

  it('handles mobile vs desktop rendering', async () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@example.com' },
      isAuthenticated: true,
      isLoading: false,
      error: null,
      isFirstTimeUser: false,
      signIn: jest.fn(),
      signUp: jest.fn(),
      clearError: jest.fn(),
      initializeAuth: jest.fn(),
      markAsExistingUser: jest.fn(),
    });

    mockUseOnboardingStore.mockReturnValue({
      isOnboardingComplete: true,
      resetOnboarding: jest.fn(),
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/welcome to your personal operating system/i)).toBeInTheDocument();
    }, { timeout: 6000 });

    // Should render mobile-specific elements
    expect(document.querySelector('.mobile-content-safe')).toBeTruthy();
  });
});