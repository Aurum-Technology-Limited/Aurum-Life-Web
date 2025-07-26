/**
 * Supabase Enhanced API Service
 * Provides real-time capabilities and direct database access for Aurum Life
 */

import { supabase } from './supabase';

class SupabaseAPI {
  // User Profile Operations
  static async getUserProfile(userId) {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('id', userId)
        .single();

      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Get user profile error:', error);
      return { success: false, error: error.message };
    }
  }

  static async updateUserProfile(userId, profileData) {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .update(profileData)
        .eq('id', userId)
        .select()
        .single();

      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Update user profile error:', error);
      return { success: false, error: error.message };
    }
  }

  // Real-time Subscriptions
  static subscribeToPillars(userId, callback) {
    return supabase
      .channel('pillars')
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'pillars',
          filter: `user_id=eq.${userId}`
        }, 
        callback
      )
      .subscribe();
  }

  static subscribeToAreas(userId, callback) {
    return supabase
      .channel('areas')
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'areas',
          filter: `user_id=eq.${userId}`
        }, 
        callback
      )
      .subscribe();
  }

  static subscribeToProjects(userId, callback) {
    return supabase
      .channel('projects')
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'projects',
          filter: `user_id=eq.${userId}`
        }, 
        callback
      )
      .subscribe();
  }

  static subscribeToTasks(userId, callback) {
    return supabase
      .channel('tasks')
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'tasks',
          filter: `user_id=eq.${userId}`
        }, 
        callback
      )
      .subscribe();
  }

  // Direct Database Queries (for performance-critical operations)
  static async getTasksWithProjects(userId) {
    try {
      const { data, error } = await supabase
        .from('tasks')
        .select(`
          *,
          projects:project_id (
            id,
            name,
            icon,
            color,
            areas:area_id (
              id,
              name,
              pillars:pillar_id (
                id,
                name
              )
            )
          )
        `)
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Get tasks with projects error:', error);
      return { success: false, error: error.message };
    }
  }

  static async getTodayTasks(userId) {
    try {
      const today = new Date().toISOString().split('T')[0];
      
      const { data, error } = await supabase
        .from('tasks')
        .select(`
          *,
          projects:project_id (
            id,
            name,
            icon,
            color
          )
        `)
        .eq('user_id', userId)
        .or(`due_date.eq.${today},status.eq.in_progress`)
        .order('priority', { ascending: false });

      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Get today tasks error:', error);
      return { success: false, error: error.message };
    }
  }

  static async getOverdueTasks(userId) {
    try {
      const today = new Date().toISOString().split('T')[0];
      
      const { data, error } = await supabase
        .from('tasks')
        .select(`
          *,
          projects:project_id (
            id,
            name,
            icon,
            color
          )
        `)
        .eq('user_id', userId)
        .lt('due_date', today)
        .neq('status', 'completed')
        .order('due_date', { ascending: true });

      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Get overdue tasks error:', error);
      return { success: false, error: error.message };
    }
  }

  // File Storage Operations
  static async uploadFile(bucket, filePath, file) {
    try {
      const { data, error } = await supabase.storage
        .from(bucket)
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false
        });

      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('File upload error:', error);
      return { success: false, error: error.message };
    }
  }

  static async getFileUrl(bucket, filePath) {
    try {
      const { data } = supabase.storage
        .from(bucket)
        .getPublicUrl(filePath);

      return { success: true, url: data.publicUrl };
    } catch (error) {
      console.error('Get file URL error:', error);
      return { success: false, error: error.message };
    }
  }

  // Analytics and Insights
  static async getDashboardStats(userId) {
    try {
      // Get counts for different entities
      const [pillarsResult, areasResult, projectsResult, tasksResult] = await Promise.all([
        supabase.from('pillars').select('id', { count: 'exact' }).eq('user_id', userId),
        supabase.from('areas').select('id', { count: 'exact' }).eq('user_id', userId),
        supabase.from('projects').select('id', { count: 'exact' }).eq('user_id', userId),
        supabase.from('tasks').select('id', { count: 'exact' }).eq('user_id', userId)
      ]);

      // Get task status breakdown
      const { data: taskStatuses, error: statusError } = await supabase
        .from('tasks')
        .select('status')
        .eq('user_id', userId);

      if (statusError) throw statusError;

      const statusCounts = taskStatuses.reduce((acc, task) => {
        acc[task.status] = (acc[task.status] || 0) + 1;
        return acc;
      }, {});

      return {
        success: true,
        data: {
          pillars: pillarsResult.count || 0,
          areas: areasResult.count || 0,
          projects: projectsResult.count || 0,
          tasks: tasksResult.count || 0,
          taskStatusBreakdown: statusCounts,
          completedTasks: statusCounts.completed || 0,
          pendingTasks: (statusCounts.todo || 0) + (statusCounts.in_progress || 0)
        }
      };
    } catch (error) {
      console.error('Get dashboard stats error:', error);
      return { success: false, error: error.message };
    }
  }

  // Utility Methods
  static unsubscribe(subscription) {
    if (subscription) {
      supabase.removeChannel(subscription);
    }
  }

  static async testConnection() {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .select('id')
        .limit(1);

      return { success: !error, connected: !error };
    } catch (error) {
      console.error('Supabase connection test failed:', error);
      return { success: false, connected: false };
    }
  }
}

export default SupabaseAPI;