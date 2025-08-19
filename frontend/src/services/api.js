import axios from 'axios';

// Central API client (axios)
const apiClient = axios.create({
  baseURL: (process.env.REACT_APP_BACKEND_URL || '') + '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Attach auth token automatically
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// -------------- Journal API --------------
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
  restoreEntry: (entryId) => apiClient.post(`/journal/${entryId}/restore`),
  getTrash: (skip = 0, limit = 20) => apiClient.get('/journal/trash', { params: { skip, limit } }),
  purgeEntry: (entryId) => apiClient.delete(`/journal/${entryId}/purge`),
  searchEntries: (query, limit = 20) => apiClient.get('/journal/search', { params: { q: query, limit } }),
  getInsights: () => apiClient.get('/journal/insights'),
  getOnThisDay: (date = null) => apiClient.get('/journal/on-this-day', { params: date ? { date } : {} }),
  // Templates
  getTemplates: () => apiClient.get('/journal/templates'),
  getTemplate: (templateId) => apiClient.get(`/journal/templates/${templateId}`),
  createTemplate: (templateData) => apiClient.post('/journal/templates', templateData),
  updateTemplate: (templateId, templateData) => apiClient.put(`/journal/templates/${templateId}`, templateData),
  deleteTemplate: (templateId) => apiClient.delete(`/journal/templates/${templateId}`),
};

// -------------- Pillars / Areas / Projects / Tasks --------------
export const pillarsAPI = {
  getPillars: (includeSubPillars = true, includeAreas = false, includeArchived = false) =>
    apiClient.get('/pillars', {
      params: {
        include_sub_pillars: includeSubPillars,
        include_areas: includeAreas,
        include_archived: includeArchived,
      },
    }),
  getPillar: (id) => apiClient.get(`/pillars/${id}`),
  createPillar: (data) => apiClient.post('/pillars', data),
  updatePillar: (id, data) => apiClient.put(`/pillars/${id}`, data),
  deletePillar: (id) => apiClient.delete(`/pillars/${id}`),
};

export const areasAPI = {
  getAreas: (includeProjects = true, includeArchived = false) =>
    apiClient.get('/areas', {
      params: { include_projects: includeProjects, include_archived: includeArchived },
    }),
  getArea: (id) => apiClient.get(`/areas/${id}`),
  createArea: (data) => apiClient.post('/areas', data),
  updateArea: (id, data) => apiClient.put(`/areas/${id}`, data),
  deleteArea: (id) => apiClient.delete(`/areas/${id}`),
};

export const projectsAPI = {
  getProjects: (areaId = null, includeArchived = false) =>
    apiClient.get('/projects', {
      params: { ...(areaId ? { area_id: areaId } : {}), include_archived: includeArchived },
    }),
  getProject: (id) => apiClient.get(`/projects/${id}`),
  createProject: (data) => apiClient.post('/projects', data),
  updateProject: (id, data) => apiClient.put(`/projects/${id}`, data),
  deleteProject: (id) => apiClient.delete(`/projects/${id}`),
};

export const tasksAPI = {
  getTasks: (projectId = null) => apiClient.get('/tasks', { params: projectId ? { project_id: projectId } : {} }),
  getTask: (taskId) => apiClient.get(`/tasks/${taskId}`),
  createTask: (data) => apiClient.post('/tasks', data),
  updateTask: (taskId, data) => apiClient.put(`/tasks/${taskId}`, data),
  deleteTask: (taskId) => apiClient.delete(`/tasks/${taskId}`),
  searchTasks: (q, limit = 20, page = 1) => apiClient.get('/tasks/search', { params: { q, limit, page } }),
  moveTaskColumn: (taskId, newColumn) => apiClient.post(`/tasks/${taskId}/move`, { column: newColumn }),
  // Subtasks
  getSubtasks: (taskId) => apiClient.get(`/tasks/${taskId}/subtasks`),
  createSubtask: (taskId, data) => apiClient.post(`/tasks/${taskId}/subtasks`, data),
  // Dependencies
  getAvailableDependencyTasks: (projectId, excludeTaskId = null) =>
    apiClient.get('/tasks/available-dependencies', { params: { project_id: projectId, exclude_task_id: excludeTaskId } }),
  getTaskDependencies: (taskId) => apiClient.get(`/tasks/${taskId}/dependencies`),
  updateTaskDependencies: (taskId, dependencyIds = []) => apiClient.post(`/tasks/${taskId}/dependencies`, { dependency_task_ids: dependencyIds }),
  // AI helpers
  suggestFocus: () => apiClient.get('/ai/suggest-focus'),
};

// Recurring tasks (used by RecurringTasks component)
export const recurringTasksAPI = {
  getRecurringTasks: () => apiClient.get('/tasks/recurring'),
  createRecurringTask: (data) => apiClient.post('/tasks/recurring', data),
  updateRecurringTask: (id, data) => apiClient.put(`/tasks/recurring/${id}`, data),
  deleteRecurringTask: (id) => apiClient.delete(`/tasks/recurring/${id}`),
  generateRecurringTaskInstances: () => apiClient.post('/tasks/recurring/generate'),
};

// -------------- Dashboard / Insights / Alignment / AI Coach --------------
export const dashboardAPI = {
  getDashboard: () => apiClient.get('/dashboard'),
};

export const insightsAPI = {
  getInsights: (dateRange = 'all_time', areaId = null) =>
    apiClient.get('/insights', { params: { date_range: dateRange, ...(areaId ? { area_id: areaId } : {}) } }),
};

export const alignmentScoreAPI = {
  // Try new dashboard endpoint; gracefully fall back to legacy '/alignment-score'
  getDashboardData: async () => {
    try {
      return await apiClient.get('/alignment/dashboard');
    } catch (err) {
      // Fallback for environments where dashboard route is not available
      return apiClient.get('/alignment-score');
    }
  },
  getWeeklyScore: () => apiClient.get('/alignment/weekly-score'),
  getMonthlyScore: () => apiClient.get('/alignment/monthly-score'),
  setMonthlyGoal: (goal) => apiClient.post('/alignment/monthly-goal', { goal }),
};

export const aiCoachAPI = {
  getTodaysPriorities: () => apiClient.get('/ai/task-why-statements'),
};

// Error handling utility
export const handleApiError = (error, defaultMessage = 'An error occurred') => {
  if (error?.response) {
    return error.response.data?.message || error.response.data?.detail || defaultMessage;
  } else if (error?.request) {
    return 'Network error - please check your connection';
  } else {
    return error?.message || defaultMessage;
  }
};

// Named and default exports for compatibility
export const api = apiClient;
export default apiClient;