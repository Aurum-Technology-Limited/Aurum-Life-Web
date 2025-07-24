import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import Login from './Login';

const ProtectedRoute = ({ children }) => {
  const { user, loading, isAuthenticated } = useAuth();

  console.log('🛡️ ProtectedRoute - Auth state:', { 
    user: user ? user.email : 'null', 
    loading, 
    isAuthenticated,
    hasToken: !!localStorage.getItem('auth_token')
  });

  if (loading) {
    console.log('🛡️ ProtectedRoute - Showing loading screen');
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#0B0D14' }}>
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    console.log('🛡️ ProtectedRoute - No user, showing login');
    return <Login />;
  }

  console.log('🛡️ ProtectedRoute - User authenticated, showing app');
  return children;
};

export default ProtectedRoute;