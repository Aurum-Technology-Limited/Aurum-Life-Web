import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/BackendAuthContext';

const ProfilePage = ({ setActiveSection }) => {
  const { handleGoogleCallback, user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Check if we have a session_id in the URL hash
        const hash = window.location.hash;
        const sessionIdMatch = hash.match(/session_id=([^&]*)/);
        
        if (sessionIdMatch) {
          const sessionId = sessionIdMatch[1];
          
          // Handle the Google callback
          const result = await handleGoogleCallback(sessionId);
          
          if (result.success) {
            // Clear the hash from URL
            window.history.replaceState(null, null, window.location.pathname);
            
            // Navigate to dashboard using section system
            if (setActiveSection) {
              setActiveSection('dashboard');
            }
          } else {
            setError(result.error || 'Authentication failed');
          }
        } else if (user) {
          // User is already authenticated, go to dashboard
          if (setActiveSection) {
            setActiveSection('dashboard');
          }
        } else {
          // No session ID found and no user, this shouldn't happen
          setError('Invalid authentication state');
        }
      } catch (err) {
        console.error('OAuth callback error:', err);
        setError('Authentication error occurred');
      } finally {
        setLoading(false);
      }
    };

    handleOAuthCallback();
  }, [handleGoogleCallback, setActiveSection, user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B0D14] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <span className="text-black font-bold text-xl">AL</span>
          </div>
          <h2 className="text-white text-xl font-semibold mb-2">Completing Sign In...</h2>
          <p className="text-gray-400">Please wait while we set up your account</p>
          <div className="mt-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400 mx-auto"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0B0D14] flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="w-16 h-16 bg-red-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-xl">!</span>
          </div>
          <h2 className="text-white text-xl font-semibold mb-2">Authentication Failed</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button
            onClick={() => window.location.href = '/'}
            className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-black px-6 py-2 rounded-lg font-medium hover:from-yellow-600 hover:to-yellow-700 transition-colors"
          >
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  // This should not render as we redirect in useEffect
  return null;
};

export default ProfilePage;