import { authService } from './auth';
import { projectId, publicAnonKey } from './info';

const API_BASE = `https://${projectId}.supabase.co/functions/v1/make-server-dd6e2894`;

interface ApiRequestOptions extends RequestInit {
  requireAuth?: boolean;
}

class ApiService {
  async makeRequest(endpoint: string, options: ApiRequestOptions = {}): Promise<any> {
    const { requireAuth = false, ...requestOptions } = options;
    const url = `${API_BASE}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${publicAnonKey}`,
      ...(requestOptions.headers as Record<string, string> || {}),
    };

    // Add access token for authenticated requests
    if (requireAuth) {
      const accessToken = authService.getAccessToken();
      if (!accessToken) {
        throw new Error('Authentication required');
      }
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const response = await fetch(url, {
      ...requestOptions,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // User preferences methods
  async getUserPreferences() {
    return this.makeRequest('/user/preferences', {
      method: 'GET',
      requireAuth: true,
    });
  }

  async updateUserPreferences(preferences: any) {
    return this.makeRequest('/user/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences),
      requireAuth: true,
    });
  }

  // Add more API methods here as needed
  // Example:
  // async getPillars() {
  //   return this.makeRequest('/pillars', {
  //     method: 'GET',
  //     requireAuth: true,
  //   });
  // }
}

export const apiService = new ApiService();