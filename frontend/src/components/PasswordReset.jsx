import React, { useEffect, useMemo, useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

function parseHashParams(hash) {
  const res = {};
  if (!hash) return res;
  const h = hash.startsWith('#') ? hash.slice(1) : hash;
  const parts = h.split('&');
  for (const p of parts) {
    const [k, v] = p.split('=');
    if (k) res[decodeURIComponent(k)] = decodeURIComponent(v || '');
  }
  return res;
}

function parseQueryParams(search) {
  const params = new URLSearchParams(search || '');
  const res = {};
  for (const [k, v] of params.entries()) res[k] = v;
  return res;
}

const PasswordReset = () => {
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const info = useMemo(() => {
    const hashParams = parseHashParams(window.location.hash || '');
    const queryParams = parseQueryParams(window.location.search || '');

    // Prefer access_token if present, else fallback to token
    const accessToken = hashParams.access_token || queryParams.access_token || queryParams.token || '';
    const type = hashParams.type || queryParams.type || '';

    return { accessToken, type, hashParams, queryParams };
  }, []);

  useEffect(() => {
    if (info.accessToken) {
      setToken(info.accessToken);
    }
  }, [info]);

  const validatePassword = (pwd) => {
    if (!pwd || pwd.length &lt; 8) return 'Password must be at least 8 characters long';
    if (!/[A-Z]/.test(pwd)) return 'Password must include at least one uppercase letter';
    if (!/[0-9]/.test(pwd)) return 'Password must include at least one number';
    return '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!token) {
      setError('Missing or invalid reset token. Please use the password reset link from your email.');
      return;
    }

    const validation = validatePassword(newPassword);
    if (validation) {
      setError(validation);
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setSubmitting(true);
    try {
      const resp = await fetch(`${BACKEND_URL}/api/auth/update-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ new_password: newPassword })
      });
      if (resp.ok) {
        setMessage('Password updated successfully. Redirecting to login...');
        setTimeout(() => {
          // Do not persist the reset token; simply send user to login
          window.location.href = '/';
        }, 1600);
      } else {
        const data = await (async () => { try { return await resp.json(); } catch { return {}; } })();
        setError(data?.detail || 'Failed to update password. Your link may have expired. Try requesting a new reset email.');
      }
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    &lt;div className="min-h-screen bg-[#0B0D14] flex flex-col justify-center py-12 sm:px-6 lg:px-8"&gt;
      &lt;div className="sm:mx-auto sm:w-full sm:max-w-md"&gt;
        &lt;div className="flex justify-center mb-6"&gt;
          &lt;div className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold text-xl"&gt;
            AL
          &lt;/div&gt;
        &lt;/div&gt;
        &lt;h2 className="text-center text-3xl font-extrabold text-white"&gt;
          Reset your password
        &lt;/h2&gt;
        &lt;p className="mt-2 text-center text-sm text-gray-400"&gt;
          Enter a new password for your account
        &lt;/p&gt;
      &lt;/div&gt;

      &lt;div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md"&gt;
        &lt;div className="bg-gray-800 py-8 px-4 shadow sm:rounded-lg sm:px-10"&gt;
          {error &amp;&amp; (
            &lt;div className="mb-4 p-3 bg-red-900 border border-red-700 text-red-300 rounded"&gt;{error}&lt;/div&gt;
          )}
          {message &amp;&amp; (
            &lt;div className="mb-4 p-3 bg-green-900 border border-green-700 text-green-300 rounded"&gt;{message}&lt;/div&gt;
          )}

          {!token &amp;&amp; (
            &lt;div className="mb-4 p-3 bg-blue-900 border border-blue-700 text-blue-200 rounded"&gt;
              We couldn't find a reset token in your link. Please navigate from the latest password reset email.
            &lt;/div&gt;
          )}

          &lt;form className="space-y-6" onSubmit={handleSubmit}&gt;
            &lt;div&gt;
              &lt;label htmlFor="newPassword" className="block text-sm font-medium text-gray-300"&gt;New Password&lt;/label&gt;
              &lt;input
                id="newPassword"
                name="newPassword"
                type="password"
                autoComplete="new-password"
                required
                value={newPassword}
                onChange={(e) =&gt; setNewPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                placeholder="Enter new password"
              /&gt;
            &lt;/div&gt;

            &lt;div&gt;
              &lt;label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300"&gt;Confirm Password&lt;/label&gt;
              &lt;input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                value={confirmPassword}
                onChange={(e) =&gt; setConfirmPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                placeholder="Re-enter new password"
              /&gt;
            &lt;/div&gt;

            &lt;div className="flex items-center justify-between"&gt;
              &lt;button
                type="button"
                onClick={() =&gt; { window.location.href = '/'; }}
                className="text-sm text-gray-300 hover:text-gray-200"
              &gt;
                Back to login
              &lt;/button&gt;

              &lt;button
                type="submit"
                disabled={submitting || !token}
                className="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-black bg-yellow-500 hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed"
              &gt;
                {submitting ? 'Updating...' : 'Update password'}
              &lt;/button&gt;
            &lt;/div&gt;
          &lt;/form&gt;
        &lt;/div&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  );
};

export default PasswordReset;