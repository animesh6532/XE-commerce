import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, type LoginPayload, type RegisterPayload, type UserResponse } from '../services/auth';

export type Role = 'admin' | 'seller' | 'customer' | string;

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  role: Role;
}

interface AuthContextValue {
  user: AuthUser | null;
  role: Role | null;
  isAuthenticated: boolean;
  isAuthLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshMe: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = 'jwt_token';

function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function setToken(token: string | null) {
  try {
    if (!token) localStorage.removeItem(TOKEN_KEY);
    else localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // ignore
  }
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  const refreshMe = useCallback(async () => {
    const token = getToken();
    if (!token) {
      setUser(null);
      return;
    }
    const me = await authService.me();
    setUser(me);
  }, []);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const token = getToken();
        if (!token) {
          if (mounted) {
            setUser(null);
            setIsAuthLoading(false);
          }
          return;
        }
        const me = await authService.me();
        if (mounted) setUser(me);
      } catch {
        setToken(null);
        if (mounted) setUser(null);
      } finally {
        if (mounted) setIsAuthLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const login = useCallback(
    async (payload: LoginPayload) => {
      setIsAuthLoading(true);
      try {
        const token = await authService.login(payload);
        setToken(token);
        const me = await authService.me();
        setUser(me);
        
        // Redirect based on role
        if (me.role === 'admin') {
          navigate('/admin');
        } else if (me.role === 'seller') {
          navigate('/dashboard');
        } else {
          navigate('/products');
        }
      } catch (err) {
        setToken(null);
        setUser(null);
        throw err;
      } finally {
        setIsAuthLoading(false);
      }
    },
    [navigate]
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      setIsAuthLoading(true);
      try {
        // 1. Call Register
        await authService.register(payload);
        // 2. Perform Auto-login to obtain access token
        const token = await authService.login({ email: payload.email, password: payload.password });
        setToken(token);
        // 3. Fetch user profile
        const me = await authService.me();
        setUser(me);
        navigate('/products');
      } catch (err) {
        setToken(null);
        setUser(null);
        throw err;
      } finally {
        setIsAuthLoading(false);
      }
    },
    [navigate]
  );

  const logout = useCallback(async () => {
    setIsAuthLoading(true);
    try {
      await authService.logout();
    } finally {
      setToken(null);
      setUser(null);
      setIsAuthLoading(false);
      navigate('/');
    }
  }, [navigate]);

  const value: AuthContextValue = useMemo(
    () => ({
      user,
      role: user?.role ?? null,
      isAuthenticated: !!user,
      isAuthLoading,
      login,
      register,
      logout,
      refreshMe,
    }),
    [user, isAuthLoading, login, register, logout, refreshMe]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
