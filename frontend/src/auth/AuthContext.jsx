import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

function safeJsonParse(value) {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function decodeJwtPayload(token) {
  if (!token) return null;
  const parts = token.split('.');
  if (parts.length !== 3) return null;

  try {
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
    const json = atob(padded);
    return JSON.parse(json);
  } catch {
    return null;
  }
}

function isTokenExpired(token, nowMs = Date.now()) {
  const payload = decodeJwtPayload(token);
  if (!payload?.exp) return false;
  return nowMs >= payload.exp * 1000;
}

function willExpireSoon(token, windowMs = 2 * 60 * 1000, nowMs = Date.now()) {
  const payload = decodeJwtPayload(token);
  if (!payload?.exp) return false;
  return payload.exp * 1000 - nowMs <= windowMs;
}

const STORAGE_KEYS = {
  token: 'token',
  user: 'user',
  biometricUpdatedAt: 'biometric_updated_at'
};

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(STORAGE_KEYS.token) || '');
  const [user, setUser] = useState(() => safeJsonParse(localStorage.getItem(STORAGE_KEYS.user)) || null);
  const [biometricUpdatedAt, setBiometricUpdatedAt] = useState(
    () => localStorage.getItem(STORAGE_KEYS.biometricUpdatedAt) || ''
  );
  const [status, setStatus] = useState('idle'); // idle | authenticating | ready
  const [authError, setAuthError] = useState('');
  const refreshAttemptedRef = useRef(false);

  useEffect(() => {
    api.setAccessToken(token || '');
    if (token) localStorage.setItem(STORAGE_KEYS.token, token);
    else localStorage.removeItem(STORAGE_KEYS.token);
  }, [token]);

  useEffect(() => {
    if (user) localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user));
    else localStorage.removeItem(STORAGE_KEYS.user);
  }, [user]);

  const logout = useCallback(() => {
    setToken('');
    setUser(null);
    setAuthError('');
    refreshAttemptedRef.current = false;
  }, []);

  const loadUser = useCallback(async () => {
    if (!token) return null;
    const resp = await api.getUser(token);
    if (resp?.success) {
      setUser(resp.data);
      return resp.data;
    }
    return null;
  }, [token]);

  // Best-effort “auto refresh”: if backend doesn’t support it, we degrade gracefully.
  const tryRefreshToken = useCallback(async () => {
    if (!token) return false;
    if (refreshAttemptedRef.current) return false;
    refreshAttemptedRef.current = true;

    try {
      const resp = await api.refreshToken(token);
      if (resp?.success && resp?.token) {
        setToken(resp.token);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }, [token]);

  useEffect(() => {
    let cancelled = false;

    async function boot() {
      setStatus('authenticating');
      setAuthError('');

      if (!token) {
        setStatus('ready');
        return;
      }

      if (isTokenExpired(token)) {
        logout();
        setStatus('ready');
        return;
      }

      if (willExpireSoon(token)) {
        await tryRefreshToken();
      }

      try {
        await loadUser();
      } catch (e) {
        if (!cancelled) {
          setAuthError(e?.message || 'Failed to load user session.');
        }
      } finally {
        if (!cancelled) setStatus('ready');
      }
    }

    boot();
    return () => {
      cancelled = true;
    };
  }, [token, loadUser, logout, tryRefreshToken]);

  const login = useCallback(async ({ username, password, face_image, fingerprint_data }) => {
    setAuthError('');
    setStatus('authenticating');
    try {
      const resp = await api.login({ username, password, face_image, fingerprint_data });
      if (resp?.success) {
        setToken(resp.token || '');
        setUser(resp.data || null);
      }
      return resp;
    } catch (e) {
      setAuthError(e?.message || 'Login failed.');
      return { success: false, message: e?.message || 'Login failed.' };
    } finally {
      setStatus('ready');
    }
  }, []);

  const register = useCallback(async ({ username, email, password, face_image, fingerprint_data }) => {
    setAuthError('');
    setStatus('authenticating');
    try {
      const resp = await api.register({ username, email, password, face_image, fingerprint_data });
      if (resp?.success) {
        setToken(resp.token || '');
        setUser(resp.data || null);
      }
      return resp;
    } catch (e) {
      setAuthError(e?.message || 'Registration failed.');
      return { success: false, message: e?.message || 'Registration failed.' };
    } finally {
      setStatus('ready');
    }
  }, []);

  const markBiometricUpdated = useCallback(() => {
    const ts = new Date().toISOString();
    localStorage.setItem(STORAGE_KEYS.biometricUpdatedAt, ts);
    setBiometricUpdatedAt(ts);
  }, []);

  const value = useMemo(() => ({
    token,
    user,
    status,
    authError,
    isAuthenticated: Boolean(token) && !isTokenExpired(token),
    decodeJwtPayload: () => decodeJwtPayload(token),
    login,
    register,
    loadUser,
    logout,
    biometricUpdatedAt,
    markBiometricUpdated
  }), [token, user, status, authError, login, register, loadUser, logout, biometricUpdatedAt, markBiometricUpdated]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

