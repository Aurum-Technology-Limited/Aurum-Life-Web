/**
 * User Profile Service
 * Handles extended user profile management and AI preferences
 */

interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar_url?: string;
  bio?: string;
  timezone: string;
  workingHours: {
    start: string;
    end: string;
  };
  focusAreas: string[];
  personalityType?: string;
  workStyle: string;
  communicationPreference: string;
  goals: string[];
  achievements: string[];
  customFields: Record<string, string>;
  createdAt: string;
  updatedAt: string;
}

interface AIPreferences {
  enableSmartSuggestions: boolean;
  enableProductivityInsights: boolean;
  enableGoalRecommendations: boolean;
  enableTimeBlocking: boolean;
  enableHabitTracking: boolean;
  dataProcessingLevel: 'minimal' | 'standard' | 'comprehensive';
  insightFrequency: 'realtime' | 'daily' | 'weekly';
  privacyMode: 'open' | 'balanced' | 'strict';
  updatedAt: string;
}

interface UserStats {
  totalTasks: number;
  completedTasks: number;
  activeProjects: number;
  totalPillars: number;
  journalEntries: number;
  daysSinceJoined: number;
  currentStreak: number;
  longestStreak: number;
  productivityScore: number;
  lastActiveDate: string;
  totalFocusTime: number;
  averageTaskCompletionTime: number;
}

interface UserAchievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlockedAt: string;
  category: 'productivity' | 'streak' | 'goals' | 'social' | 'milestone';
  points: number;
}

class UserProfileService {
  private baseUrl: string;
  private userId: string | null = null;

  constructor() {
    this.baseUrl = `${process.env.SUPABASE_URL || 'http://localhost:54321'}/functions/v1/make-server-dd6e2894`;
  }

  private getAuthToken(): string | null {
    try {
      const authData = localStorage.getItem('aurum-auth');
      if (authData) {
        const parsed = JSON.parse(authData);
        return parsed.session?.access_token;
      }
    } catch (error) {
      console.error('Failed to get auth token:', error);
    }
    return null;
  }

  private async apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getAuthToken();
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get complete user profile
   */
  async getUserProfile(): Promise<UserProfile | null> {
    try {
      return await this.apiRequest<UserProfile>('/profile');
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      
      // Fallback to localStorage
      try {
        const userData = localStorage.getItem('aurum-auth');
        if (userData) {
          const parsed = JSON.parse(userData);
          const storedProfile = localStorage.getItem(`aurum-profile-${parsed.user?.id}`);
          
          if (storedProfile) {
            return JSON.parse(storedProfile);
          }
        }
      } catch (fallbackError) {
        console.error('Fallback profile loading failed:', fallbackError);
      }
      
      return null;
    }
  }

  /**
   * Update user profile
   */
  async updateUserProfile(profile: Partial<UserProfile>): Promise<UserProfile> {
    try {
      return await this.apiRequest<UserProfile>('/profile', {
        method: 'PUT',
        body: JSON.stringify(profile),
      });
    } catch (error) {
      console.error('Failed to update user profile:', error);
      
      // Fallback to localStorage
      try {
        const userData = localStorage.getItem('aurum-auth');
        if (userData) {
          const parsed = JSON.parse(userData);
          const userId = parsed.user?.id;
          
          if (userId) {
            const existingProfile = localStorage.getItem(`aurum-profile-${userId}`);
            const currentProfile = existingProfile ? JSON.parse(existingProfile) : {};
            
            const updatedProfile = {
              ...currentProfile,
              ...profile,
              updatedAt: new Date().toISOString()
            };
            
            localStorage.setItem(`aurum-profile-${userId}`, JSON.stringify(updatedProfile));
            return updatedProfile;
          }
        }
      } catch (fallbackError) {
        console.error('Fallback profile update failed:', fallbackError);
      }
      
      throw error;
    }
  }

  /**
   * Get AI preferences
   */
  async getAIPreferences(): Promise<AIPreferences | null> {
    try {
      return await this.apiRequest<AIPreferences>('/ai-preferences');
    } catch (error) {
      console.error('Failed to fetch AI preferences:', error);
      
      // Fallback to localStorage
      try {
        const userData = localStorage.getItem('aurum-auth');
        if (userData) {
          const parsed = JSON.parse(userData);
          const stored = localStorage.getItem(`aurum-ai-preferences-${parsed.user?.id}`);
          
          if (stored) {
            return JSON.parse(stored);
          }
        }
      } catch (fallbackError) {
        console.error('Fallback AI preferences loading failed:', fallbackError);
      }
      
      return null;
    }
  }

  /**
   * Update AI preferences
   */
  async updateAIPreferences(preferences: Partial<AIPreferences>): Promise<AIPreferences> {
    try {
      return await this.apiRequest<AIPreferences>('/ai-preferences', {
        method: 'PUT',
        body: JSON.stringify(preferences),
      });
    } catch (error) {
      console.error('Failed to update AI preferences:', error);
      
      // Fallback to localStorage
      try {
        const userData = localStorage.getItem('aurum-auth');
        if (userData) {
          const parsed = JSON.parse(userData);
          const userId = parsed.user?.id;
          
          if (userId) {
            const existing = localStorage.getItem(`aurum-ai-preferences-${userId}`);
            const current = existing ? JSON.parse(existing) : {};
            
            const updated = {
              ...current,
              ...preferences,
              updatedAt: new Date().toISOString()
            };
            
            localStorage.setItem(`aurum-ai-preferences-${userId}`, JSON.stringify(updated));
            return updated;
          }
        }
      } catch (fallbackError) {
        console.error('Fallback AI preferences update failed:', fallbackError);
      }
      
      throw error;
    }
  }

  /**
   * Get user statistics
   */
  async getUserStats(): Promise<UserStats | null> {
    try {
      return await this.apiRequest<UserStats>('/profile/stats');
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
      
      // Calculate from local data
      return this.calculateLocalStats();
    }
  }

  /**
   * Get user achievements
   */
  async getUserAchievements(): Promise<UserAchievement[]> {
    try {
      return await this.apiRequest<UserAchievement[]>('/profile/achievements');
    } catch (error) {
      console.error('Failed to fetch user achievements:', error);
      
      // Return mock achievements for now
      return this.getMockAchievements();
    }
  }

  /**
   * Upload avatar
   */
  async uploadAvatar(file: File): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('avatar', file);
      
      const token = this.getAuthToken();
      const response = await fetch(`${this.baseUrl}/profile/avatar`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Avatar upload failed');
      }
      
      const result = await response.json();
      return result.avatar_url;
    } catch (error) {
      console.error('Failed to upload avatar:', error);
      throw error;
    }
  }

  /**
   * Calculate user statistics from local data
   */
  private calculateLocalStats(): UserStats {
    try {
      const pillars = JSON.parse(localStorage.getItem('aurum-pillars') || '[]');
      const areas = JSON.parse(localStorage.getItem('aurum-areas') || '[]');
      const projects = JSON.parse(localStorage.getItem('aurum-projects') || '[]');
      const tasks = JSON.parse(localStorage.getItem('aurum-tasks') || '[]');
      const journalEntries = JSON.parse(localStorage.getItem('aurum-journal-entries') || '[]');
      
      const completedTasks = tasks.filter((t: any) => t.status === 'completed');
      const activeProjects = projects.filter((p: any) => p.status === 'active');
      
      // Calculate streaks (simplified)
      const currentStreak = this.calculateCurrentStreak(tasks);
      const longestStreak = this.calculateLongestStreak(tasks);
      
      // Get user creation date
      const userData = localStorage.getItem('aurum-auth');
      let daysSinceJoined = 0;
      
      if (userData) {
        const parsed = JSON.parse(userData);
        const joinDate = new Date(parsed.user?.created_at || Date.now());
        daysSinceJoined = Math.floor((Date.now() - joinDate.getTime()) / (1000 * 60 * 60 * 24));
      }
      
      return {
        totalTasks: tasks.length,
        completedTasks: completedTasks.length,
        activeProjects: activeProjects.length,
        totalPillars: pillars.length,
        journalEntries: journalEntries.length,
        daysSinceJoined,
        currentStreak,
        longestStreak,
        productivityScore: this.calculateProductivityScore(tasks, completedTasks),
        lastActiveDate: new Date().toISOString(),
        totalFocusTime: this.calculateTotalFocusTime(),
        averageTaskCompletionTime: this.calculateAverageCompletionTime(completedTasks)
      };
    } catch (error) {
      console.error('Failed to calculate local stats:', error);
      
      // Return default stats
      return {
        totalTasks: 0,
        completedTasks: 0,
        activeProjects: 0,
        totalPillars: 0,
        journalEntries: 0,
        daysSinceJoined: 0,
        currentStreak: 0,
        longestStreak: 0,
        productivityScore: 0,
        lastActiveDate: new Date().toISOString(),
        totalFocusTime: 0,
        averageTaskCompletionTime: 0
      };
    }
  }

  private calculateCurrentStreak(tasks: any[]): number {
    // Simplified streak calculation
    const completedTasks = tasks.filter(t => t.status === 'completed').sort((a, b) => 
      new Date(b.completedAt || b.updatedAt).getTime() - new Date(a.completedAt || a.updatedAt).getTime()
    );
    
    if (completedTasks.length === 0) return 0;
    
    let streak = 0;
    let currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0);
    
    for (const task of completedTasks) {
      const taskDate = new Date(task.completedAt || task.updatedAt);
      taskDate.setHours(0, 0, 0, 0);
      
      const diffDays = Math.floor((currentDate.getTime() - taskDate.getTime()) / (1000 * 60 * 60 * 24));
      
      if (diffDays === streak) {
        streak++;
        currentDate.setDate(currentDate.getDate() - 1);
      } else {
        break;
      }
    }
    
    return streak;
  }

  private calculateLongestStreak(tasks: any[]): number {
    // Simplified longest streak calculation
    return Math.max(this.calculateCurrentStreak(tasks), 21); // Mock value
  }

  private calculateProductivityScore(allTasks: any[], completedTasks: any[]): number {
    if (allTasks.length === 0) return 0;
    
    const completionRate = completedTasks.length / allTasks.length;
    const recentTasksCount = allTasks.filter(t => {
      const taskDate = new Date(t.createdAt || t.updatedAt);
      const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      return taskDate >= weekAgo;
    }).length;
    
    const activityScore = Math.min(recentTasksCount / 10, 1); // Normalize to 0-1
    
    return Math.round((completionRate * 0.7 + activityScore * 0.3) * 100);
  }

  private calculateTotalFocusTime(): number {
    // This would integrate with time tracking data
    // For now, return a mock value
    return 45 * 60; // 45 minutes in seconds
  }

  private calculateAverageCompletionTime(completedTasks: any[]): number {
    if (completedTasks.length === 0) return 0;
    
    const tasksWithDuration = completedTasks.filter(t => 
      t.createdAt && t.completedAt
    );
    
    if (tasksWithDuration.length === 0) return 0;
    
    const totalTime = tasksWithDuration.reduce((sum: number, task: any) => {
      const created = new Date(task.createdAt);
      const completed = new Date(task.completedAt);
      return sum + (completed.getTime() - created.getTime());
    }, 0);
    
    return Math.round(totalTime / tasksWithDuration.length / (1000 * 60 * 60)); // Hours
  }

  private getMockAchievements(): UserAchievement[] {
    return [
      {
        id: '1',
        name: 'Task Master',
        description: 'Complete 100+ tasks',
        icon: '🏆',
        unlockedAt: new Date().toISOString(),
        category: 'productivity',
        points: 100
      },
      {
        id: '2',
        name: 'Streak Champion',
        description: 'Maintain a 7-day active streak',
        icon: '🔥',
        unlockedAt: new Date().toISOString(),
        category: 'streak',
        points: 75
      },
      {
        id: '3',
        name: 'Goal Setter',
        description: 'Create your first pillar',
        icon: '🎯',
        unlockedAt: new Date().toISOString(),
        category: 'goals',
        points: 50
      }
    ];
  }

  /**
   * Export user data
   */
  async exportUserData(): Promise<Blob> {
    const [profile, preferences, stats, achievements] = await Promise.all([
      this.getUserProfile(),
      this.getAIPreferences(),
      this.getUserStats(),
      this.getUserAchievements()
    ]);

    const exportData = {
      profile,
      aiPreferences: preferences,
      statistics: stats,
      achievements,
      exportedAt: new Date().toISOString(),
      version: '1.0'
    };

    return new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
  }

  /**
   * Delete user account
   */
  async deleteAccount(): Promise<void> {
    try {
      await this.apiRequest('/profile', {
        method: 'DELETE'
      });
      
      // Clear local data
      this.clearLocalData();
    } catch (error) {
      console.error('Failed to delete account:', error);
      throw error;
    }
  }

  private clearLocalData(): void {
    // Clear all Aurum Life related localStorage items
    const keys = Object.keys(localStorage).filter(key => key.startsWith('aurum-'));
    keys.forEach(key => localStorage.removeItem(key));
  }
}

export const userProfileService = new UserProfileService();
export type { 
  UserProfile, 
  AIPreferences, 
  UserStats, 
  UserAchievement 
};