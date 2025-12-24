import axios from 'axios';

// API base URL - adjust this to match your Django backend
// Note: The base URL should NOT include '/api' since endpoints already include it
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

console.log('API Base URL:', API_BASE_URL);

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor - add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle token refresh and errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Log network errors for debugging
    if (!error.response) {
      const fullUrl = `${API_BASE_URL}${originalRequest?.url || ''}`;
      console.error('Network Error Details:', {
        message: error.message,
        code: error.code,
        fullUrl: fullUrl,
        baseURL: API_BASE_URL,
        endpoint: originalRequest?.url,
        method: originalRequest?.method,
      });
      
      // Provide user-friendly error message
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        error.userMessage = `Cannot connect to server at ${API_BASE_URL}. Please make sure the backend server is running.`;
      } else if (error.code === 'ERR_NETWORK') {
        error.userMessage = 'Network error. Please check your internet connection and ensure the backend server is running.';
      } else {
        error.userMessage = `Network error: ${error.message}`;
      }
    }

    // If 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

