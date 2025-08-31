/**
 * HRM (Hierarchical Reasoning Model) API Service
 * Handles all API calls for AI insights and HRM functionality
 */

import { api as apiClient } from './api';

export const hrmAPI = {
  // Core HRM Analysis
  async analyzeEntity(entityType, entityId = null, analysisDepth = 'balanced', forceLLM = false) {
    try {
      const response = await apiClient.post('/hrm/analyze', {
        entity_type: entityType,
        entity_id: entityId,
        analysis_depth: analysisDepth,
        force_llm: forceLLM
      });
      return response.data;
    } catch (error) {
      console.error('HRM analysis failed:', error);
      throw this._handleError(error);
    }
  },

  // Insights Management
  async getInsights(params = {}) {
    try {
      const searchParams = new URLSearchParams();
      
      // Add filter parameters
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          searchParams.append(key, value.toString());
        }
      });

      const response = await apiClient.get(`/hrm/insights?${searchParams.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch insights:', error);
      throw this._handleError(error);
    }
  },

  async getInsightById(insightId) {
    try {
      const response = await apiClient.get(`/hrm/insights/${insightId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch insight:', error);
      throw this._handleError(error);
    }
  },

  async provideFeedback(insightId, feedback, feedbackDetails = null) {
    try {
      const response = await apiClient.post(`/hrm/insights/${insightId}/feedback`, {
        feedback,
        feedback_details: feedbackDetails
      });
      return response.data;
    } catch (error) {
      console.error('Failed to provide feedback:', error);
      throw this._handleError(error);
    }
  },

  async pinInsight(insightId, pinned = true) {
    try {
      const response = await apiClient.post(`/hrm/insights/${insightId}/pin`, {}, {
        params: { pinned }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to pin insight:', error);
      throw this._handleError(error);
    }
  },

  async deactivateInsight(insightId) {
    try {
      const response = await apiClient.delete(`/hrm/insights/${insightId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to deactivate insight:', error);
      throw this._handleError(error);
    }
  },

  // Statistics and Analytics
  async getStatistics(days = 30) {
    try {
      const response = await apiClient.get('/hrm/statistics', {
        params: { days }
      });
      return response.data.statistics;
    } catch (error) {
      console.error('Failed to fetch HRM statistics:', error);
      throw this._handleError(error);
    }
  },

  // Today's Priorities (Enhanced with HRM)
  async getTodayPriorities(topN = 5, includeReasoning = true) {
    try {
      const response = await apiClient.post('/hrm/prioritize-today', {}, {
        params: { 
          top_n: topN,
          include_reasoning: includeReasoning
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get today priorities:', error);
      throw this._handleError(error);
    }
  },

  // User Preferences
  async getPreferences() {
    try {
      const response = await apiClient.get('/hrm/preferences');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch HRM preferences:', error);
      throw this._handleError(error);
    }
  },

  async updatePreferences(preferences) {
    try {
      const response = await apiClient.put('/hrm/preferences', preferences);
      return response.data;
    } catch (error) {
      console.error('Failed to update HRM preferences:', error);
      throw this._handleError(error);
    }
  },

  // Batch Operations
  async batchAnalyze(entityTypes, analysisDepth = 'balanced') {
    try {
      const response = await apiClient.post('/hrm/batch-analyze', {}, {
        params: { 
          entity_types: entityTypes.join(','),
          analysis_depth: analysisDepth
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to start batch analysis:', error);
      throw this._handleError(error);
    }
  },

  // Utility Functions
  async triggerGlobalAnalysis(depth = 'balanced') {
    return this.analyzeEntity('global', null, depth, false);
  },

  async getInsightsForEntity(entityType, entityId, includeExpired = false) {
    return this.getInsights({
      entity_type: entityType,
      entity_id: entityId,
      include_expired: includeExpired
    });
  },

  async getPinnedInsights() {
    return this.getInsights({
      is_pinned: true,
      is_active: true
    });
  },

  async getHighConfidenceInsights(minConfidence = 0.8) {
    return this.getInsights({
      min_confidence: minConfidence,
      is_active: true
    });
  },

  async getRecentInsights(days = 7) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const insights = await this.getInsights({
      is_active: true,
      limit: 50
    });

    // Filter by date on client side since API might not support date filtering yet
    return {
      ...insights,
      insights: insights.insights?.filter(insight => 
        new Date(insight.created_at) >= cutoffDate
      ) || []
    };
  },

  // Enhanced Analysis Functions
  async analyzeTaskWithContext(taskId) {
    return this.analyzeEntity('task', taskId, 'detailed', true);
  },

  async analyzeProjectHealth(projectId) {
    return this.analyzeEntity('project', projectId, 'balanced', true);
  },

  async analyzeLifeBalance() {
    return this.analyzeEntity('global', null, 'detailed', true);
  },

  async analyzePillarAlignment(pillarId) {
    return this.analyzeEntity('pillar', pillarId, 'detailed', false);
  },

  // Feedback Helpers
  async markInsightAsHelpful(insightId, details = null) {
    return this.provideFeedback(insightId, 'accepted', details);
  },

  async markInsightAsNotHelpful(insightId, details = null) {
    return this.provideFeedback(insightId, 'rejected', details);
  },

  async markInsightAsModified(insightId, details = null) {
    return this.provideFeedback(insightId, 'modified', details);
  },

  // Search and Filter Helpers
  getInsightTypeDisplayName(type) {
    const displayNames = {
      priority_reasoning: 'Priority Reasoning',
      alignment_analysis: 'Alignment Analysis',
      pattern_recognition: 'Pattern Recognition',
      recommendation: 'Recommendation',
      goal_coherence: 'Goal Coherence',
      time_allocation: 'Time Allocation',
      progress_prediction: 'Progress Prediction',
      obstacle_identification: 'Obstacle Identification'
    };
    return displayNames[type] || type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  },

  getEntityTypeDisplayName(type) {
    const displayNames = {
      pillar: 'Pillar',
      area: 'Area',
      project: 'Project',
      task: 'Task',
      global: 'Global'
    };
    return displayNames[type] || type;
  },

  // Error Handling
  _handleError(error) {
    if (error.response?.data?.detail) {
      return new Error(error.response.data.detail);
    } else if (error.message) {
      return new Error(error.message);
    } else {
      return new Error('An unexpected error occurred');
    }
  },

  // Cache Management (for future implementation)
  _cacheKey(endpoint, params = {}) {
    const paramString = Object.keys(params).sort().map(key => `${key}=${params[key]}`).join('&');
    return `hrm_${endpoint}_${paramString}`;
  },

  // Real-time Features (for future WebSocket implementation)
  subscribeToInsights(callback) {
    // Placeholder for WebSocket subscription
    console.log('WebSocket subscription not yet implemented');
    return () => {}; // Return unsubscribe function
  }
};

// Default export
export default hrmAPI;