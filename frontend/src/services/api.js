import axios from 'axios';
import { API_BASE_URL, STORAGE_KEYS } from '../config/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token and handle absolute URLs
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Handle absolute URLs - if URL starts with http, use it directly
    if (config.url && (config.url.startsWith('http://') || config.url.startsWith('https://'))) {
      config.baseURL = '';
    }
    
    // Don't override Content-Type if it's already set (e.g., for FormData)
    if (config.headers['Content-Type'] === 'multipart/form-data') {
      delete config.headers['Content-Type']; // Let axios set it with boundary
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default api;