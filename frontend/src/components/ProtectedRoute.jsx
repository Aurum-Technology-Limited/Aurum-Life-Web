import React from 'react';
import { useAuth } from '../contexts/SupabaseAuthContext';
import Login from './Login';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B0D14] flex items-center justify-center">
        <div className="text-center">
          <div className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold text-xl mb-4 inline-block">
            AL
          </div>
          <div className="text-white text-lg">Loading...</div>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return children;
};

export default ProtectedRoute;