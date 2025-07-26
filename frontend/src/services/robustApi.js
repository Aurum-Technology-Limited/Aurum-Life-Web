/**
 * Robust API client with fallback mechanisms and performance optimizations
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

// Create optimized axios instance
const createApiClient = () => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 8000, // 8 second timeout
    headers: {
      'Content-Type': 'application/json',
    },
    // Performance optimizations
    withCredentials: false,
    maxRedirects: 0,
  });

  // Request interceptor with performance tracking
  client.interceptors.request.use((config) => {
    config.metadata = { startTime: Date.now() };
    
    // Add auth token
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  });

  // Response interceptor with error handling
  client.interceptors.response.use(
    (response) => {
      const duration = Date.now() - response.config.metadata.startTime;
      if (duration > 3000) {
        console.warn(`⚠️ Slow API request: ${response.config.url} took ${duration}ms`);
      }
      return response;
    },
    (error) => {
      if (error.response?.status === 401) {
        console.warn('🔑 Authentication failed - redirecting to login');
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        window.location.href = '/';
        return Promise.reject(new Error('Authentication failed'));
      }
      
      console.error('🚨 API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        message: error.message
      });
      
      return Promise.reject(error);
    }
  );

  return client;
};

// Robust API wrapper with retry logic
const robustApiCall = async (apiCall, retries = 2) => {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const result = await apiCall();
      return result;
    } catch (error) {
      console.log(`🔄 API attempt ${attempt + 1} failed:`, error.message);
      
      if (attempt === retries) {
        throw error;
      }
      
      // Wait before retry
      await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
    }
  }
};

const apiClient = createApiClient();

// Optimized API methods
export const insightsAPI = {
  getInsights: (dateRange = 'all_time', areaId = null) => {
    return robustApiCall(() => {
      let url = `/api/insights?date_range=${dateRange}`;
      if (areaId) url += `&area_id=${areaId}`;
      console.log('📊 Making insights API call to:', url);
      return apiClient.get(url);
    });
  }
};

export const areasAPI = {
  getAreas: (includeProjects = true, includeArchived = false) => {
    return robustApiCall(() => {
      const url = `/api/areas?include_projects=${includeProjects}&include_archived=${includeArchived}`;
      console.log('🗂️ Making areas API call to:', url);
      return apiClient.get(url);
    });
  }
};

export const authAPI = {
  login: (credentials) => {
    return robustApiCall(() => {
      console.log('🔐 Making login API call');
      return apiClient.post('/api/auth/login', credentials);
    });
  }
};

export default apiClient;