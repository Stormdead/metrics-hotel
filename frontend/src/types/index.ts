// Tipos de Usuario
export interface User {
  id: number;
  email: string;
  role: 'admin' | 'trabajador' | 'cliente';
  nombre_completo: string;
  rut: string;
  edad?: number;
  telefono?: string;
  direccion?: string;
  activo: boolean;
  debe_cambiar_password: boolean;
  fecha_creacion: string;
  ultima_conexion?: string;
}

// Tipos de Autenticación
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  nombre_completo: string;
  rut: string;
  edad?: number;
  telefono?: string;
  direccion?: string;
}

export interface AuthResponse {
  access_token: string;
  user: User;
  message: string;
  debe_cambiar_password?: boolean;
}

// Tipos de Habitación
export interface RoomType {
  id: number;
  nombre: string;
  descripcion?: string;
  capacidad_personas: number;
  precio_base: number;
  amenidades: string[];
  imagenes: string[];
  activo: boolean;
}

export interface Room {
  id: number;
  room_type_id: number;
  numero_habitacion: string;
  piso?: number;
  estado: 'disponible' | 'ocupada' | 'limpieza' | 'mantenimiento';
  activo: boolean;
  room_type?: RoomType;
}

// Tipos de Reserva
export interface Booking {
  id: number;
  user_id: number;
  room_id: number;
  check_in: string;
  check_out: string;
  noches: number;
  precio_por_noche: number;
  precio_servicios_extra: number;
  precio_total: number;
  estado: 'pendiente' | 'confirmada' | 'check_in_realizado' | 'check_out_realizado' | 'cancelada';
  metodo_pago: string;
  pagado: boolean;
  monto_pagado: number;
  notas_especiales?: string;
  fecha_reserva: string;
  user?: User;
  room?: Room;
}

// Tipos de Métricas
export interface DashboardMetrics {
  periodo: {
    fecha_inicio: string;
    fecha_fin: string;
  };
  habitaciones: {
    total: number;
    disponibles: number;
    ocupadas: number;
    limpieza: number;
    mantenimiento: number;
    tasa_ocupacion: number;
  };
  reservas: {
    total: number;
    pendientes: number;
    confirmadas: number;
    check_in_realizado: number;
    completadas: number;
    canceladas: number;
  };
  ingresos: {
    totales: number;
    proyectados: number;
  };
  clientes: {
    total: number;
    nuevos_periodo: number;
  };
}