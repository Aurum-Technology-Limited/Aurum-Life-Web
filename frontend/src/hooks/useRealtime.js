/**
 * Real-time Hook for Supabase Subscriptions
 * Provides live updates for Aurum Life data
 */

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/SupabaseAuthContext';
import SupabaseAPI from '../services/supabaseApi';

export const useRealtime = (table, options = {}) => {
  const { user } = useAuth();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const subscriptionRef = useRef(null);

  const { 
    enableRealtime = true, 
    initialLoad = true,
    onInsert,
    onUpdate,
    onDelete
  } = options;

  useEffect(() => {
    if (!user) {
      setData([]);
      setLoading(false);
      return;
    }

    let isMounted = true;

    const handleRealtimeEvent = (payload) => {
      const { eventType, new: newRecord, old: oldRecord } = payload;

      if (!isMounted) return;

      console.log(`Real-time ${eventType} event for ${table}:`, payload);

      switch (eventType) {
        case 'INSERT':
          setData(prev => [...prev, newRecord]);
          onInsert?.(newRecord);
          break;

        case 'UPDATE':
          setData(prev => prev.map(item => 
            item.id === newRecord.id ? newRecord : item
          ));
          onUpdate?.(newRecord, oldRecord);
          break;

        case 'DELETE':
          setData(prev => prev.filter(item => item.id !== oldRecord.id));
          onDelete?.(oldRecord);
          break;

        default:
          console.warn('Unknown real-time event:', eventType);
      }
    };

    // Setup real-time subscription
    if (enableRealtime) {
      const subscriptionMethod = {
        pillars: SupabaseAPI.subscribeToPillars,
        areas: SupabaseAPI.subscribeToAreas,
        projects: SupabaseAPI.subscribeToProjects,
        tasks: SupabaseAPI.subscribesToTasks
      }[table];

      if (subscriptionMethod) {
        subscriptionRef.current = subscriptionMethod(user.id, handleRealtimeEvent);
        console.log(`✅ Real-time subscription active for ${table}`);
      }
    }

    return () => {
      isMounted = false;
      if (subscriptionRef.current) {
        SupabaseAPI.unsubscribe(subscriptionRef.current);
        console.log(`🔌 Real-time subscription closed for ${table}`);
      }
    };
  }, [user, table, enableRealtime]);

  return { data, loading, error, setData, setLoading, setError };
};

export const useTodayTasks = () => {
  const { user } = useAuth();
  const [todayTasks, setTodayTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) {
      setTodayTasks([]);
      setLoading(false);
      return;
    }

    const fetchTodayTasks = async () => {
      try {
        setLoading(true);
        const result = await SupabaseAPI.getTodayTasks(user.id);
        
        if (result.success) {
          setTodayTasks(result.data);
          setError(null);
        } else {
          setError(result.error);
        }
      } catch (error) {
        console.error('Error fetching today tasks:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTodayTasks();

    // Set up real-time updates for tasks
    const subscription = SupabaseAPI.subscribeToTasks(user.id, (payload) => {
      const { eventType, new: newTask, old: oldTask } = payload;
      const today = new Date().toISOString().split('T')[0];
      
      // Update today tasks based on real-time changes
      switch (eventType) {
        case 'INSERT':
          if (newTask.due_date === today || newTask.status === 'in_progress') {
            setTodayTasks(prev => [...prev, newTask]);
          }
          break;
          
        case 'UPDATE':
          setTodayTasks(prev => {
            // Remove from today tasks if no longer relevant
            if (newTask.due_date !== today && newTask.status !== 'in_progress') {
              return prev.filter(task => task.id !== newTask.id);
            }
            
            // Update existing task or add if now relevant
            const existingIndex = prev.findIndex(task => task.id === newTask.id);
            if (existingIndex >= 0) {
              return prev.map(task => task.id === newTask.id ? newTask : task);
            } else {
              return [...prev, newTask];
            }
          });
          break;
          
        case 'DELETE':
          setTodayTasks(prev => prev.filter(task => task.id !== oldTask.id));
          break;
      }
    });

    return () => {
      if (subscription) {
        SupabaseAPI.unsubscribe(subscription);
      }
    };
  }, [user]);

  const refreshTasks = async () => {
    if (user) {
      setLoading(true);
      const result = await SupabaseAPI.getTodayTasks(user.id);
      if (result.success) {
        setTodayTasks(result.data);
        setError(null);
      } else {
        setError(result.error);
      }
      setLoading(false);
    }
  };

  return { 
    todayTasks, 
    loading, 
    error, 
    refreshTasks,
    setTodayTasks
  };
};

export const useDashboardStats = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) {
      setStats(null);
      setLoading(false);
      return;
    }

    const fetchStats = async () => {
      try {
        setLoading(true);
        const result = await SupabaseAPI.getDashboardStats(user.id);
        
        if (result.success) {
          setStats(result.data);
          setError(null);
        } else {
          setError(result.error);
        }
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [user]);

  const refreshStats = async () => {
    if (user) {
      const result = await SupabaseAPI.getDashboardStats(user.id);
      if (result.success) {
        setStats(result.data);
        setError(null);
      } else {
        setError(result.error);
      }
    }
  };

  return { stats, loading, error, refreshStats };
};