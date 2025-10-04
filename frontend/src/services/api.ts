import axios from 'axios';
import type {
  AWRReport,
  ListResponse,
  UploadResponse,
  PerformanceMetric,
  DiagnosticSummary,
} from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败';
    return Promise.reject(new Error(message));
  }
);

// Report APIs
export const reportApi = {
  // Upload AWR report
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<any, UploadResponse>('/reports/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Get report list
  list: (params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }) => {
    return api.get<any, ListResponse<AWRReport>>('/reports', { params });
  },

  // Get report detail
  get: (id: number) => {
    return api.get<any, AWRReport>(`/reports/${id}`);
  },

  // Delete report
  delete: (id: number) => {
    return api.delete(`/reports/${id}`);
  },

  // Get metrics
  getMetrics: (id: number, category?: string) => {
    return api.get<any, PerformanceMetric[]>(`/reports/${id}/metrics`, {
      params: { category },
    });
  },

  // Trigger analysis
  analyze: (id: number) => {
    return api.post(`/reports/${id}/analyze`);
  },

  // Get diagnostics
  getDiagnostics: (id: number) => {
    return api.get<any, DiagnosticSummary>(`/reports/${id}/diagnostics`);
  },
};

export default api;
