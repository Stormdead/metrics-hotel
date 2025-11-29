import { api } from './api';
import type { DashboardMetrics } from '../types';

interface OccupancyData {
  fecha: string;
  total_habitaciones: number;
  ocupadas: number;
  disponibles: number;
  tasa_ocupacion: number;
}

interface IncomeData {
  fecha: string;
  ingresos: number;
}

interface PopularRoom {
  room_type_id: number;
  nombre_tipo: string;
  total_reservas: number;
  ingresos_totales: number;
}

interface FrequentClient {
  user_id: number;
  nombre_completo: string;
  email: string;
  total_reservas: number;
  total_gastado: number;
}

export const metricsService = {
  async getDashboard(fechaInicio?: string, fechaFin?: string) {
    const response = await api.get<DashboardMetrics>('/metrics/dashboard', {
      params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin },
    });
    return response. data;
  },

  async getDailyOccupancy(fecha: string) {
    const response = await api.get<OccupancyData>('/metrics/occupancy/daily', {
      params: { fecha },
    });
    return response.data;
  },

  async getHistoricalOccupancy(fechaInicio: string, fechaFin: string) {
    const response = await api.get<OccupancyData[]>('/metrics/occupancy/historical', {
      params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin },
    });
    return response. data;
  },

  async getDailyIncome(fecha: string) {
    const response = await api.get<{ fecha: string; ingresos: number }>(
      '/metrics/income/daily',
      { params: { fecha } }
    );
    return response.data;
  },

  async getMonthlyIncome(anio: number, mes: number) {
    const response = await api.get<IncomeData[]>('/metrics/income/monthly', {
      params: { anio, mes },
    });
    return response.data;
  },

  async getPopularRooms(fechaInicio?: string, fechaFin?: string, limit: number = 5) {
    const response = await api.get<PopularRoom[]>('/metrics/popular-rooms', {
      params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin, limit },
    });
    return response.data;
  },

  async getFrequentClients(fechaInicio?: string, fechaFin?: string, limit: number = 10) {
    const response = await api.get<FrequentClient[]>('/metrics/frequent-clients', {
      params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin, limit },
    });
    return response.data;
  },
};