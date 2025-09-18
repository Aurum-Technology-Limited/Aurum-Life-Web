import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  AlertCircle, 
  RefreshCw, 
  Wifi, 
  WifiOff, 
  ChevronDown, 
  ChevronUp,
  ExternalLink,
  Bug,
  Shield
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { cn } from '../../lib/utils';
import { toast } from 'sonner@2.0.3';

interface ErrorRecoveryProps {
  error: Error | string;
  onRetry?: () => void;
  onReport?: (error: Error | string) => void;
  context?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  suggestions?: string[];
  className?: string;
}

export function ErrorRecovery({ 
  error, 
  onRetry, 
  onReport,
  context = 'application',
  severity = 'medium',
  suggestions = [],
  className 
}: ErrorRecoveryProps) {
  const [isRetrying, setIsRetrying] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleRetry = async () => {
    if (!onRetry) return;

    setIsRetrying(true);
    setRetryCount(prev => prev + 1);

    try {
      await new Promise(resolve => setTimeout(resolve, 1000)); // Brief delay
      await onRetry();
      toast.success('Issue resolved successfully');
    } catch (retryError) {
      toast.error('Retry failed. Please try again.');
      console.error('Retry failed:', retryError);
    } finally {
      setIsRetrying(false);
    }
  };

  const handleReport = () => {
    if (onReport) {
      onReport(error);
      toast.success('Error report sent. Thank you for helping us improve!');
    }
  };

  const getErrorMessage = () => {
    if (typeof error === 'string') return error;
    
    // User-friendly error messages
    const message = error.message.toLowerCase();
    
    if (message.includes('network') || message.includes('fetch')) {
      return 'Connection issue detected. Please check your internet connection.';
    }
    
    if (message.includes('timeout')) {
      return 'Request timed out. The server might be busy.';
    }
    
    if (message.includes('unauthorized') || message.includes('401')) {
      return 'Authentication expired. Please sign in again.';
    }
    
    if (message.includes('forbidden') || message.includes('403')) {
      return 'Access denied. You may not have permission for this action.';
    }
    
    if (message.includes('not found') || message.includes('404')) {
      return 'The requested resource could not be found.';
    }
    
    if (message.includes('server') || message.includes('500')) {
      return 'Server error occurred. Our team has been notified.';
    }

    return `Something went wrong in ${context}. We're working to fix this.`;
  };

  const getSeverityColor = () => {
    switch (severity) {
      case 'low': return 'text-blue-400 border-blue-400/20 bg-blue-400/10';
      case 'medium': return 'text-yellow-400 border-yellow-400/20 bg-yellow-400/10';
      case 'high': return 'text-orange-400 border-orange-400/20 bg-orange-400/10';
      case 'critical': return 'text-red-400 border-red-400/20 bg-red-400/10';
      default: return 'text-yellow-400 border-yellow-400/20 bg-yellow-400/10';
    }
  };

  const getDefaultSuggestions = (): string[] => {
    const defaultSuggestions = [];
    
    if (!isOnline) {
      defaultSuggestions.push('Check your internet connection');
    }
    
    if (typeof error === 'object' && error.message.includes('timeout')) {
      defaultSuggestions.push('Try again in a few moments');
      defaultSuggestions.push('Close other browser tabs to free up memory');
    }
    
    defaultSuggestions.push('Refresh the page');
    defaultSuggestions.push('Clear your browser cache');
    
    return [...suggestions, ...defaultSuggestions];
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("w-full max-w-2xl mx-auto", className)}
    >
      <Card className={cn("glassmorphism-card border-2", getSeverityColor())}>
        <CardHeader className="pb-4">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              <div className={cn(
                "p-2 rounded-lg",
                getSeverityColor()
              )}>
                <AlertCircle className="w-6 h-6" />
              </div>
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <CardTitle className="text-lg">Something went wrong</CardTitle>
                <Badge variant="outline" className={getSeverityColor()}>
                  {severity}
                </Badge>
              </div>
              
              <p className="text-muted-foreground text-sm mb-4">
                {getErrorMessage()}
              </p>

              {/* Connection status */}
              <div className="flex items-center gap-2 text-xs">
                {isOnline ? (
                  <>
                    <Wifi className="w-3 h-3 text-green-400" />
                    <span className="text-green-400">Connected</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="w-3 h-3 text-red-400" />
                    <span className="text-red-400">Offline</span>
                  </>
                )}
                
                {retryCount > 0 && (
                  <>
                    <Separator orientation="vertical" className="h-3" />
                    <span className="text-muted-foreground">
                      Retry attempts: {retryCount}
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Action buttons */}
          <div className="flex flex-wrap gap-2">
            {onRetry && (
              <Button
                onClick={handleRetry}
                disabled={isRetrying}
                className="flex items-center gap-2"
                variant="default"
              >
                <RefreshCw className={cn("w-4 h-4", isRetrying && "animate-spin")} />
                {isRetrying ? 'Retrying...' : 'Try Again'}
              </Button>
            )}

            <Button
              onClick={() => window.location.reload()}
              variant="outline"
              className="flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh Page
            </Button>

            {onReport && (
              <Button
                onClick={handleReport}
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
              >
                <Bug className="w-4 h-4" />
                Report Issue
              </Button>
            )}
          </div>

          {/* Suggestions */}
          {getDefaultSuggestions().length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Suggested solutions:
              </h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                {getDefaultSuggestions().slice(0, 3).map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="w-1 h-1 bg-primary rounded-full mt-2 flex-shrink-0" />
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Error details (collapsible) */}
          <Collapsible open={showDetails} onOpenChange={setShowDetails}>
            <CollapsibleTrigger className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
              {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              Technical details
            </CollapsibleTrigger>
            <CollapsibleContent className="space-y-2 mt-2">
              <div className="p-3 bg-muted/50 rounded-lg">
                <code className="text-xs font-mono break-all">
                  {typeof error === 'string' ? error : error.message}
                </code>
                {typeof error === 'object' && error.stack && (
                  <details className="mt-2">
                    <summary className="text-xs cursor-pointer hover:text-foreground">
                      Stack trace
                    </summary>
                    <pre className="text-xs mt-1 overflow-x-auto">
                      {error.stack}
                    </pre>
                  </details>
                )}
              </div>
            </CollapsibleContent>
          </Collapsible>

          {/* Help link */}
          <div className="pt-2 border-t border-border/50">
            <Button
              variant="link"
              size="sm"
              className="h-auto p-0 text-xs"
              onClick={() => window.open('/help/troubleshooting', '_blank')}
            >
              <ExternalLink className="w-3 h-3 mr-1" />
              Need more help?
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

interface GracefulDegradationProps {
  fallback: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function GracefulDegradation({ fallback, children, className }: GracefulDegradationProps) {
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const handleError = () => setHasError(true);
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError) {
    return (
      <div className={className}>
        {fallback}
      </div>
    );
  }

  return <div className={className}>{children}</div>;
}

export function useErrorRecovery() {
  const [error, setError] = useState<Error | null>(null);
  const [isRecovering, setIsRecovering] = useState(false);

  const clearError = () => setError(null);
  
  const recover = async (recoveryFn: () => Promise<void>) => {
    setIsRecovering(true);
    try {
      await recoveryFn();
      setError(null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsRecovering(false);
    }
  };

  return {
    error,
    isRecovering,
    setError,
    clearError,
    recover
  };
}