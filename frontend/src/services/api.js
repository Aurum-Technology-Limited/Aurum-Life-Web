import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with enhanced config for stability
const apiClient = axios.create({
  baseURL: API,
  timeout: 30000, // Increase to 30 seconds for complex operations
  headers: {
    'Content-Type': 'application/json',
  },
  // Add retry configuration
  maxRetries: 2,
  retryDelay: 1000, // 1 second delay between retries
});

// Add request interceptor for common parameters and authentication
apiClient.interceptors.request.use((config) => {
  // Add performance timing
  config.metadata = { startTime: Date.now() };
  
  // Add authentication token if available
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
  
  // Add performance headers
  config.headers['Cache-Control'] = 'no-cache';
  
  return config;
});

// Helper function to get CSRF token from cookie
function getCsrfToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrf_token='));
  return cookieValue ? cookieValue.split('=')[1] : null;
}

// Add response interceptor for error handling and performance tracking
apiClient.interceptors.response.use(
  (response) => {
    // Log slow requests
    const duration = Date.now() - response.config.metadata.startTime;
    if (duration > 2000) {
      console.warn(`🐌 Slow API request: ${response.config.url} took ${duration}ms`);
    }
    return response;
  },
  (error) => {
    const config = error.config;
    
    // Handle 401 Unauthorized errors
    if (error.response?.status === 401) {
      console.warn('Authentication failed - clearing token and redirecting to login');
      
      // Clear invalid token
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      
      // Redirect to correct login page
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
      
      return Promise.reject(new Error('Authentication failed. Please log in again.'));
    }
    
    // Implement automatic retry logic for certain types of errors
    const shouldRetry = (
      (error.code === 'ECONNABORTED' || error.message.includes('timeout')) ||
      (error.response?.status >= 500) ||
      (error.code === 'NETWORK_ERROR')
    );
    
    // Initialize retry count if not present
    config._retryCount = config._retryCount || 0;
    const maxRetries = config.maxRetries || 2;
    const retryDelay = config.retryDelay || 1000;
    
    if (shouldRetry && config._retryCount < maxRetries) {
      config._retryCount += 1;
      
      console.warn(`🔄 Retrying request (${config._retryCount}/${maxRetries}): ${config.url}`);
      
      // Return a promise that retries the request after delay
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(apiClient(config));
        }, retryDelay * config._retryCount); // Exponential backoff
      });
    }
    
    // Handle timeout errors specifically after retries exhausted
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      console.error('Request timed out after retries:', error.config?.url);
      return Promise.reject(new Error('Request timed out. Please check your connection and try again.'));
    }
    
    // Handle server errors
    if (error.response?.status >= 500) {
      console.error('Server error after retries:', error.response?.status, error.config?.url);
      return Promise.reject(new Error('Server temporarily unavailable. Please try again later.'));
    }
    
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Project Templates API
export const projectTemplatesAPI = {
  getTemplates: () => apiClient.get('/project-templates'),
  getTemplate: (templateId) => apiClient.get(`/project-templates/${templateId}`),
  createTemplate: (templateData) => apiClient.post('/project-templates', templateData),
  updateTemplate: (templateId, templateData) => apiClient.put(`/project-templates/${templateId}`, templateData),
  deleteTemplate: (templateId) => apiClient.delete(`/project-templates/${templateId}`),
  useTemplate: (templateId, projectData) => apiClient.post(`/project-templates/${templateId}/use`, projectData)
};

// Pillars API
export const pillarsAPI = {
  getPillars: (includeSubPillars = true, includeAreas = false, includeArchived = false) => apiClient.get('/pillars', {
    params: {
      include_sub_pillars: includeSubPillars,
      include_areas: includeAreas,
      include_archived: includeArchived
    }
  }),
  getPillar: (pillarId, includeSubPillars = true, includeAreas = false) => apiClient.get(`/pillars/${pillarId}`, {
    params: {
      include_sub_pillars: includeSubPillars,
      include_areas: includeAreas
    }
  }),
  createPillar: (pillarData) => apiClient.post('/pillars', pillarData),
  updatePillar: (pillarId, pillarData) => apiClient.put(`/pillars/${pillarId}`, pillarData),
  archivePillar: (pillarId) => apiClient.put(`/pillars/${pillarId}/archive`),
  unarchivePillar: (pillarId) => apiClient.put(`/pillars/${pillarId}/unarchive`),
  deletePillar: (pillarId) => apiClient.delete(`/pillars/${pillarId}`)
};
// Enhanced notifications API with bulk actions
export const notificationsAPI = {
  getPreferences: () => apiClient.get('/notifications/preferences'),
  updatePreferences: (preferences) => apiClient.put('/notifications/preferences', preferences),
  getNotifications: (unreadOnly = false) => apiClient.get('/notifications', { 
    params: { unread_only: unreadOnly } 
  }),
  markAsRead: (notificationId) => apiClient.put(`/notifications/${notificationId}/read`),
  deleteNotification: (notificationId) => apiClient.delete(`/notifications/${notificationId}`),
  sendTest: () => apiClient.post('/notifications/test'),
  
  // Bulk actions
  markAllRead: () => apiClient.put('/notifications/mark-all-read'),
  clearAllNotifications: () => apiClient.delete('/notifications/clear-all')
};

// Areas API with enhanced archiving support
export const areasAPI = {
  getAreas: (includeProjects = false, includeArchived = false) => apiClient.get('/areas', { 
    params: { 
      include_projects: includeProjects,
      include_archived: includeArchived
    } 
  }),
  getArea: (areaId) => apiClient.get(`/areas/${areaId}`),
  createArea: (areaData) => apiClient.post('/areas', areaData),
  updateArea: (areaId, areaData) => apiClient.put(`/areas/${areaId}`, areaData),
  deleteArea: (areaId) => apiClient.delete(`/areas/${areaId}`),
  archiveArea: (areaId) => apiClient.put(`/areas/${areaId}/archive`),
  unarchiveArea: (areaId) => apiClient.put(`/areas/${areaId}/unarchive`),
};

// Projects API with enhanced archiving support
export const projectsAPI = {
  getProjects: (areaId = null, includeArchived = false) => apiClient.get('/projects', { 
    params: { 
      ...(areaId && { area_id: areaId }),
      include_archived: includeArchived
    } 
  }),
  getProject: (projectId, includeTasks = false) => apiClient.get(`/projects/${projectId}`, { params: { include_tasks: includeTasks } }),
  createProject: (projectData) => apiClient.post('/projects', projectData),
  updateProject: (projectId, projectData) => apiClient.put(`/projects/${projectId}`, projectData),
  deleteProject: (projectId) => apiClient.delete(`/projects/${projectId}`),
  archiveProject: (projectId) => apiClient.put(`/projects/${projectId}/archive`),
  unarchiveProject: (projectId) => apiClient.put(`/projects/${projectId}/unarchive`),
  getProjectTasks: (projectId) => apiClient.get(`/projects/${projectId}/tasks`),
  getKanbanBoard: (projectId) => apiClient.get(`/projects/${projectId}/kanban`),
  reorderProjectTasks: (projectId, taskIds) => apiClient.put(`/projects/${projectId}/tasks/reorder`, { task_ids: taskIds }),
  
  // Create project with tasks from Goal Decomposition workflow
  createWithTasks: (projectData, tasksData) => apiClient.post('/projects/create-with-tasks', {
    project: projectData,
    tasks: tasksData
  })
};

// Enhanced Tasks API with Sub-task support
export const tasksAPI = {
  getTasks: (projectId = null) => apiClient.get('/tasks', { params: projectId ? { project_id: projectId } : {} }),
  getTask: (taskId) => apiClient.get(`/tasks/${taskId}`),
  getTaskWithSubtasks: (taskId) => apiClient.get(`/tasks/${taskId}/with-subtasks`),
  getSubtasks: (parentTaskId) => apiClient.get(`/tasks/${parentTaskId}/subtasks`),
  createTask: (taskData) => apiClient.post('/tasks', taskData),
  createSubtask: (parentTaskId, subtaskData) => apiClient.post(`/tasks/${parentTaskId}/subtasks`, subtaskData),
  updateTask: (taskId, taskData) => apiClient.put(`/tasks/${taskId}`, taskData),
  deleteTask: (taskId) => apiClient.delete(`/tasks/${taskId}`),
  getTodayTasks: () => apiClient.get('/today'),
  moveTaskColumn: (taskId, newColumn) => apiClient.put(`/tasks/${taskId}/column`, null, { params: { new_column: newColumn } }),
  // Task Dependencies API (Phase 1)
  getTaskDependencies: (taskId) => apiClient.get(`/tasks/${taskId}/dependencies`),
  updateTaskDependencies: (taskId, dependencyIds) => apiClient.put(`/tasks/${taskId}/dependencies`, dependencyIds),
  getAvailableDependencyTasks: (projectId, excludeTaskId = null) => apiClient.get(`/projects/${projectId}/tasks/available-dependencies`, { 
    params: excludeTaskId ? { task_id: excludeTaskId } : {} 
  }),
};

// Enhanced Today API with Daily Task Curation
export const todayAPI = {
  getTodayView: () => apiClient.get('/today'),
  getAvailableTasks: () => apiClient.get('/today/available-tasks'),
  addTaskToToday: (taskId) => apiClient.post(`/today/tasks/${taskId}`),
  removeTaskFromToday: (taskId) => apiClient.delete(`/today/tasks/${taskId}`),
  reorderDailyTasks: (taskIds) => apiClient.put('/today/reorder', { task_ids: taskIds })
};

// Recurring Tasks API
export const recurringTasksAPI = {
  getRecurringTasks: () => apiClient.get('/recurring-tasks'),
  createRecurringTask: (taskData) => apiClient.post('/recurring-tasks', taskData),
  updateRecurringTask: (templateId, taskData) => apiClient.put(`/recurring-tasks/${templateId}`, taskData),
  deleteRecurringTask: (templateId) => apiClient.delete(`/recurring-tasks/${templateId}`),
  getRecurringTaskInstances: (templateId, startDate = null, endDate = null) => 
    apiClient.get(`/recurring-tasks/${templateId}/instances`, { 
      params: { 
        ...(startDate && { start_date: startDate }),
        ...(endDate && { end_date: endDate })
      } 
    }),
  completeRecurringTaskInstance: (instanceId) => apiClient.put(`/recurring-task-instances/${instanceId}/complete`),
  skipRecurringTaskInstance: (instanceId) => apiClient.put(`/recurring-task-instances/${instanceId}/skip`),
  generateRecurringTaskInstances: () => apiClient.post('/recurring-tasks/generate-instances')
};

// Insights API
export const insightsAPI = {
  getInsights: (dateRange = 'all_time', areaId = null) => {
    let url = `/insights?date_range=${dateRange}`;
    if (areaId) {
      url += `&area_id=${areaId}`;
    }
    return apiClient.get(url);
  },
  getAreaDrillDown: (areaId, dateRange = 'all_time') => apiClient.get(`/insights/areas/${areaId}?date_range=${dateRange}`),
  getProjectDrillDown: (projectId, dateRange = 'all_time') => apiClient.get(`/insights/projects/${projectId}?date_range=${dateRange}`),
};

// Dashboard API (updated)
export const dashboardAPI = {
  getDashboard: () => apiClient.get('/dashboard'),
};

// User API
export const userAPI = {
  getUser: (userId) => apiClient.get(`/users/${userId}`),
  updateUser: (userData, userId) => apiClient.put(`/users/${userId}`, userData),
  createUser: (userData) => apiClient.post('/users', userData),
};

// Journal API
export const journalAPI = {
  getEntries: (skip = 0, limit = 20, moodFilter = null, tagFilter = null, dateFrom = null, dateTo = null) => {
    const params = { skip, limit };
    if (moodFilter) params.mood_filter = moodFilter;
    if (tagFilter) params.tag_filter = tagFilter;
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    return apiClient.get('/journal', { params });
  },
  createEntry: (entryData) => apiClient.post('/journal', entryData),
  updateEntry: (entryId, entryData) => apiClient.put(`/journal/${entryId}`, entryData),
  deleteEntry: (entryId) => apiClient.delete(`/journal/${entryId}`),
  searchEntries: (query, limit = 20) => apiClient.get('/journal/search', { params: { q: query, limit } }),
  getInsights: () => apiClient.get('/journal/insights'),
  getOnThisDay: (date = null) => apiClient.get('/journal/on-this-day', { params: date ? { date } : {} }),
  
  // Template API
  getTemplates: () => apiClient.get('/journal/templates'),
  getTemplate: (templateId) => apiClient.get(`/journal/templates/${templateId}`),
  createTemplate: (templateData) => apiClient.post('/journal/templates', templateData),
  updateTemplate: (templateId, templateData) => apiClient.put(`/journal/templates/${templateId}`, templateData),
  deleteTemplate: (templateId) => apiClient.delete(`/journal/templates/${templateId}`),
};

// Chat API
export const chatAPI = {
  sendMessage: (messageData) => apiClient.post('/chat', messageData),
  getMessages: (sessionId) => apiClient.get(`/chat/${sessionId}`),
};

// Courses API
export const coursesAPI = {
  getAllCourses: () => apiClient.get('/courses'),
  getEnrolledCourses: () => apiClient.get('/courses/enrolled'),
  enrollInCourse: (courseId) => apiClient.post(`/courses/${courseId}/enroll`),
};

// Stats API
export const statsAPI = {
  getUserStats: () => apiClient.get('/stats'),
  updateUserStats: () => apiClient.post('/stats/update'),
};

// Health check
export const healthAPI = {
  check: () => apiClient.get('/health'),
  root: () => apiClient.get('/'),
};

// Utility functions
export const handleApiError = (error, defaultMessage = 'An error occurred') => {
  let message = defaultMessage;
  
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    
    // Handle FastAPI validation errors (arrays of error objects)
    if (Array.isArray(detail)) {
      const validationErrors = detail.map(err => {
        if (typeof err === 'object' && err.msg) {
          const field = Array.isArray(err.loc) ? err.loc.join('.') : 'field';
          return `${field}: ${err.msg}`;
        }
        return typeof err === 'string' ? err : 'Validation error';
      });
      message = validationErrors.join(', ');
    }
    // Handle simple string messages
    else if (typeof detail === 'string') {
      message = detail;
    }
    // Handle object with message property
    else if (typeof detail === 'object' && detail.message) {
      message = detail.message;
    }
    // Handle any other object by converting to string
    else if (typeof detail === 'object') {
      message = JSON.stringify(detail);
    }
  }
  // Fallback to error message
  else if (error.message) {
    message = error.message;
  }
  
  console.error('API Error:', {
    url: error.config?.url,
    status: error.response?.status,
    message: message,
    originalError: error.response?.data
  });
  
  return message;
};

export const isApiError = (error) => {
  return error.response && error.response.status;
};

export const getApiErrorStatus = (error) => {
  return error.response?.status;
};

// Default export with all APIs
export const api = apiClient;

// Google OAuth API
export const googleAuthAPI = {
  authenticate: (token) => apiClient.post('/auth/google', { token })
};

// Resources API for File Management
export const resourcesAPI = {
  // Basic CRUD operations
  getResources: (category = null, fileType = null, folderPath = null, includeArchived = false, search = null, skip = 0, limit = 50) => {
    const params = { skip, limit, include_archived: includeArchived };
    if (category) params.category = category;
    if (fileType) params.file_type = fileType;
    if (folderPath) params.folder_path = folderPath;
    if (search) params.search = search;
    return apiClient.get('/resources', { params });
  },
  getResource: (resourceId) => apiClient.get(`/resources/${resourceId}`),
  getResourceContent: (resourceId) => apiClient.get(`/resources/${resourceId}/content`),
  createResource: (resourceData) => apiClient.post('/resources', resourceData),
  updateResource: (resourceId, resourceData) => apiClient.put(`/resources/${resourceId}`, resourceData),
  deleteResource: (resourceId) => apiClient.delete(`/resources/${resourceId}`),
  
  // Resource attachment operations
  attachToEntity: (resourceId, entityType, entityId) => 
    apiClient.post(`/resources/${resourceId}/attach`, {
      resource_id: resourceId,
      entity_type: entityType,
      entity_id: entityId
    }),
  detachFromEntity: (resourceId, entityType, entityId) => 
    apiClient.delete(`/resources/${resourceId}/detach`, {
      data: {
        resource_id: resourceId,
        entity_type: entityType,
        entity_id: entityId
      }
    }),
  getEntityResources: (entityType, entityId) => 
    apiClient.get(`/resources/entity/${entityType}/${entityId}`),
  
  // Contextual attachment operations (new approach)
  getParentResources: (parentType, parentId) => 
    apiClient.get(`/resources/parent/${parentType}/${parentId}`),
  
  // Utility function for file upload with validation and base64 conversion
  uploadFile: async (file, description = '', tags = [], category = 'document', folderPath = '/') => {
    // File validation
    const allowedTypes = [
      'image/png', 'image/jpeg', 'image/gif',
      'application/pdf', 'application/msword', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];
    
    if (!allowedTypes.includes(file.type)) {
      throw new Error(`File type ${file.type} is not supported. Allowed types: PNG, JPEG, GIF, PDF, DOC, DOCX, TXT`);
    }
    
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      throw new Error(`File size ${(file.size / 1024 / 1024).toFixed(2)}MB exceeds the 10MB limit`);
    }
    
    try {
      // Convert file to base64
      const base64Content = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          // Remove the data URL prefix (e.g., "data:image/png;base64,")
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
      
      // Determine file type enum
      let fileType = 'other';
      if (file.type.startsWith('image/')) {
        fileType = 'image';
      } else if (file.type.includes('pdf') || file.type.includes('msword') || file.type.includes('wordprocessingml') || file.type === 'text/plain') {
        fileType = 'document';
      }
      
      // Create resource data
      const resourceData = {
        filename: file.name,
        original_filename: file.name,
        file_type: fileType,
        category: category,
        mime_type: file.type,
        file_size: file.size,
        file_content: base64Content,
        description: description,
        tags: tags,
        folder_path: folderPath
      };
      
      const response = await resourcesAPI.createResource(resourceData);
      return response.data;
      
    } catch (error) {
      console.error('File upload error:', error);
      throw error;
    }
  },

  // Contextual file upload with parent relationship (new approach)
  uploadFileWithParent: async (file, description = '', parentType, parentId, category = 'document', folderPath = '/') => {
    // File validation
    const allowedTypes = [
      'image/png', 'image/jpeg', 'image/gif',
      'application/pdf', 'application/msword', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];
    
    if (!allowedTypes.includes(file.type)) {
      throw new Error(`File type ${file.type} is not supported. Allowed types: PNG, JPEG, GIF, PDF, DOC, DOCX, TXT`);
    }
    
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      throw new Error(`File size ${(file.size / 1024 / 1024).toFixed(2)}MB exceeds the 10MB limit`);
    }
    
    try {
      // Convert file to base64
      const base64Content = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          // Remove the data URL prefix (e.g., "data:image/png;base64,")
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
      
      // Determine file type enum
      let fileType = 'other';
      if (file.type.startsWith('image/')) {
        fileType = 'image';
      } else if (file.type.includes('pdf') || file.type.includes('msword') || file.type.includes('wordprocessingml') || file.type === 'text/plain') {
        fileType = 'document';
      }
      
      // Create resource data with parent relationship
      const resourceData = {
        filename: file.name,
        original_filename: file.name,
        file_type: fileType,
        category: category,
        mime_type: file.type,
        file_size: file.size,
        file_content: base64Content,
        description: description,
        tags: [],
        folder_path: folderPath,
        parent_id: parentId,
        parent_type: parentType
      };
      
      const response = await resourcesAPI.createResource(resourceData);
      return response.data;
      
    } catch (error) {
      console.error('Contextual file upload error:', error);
      throw error;
    }
  }
};

// AI Coach API
// AI Coach MVP API with Safeguards
export const aiCoachAPI = {
  // Get user's AI interaction quota
  getQuota: () => apiClient.get('/ai/quota'),
  
  // Feature 1: Goal Decomposition (Enhanced Interactive Workflow)
  decomposeGoal: (goalText) => apiClient.post('/ai/decompose-project', {
    project_name: goalText,
    project_description: goalText,
    template_type: 'general'
  }),
  
  // Feature 2: Weekly Strategic Review
  getWeeklyReview: () => apiClient.post('/ai/weekly-review'),
  
  // Feature 3: Obstacle Analysis
  analyzeObstacle: (projectId, problemDescription) => apiClient.post('/ai/obstacle-analysis', {
    project_id: projectId,
    problem_description: problemDescription
  }),
  
  // Legacy support (for existing code)
  chatWithCoach: (message) => apiClient.post('/ai/decompose-project', {
    project_name: message,
    project_description: message,
    template_type: 'general'
  }),
  getTodaysPriorities: () => apiClient.get('/ai/task-why-statements')
};

// Feedback API
export const feedbackAPI = {
  submitFeedback: (feedbackData) => apiClient.post('/feedback', feedbackData)
};

// Alignment Score API
export const alignmentScoreAPI = {
  getDashboardData: () => apiClient.get('/alignment/dashboard'),
  getWeeklyScore: () => apiClient.get('/alignment/weekly-score'),
  getMonthlyScore: () => apiClient.get('/alignment/monthly-score'),
  getMonthlyGoal: () => apiClient.get('/alignment/monthly-goal'),
  setMonthlyGoal: (goal) => apiClient.post('/alignment/monthly-goal', { goal })
};

export default {
  client: apiClient,
  areas: areasAPI,
  projects: projectsAPI,
  tasks: tasksAPI,
  journal: journalAPI,
  chat: chatAPI,
  courses: coursesAPI,
  stats: statsAPI,
  health: healthAPI,
  dashboard: dashboardAPI,
  today: todayAPI,
  user: userAPI,
  projectTemplates: projectTemplatesAPI,
  pillars: pillarsAPI,
  recurringTasks: recurringTasksAPI,
  insights: insightsAPI,
  resources: resourcesAPI,
  googleAuth: googleAuthAPI,
  aiCoach: aiCoachAPI,
  feedback: feedbackAPI,
  alignmentScore: alignmentScoreAPI
};