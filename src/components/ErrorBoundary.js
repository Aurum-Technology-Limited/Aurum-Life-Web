import React from 'react';

/**
 * Industry Standard Error Boundary Component
 * Follows React best practices for error handling
 * Provides proper error reporting and graceful fallbacks
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { 
      hasError: true,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error with proper context
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Update state with error details
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Report to error tracking service (if available)
    if (window.reportError) {
      window.reportError(error, {
        componentStack: errorInfo?.componentStack,
        errorBoundary: this.constructor.name
      });
    }
  }

  handleRetry = () => {
    // Reset error state to retry rendering
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null 
    });
  };

  render() {
    if (this.state.hasError) {
      // Render fallback UI
      return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
          <div className="bg-gray-800 rounded-lg p-6 max-w-lg w-full">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center mr-3">
                <span className="text-white text-sm font-bold">!</span>
              </div>
              <h2 className="text-xl font-semibold text-white">
                Something went wrong
              </h2>
            </div>
            
            <p className="text-gray-300 mb-4">
              We encountered an unexpected error. This has been logged and our team will investigate.
            </p>
            
            <div className="flex space-x-3 mb-4">
              <button
                onClick={this.handleRetry}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
              >
                Try Again
              </button>
              <button
                onClick={() => window.location.reload()}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded transition-colors"
              >
                Reload Page
              </button>
            </div>

            {/* Development error details */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mt-4">
                <details className="bg-gray-900 rounded p-3">
                  <summary className="text-red-400 text-sm font-medium cursor-pointer">
                    Error Details (Development Only)
                  </summary>
                  <div className="mt-2 text-xs text-gray-400">
                    <div className="mb-2">
                      <strong>Error ID:</strong> {this.state.errorId}
                    </div>
                    <div className="mb-2">
                      <strong>Error:</strong> {this.state.error?.toString()}
                    </div>
                    {this.state.errorInfo?.componentStack && (
                      <div>
                        <strong>Component Stack:</strong>
                        <pre className="text-xs mt-1 bg-gray-800 p-2 rounded overflow-auto max-h-40 whitespace-pre-wrap">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;