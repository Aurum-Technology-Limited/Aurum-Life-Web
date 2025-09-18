import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService, AuthResponse, SignUpData, SignInData } from '../utils/supabase/auth';
import { User } from '../types/app';

export interface AuthState {
  // Auth state
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // First time user flag (for onboarding)
  isFirstTimeUser: boolean;
  
  // Actions
  signUp: (data: SignUpData) => Promise<void>;
  signIn: (data: SignInData) => Promise<void>;
  demoLogin: () => Promise<void>;
  signOut: () => Promise<void>;
  refreshSession: () => Promise<void>;
  clearError: () => void;
  initializeAuth: () => Promise<void>;
  markAsExistingUser: () => void;
  resetDemoOnboarding: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      isFirstTimeUser: false,
      
      signUp: async (data: SignUpData) => {
        set({ isLoading: true, error: null });
        
        try {
          // Timeout protection for signUp
          const timeoutPromise = new Promise<never>((_, reject) => {
            setTimeout(() => reject(new Error('Sign up request timed out')), 3000);
          });
          
          const response: AuthResponse = await Promise.race([
            authService.signUp(data),
            timeoutPromise
          ]);
          
          if (response.error) {
            set({ error: response.error, isLoading: false });
            return;
          }
          
          if (response.user) {
            set({ 
              user: response.user, 
              isAuthenticated: true, 
              isFirstTimeUser: true, // New user should see onboarding
              isLoading: false 
            });
          }
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to create account', 
            isLoading: false 
          });
        }
      },
      
      signIn: async (data: SignInData) => {
        set({ isLoading: true, error: null });
        
        try {
          // Timeout protection for signIn
          const timeoutPromise = new Promise<never>((_, reject) => {
            setTimeout(() => reject(new Error('Sign in request timed out')), 3000);
          });
          
          const response: AuthResponse = await Promise.race([
            authService.signIn(data),
            timeoutPromise
          ]);
          
          if (response.error) {
            set({ error: response.error, isLoading: false });
            return;
          }
          
          if (response.user) {
            // Check if user has completed onboarding before by checking localStorage
            const onboardingCompleted = localStorage.getItem('aurum-onboarding');
            const onboardingData = onboardingCompleted ? JSON.parse(onboardingCompleted) : null;
            const hasCompletedOnboarding = onboardingData?.state?.isOnboardingComplete || false;
            
            set({ 
              user: response.user, 
              isAuthenticated: true,
              // First time user if they haven't completed onboarding
              isFirstTimeUser: !hasCompletedOnboarding,
              isLoading: false 
            });
          }
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to sign in', 
            isLoading: false 
          });
        }
      },

      demoLogin: async () => {
        set({ isLoading: true, error: null });
        
        try {
          console.log('Starting local demo login...');
          
          // Since demo login is now local, we don't need timeout protection, but keep it for safety
          const timeoutPromise = new Promise<never>((_, reject) => {
            setTimeout(() => reject(new Error('Demo login took too long')), 1000); // Reduced to 1 second
          });
          
          const response: AuthResponse = await Promise.race([
            authService.demoLogin(),
            timeoutPromise
          ]);
          
          if (response.error) {
            console.error('Demo login failed:', response.error);
            set({ error: response.error, isLoading: false });
            return;
          }
          
          if (response.user) {
            console.log('Demo login successful:', response.user.id);
            
            // Enable smart onboarding for demo users to test the full flow
            set({ 
              user: response.user, 
              isAuthenticated: true,
              isFirstTimeUser: true, // Demo user should see onboarding flow
              isLoading: false 
            });
            
            // Clear any existing onboarding data to ensure fresh start
            localStorage.removeItem('aurum-onboarding');
            
            console.log('Demo user setup for onboarding flow - localStorage cleared');
          } else {
            console.error('Demo login succeeded but no user returned');
            set({ 
              error: 'Demo login succeeded but no user data received', 
              isLoading: false 
            });
          }
        } catch (error) {
          console.error('Demo login exception:', error);
          
          // Fallback: Create demo user directly in store if auth service fails
          console.log('Demo login failed, creating fallback demo user...');
          const fallbackDemoUser = {
            id: 'demo-user-fallback-' + Date.now(),
            email: 'demo@aurumlife.com',
            name: 'Demo User',
            avatar_url: null,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };
          
          // Save fallback user to localStorage
          localStorage.setItem('supabase_user', JSON.stringify(fallbackDemoUser));
          localStorage.setItem('supabase_access_token', 'demo-fallback-token');
          
          set({ 
            user: fallbackDemoUser,
            isAuthenticated: true,
            isFirstTimeUser: true,
            isLoading: false,
            error: null
          });
          
          console.log('Fallback demo user created successfully');
        }
      },
      
      signOut: async () => {
        set({ isLoading: true });
        
        try {
          await authService.signOut();
          set({ 
            user: null, 
            isAuthenticated: false, 
            isFirstTimeUser: false,
            error: null,
            isLoading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to sign out', 
            isLoading: false 
          });
        }
      },
      
      refreshSession: async () => {
        set({ isLoading: true });
        
        try {
          // Timeout protection for session refresh
          const timeoutPromise = new Promise<never>((_, reject) => {
            setTimeout(() => reject(new Error('Session refresh timed out')), 3000);
          });
          
          const response: AuthResponse = await Promise.race([
            authService.refreshSession(),
            timeoutPromise
          ]);
          
          if (response.error || !response.user) {
            // Session refresh failed, sign out
            set({ 
              user: null, 
              isAuthenticated: false, 
              isFirstTimeUser: false,
              error: null,
              isLoading: false 
            });
            return;
          }
          
          set({ 
            user: response.user, 
            isAuthenticated: true,
            isLoading: false 
          });
        } catch (error) {
          set({ 
            user: null, 
            isAuthenticated: false, 
            isFirstTimeUser: false,
            error: null,
            isLoading: false 
          });
        }
      },
      
      clearError: () => {
        set({ error: null });
      },
      
      initializeAuth: async () => {
        set({ isLoading: true });
        
        try {
          // Ultra-quick timeout protection - 500ms max
          const timeoutPromise = new Promise<never>((_, reject) => {
            setTimeout(() => reject(new Error('Auth initialization timeout')), 500);
          });
          
          const user = await Promise.race([
            authService.getStoredUser(),
            timeoutPromise
          ]);
          
          if (user) {
            // Check if user has completed onboarding before by checking localStorage
            const onboardingCompleted = localStorage.getItem('aurum-onboarding');
            const onboardingData = onboardingCompleted ? JSON.parse(onboardingCompleted) : null;
            const hasCompletedOnboarding = onboardingData?.state?.isOnboardingComplete || false;
            
            set({ 
              user, 
              isAuthenticated: true,
              // First time user if they haven't completed onboarding
              isFirstTimeUser: !hasCompletedOnboarding,
              isLoading: false,
              error: null
            });
          } else {
            set({ 
              user: null, 
              isAuthenticated: false,
              isFirstTimeUser: false,
              isLoading: false,
              error: null
            });
          }
        } catch (error) {
          console.error('Failed to initialize auth:', error);
          set({ 
            user: null, 
            isAuthenticated: false,
            isFirstTimeUser: false,
            isLoading: false,
            error: null // Don't show auth init errors to user
          });
        }
      },
      
      markAsExistingUser: () => {
        set({ isFirstTimeUser: false });
      },
      
      resetDemoOnboarding: () => {
        const { user } = get();
        if (user?.email === 'demo@aurumlife.com') {
          // Reset demo user to first-time status
          set({ isFirstTimeUser: true });
          
          // Clear onboarding data
          localStorage.removeItem('aurum-onboarding');
          
          console.log('Demo onboarding reset - user will see onboarding flow on next load');
        }
      },
    }),
    {
      name: 'aurum-auth',
      partialize: (state) => ({
        isFirstTimeUser: state.isFirstTimeUser,
      }),
    }
  )
);