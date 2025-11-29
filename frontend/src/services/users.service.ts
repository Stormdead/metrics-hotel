import { api } from './api';
import type { User } from '../types';

export const usersService = {
  async getUsers(params?: { role?: string; activo?: boolean }) {
    const response = await api.get<User[]>('/users', { params });
    return response.data;
  },

  async getUser(id: number) {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },

  async createUser(data: {
    email: string;
    password: string;
    nombre_completo: string;
    rut: string;
    role: 'admin' | 'trabajador';
    edad?: number;
    telefono?: string;
    direccion?: string;
  }) {
    const response = await api.post<User>('/users', data);
    return response. data;
  },

  async deactivateUser(id: number) {
    const response = await api.post<User>(`/users/${id}/deactivate`);
    return response.data;
  },

  async activateUser(id: number) {
    const response = await api.post<User>(`/users/${id}/activate`);
    return response. data;
  },
};