import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for common parameters and authentication
apiClient.interceptors.request.use((config) => {
  // Add authentication token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Don't add user_id anymore since we use authentication
  return config;
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized errors
    if (error.response?.status === 401) {
      console.warn('Authentication failed - clearing token and redirecting to login');
      
      // Clear invalid token
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      
      // Redirect to login page
      window.location.href = '/login';
      
      return Promise.reject(new Error('Authentication failed. Please log in again.'));
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
// Notifications API
export const notificationsAPI = {
  getPreferences: () => apiClient.get('/notifications/preferences'),
  updatePreferences: (preferences) => apiClient.put('/notifications/preferences', preferences),
  getNotifications: (unreadOnly = false) => apiClient.get('/notifications', { 
    params: { unread_only: unreadOnly } 
  }),
  markAsRead: (notificationId) => apiClient.put(`/notifications/${notificationId}/read`),
  sendTest: () => apiClient.post('/notifications/test')
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
  const message = error.response?.data?.detail || error.message || defaultMessage;
  console.error('API Error:', message);
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
  getResources: (parentType = null, parentId = null) => {
    const params = {};
    if (parentType && parentId) {
      params.parent_type = parentType;
      params.parent_id = parentId;
    }
    return apiClient.get('/resources', { params });
  },
  getResource: (resourceId) => apiClient.get(`/resources/${resourceId}`),
  createResource: (resourceData) => apiClient.post('/resources', resourceData),
  deleteResource: (resourceId) => apiClient.delete(`/resources/${resourceId}`),
  
  // Chunked file upload process
  startUpload: (uploadData) => apiClient.post('/resources/upload/start', uploadData),
  uploadChunk: (chunkData) => {
    // For file uploads, we need to use FormData and multipart/form-data
    const formData = new FormData();
    formData.append('resource_id', chunkData.resource_id);
    formData.append('chunk_index', chunkData.chunk_index);
    formData.append('chunk_data', chunkData.chunk_data);
    
    return apiClient.post('/resources/upload/chunk', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 30000, // 30 seconds for chunk uploads
    });
  },
  completeUpload: (resourceId) => apiClient.post('/resources/upload/complete', { resource_id: resourceId }),
  
  // Utility function for chunked file upload
  uploadFile: async (file, parentType = null, parentId = null, onProgress = null) => {
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
    
    const chunkSize = 1024 * 1024; // 1MB chunks
    const totalChunks = Math.ceil(file.size / chunkSize);
    
    try {
      // Start upload session
      const startResponse = await resourcesAPI.startUpload({
        filename: file.name,
        content_type: file.type,
        file_size: file.size,
        total_chunks: totalChunks,
        parent_type: parentType,
        parent_id: parentId
      });
      
      const resourceId = startResponse.data.resource_id;
      
      // Upload chunks
      for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
        const start = chunkIndex * chunkSize;
        const end = Math.min(start + chunkSize, file.size);
        const chunkBlob = file.slice(start, end);
        
        await resourcesAPI.uploadChunk({
          resource_id: resourceId,
          chunk_index: chunkIndex,
          chunk_data: chunkBlob
        });
        
        // Report progress
        if (onProgress) {
          onProgress({
            loaded: (chunkIndex + 1) * chunkSize,
            total: file.size,
            percentage: Math.round(((chunkIndex + 1) / totalChunks) * 100)
          });
        }
      }
      
      // Complete upload
      const completeResponse = await resourcesAPI.completeUpload(resourceId);
      return completeResponse.data;
      
    } catch (error) {
      console.error('File upload error:', error);
      throw error;
    }
  }
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
  insights: insightsAPI
};