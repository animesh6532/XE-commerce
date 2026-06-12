import { api } from './api';

export type Role = 'admin' | 'seller' | 'customer' | string;

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  role: Role;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface VerifyTokenResponse {
  valid: boolean;
  user_id: number;
  email: string;
  role: Role;
}

const TOKEN_KEY = 'jwt_token';

function persistToken(token: string) {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // ignore
  }
}

export const authService = {
  async register(payload: RegisterPayload): Promise<UserResponse> {
    const res = await api.post<UserResponse>('/api/auth/register', payload);
    return res.data;
  },

  async login(payload: LoginPayload): Promise<string> {
    const res = await api.post<TokenResponse>('/api/auth/login', payload);
    persistToken(res.data.access_token);
    return res.data.access_token;
  },

  async me(): Promise<UserResponse> {
    const res = await api.get<UserResponse>('/api/auth/me');
    return res.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/api/auth/logout');
    } finally {
      try {
        localStorage.removeItem(TOKEN_KEY);
      } catch {
        // ignore
      }
    }
  },

  async verifyToken(): Promise<VerifyTokenResponse> {
    const res = await api.get<VerifyTokenResponse>('/api/auth/verify-token');
    return res.data;
  },

  async getAdminMessage(): Promise<{ message: string }> {
    const res = await api.get<{ message: string }>('/api/auth/admin');
    return res.data;
  },

  async getSellerMessage(): Promise<{ message: string }> {
    const res = await api.get<{ message: string }>('/api/auth/seller');
    return res.data;
  }
};
