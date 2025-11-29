import { api } from './api';
import type { Room, RoomType } from '../types';

export const roomsService = {
  // Room Types
  async getRoomTypes() {
    const response = await api.get<RoomType[]>('/rooms/types');
    return response. data;
  },

  async getRoomType(id: number) {
    const response = await api.get<RoomType>(`/rooms/types/${id}`);
    return response.data;
  },

  async createRoomType(data: Partial<RoomType>) {
    const response = await api.post<RoomType>('/rooms/types', data);
    return response. data;
  },

  async updateRoomType(id: number, data: Partial<RoomType>) {
    const response = await api.put<RoomType>(`/rooms/types/${id}`, data);
    return response.data;
  },

  async deleteRoomType(id: number) {
    await api.delete(`/rooms/types/${id}`);
  },

  // Rooms
  async getRooms(params?: { estado?: string; room_type_id?: number }) {
    const response = await api.get<Room[]>('/rooms', { params });
    return response.data;
  },

  async getRoom(id: number) {
    const response = await api.get<Room>(`/rooms/${id}`);
    return response.data;
  },

  async createRoom(data: Partial<Room>) {
    const response = await api. post<Room>('/rooms', data);
    return response.data;
  },

  async updateRoom(id: number, data: Partial<Room>) {
    const response = await api.put<Room>(`/rooms/${id}`, data);
    return response.data;
  },

  async deleteRoom(id: number) {
    await api.delete(`/rooms/${id}`);
  },

  async updateRoomStatus(id: number, estado: string) {
    const response = await api.patch<Room>(`/rooms/${id}/status`, { estado });
    return response.data;
  },
};