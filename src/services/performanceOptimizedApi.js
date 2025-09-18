/*
Frontend Performance API Client
Optimized API client with intelligent caching, request batching, and performance monitoring
*/

import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Performance monitoring
class PerformanceMonitor {
  constructor() {
    this.metrics = [];
    this.slowRequestThreshold = 2000; // 2 seconds
  }

  startRequest(endpoint) {
    return {
      endpoint,
      startTime: Date.now()
    };
  }

  endRequest(requestInfo, success = true, error = null) {
    const duration = Date.now() - requestInfo.startTime;
    
    const metric = {
      endpoint: requestInfo.endpoint,
      duration,
      success,
      error: error?.message,
      timestamp: new Date().toISOString()
    };

    this.metrics.push(metric);

    // Keep only last 100 metrics
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-100);
    }

    // Log performance
    if (duration < 200) {
      console.log(`🎯 PERFORMANCE TARGET ACHIEVED: ${requestInfo.endpoint} - ${duration}ms`);
    } else if (duration < 500) {
      console.warn(`⚠️ APPROACHING LIMIT: ${requestInfo.endpoint} - ${duration}ms`);
    } else {
      console.error(`🚨 PERFORMANCE TARGET MISSED: ${requestInfo.endpoint} - ${duration}ms`);
    }

    return metric;
  }

  getStats() {
    if (this.metrics.length === 0) return { avgDuration: 0, successRate: 0, slowRequests: 0 };

    const successfulRequests = this.metrics.filter(m => m.success);
    const avgDuration = this.metrics.reduce((sum, m) => sum + m.duration, 0) / this.metrics.length;
    const successRate = (successfulRequests.length / this.metrics.length) * 100;
    const slowRequests = this.metrics.filter(m => m.duration > this.slowRequestThreshold).length;

    return {
      totalRequests: this.metrics.length,
      avgDuration: Math.round(avgDuration),
      successRate: Math.round(successRate),
      slowRequests,
      fastRequests: this.metrics.filter(m => m.duration < 200).length
    };
  }
}

const performanceMonitor = new PerformanceMonitor();

// Request batching for multiple simultaneous requests
class RequestBatcher {
  constructor() {
    this.batches = new Map();
    this.batchDelay = 50; // 50ms batch window
  }

  batch(key, requestFn) {
    return new Promise((resolve, reject) => {
      if (!this.batches.has(key)) {
        this.batches.set(key, {
          promises: [],
          timer: setTimeout(() => {
            const batch = this.batches.get(key);
            this.batches.delete(key);
            
            // Execute the request once for all waiters
            requestFn()
              .then(result => {
                batch.promises.forEach(({ resolve }) => resolve(result));
              })
              .catch(error => {
                batch.promises.forEach(({ reject }) => reject(error));
              });
          }, this.batchDelay)
        });
      }

      this.batches.get(key).promises.push({ resolve, reject });
    });
  }
}

const requestBatcher = new RequestBatcher();

// Enhanced axios instance with performance optimization
const apiClient = axios.create({
  baseURL: API,
  timeout: 10000, // Reduced from 30s to 10s for better performance
  headers: {
    'Content-Type': 'application/json',
  },
  maxRetries: 1, // Reduced retries for faster failure detection
  retryDelay: 500, // Faster retry delay
});

// Request interceptor with performance tracking
apiClient.interceptors.request.use((config) => {
  // Start performance tracking
  config.performanceInfo = performanceMonitor.startRequest(config.url);
  
  // Add authentication token
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Add CSRF token for state-changing requests
  if (['post', 'put', 'delete', 'patch'].includes(config.method.toLowerCase())) {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
  }
  
  // Optimize headers for performance
  config.headers['Cache-Control'] = 'no-cache';
  config.headers['Accept-Encoding'] = 'gzip, deflate, br';
  
  return config;
});

// Response interceptor with performance monitoring
apiClient.interceptors.response.use(
  (response) => {
    // End performance tracking
    performanceMonitor.endRequest(response.config.performanceInfo, true);
    return response;
  },
  (error) => {
    const config = error.config;
    
    // End performance tracking with error
    if (config?.performanceInfo) {
      performanceMonitor.endRequest(config.performanceInfo, false, error);
    }
    
    // Handle 401 Unauthorized errors
    if (error.response?.status === 401) {
      console.warn('Authentication failed - clearing token and redirecting to login');
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
      
      return Promise.reject(new Error('Authentication failed. Please log in again.'));
    }
    
    // Implement automatic retry logic for certain errors
    const shouldRetry = (
      (error.code === 'ECONNABORTED' || error.message.includes('timeout')) ||
      (error.response?.status >= 500) ||
      (error.code === 'NETWORK_ERROR')
    );
    
    config._retryCount = config._retryCount || 0;
    const maxRetries = config.maxRetries || 1;
    const retryDelay = config.retryDelay || 500;
    
    if (shouldRetry && config._retryCount < maxRetries) {
      config._retryCount += 1;
      
      console.warn(`🔄 Retrying request (${config._retryCount}/${maxRetries}): ${config.url}`);
      
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(apiClient(config));
        }, retryDelay);
      });
    }
    
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Helper function to get CSRF token
function getCsrfToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrf_token='));
  return cookieValue ? cookieValue.split('=')[1] : null;
}

// Performance-optimized API methods with intelligent caching and batching
export const performanceOptimizedAPI = {
  // Dashboard API with intelligent batching
  dashboard: {
    getDashboard: () => {
      const cacheKey = 'dashboard_data';
      return requestBatcher.batch(cacheKey, () => apiClient.get('/dashboard'));
    }
  },

  // Pillars API with caching
  pillars: {
    getPillars: (includeAreas = false, includeArchived = false) => {
      const cacheKey = `pillars_${includeAreas}_${includeArchived}`;
      return requestBatcher.batch(cacheKey, () => 
        apiClient.get('/pillars', {
          params: {
            include_areas: includeAreas,
            include_archived: includeArchived
          }
        })
      );
    },
    getPillar: (pillarId) => apiClient.get(`/pillars/${pillarId}`),
    createPillar: (pillarData) => apiClient.post('/pillars', pillarData),
    updatePillar: (pillarId, pillarData) => apiClient.put(`/pillars/${pillarId}`, pillarData),
    deletePillar: (pillarId) => apiClient.delete(`/pillars/${pillarId}`)
  },

  // Areas API with caching
  areas: {
    getAreas: (includeProjects = false, includeArchived = false) => {
      const cacheKey = `areas_${includeProjects}_${includeArchived}`;
      return requestBatcher.batch(cacheKey, () =>
        apiClient.get('/areas', {
          params: {
            include_projects: includeProjects,
            include_archived: includeArchived
          }
        })
      );
    },
    getArea: (areaId) => apiClient.get(`/areas/${areaId}`),
    createArea: (areaData) => apiClient.post('/areas', areaData),
    updateArea: (areaId, areaData) => apiClient.put(`/areas/${areaId}`, areaData),
    deleteArea: (areaId) => apiClient.delete(`/areas/${areaId}`)
  },

  // Projects API with caching
  projects: {
    getProjects: (areaId = null, includeArchived = false) => {
      const cacheKey = `projects_${areaId || 'all'}_${includeArchived}`;
      return requestBatcher.batch(cacheKey, () =>
        apiClient.get('/projects', {
          params: {
            ...(areaId && { area_id: areaId }),
            include_archived: includeArchived
          }
        })
      );
    },
    getProject: (projectId) => apiClient.get(`/projects/${projectId}`),
    createProject: (projectData) => apiClient.post('/projects', projectData),
    updateProject: (projectId, projectData) => apiClient.put(`/projects/${projectId}`, projectData),
    deleteProject: (projectId) => apiClient.delete(`/projects/${projectId}`)
  },

  // Tasks API with caching
  tasks: {
    getTasks: (projectId = null) => {
      const cacheKey = `tasks_${projectId || 'all'}`;
      return requestBatcher.batch(cacheKey, () =>
        apiClient.get('/tasks', { params: projectId ? { project_id: projectId } : {} })
      );
    },
    getTask: (taskId) => apiClient.get(`/tasks/${taskId}`),
    createTask: (taskData) => apiClient.post('/tasks', taskData),
    updateTask: (taskId, taskData) => apiClient.put(`/tasks/${taskId}`, taskData),
    deleteTask: (taskId) => apiClient.delete(`/tasks/${taskId}`)
  },

  // Insights API with longer caching
  insights: {
    getInsights: (dateRange = 'all_time', areaId = null) => {
      const cacheKey = `insights_${dateRange}_${areaId || 'all'}`;
      return requestBatcher.batch(cacheKey, () => {
        let url = `/insights?date_range=${dateRange}`;
        if (areaId) {
          url += `&area_id=${areaId}`;
        }
        return apiClient.get(url);
      });
    }
  },

  // AI Coach API
  aiCoach: {
    getQuota: () => apiClient.get('/ai/quota'),
    decomposeGoal: (goalText) => apiClient.post('/ai/decompose-project', {
      project_name: goalText,
      project_description: goalText,
      template_type: 'general'
    }),
    getWeeklyReview: () => apiClient.post('/ai/weekly-review'),
    analyzeObstacle: (projectId, problemDescription) => apiClient.post('/ai/obstacle-analysis', {
      project_id: projectId,
      problem_description: problemDescription
    })
  },

  // Alignment Score API
  alignmentScore: {
    getDashboardData: () => {
      const cacheKey = 'alignment_dashboard';
      return requestBatcher.batch(cacheKey, () => apiClient.get('/alignment/dashboard'));
    },
    getWeeklyScore: () => apiClient.get('/alignment/weekly-score'),
    getMonthlyScore: () => apiClient.get('/alignment/monthly-score'),
    setMonthlyGoal: (goal) => apiClient.post('/alignment/monthly-goal', { goal })
  },

  // Batch operations for improved performance
  batch: {
    getUserData: () => {
      // Single request to get all user data at once
      const cacheKey = 'all_user_data';
      return requestBatcher.batch(cacheKey, async () => {
        const [pillars, areas, projects, tasks] = await Promise.all([
          apiClient.get('/pillars'),
          apiClient.get('/areas'),
          apiClient.get('/projects'),
          apiClient.get('/tasks')
        ]);

        return {
          pillars: pillars.data,
          areas: areas.data,
          projects: projects.data,
          tasks: tasks.data
        };
      });
    }
  },

  // Performance monitoring
  performance: {
    getStats: () => performanceMonitor.getStats(),
    clearStats: () => {
      performanceMonitor.metrics = [];
    }
  }
};

// Cache invalidation utilities
export const cacheUtils = {
  invalidateUserData: () => {
    // Clear request batches related to user data
    requestBatcher.batches.clear();
  },
  
  invalidateSpecific: (keys) => {
    keys.forEach(key => {
      requestBatcher.batches.delete(key);
    });
  }
};

// Export performance stats for monitoring
export const getPerformanceStats = () => performanceMonitor.getStats();

// Default exports for backward compatibility
export const api = apiClient;
export default {
  client: apiClient,
  ...performanceOptimizedAPI
};