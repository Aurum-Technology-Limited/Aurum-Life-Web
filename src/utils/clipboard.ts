/**
 * Comprehensive clipboard utility with multiple fallback strategies
 * for environments where Clipboard API may be blocked
 */

export interface ClipboardResult {
  success: boolean;
  method: 'clipboard-api' | 'exec-command' | 'selection' | 'manual' | 'failed';
  message: string;
}

export interface ClipboardOptions {
  showToast?: boolean;
  fallbackMessage?: string;
  timeout?: number;
}

/**
 * Multi-layered clipboard copy with comprehensive fallbacks
 */
export async function copyToClipboard(
  text: string, 
  options: ClipboardOptions = {}
): Promise<ClipboardResult> {
  const { 
    showToast = true, 
    fallbackMessage = 'Copy this text manually:',
    timeout = 2000 
  } = options;

  // Method 1: Modern Clipboard API
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return {
        success: true,
        method: 'clipboard-api',
        message: 'Copied to clipboard!'
      };
    }
  } catch (error) {
    console.log('Clipboard API failed:', error);
  }

  // Method 2: Legacy execCommand with temporary textarea
  try {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    textArea.style.top = '-9999px';
    textArea.style.opacity = '0';
    textArea.style.pointerEvents = 'none';
    textArea.setAttribute('readonly', 'readonly');
    
    document.body.appendChild(textArea);
    textArea.select();
    textArea.setSelectionRange(0, text.length);
    
    const successful = document.execCommand('copy');
    document.body.removeChild(textArea);
    
    if (successful) {
      return {
        success: true,
        method: 'exec-command',
        message: 'Copied to clipboard!'
      };
    }
  } catch (error) {
    console.log('execCommand failed:', error);
  }

  // Method 3: Manual selection fallback
  try {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'absolute';
    textArea.style.left = '50%';
    textArea.style.top = '50%';
    textArea.style.transform = 'translate(-50%, -50%)';
    textArea.style.width = '300px';
    textArea.style.height = '100px';
    textArea.style.zIndex = '10000';
    textArea.style.backgroundColor = '#1A1D29';
    textArea.style.color = '#F4D03F';
    textArea.style.border = '2px solid #F4D03F';
    textArea.style.borderRadius = '8px';
    textArea.style.padding = '12px';
    textArea.style.fontSize = '14px';
    textArea.setAttribute('readonly', 'readonly');
    
    document.body.appendChild(textArea);
    textArea.select();
    textArea.setSelectionRange(0, text.length);
    
    // Auto-remove after timeout
    setTimeout(() => {
      if (document.body.contains(textArea)) {
        document.body.removeChild(textArea);
      }
    }, timeout);
    
    return {
      success: true,
      method: 'selection',
      message: 'Text selected - press Ctrl+C (Cmd+C on Mac) to copy'
    };
  } catch (error) {
    console.log('Selection method failed:', error);
  }

  // Method 4: Manual copy instructions
  return {
    success: false,
    method: 'manual',
    message: `${fallbackMessage} ${text}`
  };
}

/**
 * Copy text with visual feedback
 */
export async function copyWithFeedback(
  text: string,
  onSuccess?: (result: ClipboardResult) => void,
  onError?: (result: ClipboardResult) => void,
  options: ClipboardOptions = {}
): Promise<ClipboardResult> {
  const result = await copyToClipboard(text, options);
  
  if (result.success) {
    onSuccess?.(result);
  } else {
    onError?.(result);
  }
  
  return result;
}

/**
 * Check if clipboard functionality is available
 */
export function isClipboardAvailable(): boolean {
  return !!(
    (navigator.clipboard && navigator.clipboard.writeText) ||
    document.execCommand
  );
}

/**
 * Get clipboard permissions status
 */
export async function getClipboardPermission(): Promise<'granted' | 'denied' | 'prompt' | 'unsupported'> {
  try {
    if (navigator.permissions && navigator.permissions.query) {
      const permission = await navigator.permissions.query({ name: 'clipboard-write' as PermissionName });
      return permission.state;
    }
  } catch (error) {
    console.log('Permission query failed:', error);
  }
  
  return isClipboardAvailable() ? 'granted' : 'unsupported';
}

/**
 * Enhanced copy function with automatic toast notifications
 */
export async function smartCopy(
  text: string,
  successMessage = 'Copied to clipboard!',
  errorMessage = 'Copy failed - text selected for manual copy'
): Promise<ClipboardResult> {
  const result = await copyToClipboard(text, { showToast: true });
  
  // Dynamic import to avoid circular dependencies
  try {
    const { showClipboardSuccess, showClipboardError } = await import('./toast');
    
    if (result.success) {
      showClipboardSuccess(successMessage);
    } else {
      showClipboardError(errorMessage);
    }
  } catch (toastError) {
    console.log('Toast notification failed:', toastError);
  }
  
  return result;
}

/**
 * Copy demo credentials helper
 */
export async function copyDemoCredentials(): Promise<ClipboardResult> {
  const credentials = 'Email: demo@aurumlife.com\nPassword: demo123';
  
  return smartCopy(
    credentials,
    'Demo credentials copied!',
    'Demo credentials selected - press Ctrl+C to copy'
  );
}

/**
 * Copy formatted text helper
 */
export async function copyFormattedText(
  title: string,
  content: string,
  separator = '\n\n'
): Promise<ClipboardResult> {
  const formattedText = `${title}${separator}${content}`;
  
  return smartCopy(
    formattedText,
    `${title} copied!`,
    `${title} selected for manual copy`
  );
}