import { createClient } from '@supabase/supabase-js';
import { projectId, publicAnonKey } from '../utils/supabase/info';

// Types for backend API responses
export interface UserStats {
  id: string;
  user_id: string;
  active_pillars: number;
  total_tasks: number;
  completed_tasks_today: number;
  total_tasks_today: number;
  weekly_progress: number;
  growth_trend: number;
  urgent_tasks_count: number;
  high_tasks_count: number;
  last_updated: string;
}

export interface PillarHealth {
  id: string;
  pillar_id: string;
  health_score: number;
  streak_days: number;
  weekly_time_actual: number;
  weekly_time_target: number;
  trend_direction: 'up' | 'down' | 'stable';
  last_updated: string;
}

export interface PillarAnalytics {
  id: string;
  pillar_id: string;
  completion_rate: number;
  time_allocation: number;
  priority_distribution: {
    urgent: number;
    high: number;
    medium: number;
    low: number;
  };
  streak_data: {
    current_streak: number;
    longest_streak: number;
    weekly_consistency: number;
  };
  behavioral_patterns: {
    best_time_of_day: string;
    most_productive_day: string;
    completion_velocity: number;
  };
}

export interface AIRecommendation {
  id: string;
  user_id: string;
  type: 'tip' | 'insight' | 'coaching' | 'warning';
  title: string;
  description: string;
  action_text?: string;
  pillar_id?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  context: Record<string, any>;
  created_at: string;
  expires_at?: string;
}

class ApiService {
  private supabase;
  private baseUrl: string;

  constructor() {
    this.supabase = createClient(
      `https://${projectId}.supabase.co`,
      publicAnonKey
    );
    this.baseUrl = `https://${projectId}.supabase.co/functions/v1/make-server-dd6e2894`;
  }

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = localStorage.getItem('supabase_access_token') || publicAnonKey;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          ...options.headers,
        },
        // Add timeout to prevent hanging requests
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error (${response.status}): ${errorText}`);
      }

      return response.json();
    } catch (error) {
      // Log but don't throw for network errors - use fallbacks instead
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.log(`Backend API not available for ${endpoint} - using fallback data`);
      } else if (error.name === 'TimeoutError') {
        console.log(`API request timeout for ${endpoint} - using fallback data`);
      } else if (error.name === 'AbortError') {
        console.log(`API request aborted for ${endpoint} - using fallback data`);
      }
      throw error; // Re-throw to trigger fallback logic in the calling methods
    }
  }

  // User Statistics Endpoints
  async getUserStats(): Promise<UserStats> {
    try {
      return await this.makeRequest<UserStats>('/api/user-stats');
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
      // Fallback to local calculation or default values
      return this.getFallbackUserStats();
    }
  }

  private getFallbackUserStats(): UserStats {
    // Return reasonable fallback data when backend is unavailable
    const now = new Date().toISOString();
    return {
      id: 'fallback',
      user_id: 'local',
      active_pillars: 4,
      total_tasks: 12,
      completed_tasks_today: 3,
      total_tasks_today: 8,
      weekly_progress: 68,
      growth_trend: 75,
      urgent_tasks_count: 2,
      high_tasks_count: 4,
      last_updated: now
    };
  }

  // Pillar Health Endpoints
  async getPillarHealth(pillarId?: string): Promise<PillarHealth[]> {
    try {
      const endpoint = pillarId 
        ? `/api/pillars/${pillarId}/health` 
        : '/api/pillar-health';
      return await this.makeRequest<PillarHealth[]>(endpoint);
    } catch (error) {
      console.error('Failed to fetch pillar health:', error);
      return this.getFallbackPillarHealth();
    }
  }

  private getFallbackPillarHealth(): PillarHealth[] {
    const now = new Date().toISOString();
    return [
      {
        id: 'health-1',
        pillar_id: 'pillar-1',
        health_score: 85,
        streak_days: 7,
        weekly_time_actual: 12,
        weekly_time_target: 15,
        trend_direction: 'up',
        last_updated: now
      },
      {
        id: 'health-2',
        pillar_id: 'pillar-2',
        health_score: 72,
        streak_days: 3,
        weekly_time_actual: 8,
        weekly_time_target: 10,
        trend_direction: 'stable',
        last_updated: now
      }
    ];
  }

  // Pillar Analytics Endpoints
  async getPillarAnalytics(pillarId: string): Promise<PillarAnalytics> {
    try {
      return await this.makeRequest<PillarAnalytics>(`/api/pillars/${pillarId}/analytics`);
    } catch (error) {
      console.error('Failed to fetch pillar analytics:', error);
      return this.getFallbackPillarAnalytics(pillarId);
    }
  }

  private getFallbackPillarAnalytics(pillarId: string): PillarAnalytics {
    return {
      id: `analytics-${pillarId}`,
      pillar_id: pillarId,
      completion_rate: 78,
      time_allocation: 65,
      priority_distribution: {
        urgent: 2,
        high: 5,
        medium: 8,
        low: 3
      },
      streak_data: {
        current_streak: 5,
        longest_streak: 14,
        weekly_consistency: 82
      },
      behavioral_patterns: {
        best_time_of_day: '09:00',
        most_productive_day: 'Tuesday',
        completion_velocity: 2.3
      }
    };
  }

  // AI Recommendations Endpoints
  async getAIRecommendations(limit = 5): Promise<AIRecommendation[]> {
    try {
      return await this.makeRequest<AIRecommendation[]>(`/api/ai/recommendations?limit=${limit}`);
    } catch (error) {
      console.error('Failed to fetch AI recommendations:', error);
      return this.getFallbackRecommendations();
    }
  }

  private getFallbackRecommendations(): AIRecommendation[] {
    const now = new Date().toISOString();
    return [
      {
        id: 'rec-1',
        user_id: 'local',
        type: 'tip',
        title: 'Focus on urgent tasks',
        description: 'You have 2 urgent tasks requiring immediate attention.',
        action_text: 'Review Tasks',
        priority: 'high',
        context: { urgent_count: 2 },
        created_at: now
      },
      {
        id: 'rec-2',
        user_id: 'local',
        type: 'coaching',
        title: 'Great progress in Health & Wellness!',
        description: 'Your consistency in this pillar has improved by 15% this week.',
        action_text: 'View Details',
        pillar_id: 'pillar-1',
        priority: 'medium',
        context: { improvement: 15 },
        created_at: now
      }
    ];
  }

  // RAG Suggestions for Quick Capture
  async getRAGSuggestions(content: string): Promise<{
    suggested_pillar: string;
    suggested_area: string;
    confidence: number;
    reasoning: string;
  }> {
    try {
      return await this.makeRequest('/api/rag/suggestions', {
        method: 'POST',
        body: JSON.stringify({ content })
      });
    } catch (error) {
      console.error('Failed to get RAG suggestions:', error);
      // Fallback to simple keyword matching
      return this.getFallbackRAGSuggestions(content);
    }
  }

  private getFallbackRAGSuggestions(content: string): {
    suggested_pillar: string;
    suggested_area: string;
    confidence: number;
    reasoning: string;
  } {
    const lowerContent = content.toLowerCase();
    
    if (lowerContent.includes('exercise') || lowerContent.includes('health') || lowerContent.includes('workout')) {
      return {
        suggested_pillar: 'Health & Wellness',
        suggested_area: 'Physical Health',
        confidence: 0.8,
        reasoning: 'Content mentions health-related keywords'
      };
    }
    
    if (lowerContent.includes('work') || lowerContent.includes('project') || lowerContent.includes('meeting')) {
      return {
        suggested_pillar: 'Career & Professional',
        suggested_area: 'Work Projects',
        confidence: 0.75,
        reasoning: 'Content mentions work-related keywords'
      };
    }
    
    return {
      suggested_pillar: 'Personal Development',
      suggested_area: 'Learning & Growth',
      confidence: 0.6,
      reasoning: 'Default categorization for general content'
    };
  }

  // Task Completion Patterns
  async getTaskCompletionPatterns(): Promise<{
    daily_patterns: Array<{ hour: number; completion_rate: number; }>;
    weekly_patterns: Array<{ day: string; completion_rate: number; }>;
    priority_patterns: Array<{ priority: string; avg_completion_time: number; }>;
  }> {
    try {
      return await this.makeRequest('/api/tasks/completion-patterns');
    } catch (error) {
      console.error('Failed to fetch task completion patterns:', error);
      return this.getFallbackCompletionPatterns();
    }
  }

  private getFallbackCompletionPatterns() {
    return {
      daily_patterns: [
        { hour: 9, completion_rate: 0.85 },
        { hour: 14, completion_rate: 0.72 },
        { hour: 16, completion_rate: 0.68 }
      ],
      weekly_patterns: [
        { day: 'Monday', completion_rate: 0.82 },
        { day: 'Tuesday', completion_rate: 0.88 },
        { day: 'Wednesday', completion_rate: 0.75 },
        { day: 'Thursday', completion_rate: 0.79 },
        { day: 'Friday', completion_rate: 0.71 }
      ],
      priority_patterns: [
        { priority: 'urgent', avg_completion_time: 2.5 },
        { priority: 'high', avg_completion_time: 4.2 },
        { priority: 'medium', avg_completion_time: 6.8 },
        { priority: 'low', avg_completion_time: 12.1 }
      ]
    };
  }

  // Behavioral Analytics
  async getBehavioralAnalytics(): Promise<{
    productivity_score: number;
    focus_time_trends: Array<{ date: string; focus_minutes: number; }>;
    energy_patterns: Array<{ time: string; energy_level: number; }>;
    goal_alignment_score: number;
  }> {
    try {
      return await this.makeRequest('/api/behavioral-analysis');
    } catch (error) {
      console.error('Failed to fetch behavioral analytics:', error);
      return this.getFallbackBehavioralAnalytics();
    }
  }

  private getFallbackBehavioralAnalytics() {
    return {
      productivity_score: 78,
      focus_time_trends: [
        { date: '2024-01-15', focus_minutes: 180 },
        { date: '2024-01-16', focus_minutes: 165 },
        { date: '2024-01-17', focus_minutes: 200 }
      ],
      energy_patterns: [
        { time: '09:00', energy_level: 85 },
        { time: '14:00', energy_level: 70 },
        { time: '16:00', energy_level: 60 }
      ],
      goal_alignment_score: 82
    };
  }

  // Update user preferences
  async updateUserPreferences(preferences: Record<string, any>): Promise<void> {
    try {
      await this.makeRequest('/api/user/preferences', {
        method: 'PUT',
        body: JSON.stringify(preferences)
      });
    } catch (error) {
      console.error('Failed to update user preferences:', error);
      // Store locally as fallback
      localStorage.setItem('user_preferences', JSON.stringify(preferences));
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; }> {
    try {
      return await this.makeRequest('/api/health');
    } catch (error) {
      console.error('Health check failed:', error);
      return {
        status: 'offline',
        timestamp: new Date().toISOString()
      };
    }
  }
}

export const apiService = new ApiService();
export default apiService;