// Central helper to resolve backend base URL at runtime safely.
// Priority: env var -> sane host -> fallback to window.origin.

export function getBackendBaseUrl() {
  try {
    const envUrl = (typeof process !== 'undefined' && process.env && process.env.REACT_APP_BACKEND_URL) ? process.env.REACT_APP_BACKEND_URL : '';
    if (envUrl) {
      try {
        const u = new URL(envUrl);
        const badHost = /^(none|home|www)\.preview\.emergentagent\.com$/i.test(u.host);
        if (!badHost) {
          return envUrl.replace(/\/$/, '');
        }
      } catch (_) {
        // ignore parse errors, fall through to fallback
      }
    }
    if (typeof window !== 'undefined' && window.location && window.location.origin) {
      return window.location.origin.replace(/\/$/, '');
    }
  } catch (_) {}
  return '';
}