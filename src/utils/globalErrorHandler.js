/**
 * Global Error Handler for Aurum Life Application
 * Provides centralized error handling and user-friendly error messages
 */

class GlobalErrorHandler {
  constructor() {
    this.errorQueue = [];
    this.isHandlingErrors = false;
    this.setupGlobalHandlers();
  }

  setupGlobalHandlers() {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled promise rejection:', event.reason);
      
      if (this.isApiError(event.reason)) {
        event.preventDefault(); // Prevent default browser error handling
        this.handleApiError(event.reason);
      }
    });

    // Handle general JavaScript errors
    window.addEventListener('error', (event) => {
      console.error('Global error:', event.error);
      
      if (this.isApiError(event.error)) {
        this.handleApiError(event.error);
      }
    });
  }

  isApiError(error) {
    return (
      error?.message?.includes('Request timed out') ||
      error?.message?.includes('timeout') ||
      error?.message?.includes('Network Error') ||
      error?.code === 'ECONNABORTED' ||
      error?.response?.status >= 500
    );
  }

  handleApiError(error) {
    const errorInfo = {
      type: 'API_ERROR',
      message: this.getUserFriendlyMessage(error),
      timestamp: new Date().toISOString(),
      originalError: error
    };

    // Add to queue to prevent spam
    this.errorQueue.push(errorInfo);
    
    if (!this.isHandlingErrors) {
      this.processErrorQueue();
    }
  }

  getUserFriendlyMessage(error) {
    if (error?.message?.includes('timeout')) {
      return 'The request is taking longer than expected. The app will continue to work with available data.';
    }
    
    if (error?.response?.status >= 500) {
      return 'Server temporarily unavailable. Please try again in a few moments.';
    }
    
    if (error?.message?.includes('Network Error')) {
      return 'Network connection issue. Please check your internet connection.';
    }
    
    return 'Something went wrong, but the app will continue working with available data.';
  }

  async processErrorQueue() {
    this.isHandlingErrors = true;
    
    while (this.errorQueue.length > 0) {
      const errorInfo = this.errorQueue.shift();
      
      // Show user-friendly notification (if notification system is available)
      this.showUserNotification(errorInfo);
      
      // Small delay to prevent overwhelming the user
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    this.isHandlingErrors = false;
  }

  showUserNotification(errorInfo) {
    // Check if notification system is available
    if (window.showNotification) {
      window.showNotification({
        type: 'warning',
        title: 'Connection Issue',
        message: errorInfo.message,
        duration: 5000
      });
    } else {
      // Fallback to console warning for development
      console.warn('🚨 User notification:', errorInfo.message);
    }
  }

  // Method to manually report errors from components
  reportError(error, context = '') {
    console.error(`Error in ${context}:`, error);
    
    if (this.isApiError(error)) {
      this.handleApiError(error);
    }
  }
}

// Create global instance
const globalErrorHandler = new GlobalErrorHandler();

// Export for manual error reporting
export default globalErrorHandler;

// Make it available globally for components that need it
window.globalErrorHandler = globalErrorHandler;