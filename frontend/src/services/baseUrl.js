// Central helper to resolve backend base URL at runtime safely.
// Priority: env var -> sane host -> fallback to window.origin.

export function getBackendBaseUrl() {
  try {
    // Try multiple ways to get the environment variable
    const envUrl = process.env.REACT_APP_BACKEND_URL || 
                   (typeof window !== 'undefined' && window.process?.env?.REACT_APP_BACKEND_URL) ||
                   (typeof import.meta !== 'undefined' && import.meta.env?.REACT_APP_BACKEND_URL);
    
    console.log('🔧 BaseURL Debug - envUrl:', envUrl);
    console.log('🔧 BaseURL Debug - process.env.REACT_APP_BACKEND_URL:', process.env.REACT_APP_BACKEND_URL);
    console.log('🔧 BaseURL Debug - window.location.origin:', typeof window !== 'undefined' ? window.location.origin : 'not available');
    
    if (envUrl) {
      try {
        const u = new URL(envUrl);
        const badHost = /^(none|home|www)\.preview\.emergentagent\.com$/i.test(u.host);
        if (!badHost) {
          const finalUrl = envUrl.replace(/\/$/, '');
          console.log('✅ BaseURL resolved from env:', finalUrl);
          return finalUrl;
        }
      } catch (_) {
        console.log('❌ BaseURL env parse error:', _);
        // ignore parse errors, fall through to fallback
      }
    }
    
    // Fallback to window.origin but ensure it's the same domain as expected
    if (typeof window !== 'undefined' && window.location && window.location.origin) {
      const origin = window.location.origin.replace(/\/$/, '');
      console.log('⚠️ BaseURL using window.origin fallback:', origin);
      return origin;
    }
  } catch (e) {
    console.log('❌ BaseURL error:', e);
  }
  
  // Last resort hardcoded fallback
  const fallback = 'https://prodflow-auth.preview.emergentagent.com';
  console.log('🚨 BaseURL using hardcoded fallback:', fallback);
  return fallback;
}