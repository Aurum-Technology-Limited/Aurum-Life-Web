import React, { useState } from 'react';
import { useAuth } from '../contexts/SupabaseAuthContext';
import { getBackendBaseUrl, getURLResolutionDebugInfo } from '../services/baseUrl';
import { Settings, Eye, EyeOff, RefreshCw } from 'lucide-react';

/**
 * Authentication Debug Panel
 * Helps diagnose authentication issues by showing URL resolution and token status
 */
const AuthDebugPanel = () => {
  const { user, token, login, logout } = useAuth();
  const [showDebugInfo, setShowDebugInfo] = useState(false);
  const [debugInfo, setDebugInfo] = useState(null);
  const [testingAuth, setTestingAuth] = useState(false);

  const refreshDebugInfo = () => {
    const info = getURLResolutionDebugInfo();
    const backendUrl = getBackendBaseUrl();
    
    setDebugInfo({
      ...info,
      currentBackendUrl: backendUrl,
      tokenPresent: !!token,
      tokenLength: token ? token.length : 0,
      userPresent: !!user,
      userId: user?.id || 'No user',
      windowOrigin: window.location.origin,
      currentURL: window.location.href
    });
  };

  const testAuthentication = async () => {
    setTestingAuth(true);
    try {
      const backendUrl = getBackendBaseUrl();
      
      // Test health endpoint
      const healthResponse = await fetch(`${backendUrl}/api/health`);
      const healthData = await healthResponse.json();
      
      console.log('Health check result:', healthData);
      
      // Test login
      const loginResult = await login('marc.alleyne@aurumtechnologyltd.com', 'password123');
      console.log('Login test result:', loginResult);
      
    } catch (error) {
      console.error('Authentication test failed:', error);
    } finally {
      setTestingAuth(false);
    }
  };

  React.useEffect(() => {
    refreshDebugInfo();
  }, [user, token]);

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={() => setShowDebugInfo(!showDebugInfo)}
        className="p-3 bg-gray-800 hover:bg-gray-700 rounded-lg border border-gray-600 text-white"
        title="Authentication Debug Panel"
      >
        <Settings className="h-5 w-5" />
      </button>

      {showDebugInfo && (
        <div className="absolute bottom-16 right-0 w-96 bg-gray-900 border border-gray-600 rounded-lg p-4 text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Auth Debug Panel</h3>
            <button
              onClick={() => setShowDebugInfo(false)}
              className="text-gray-400 hover:text-white"
            >
              <EyeOff className="h-4 w-4" />
            </button>
          </div>

          <div className="space-y-3">
            {/* Authentication Status */}
            <div className="p-3 bg-gray-800 rounded border border-gray-700">
              <h4 className="font-medium mb-2">Authentication Status</h4>
              <div className="text-sm space-y-1">
                <p>User: {user ? '✅ Logged in' : '❌ Not logged in'}</p>
                <p>Token: {token ? '✅ Present' : '❌ Missing'}</p>
                {user && <p>User ID: {user.id?.slice(0, 8)}...</p>}
              </div>
            </div>

            {/* URL Resolution */}
            <div className="p-3 bg-gray-800 rounded border border-gray-700">
              <h4 className="font-medium mb-2">URL Resolution</h4>
              <div className="text-xs space-y-1">
                <p>Current Domain: {window.location.origin}</p>
                <p>Backend URL: {debugInfo?.currentBackendUrl || 'Loading...'}</p>
                <p>Env Variable: {debugInfo?.environmentURL || 'Not set'}</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <button
                onClick={refreshDebugInfo}
                className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm"
              >
                <RefreshCw className="h-4 w-4 inline mr-1" />
                Refresh
              </button>
              <button
                onClick={testAuthentication}
                disabled={testingAuth}
                className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm disabled:opacity-50"
              >
                {testingAuth ? 'Testing...' : 'Test Auth'}
              </button>
            </div>

            {/* Debug Details */}
            {debugInfo && (
              <details className="text-xs">
                <summary className="cursor-pointer text-gray-400 hover:text-white">
                  Debug Details
                </summary>
                <pre className="mt-2 p-2 bg-gray-800 rounded text-xs overflow-auto max-h-32">
                  {JSON.stringify(debugInfo, null, 2)}
                </pre>
              </details>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AuthDebugPanel;