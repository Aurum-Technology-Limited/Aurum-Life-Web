import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class SimpleErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by ErrorBoundary:', error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-[#0B0D14] flex items-center justify-center p-4">
          <div className="glassmorphism-card border-0 max-w-lg w-full p-8 text-center">
            <AlertTriangle className="w-12 h-12 text-[#F59E0B] mx-auto mb-4" />
            <h2 className="text-white text-xl mb-2">Something went wrong</h2>
            <p className="text-[#B8BCC8] mb-6">
              We apologize for the inconvenience. An unexpected error occurred.
            </p>
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] rounded-lg p-4 mb-6 text-left">
                <h4 className="text-[#EF4444] font-medium mb-2">Error Details:</h4>
                <p className="text-sm text-[#B8BCC8] font-mono break-all">
                  {this.state.error.message}
                </p>
              </div>
            )}
            
            <div className="flex flex-col sm:flex-row gap-3">
              <button 
                onClick={this.handleReset}
                className="flex-1 bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] px-4 py-2 rounded-lg flex items-center justify-center transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </button>
              <button 
                onClick={() => window.location.reload()}
                className="flex-1 border border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)] px-4 py-2 rounded-lg transition-colors"
              >
                Reload Page
              </button>
            </div>
            
            <p className="text-xs text-[#6B7280] mt-4">
              If this problem persists, please contact support.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}