import React, { Component, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '../ui/button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  isTimeout: boolean;
}

export default class TimeoutErrorBoundary extends Component<Props, State> {
  private timeoutId: NodeJS.Timeout | null = null;

  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      isTimeout: false
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Check if this is a timeout-related error including getPage errors
    const errorMessage = error.message?.toLowerCase() || '';
    const errorName = error.name?.toLowerCase() || '';
    
    const isTimeout = errorMessage.includes('timeout') || 
                     errorMessage.includes('timed out') ||
                     errorMessage.includes('emergency timeout') ||
                     errorMessage.includes('exceeded') ||
                     errorMessage.includes('getpage') ||
                     errorMessage.includes('response timed out') ||
                     errorName.includes('timeout');

    return {
      hasError: true,
      error,
      isTimeout
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('TimeoutErrorBoundary caught an error:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
    
    // Set up automatic recovery for timeout errors - shorter recovery time
    if (this.state.isTimeout) {
      this.timeoutId = setTimeout(() => {
        console.log('Auto-recovering from timeout error');
        this.setState({
          hasError: false,
          error: null,
          isTimeout: false
        });
      }, 3000); // Reduced from 5000ms to 3000ms
    }
  }

  componentWillUnmount() {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      isTimeout: false
    });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleRefresh = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const { error, isTimeout } = this.state;

      return (
        <div className="min-h-[400px] flex items-center justify-center p-6">
          <div className="glassmorphism-card p-8 max-w-lg w-full text-center">
            <AlertTriangle className="w-16 h-16 text-[#F59E0B] mx-auto mb-6" />
            
            <h2 className="text-2xl font-semibold text-white mb-4">
              {isTimeout ? 'Connection Timeout' : 'Something Went Wrong'}
            </h2>
            
            <p className="text-[#B8BCC8] mb-6">
              {isTimeout 
                ? 'The request took too long to complete. This might be due to a slow connection or server issues.'
                : 'An unexpected error occurred while loading this section.'
              }
            </p>

            {error && (
              <details className="mb-6 text-left">
                <summary className="text-sm text-[#F4D03F] cursor-pointer hover:text-[#F7DC6F] mb-2">
                  Technical Details
                </summary>
                <div className="bg-[rgba(244,208,63,0.1)] border border-[rgba(244,208,63,0.2)] rounded p-3 text-xs text-[#B8BCC8] font-mono">
                  <div className="mb-2">
                    <strong>Error:</strong> {error.name}
                  </div>
                  <div className="break-all">
                    <strong>Message:</strong> {error.message}
                  </div>
                </div>
              </details>
            )}

            <div className="space-y-3">
              <Button
                onClick={this.handleRetry}
                className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
              
              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  onClick={this.handleRefresh}
                  className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                >
                  Refresh Page
                </Button>
                
                <Button
                  variant="outline"
                  onClick={this.handleGoHome}
                  className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Home
                </Button>
              </div>
            </div>

            {isTimeout && (
              <div className="mt-6 p-4 bg-[rgba(59,130,246,0.1)] border border-[rgba(59,130,246,0.2)] rounded">
                <p className="text-sm text-[#3B82F6]">
                  💡 <strong>Tip:</strong> This will automatically retry in a few seconds, or you can try again manually.
                </p>
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}