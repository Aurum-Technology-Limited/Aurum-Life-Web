/**
 * Phase 2 Status Bar Component
 * Shows connection status, sync status, and PWA capabilities
 */

import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Wifi, WifiOff, Sync, Download, Share2, 
  AlertTriangle, CheckCircle, Clock, 
  Smartphone, Cloud, CloudOff, X 
} from 'lucide-react';
import { usePhase2Store, useRealTimeSync, usePWAFeatures } from '../../stores/phase2IntegrationStore';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Card, CardContent } from '../ui/card';
import toast from '../../utils/toast';

interface Phase2StatusBarProps {
  className?: string;
}

const Phase2StatusBar: React.FC<Phase2StatusBarProps> = ({
  className = ''
}) => {
  const {
    isOnline,
    syncStatus,
    pendingChanges,
    lastSyncTime,
  } = useRealTimeSync();

  const {
    pwaCapabilities,
    installPromptAvailable,
    showInstallPrompt,
    showOfflineBanner,
    showSyncStatus,
    promptInstall,
    cacheOfflineData,
    setShowInstallPrompt,
    setShowOfflineBanner
  } = usePWAFeatures();

  const {
    setShowSyncStatus
  } = usePhase2Store();

  const handleInstallApp = async () => {
    const success = await promptInstall();
    if (success) {
      toast.success('App installed successfully!');
    } else {
      toast.error('Installation cancelled or failed');
    }
  };

  const handleCacheData = async () => {
    try {
      await cacheOfflineData();
      toast.success('Data cached for offline use');
      setShowOfflineBanner(false);
    } catch (error) {
      toast.error('Failed to cache data');
    }
  };

  const getSyncStatusColor = () => {
    switch (syncStatus) {
      case 'syncing': return 'text-blue-400';
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      default: return 'text-muted-foreground';
    }
  };

  const getSyncStatusIcon = () => {
    switch (syncStatus) {
      case 'syncing': return <Sync className="w-4 h-4 animate-spin" />;
      case 'success': return <CheckCircle className="w-4 h-4" />;
      case 'error': return <AlertTriangle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const getConnectionIcon = () => {
    return isOnline ? (
      <Wifi className="w-4 h-4 text-green-400" />
    ) : (
      <WifiOff className="w-4 h-4 text-red-400" />
    );
  };

  const formatLastSync = () => {
    if (!lastSyncTime) return 'Never';
    
    const date = new Date(lastSyncTime);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Main Status Bar */}
      <div className="flex items-center justify-between px-4 py-2 glassmorphism-panel rounded-lg">
        {/* Connection Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            {getConnectionIcon()}
            <span className="text-sm font-medium">
              {isOnline ? 'Online' : 'Offline'}
            </span>
          </div>
          
          <div className="w-px h-4 bg-border" />
          
          {/* Sync Status */}
          <div className={`flex items-center gap-2 ${getSyncStatusColor()}`}>
            {getSyncStatusIcon()}
            <span className="text-sm">
              {syncStatus === 'syncing' ? 'Syncing...' : 
               syncStatus === 'success' ? 'Synced' :
               syncStatus === 'error' ? 'Sync Error' : 'Idle'}
            </span>
            {pendingChanges > 0 && (
              <Badge variant="secondary" className="text-xs">
                {pendingChanges} pending
              </Badge>
            )}
          </div>
          
          <div className="w-px h-4 bg-border" />
          
          {/* Last Sync Time */}
          <span className="text-xs text-muted-foreground">
            Last sync: {formatLastSync()}
          </span>
        </div>

        {/* PWA Features */}
        <div className="flex items-center gap-2">
          {pwaCapabilities.isStandalone && (
            <Badge variant="outline" className="text-xs">
              <Smartphone className="w-3 h-3 mr-1" />
              PWA
            </Badge>
          )}
          
          {!isOnline && pwaCapabilities.hasOfflineCapability && (
            <Badge variant="outline" className="text-xs text-orange-400">
              <CloudOff className="w-3 h-3 mr-1" />
              Offline Ready
            </Badge>
          )}
          
          {installPromptAvailable && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowInstallPrompt(true)}
              className="text-xs h-7"
            >
              <Download className="w-3 h-3 mr-1" />
              Install
            </Button>
          )}
        </div>
      </div>

      {/* Install Prompt Banner */}
      <AnimatePresence>
        {showInstallPrompt && installPromptAvailable && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card className="glassmorphism-card border-primary/30">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/20 rounded-full">
                      <Smartphone className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-medium text-foreground">
                        Install Aurum Life
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        Get the full app experience with offline access and faster loading
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowInstallPrompt(false)}
                    >
                      Later
                    </Button>
                    <Button
                      size="sm"
                      onClick={handleInstallApp}
                      className="bg-primary text-primary-foreground"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Install
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Offline Banner */}
      <AnimatePresence>
        {showOfflineBanner && !isOnline && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card className="glassmorphism-card border-orange-500/30">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-500/20 rounded-full">
                      <WifiOff className="w-5 h-5 text-orange-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-foreground">
                        You're offline
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        Some features may be limited. Cache data for better offline experience.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowOfflineBanner(false)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCacheData}
                    >
                      <Cloud className="w-4 h-4 mr-2" />
                      Cache Data
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sync Status Detail */}
      <AnimatePresence>
        {showSyncStatus && syncStatus === 'syncing' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="glassmorphism-panel p-3 rounded-lg"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sync className="w-4 h-4 animate-spin text-blue-400" />
                <span className="text-sm text-foreground">Syncing changes...</span>
                {pendingChanges > 0 && (
                  <Badge variant="secondary" className="text-xs">
                    {pendingChanges} items
                  </Badge>
                )}
              </div>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSyncStatus(false)}
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Phase2StatusBar;