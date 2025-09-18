/**
 * Enhanced toast utility for consistent notifications throughout the app
 */

import { toast } from 'sonner@2.0.3';

// Toast styling configuration
const toastStyles = {
  success: {
    background: 'rgba(244, 208, 63, 0.1)',
    border: '1px solid rgba(244, 208, 63, 0.3)',
    color: '#F4D03F'
  },
  error: {
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    color: '#EF4444'
  },
  warning: {
    background: 'rgba(245, 158, 11, 0.1)',
    border: '1px solid rgba(245, 158, 11, 0.3)',
    color: '#F59E0B'
  },
  info: {
    background: 'rgba(59, 130, 246, 0.1)',
    border: '1px solid rgba(59, 130, 246, 0.3)',
    color: '#3B82F6'
  }
};

export interface ToastOptions {
  duration?: number;
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
  dismissible?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

/**
 * Show success toast
 */
export function showSuccess(message: string, options: ToastOptions = {}) {
  const { duration = 2000, ...otherOptions } = options;
  
  return toast.success(message, {
    duration,
    style: toastStyles.success,
    ...otherOptions
  });
}

/**
 * Show error toast
 */
export function showError(message: string, options: ToastOptions = {}) {
  const { duration = 4000, ...otherOptions } = options;
  
  return toast.error(message, {
    duration,
    style: toastStyles.error,
    ...otherOptions
  });
}

/**
 * Show warning toast
 */
export function showWarning(message: string, options: ToastOptions = {}) {
  const { duration = 3000, ...otherOptions } = options;
  
  return toast.warning(message, {
    duration,
    style: toastStyles.warning,
    ...otherOptions
  });
}

/**
 * Show info toast
 */
export function showInfo(message: string, options: ToastOptions = {}) {
  const { duration = 3000, ...otherOptions } = options;
  
  return toast(message, {
    duration,
    style: toastStyles.info,
    ...otherOptions
  });
}

/**
 * Show clipboard success toast
 */
export function showClipboardSuccess(message = 'Copied to clipboard!') {
  return showSuccess(message, { duration: 2000 });
}

/**
 * Show clipboard error toast
 */
export function showClipboardError(message = 'Copy failed - text selected for manual copy') {
  return showError(message, { duration: 4000 });
}

/**
 * Show loading toast
 */
export function showLoading(message: string, options: ToastOptions = {}) {
  return toast.loading(message, {
    style: toastStyles.info,
    ...options
  });
}

/**
 * Dismiss all toasts
 */
export function dismissAll() {
  toast.dismiss();
}

/**
 * Show toast with custom style
 */
export function showCustom(
  message: string,
  type: 'success' | 'error' | 'warning' | 'info' = 'info',
  options: ToastOptions = {}
) {
  const { duration = 3000, ...otherOptions } = options;
  
  return toast(message, {
    duration,
    style: toastStyles[type],
    ...otherOptions
  });
}

/**
 * Auth-specific toasts
 */
export const authToasts = {
  loginSuccess: () => showSuccess('Welcome back!'),
  loginError: (error: string) => showError(`Login failed: ${error}`),
  signupSuccess: () => showSuccess('Account created successfully!'),
  signupError: (error: string) => showError(`Signup failed: ${error}`),
  demoLoginSuccess: () => showSuccess('Demo account loaded!'),
  demoLoginError: (error: string) => showError(`Demo login failed: ${error}`),
  logoutSuccess: () => showInfo('You have been logged out'),
  sessionExpired: () => showWarning('Your session has expired. Please sign in again.')
};

/**
 * Data operation toasts
 */
export const dataToasts = {
  saveSuccess: (item = 'Item') => showSuccess(`${item} saved successfully!`),
  saveError: (item = 'Item') => showError(`Failed to save ${item.toLowerCase()}`),
  deleteSuccess: (item = 'Item') => showSuccess(`${item} deleted successfully!`),
  deleteError: (item = 'Item') => showError(`Failed to delete ${item.toLowerCase()}`),
  updateSuccess: (item = 'Item') => showSuccess(`${item} updated successfully!`),
  updateError: (item = 'Item') => showError(`Failed to update ${item.toLowerCase()}`),
  loadError: (item = 'Data') => showError(`Failed to load ${item.toLowerCase()}`)
};

/**
 * Network-specific toasts
 */
export const networkToasts = {
  offline: () => showWarning('You are offline. Some features may not work.'),
  online: () => showInfo('Connection restored'),
  syncSuccess: () => showSuccess('Data synced successfully!'),
  syncError: () => showError('Sync failed - please try again'),
  uploadSuccess: (item = 'File') => showSuccess(`${item} uploaded successfully!`),
  uploadError: (item = 'File') => showError(`Failed to upload ${item.toLowerCase()}`)
};

export default {
  success: showSuccess,
  error: showError,
  warning: showWarning,
  info: showInfo,
  loading: showLoading,
  custom: showCustom,
  dismissAll,
  clipboard: {
    success: showClipboardSuccess,
    error: showClipboardError
  },
  auth: authToasts,
  data: dataToasts,
  network: networkToasts
};