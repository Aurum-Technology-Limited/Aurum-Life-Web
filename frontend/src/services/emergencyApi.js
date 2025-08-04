/**
 * EMERGENCY FIX: Ultra-lightweight API client to resolve timeout cascade
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

// Request queue to prevent overwhelming the server
const requestQueue = [];
let isProcessingQueue = false;

// Request deduplication map
const pendingRequests = new Map();

const processQueue = async () => {
  if (isProcessingQueue || requestQueue.length === 0) return;
  
  isProcessingQueue = true;
  
  while (requestQueue.length > 0) {
    const { resolve, reject, requestFn } = requestQueue.shift();
    
    try {
      const result = await requestFn();
      resolve(result);
    } catch (error) {
      reject(error);
    }
    
    // Small delay between requests to prevent overwhelming
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  isProcessingQueue = false;
};

// Create ultra-simple axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Simple error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Request failed:', error.config?.url, error.message);
    
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    
    return Promise.reject(error);
  }
);

// Queued API call wrapper
const queuedApiCall = (requestFn, cacheKey) => {
  // Check if request is already pending
  if (cacheKey && pendingRequests.has(cacheKey)) {
    return pendingRequests.get(cacheKey);
  }
  
  const promise = new Promise((resolve, reject) => {
    requestQueue.push({ resolve, reject, requestFn });
    processQueue();
  });
  
  // Cache the promise to prevent duplicate requests
  if (cacheKey) {
    pendingRequests.set(cacheKey, promise);
    
    // Clear cache after request completes
    promise.finally(() => {
      pendingRequests.delete(cacheKey);
    });
  }
  
  return promise;
};

// Emergency API methods with request queuing and ultra-performance optimization
export const emergencyAPI = {
  dashboard: () => queuedApiCall(
    async () => {
      try {
        // Try ultra-performance endpoint first
        console.log('🚀 Emergency API: Attempting ultra-performance dashboard...');
        const startTime = Date.now();
        const response = await apiClient.get('/api/ultra/dashboard');
        const duration = Date.now() - startTime;
        console.log(`✅ Emergency API: Ultra dashboard completed in ${duration}ms`);
        return response;
      } catch (error) {
        console.warn('⚠️ Emergency API: Ultra dashboard failed, falling back to regular endpoint:', error.message);
        // Fallback to regular endpoint
        return apiClient.get('/api/dashboard');
      }
    },
    'dashboard'
  ),
  
  insights: (dateRange = 'all_time', areaId = null) => {
    const cacheKey = `insights_${dateRange}_${areaId}`;
    return queuedApiCall(
      () => {
        let url = `/api/insights?date_range=${dateRange}`;
        if (areaId) url += `&area_id=${areaId}`;
        return apiClient.get(url);
      },
      cacheKey
    );
  },
  
  areas: (includeProjects = true, includeArchived = false) => {
    const cacheKey = `areas_${includeProjects}_${includeArchived}`;
    return queuedApiCall(
      () => {
        const url = `/api/areas?include_projects=${includeProjects}&include_archived=${includeArchived}`;
        return apiClient.get(url);
      },
      cacheKey
    );
  },
  
  aiCoach: () => queuedApiCall(
    () => apiClient.get('/api/ai/task-why-statements'),
    'ai_coach'
  ),
  
  aiCoachChat: (message) => queuedApiCall(
    () => apiClient.post('/api/ai/decompose-project', { 
      project_name: message,
      template_type: 'general'
    }),
    null // No caching for chat messages
  ),
  
  currentUser: () => queuedApiCall(
    () => apiClient.get('/api/auth/me'),
    'current_user'
  )
};

export default emergencyAPI;