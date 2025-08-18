@@
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
+  restoreEntry: (entryId) => apiClient.post(`/journal/${entryId}/restore`),
+  getTrash: (skip = 0, limit = 20) => apiClient.get('/journal/trash', { params: { skip, limit } }),
+  purgeEntry: (entryId) => apiClient.delete(`/journal/${entryId}/purge`),
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