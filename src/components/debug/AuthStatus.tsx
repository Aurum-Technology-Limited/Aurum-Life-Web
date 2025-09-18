import { useState } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { useAppStore } from '../../stores/basicAppStore';
import { authService } from '../../utils/supabase/auth';
import { projectId, publicAnonKey } from '../../utils/supabase/info';

export default function AuthStatus() {
  const [setupResult, setSetupResult] = useState<string | null>(null);
  const [isSettingUp, setIsSettingUp] = useState(false);
  
  const isAuthenticated = useAppStore(state => state.isAuthenticated);
  const user = useAppStore(state => state.user);
  const isLoading = useAppStore(state => state.isLoading);
  const error = useAppStore(state => state.error);

  const handleSetupDemo = async () => {
    setIsSettingUp(true);
    setSetupResult(null);
    
    try {
      const response = await fetch(`https://${projectId}.supabase.co/functions/v1/make-server-dd6e2894/setup-demo`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${publicAnonKey}`,
        },
      });

      const result = await response.json();
      
      if (response.ok) {
        setSetupResult(`✅ ${result.message}`);
      } else {
        setSetupResult(`❌ ${result.error || 'Failed to setup demo'}`);
      }
    } catch (error) {
      setSetupResult(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSettingUp(false);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white w-80">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-[#F4D03F]">Authentication Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-[#B8BCC8]">Authenticated:</span>
              <span className={isAuthenticated ? "text-green-400" : "text-red-400"}>
                {isAuthenticated ? "✅ Yes" : "❌ No"}
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-[#B8BCC8]">Loading:</span>
              <span className={isLoading ? "text-yellow-400" : "text-[#B8BCC8]"}>
                {isLoading ? "⏳ Yes" : "No"}
              </span>
            </div>
            
            {user && (
              <>
                <div className="flex justify-between">
                  <span className="text-[#B8BCC8]">User:</span>
                  <span className="text-[#F4D03F] truncate max-w-[120px]">{user.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#B8BCC8]">Email:</span>
                  <span className="text-[#B8BCC8] truncate max-w-[120px]">{user.email}</span>
                </div>
              </>
            )}
            
            {error && (
              <div className="flex justify-between">
                <span className="text-[#B8BCC8]">Error:</span>
                <span className="text-red-400 truncate max-w-[120px]" title={error}>
                  {error}
                </span>
              </div>
            )}
            
            <div className="flex justify-between">
              <span className="text-[#B8BCC8]">Session:</span>
              <span className={authService.isAuthenticated() ? "text-green-400" : "text-red-400"}>
                {authService.isAuthenticated() ? "✅ Valid" : "❌ None"}
              </span>
            </div>
          </div>
          
          <div className="pt-2 border-t border-[rgba(244,208,63,0.1)]">
            <Button
              onClick={handleSetupDemo}
              disabled={isSettingUp}
              size="sm"
              className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] text-xs h-8"
            >
              {isSettingUp ? 'Setting up...' : 'Setup Demo User'}
            </Button>
            
            {setupResult && (
              <p className="text-xs mt-2 break-words">
                {setupResult}
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}