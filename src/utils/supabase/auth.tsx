import { projectId, publicAnonKey } from './info';
import { User } from '../../types/app';

export interface AuthResponse {
  user?: User;
  session?: {
    access_token: string;
    refresh_token: string;
    expires_at: number;
  };
  error?: string;
}

export interface SignUpData {
  email: string;
  password: string;
  name: string;
}

export interface SignInData {
  email: string;
  password: string;
}

const API_BASE = `https://${projectId}.supabase.co/functions/v1/make-server-dd6e2894`;

class AuthService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    // Try to restore session from localStorage
    this.restoreSession();
  }

  private saveSession(session: { access_token: string; refresh_token: string; expires_at: number }) {
    this.accessToken = session.access_token;
    this.refreshToken = session.refresh_token;
    
    localStorage.setItem('supabase_access_token', session.access_token);
    localStorage.setItem('supabase_refresh_token', session.refresh_token);
    localStorage.setItem('supabase_expires_at', session.expires_at.toString());
  }

  private saveUser(user: User) {
    localStorage.setItem('supabase_user', JSON.stringify(user));
  }

  private getStoredUserData(): User | null {
    try {
      const userData = localStorage.getItem('supabase_user');
      return userData ? JSON.parse(userData) : null;
    } catch {
      return null;
    }
  }

  private restoreSession() {
    this.accessToken = localStorage.getItem('supabase_access_token');
    this.refreshToken = localStorage.getItem('supabase_refresh_token');
  }

  private clearSession() {
    this.accessToken = null;
    this.refreshToken = null;
    
    localStorage.removeItem('supabase_access_token');
    localStorage.removeItem('supabase_refresh_token');
    localStorage.removeItem('supabase_expires_at');
    localStorage.removeItem('supabase_user');
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${API_BASE}${endpoint}`;
    
    // Create an AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // Reduced to 5 second timeout
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${publicAnonKey}`,
          ...(options.headers || {}),
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timed out - please check your connection and try again');
      }
      throw error;
    }
  }

  async signUp(data: SignUpData): Promise<AuthResponse> {
    try {
      const result = await this.makeRequest('/auth/signup', {
        method: 'POST',
        body: JSON.stringify(data),
      });

      if (result.user) {
        this.saveUser(result.user);
      }

      return { user: result.user };
    } catch (error) {
      console.error('Sign up error:', error);
      return { error: error instanceof Error ? error.message : 'Failed to create account' };
    }
  }

  async signIn(data: SignInData): Promise<AuthResponse> {
    try {
      // Special handling for demo credentials - work offline
      if (data.email === 'demo@aurumlife.com' && data.password === 'demo123') {
        console.log('AuthService: Handling demo credentials locally...');
        return this.demoLogin();
      }

      const result = await this.makeRequest('/auth/signin', {
        method: 'POST',
        body: JSON.stringify(data),
      });

      if (result.session) {
        this.saveSession(result.session);
      }

      if (result.user) {
        this.saveUser(result.user);
      }

      return { user: result.user, session: result.session };
    } catch (error) {
      console.error('Sign in error:', error);
      
      // Fallback for demo credentials if network fails
      if (data.email === 'demo@aurumlife.com' && data.password === 'demo123') {
        console.log('AuthService: Network failed, using local demo fallback...');
        return this.demoLogin();
      }
      
      return { error: error instanceof Error ? error.message : 'Failed to sign in' };
    }
  }

  async refreshSession(): Promise<AuthResponse> {
    if (!this.refreshToken) {
      return { error: 'No refresh token available' };
    }

    try {
      const result = await this.makeRequest('/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      if (result.session) {
        this.saveSession(result.session);
      }

      if (result.user) {
        this.saveUser(result.user);
      }

      return { user: result.user, session: result.session };
    } catch (error) {
      console.error('Session refresh error:', error);
      this.clearSession();
      return { error: error instanceof Error ? error.message : 'Failed to refresh session' };
    }
  }

  async signOut(): Promise<void> {
    this.clearSession();
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  isSessionExpired(): boolean {
    const expiresAt = localStorage.getItem('supabase_expires_at');
    if (!expiresAt) return true;
    
    return Date.now() >= parseInt(expiresAt) * 1000;
  }

  async demoLogin(): Promise<AuthResponse> {
    try {
      console.log('AuthService: Starting local demo login...');
      
      // Create demo user locally without network request
      const demoUser: User = {
        id: 'demo-user-12345',
        email: 'demo@aurumlife.com',
        name: 'Demo User',
        avatar_url: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      // Create demo session locally
      const demoSession = {
        access_token: 'demo-access-token-' + Date.now(),
        refresh_token: 'demo-refresh-token-' + Date.now(),
        expires_at: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hours from now
      };

      console.log('AuthService: Saving demo session and user...');
      this.saveSession(demoSession);
      this.saveUser(demoUser);

      console.log('AuthService: Demo login completed successfully');
      return { user: demoUser, session: demoSession };
    } catch (error) {
      console.error('AuthService: Demo login error:', error);
      return { 
        error: error instanceof Error 
          ? `Demo login failed: ${error.message}` 
          : 'Demo login failed - please try again' 
      };
    }
  }

  async getStoredUser(): Promise<User | null> {
    try {
      // Quick check - if no access token, return null immediately
      if (!this.isAuthenticated()) {
        return null;
      }

      // If session is expired, try to refresh but with shorter timeout
      if (this.isSessionExpired()) {
        try {
          const refreshResult = await this.refreshSession();
          if (refreshResult.error || !refreshResult.user) {
            this.clearSession(); // Clear invalid session
            return null;
          }
          return refreshResult.user;
        } catch (refreshError) {
          console.warn('Session refresh failed, clearing session:', refreshError);
          this.clearSession();
          return null;
        }
      }

      // Return stored user data if session is still valid
      return this.getStoredUserData();
    } catch (error) {
      console.error('Error getting stored user:', error);
      this.clearSession(); // Clear session on any error
      return null;
    }
  }
}

export const authService = new AuthService();