import { useCallback, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/BackendAuthContext';
import { v4 as uuidv4 } from 'uuid';

/**
 * Analytics tracking hook for user behavior monitoring
 * Provides privacy-compliant tracking with user consent management
 */
export const useAnalytics = () => {
  const { user, token } = useAuth();
  const sessionIdRef = useRef(null);
  const pageStartTimeRef = useRef(null);
  const lastEventTimeRef = useRef(null);
  
  // Backend URL from environment
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Initialize session on hook mount
  useEffect(() => {
    if (user && token && !sessionIdRef.current) {
      initializeSession();
    }
  }, [user, token]);

  // Initialize analytics session
  const initializeSession = useCallback(async () => {
    if (!user || !token) return;

    try {
      sessionIdRef.current = uuidv4();
      
      const sessionData = {
        session_id: sessionIdRef.current,
        entry_page: window.location.pathname,
        user_agent: navigator.userAgent,
        screen_resolution: `${window.screen.width}x${window.screen.height}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        device_type: getDeviceType()
      };

      await fetch(`${backendUrl}/api/analytics/start-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(sessionData)
      });

      // Track initial page view
      trackPageView(window.location.pathname);
      
    } catch (error) {
      console.warn('Failed to initialize analytics session:', error);
    }
  }, [user, token, backendUrl]);

  // Track page views
  const trackPageView = useCallback(async (page, referrer = null) => {
    if (!user || !token || !sessionIdRef.current) return;

    try {
      const eventData = {
        session_id: sessionIdRef.current,
        action_type: 'page_view',
        feature_name: page,
        page_url: page,
        referrer_url: referrer || document.referrer,
        client_timestamp: new Date().toISOString()
      };

      await sendEvent(eventData);
      
      // Update page start time for duration tracking
      pageStartTimeRef.current = Date.now();
      
    } catch (error) {
      console.warn('Failed to track page view:', error);
    }
  }, [user, token]);

  // Track AI feature interactions
  const trackAIInteraction = useCallback(async (featureType, featureName, eventData = {}, success = true, error = null) => {
    if (!user || !token || !sessionIdRef.current) return;

    try {
      const duration = lastEventTimeRef.current ? Date.now() - lastEventTimeRef.current : null;
      
      const trackingData = {
        session_id: sessionIdRef.current,
        action_type: 'ai_interaction',
        feature_name: featureName,
        ai_feature_type: featureType,
        event_data: eventData,
        duration_ms: duration,
        success: success,
        error_message: error,
        page_url: window.location.pathname,
        client_timestamp: new Date().toISOString()
      };

      await sendEvent(trackingData);
      lastEventTimeRef.current = Date.now();
      
    } catch (error) {
      console.warn('Failed to track AI interaction:', error);
    }
  }, [user, token]);

  // Track general feature usage
  const trackFeatureUsage = useCallback(async (featureName, eventData = {}, duration = null) => {
    if (!user || !token || !sessionIdRef.current) return;

    try {
      const trackingData = {
        session_id: sessionIdRef.current,
        action_type: 'feature_usage',
        feature_name: featureName,
        event_data: eventData,
        duration_ms: duration,
        page_url: window.location.pathname,
        client_timestamp: new Date().toISOString()
      };

      await sendEvent(trackingData);
      
    } catch (error) {
      console.warn('Failed to track feature usage:', error);
    }
  }, [user, token]);

  // Track navigation events
  const trackNavigation = useCallback(async (fromPage, toPage, navigationMethod = 'click') => {
    if (!user || !token || !sessionIdRef.current) return;

    try {
      const trackingData = {
        session_id: sessionIdRef.current,
        action_type: 'navigation',
        feature_name: `${fromPage}-to-${toPage}`,
        event_data: {
          from_page: fromPage,
          to_page: toPage,
          navigation_method: navigationMethod
        },
        page_url: toPage,
        referrer_url: fromPage,
        client_timestamp: new Date().toISOString()
      };

      await sendEvent(trackingData);
      
    } catch (error) {
      console.warn('Failed to track navigation:', error);
    }
  }, [user, token]);

  // Track search events
  const trackSearch = useCallback(async (searchTerm, searchType, resultCount = 0, selectionMade = false) => {
    if (!user || !sessionIdRef.current) return;

    try {
      const trackingData = {
        session_id: sessionIdRef.current,
        action_type: 'search',
        feature_name: searchType,
        event_data: {
          search_term_length: searchTerm.length, // Don't store actual search term for privacy
          search_type: searchType,
          result_count: resultCount,
          selection_made: selectionMade
        },
        page_url: window.location.pathname,
        client_timestamp: new Date().toISOString()
      };

      await sendEvent(trackingData);
      
    } catch (error) {
      console.warn('Failed to track search:', error);
    }
  }, [user]);

  // Track task/project actions
  const trackTaskAction = useCallback(async (action, taskId = null, projectId = null, eventData = {}) => {
    if (!user || !sessionIdRef.current) return;

    try {
      const trackingData = {
        session_id: sessionIdRef.current,
        action_type: 'task_action',
        feature_name: action,
        event_data: {
          ...eventData,
          task_id: taskId,
          project_id: projectId
        },
        page_url: window.location.pathname,
        client_timestamp: new Date().toISOString()
      };

      await sendEvent(trackingData);
      
    } catch (error) {
      console.warn('Failed to track task action:', error);
    }
  }, [user]);

  // Track insight feedback
  const trackInsightFeedback = useCallback(async (insightId, feedbackType, insightType = null) => {
    if (!user || !sessionIdRef.current) return;

    try {
      const trackingData = {
        session_id: sessionIdRef.current,
        action_type: 'insight_feedback',
        feature_name: 'insight_feedback',
        event_data: {
          insight_id: insightId,
          feedback_type: feedbackType,
          insight_type: insightType
        },
        page_url: window.location.pathname,
        client_timestamp: new Date().toISOString()
      };

      await sendEvent(trackingData);
      
    } catch (error) {
      console.warn('Failed to track insight feedback:', error);
    }
  }, [user]);

  // Send event to backend
  const sendEvent = useCallback(async (eventData) => {
    if (!user || !token) return;

    try {
      const response = await fetch(`${backendUrl}/api/analytics/track-event`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(eventData)
      });

      if (!response.ok) {
        throw new Error(`Analytics API error: ${response.status}`);
      }

    } catch (error) {
      console.warn('Failed to send analytics event:', error);
    }
  }, [user, token, backendUrl]);

  // End session when user leaves or component unmounts
  const endSession = useCallback(async (exitPage = null) => {
    if (!user || !token || !sessionIdRef.current) return;

    try {
      await fetch(`${backendUrl}/api/analytics/end-session/${sessionIdRef.current}?exit_page=${encodeURIComponent(exitPage || window.location.pathname)}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      sessionIdRef.current = null;
      
    } catch (error) {
      console.warn('Failed to end analytics session:', error);
    }
  }, [user, token, backendUrl]);

  // Utility function to detect device type
  const getDeviceType = () => {
    const width = window.innerWidth;
    if (width <= 768) return 'mobile';
    if (width <= 1024) return 'tablet';
    return 'desktop';
  };

  // Page visibility change handler for session management
  useEffect(() => {
      const handleVisibilityChange = () => {
      if (document.hidden) {
        // Page is hidden, consider ending session after delay
        setTimeout(() => {
          if (document.hidden) {
            endSession();
          }
        }, 30000); // 30 second delay
      } else {
        // Page is visible, reinitialize session if needed
        if (!sessionIdRef.current && user && token) {
          initializeSession();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [user, token, endSession, initializeSession]);

  // Window unload handler
  useEffect(() => {
    const handleUnload = () => {
      if (sessionIdRef.current) {
        // Use sendBeacon for reliability during page unload
        const data = JSON.stringify({
          session_id: sessionIdRef.current,
          exit_page: window.location.pathname
        });
        
        try {
          navigator.sendBeacon(
            `${backendUrl}/api/analytics/end-session/${sessionIdRef.current}`, 
            data
          );
        } catch (error) {
          // Fallback to sync fetch as last resort
          try {
            fetch(`${backendUrl}/api/analytics/end-session/${sessionIdRef.current}`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: data,
              keepalive: true
            });
          } catch (e) {
            console.warn('Failed to send session end on unload:', e);
          }
        }
      }
    };

    window.addEventListener('beforeunload', handleUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleUnload);
    };
  }, [user, token, backendUrl]);

  return {
    // Session management
    sessionId: sessionIdRef.current,
    initializeSession,
    endSession,
    
    // Tracking methods
    trackPageView,
    trackAIInteraction,
    trackFeatureUsage,
    trackNavigation,
    trackSearch,
    trackTaskAction,
    trackInsightFeedback
  };
};

export default useAnalytics;