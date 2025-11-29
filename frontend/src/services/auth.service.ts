import { api } from './api';
import type { LoginCredentials, RegisterData, AuthResponse, User } from '../types';

export const authService = {
  // Login
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON. stringify(response.data.user));
    }
    return response.data;
  },

  // Registro
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', data);
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON. stringify(response.data.user));
    }
    return response. data;
  },

  // Obtener usuario actual
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    localStorage.setItem('user', JSON. stringify(response.data));
    return response.data;
  },

  // Cambiar contraseña
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  // Logout
  logout() {
    localStorage.removeItem('access_token');
    localStorage. removeItem('user');
    window.location.href = '/login';
  },

  // Verificar si está autenticado
  isAuthenticated(): boolean {
    return !! localStorage.getItem('access_token');
  },

  // Obtener usuario del localStorage
  getUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON. parse(userStr) : null;
  },
};