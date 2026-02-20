import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 150000, // 2.5 minutes for audio processing
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
      toast.error('Session expired. Please log in again.');
    } else if (error.response?.status === 402) {
      // Usage limit exceeded
      const detail = error.response.data?.detail;
      if (typeof detail === 'object' && detail.upgrade_required) {
        toast.error(detail.message || 'Usage limit exceeded. Please upgrade to premium.');
      } else {
        toast.error('Usage limit exceeded. Please upgrade to premium.');
      }
    } else if (error.response?.status === 403) {
      toast.error('Access denied. Insufficient permissions.');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    }
    
    return Promise.reject(error);
  }
);

// API utility functions
export const apiUtils = {
  // Authentication
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  
  register: (name: string, email: string, password: string) =>
    api.post('/auth/register', { name, email, password }),
  
  logout: () => api.post('/auth/logout'),
  
  getCurrentUser: () => api.get('/auth/me'),
  
  validateToken: () => api.get('/auth/validate-token'),

  // User management
  getUserProfile: () => api.get('/users/profile'),
  
  updateProfile: (data: { name?: string; email?: string }) =>
    api.put('/users/profile', data),
  
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    }),
  
  getUserUsage: () => api.get('/users/usage'),
  
  getUserSubscription: () => api.get('/users/subscription'),
  
  createSubscription: (planType: string, durationMonths: number = 1) =>
    api.post('/users/subscription', {
      plan_type: planType,
      duration_months: durationMonths,
    }),
  
  cancelSubscription: () => api.delete('/users/subscription'),

  // Audio processing
  enhanceSpeech: (formData: FormData) =>
    api.post('/enhance-speech', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
  
  downloadAudio: (filename: string) =>
    api.get(`/download/${filename}`, {
      responseType: 'blob',
    }),

  // Dashboard
  getDashboardOverview: () => api.get('/dashboard/overview'),
  
  getUserStatistics: () => api.get('/dashboard/statistics'),
  
  getRecentActivity: (limit: number = 20) =>
    api.get(`/dashboard/activity?limit=${limit}`),
  
  getUserAnalytics: (days: number = 30) =>
    api.get(`/dashboard/analytics?days=${days}`),

  // History
  getProcessingHistory: (params: {
    page?: number;
    per_page?: number;
    output_mode?: string;
    days?: number;
    search?: string;
  } = {}) => {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, value.toString());
      }
    });
    return api.get(`/history?${queryParams.toString()}`);
  },
  
  getAudioDetails: (audioId: number) =>
    api.get(`/history/${audioId}`),
  
  deleteAudioRecord: (audioId: number) =>
    api.delete(`/history/${audioId}`),
  
  bulkDeleteRecords: (audioIds: number[]) =>
    api.post('/history/bulk-delete', { audio_ids: audioIds }),
  
  getHistorySummary: () => api.get('/history/stats/summary'),

  // Public endpoints
  getPricing: () => api.get('/pricing'),
  
  getHealth: () => api.get('/health'),

  // Admin endpoints (admin only)
  admin: {
    getAllUsers: (params: {
      page?: number;
      per_page?: number;
      role?: string;
      search?: string;
      is_active?: boolean;
    } = {}) => {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
      return api.get(`/admin/users?${queryParams.toString()}`);
    },
    
    getUserDetails: (userId: number) =>
      api.get(`/admin/users/${userId}`),
    
    updateUser: (userId: number, data: any) =>
      api.put(`/admin/users/${userId}`, data),
    
    deleteUser: (userId: number) =>
      api.delete(`/admin/users/${userId}`),
    
    getSystemStatistics: () =>
      api.get('/admin/statistics'),
    
    getSystemSettings: () =>
      api.get('/admin/settings'),
    
    updateSystemSetting: (key: string, value: string) =>
      api.put(`/admin/settings/${key}`, { setting_value: value }),
    
    upgradeUserToPremium: (userId: number, planType: string = 'yearly_premium') =>
      api.post(`/admin/users/${userId}/upgrade-to-premium?plan_type=${planType}`),
    
    resetUserUsage: (userId: number, newLimit: number = 10) =>
      api.post(`/admin/users/${userId}/reset-usage?new_limit=${newLimit}`),
  },
};

export default api;