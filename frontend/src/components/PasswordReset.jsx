import React, { useEffect, useMemo, useState } from 'react';
import { getBackendBaseUrl } from '../services/baseUrl';

const BACKEND_URL = getBackendBaseUrl();

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
    if (!pwd || pwd.length < 8) return 'Password must be at least 8 characters long';
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
    <div className="min-h-screen bg-[#0B0D14] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center mb-6">
          <div className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold text-xl">
            AL
          </div>
        </div>
        <h2 className="text-center text-3xl font-extrabold text-white">
          Reset your password
        </h2>
        <p className="mt-2 text-center text-sm text-gray-400">
          Enter a new password for your account
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-gray-800 py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 p-3 bg-red-900 border border-red-700 text-red-300 rounded">{error}</div>
          )}
          {message && (
            <div className="mb-4 p-3 bg-green-900 border border-green-700 text-green-300 rounded">{message}</div>
          )}

          {!token && (
            <div className="mb-4 p-3 bg-blue-900 border border-blue-700 text-blue-200 rounded">
              We couldn't find a reset token in your link. Please navigate from the latest password reset email.
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-gray-300">New Password</label>
              <input
                id="newPassword"
                name="newPassword"
                type="password"
                autoComplete="new-password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                placeholder="Enter new password"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300">Confirm Password</label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                placeholder="Re-enter new password"
              />
            </div>

            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => { window.location.href = '/'; }}
                className="text-sm text-gray-300 hover:text-gray-200"
              >
                Back to login
              </button>

              <button
                type="submit"
                disabled={submitting || !token}
                className="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-black bg-yellow-500 hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'Updating...' : 'Update password'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PasswordReset;