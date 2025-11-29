import { api } from './api';
import type { Booking } from '../types';

export const bookingsService = {
  async getBookings(params?: { 
    estado?: string; 
    user_id?: number;
    fecha_inicio?: string;
    fecha_fin?: string;
  }) {
    const response = await api.get<Booking[]>('/bookings', { params });
    return response.data;
  },

  async getBooking(id: number) {
    const response = await api.get<Booking>(`/bookings/${id}`);
    return response.data;
  },

  async createBooking(data: {
    room_id: number;
    check_in: string;
    check_out: string;
    metodo_pago: string;
    notas_especiales?: string;
  }) {
    const response = await api. post<Booking>('/bookings', data);
    return response. data;
  },

  async checkAvailability(roomId: number, checkIn: string, checkOut: string) {
    const response = await api.post<{ disponible: boolean; mensaje: string }>(
      '/bookings/check-availability',
      {
        room_id: roomId,
        check_in: checkIn,
        check_out: checkOut,
      }
    );
    return response.data;
  },

  async checkIn(id: number) {
    const response = await api.post<Booking>(`/bookings/${id}/check-in`);
    return response. data;
  },

  async checkOut(id: number, data?: {
    precio_servicios_extra?: number;
    monto_pagado?: number;
  }) {
    const response = await api.post<Booking>(`/bookings/${id}/check-out`, data);
    return response.data;
  },

  async cancelBooking(id: number) {
    const response = await api. post<Booking>(`/bookings/${id}/cancel`);
    return response.data;
  },
};