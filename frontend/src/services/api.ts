import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Camera {
  id: number;
  name: string;
  location: string;
  rtsp_url: string;
  is_active: boolean;
  created_at: string;
}

export interface Detection {
  id: number;
  camera: number;
  plate_number: string;
  confidence: number;
  timestamp: string;
  image_path?: string;
  blacklist_flag: boolean;
}

export interface BlacklistEntry {
  id: number;
  plate_number: string;
  reason: string;
  added_at: string;
  is_active: boolean;
}

export interface Alert {
  id: number;
  detection: number;
  blacklist_entry: number;
  timestamp: string;
  is_resolved: boolean;
}

// API functions
export const cameraAPI = {
  getAll: () => api.get<Camera[]>('/cameras/'),
  getById: (id: number) => api.get<Camera>(`/cameras/${id}/`),
  create: (data: Partial<Camera>) => api.post<Camera>('/cameras/', data),
  update: (id: number, data: Partial<Camera>) => api.put<Camera>(`/cameras/${id}/`, data),
  delete: (id: number) => api.delete(`/cameras/${id}/`),
};

export const detectionAPI = {
  getAll: (params?: any) => api.get<Detection[]>('/detections/', { params }),
  getById: (id: number) => api.get<Detection>(`/detections/${id}/`),
  getStats: () => api.get('/detections/stats/'),
};

export const blacklistAPI = {
  getAll: () => api.get<BlacklistEntry[]>('/blacklist/'),
  getById: (id: number) => api.get<BlacklistEntry>(`/blacklist/${id}/`),
  create: (data: Partial<BlacklistEntry>) => api.post<BlacklistEntry>('/blacklist/', data),
  update: (id: number, data: Partial<BlacklistEntry>) => api.put<BlacklistEntry>(`/blacklist/${id}/`, data),
  delete: (id: number) => api.delete(`/blacklist/${id}/`),
};

export const alertAPI = {
  getAll: (params?: any) => api.get<Alert[]>('/alerts/', { params }),
  getById: (id: number) => api.get<Alert>(`/alerts/${id}/`),
  resolve: (id: number) => api.patch(`/alerts/${id}/`, { is_resolved: true }),
};

export const reportAPI = {
  generate: (params: any) => api.get('/reports/', { params }),
};

export default api;