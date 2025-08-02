import React from 'react';
import { RefreshCcw } from 'lucide-react';

/**
 * Specialized Error Boundary for Lazy-Loaded Components
 * Specifically handles ChunkLoadError and other dynamic import failures
 * Provides targeted fallback UI with retry functionality for component chunks
 */
class LazyComponentErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      isChunkError: false,
      isRetrying: false
    };
  }

  static getDerivedStateFromError(error) {
    // Check if this is a chunk loading error
    const isChunkError = error?.name === 'ChunkLoadError' || 
                        error?.message?.includes('Loading chunk') ||
                        error?.message?.includes('chunk.js failed');

    return { 
      hasError: true,
      isChunkError: isChunkError
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error with component-specific context
    console.error('LazyComponentErrorBoundary caught an error:', {
      error,
      errorInfo,
      componentName: this.props.componentName || 'Unknown',
      isChunkError: this.state.isChunkError
    });
    
    this.setState({ error });

    // Report chunk loading errors specifically
    if (this.state.isChunkError && window.reportError) {
      window.reportError(error, {
        errorType: 'ChunkLoadError',
        componentName: this.props.componentName,
        componentStack: errorInfo?.componentStack
      });
    }
  }

  handleRetry = async () => {
    this.setState({ isRetrying: true });
    
    // For chunk errors, we might need to force a page reload
    // as the chunk may be cached incorrectly
    if (this.state.isChunkError) {
      // Give user feedback that we're retrying
      setTimeout(() => {
        window.location.reload();
      }, 500);
    } else {
      // For other errors, try to reset the component
      setTimeout(() => {
        this.setState({ 
          hasError: false, 
          error: null, 
          isChunkError: false,
          isRetrying: false 
        });
      }, 500);
    }
  };

  render() {
    if (this.state.hasError) {
      const componentName = this.props.componentName || 'Component';
      
      return (
        <div className="min-h-[400px] bg-gray-900 flex items-center justify-center p-6">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full text-center border border-gray-700">
            <div className="w-12 h-12 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-yellow-400 text-2xl">⚠️</span>
            </div>
            
            <h3 className="text-lg font-semibold text-white mb-2">
              {componentName} Failed to Load
            </h3>
            
            {this.state.isChunkError ? (
              <p className="text-gray-300 mb-4 text-sm">
                The {componentName.toLowerCase()} component failed to load. This can happen due to network issues or updates to the application.
              </p>
            ) : (
              <p className="text-gray-300 mb-4 text-sm">
                There was an error loading the {componentName.toLowerCase()}. Please try again.
              </p>
            )}
            
            <div className="flex flex-col space-y-2">
              <button
                onClick={this.handleRetry}
                disabled={this.state.isRetrying}
                className="flex items-center justify-center space-x-2 bg-yellow-500 hover:bg-yellow-600 disabled:bg-yellow-600 text-black font-semibold px-4 py-2 rounded-lg transition-colors"
              >
                {this.state.isRetrying ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black"></div>
                    <span>Retrying...</span>
                  </>
                ) : (
                  <>
                    <RefreshCcw className="w-4 h-4" />
                    <span>Retry</span>
                  </>
                )}
              </button>
              
              <p className="text-xs text-gray-500 mt-2">
                {this.state.isChunkError 
                  ? "Retrying will reload the page to fetch the latest version"
                  : "If the problem persists, try refreshing the page"
                }
              </p>
            </div>

            {/* Development error details */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mt-4">
                <details className="bg-gray-900 rounded p-3 text-left">
                  <summary className="text-red-400 text-sm font-medium cursor-pointer">
                    Error Details (Development)
                  </summary>
                  <div className="mt-2 text-xs text-gray-400">
                    <div className="mb-2">
                      <strong>Component:</strong> {componentName}
                    </div>
                    <div className="mb-2">
                      <strong>Error Type:</strong> {this.state.isChunkError ? 'ChunkLoadError' : 'Generic Error'}
                    </div>
                    <div>
                      <strong>Error Message:</strong> {this.state.error?.message || 'Unknown error'}
                    </div>
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

export default LazyComponentErrorBoundary;