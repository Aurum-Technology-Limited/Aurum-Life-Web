/**
 * Auth Store Tests
 * Testing authentication state management
 */

import { renderHook, act } from '@testing-library/react';

// We need to unmock the authStore for this test
jest.unmock('../../stores/authStore');

// Mock Supabase client
const mockSupabaseClient = {
  auth: {
    getSession: jest.fn(),
    signInWithPassword: jest.fn(),
    signUp: jest.fn(),
    signOut: jest.fn(),
    onAuthStateChange: jest.fn(),
  },
};

jest.mock('../../utils/supabase/client', () => ({
  createClient: () => mockSupabaseClient,
}));

import { useAuthStore } from '../../stores/authStore';

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      isFirstTimeUser: true,
    });
    
    // Clear all mocks
    jest.clearAllMocks();
    
    // Reset localStorage
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

  it('initializes with correct default state', () => {
    const { result } = renderHook(() => useAuthStore());

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.isFirstTimeUser).toBe(true);
  });

  it('handles successful sign in', async () => {
    const mockUser = { id: '1', email: 'test@example.com' };
    const mockSession = { access_token: 'mock-token' };

    mockSupabaseClient.auth.signInWithPassword.mockResolvedValue({
      data: { user: mockUser, session: mockSession },
      error: null,
    });

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.signIn('test@example.com', 'password');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('handles sign in errors', async () => {
    const mockError = { message: 'Invalid credentials' };

    mockSupabaseClient.auth.signInWithPassword.mockResolvedValue({
      data: { user: null, session: null },
      error: mockError,
    });

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.signIn('test@example.com', 'wrongpassword');
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Invalid credentials');
  });

  it('handles successful sign up', async () => {
    const mockUser = { id: '1', email: 'newuser@example.com' };
    const mockSession = { access_token: 'mock-token' };

    mockSupabaseClient.auth.signUp.mockResolvedValue({
      data: { user: mockUser, session: mockSession },
      error: null,
    });

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.signUp('newuser@example.com', 'password', 'New User');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.isFirstTimeUser).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it('handles sign up errors', async () => {
    const mockError = { message: 'Email already exists' };

    mockSupabaseClient.auth.signUp.mockResolvedValue({
      data: { user: null, session: null },
      error: mockError,
    });

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.signUp('existing@example.com', 'password', 'User');
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.error).toBe('Email already exists');
  });

  it('handles sign out', async () => {
    // First sign in
    const mockUser = { id: '1', email: 'test@example.com' };
    
    useAuthStore.setState({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false,
      error: null,
    });

    mockSupabaseClient.auth.signOut.mockResolvedValue({
      error: null,
    });

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.signOut();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('clears errors', () => {
    useAuthStore.setState({
      error: 'Some error',
    });

    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
  });

  it('marks user as existing', () => {
    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.markAsExistingUser();
    });

    expect(result.current.isFirstTimeUser).toBe(false);
  });

  it('persists auth state to localStorage', async () => {
    const mockUser = { id: '1', email: 'test@example.com' };
    const mockSession = { access_token: 'mock-token' };

    mockSupabaseClient.auth.signInWithPassword.mockResolvedValue({
      data: { user: mockUser, session: mockSession },
      error: null,
    });

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.signIn('test@example.com', 'password');
    });

    expect(localStorage.setItem).toHaveBeenCalledWith(
      'aurum-auth',
      expect.stringContaining('"isAuthenticated":true')
    );
  });

  it('handles session initialization', async () => {
    const mockUser = { id: '1', email: 'test@example.com' };
    const mockSession = { access_token: 'mock-token' };

    mockSupabaseClient.auth.getSession.mockResolvedValue({
      data: { session: mockSession },
      error: null,
    });

    // Mock stored auth data
    (localStorage.getItem as jest.Mock).mockReturnValue(
      JSON.stringify({
        user: mockUser,
        isAuthenticated: true,
        isFirstTimeUser: false,
      })
    );

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.initializeAuth();
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('handles loading states correctly', async () => {
    mockSupabaseClient.auth.signInWithPassword.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        data: { user: null, session: null },
        error: { message: 'Error' },
      }), 100))
    );

    const { result } = renderHook(() => useAuthStore());

    expect(result.current.isLoading).toBe(false);

    act(() => {
      result.current.signIn('test@example.com', 'password');
    });

    expect(result.current.isLoading).toBe(true);

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 150));
    });

    expect(result.current.isLoading).toBe(false);
  });

  it('handles network timeouts gracefully', async () => {
    mockSupabaseClient.auth.signInWithPassword.mockImplementation(
      () => new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Network timeout')), 100)
      )
    );

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.signIn('test@example.com', 'password');
    });

    expect(result.current.error).toBe('Network timeout');
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('handles auth state changes from Supabase', () => {
    let authChangeCallback: any;

    mockSupabaseClient.auth.onAuthStateChange.mockImplementation((callback) => {
      authChangeCallback = callback;
      return { data: { subscription: { unsubscribe: jest.fn() } } };
    });

    const { result } = renderHook(() => useAuthStore());

    // Initialize auth to set up the listener
    act(() => {
      result.current.initializeAuth();
    });

    // Simulate auth state change
    const mockUser = { id: '1', email: 'test@example.com' };
    const mockSession = { access_token: 'mock-token' };

    act(() => {
      authChangeCallback('SIGNED_IN', mockSession);
    });

    expect(result.current.isAuthenticated).toBe(true);
  });
});

describe('AuthStore Edge Cases', () => {
  it('handles malformed localStorage data', async () => {
    (localStorage.getItem as jest.Mock).mockReturnValue('invalid-json');

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.initializeAuth();
    });

    // Should not crash and should use default state
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('handles missing user data in session', async () => {
    mockSupabaseClient.auth.getSession.mockResolvedValue({
      data: { session: { access_token: 'token' } },
      error: null,
    });

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.initializeAuth();
    });

    expect(result.current.isAuthenticated).toBe(false);
  });

  it('handles concurrent sign in attempts', async () => {
    const mockUser = { id: '1', email: 'test@example.com' };

    mockSupabaseClient.auth.signInWithPassword.mockResolvedValue({
      data: { user: mockUser, session: { access_token: 'token' } },
      error: null,
    });

    const { result } = renderHook(() => useAuthStore());

    // Start multiple sign in attempts
    const promises = [
      result.current.signIn('test@example.com', 'password'),
      result.current.signIn('test@example.com', 'password'),
      result.current.signIn('test@example.com', 'password'),
    ];

    await act(async () => {
      await Promise.all(promises);
    });

    // Should handle gracefully without breaking state
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });
});