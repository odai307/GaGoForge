import api from './api';

/**
 * Authentication API endpoints
 */
export const authAPI = {
  /**
   * Login user
   * @param {string} username - Username or email
   * @param {string} password - User password
   * @returns {Promise} Response with access and refresh tokens
   */
  login: async (username, password) => {
    const response = await api.post('/api/auth/login/', {
      username, // JWT TokenObtainPairView expects 'username' field
      password,
    });
    return response.data;
  },

  /**
   * Register new user
   * @param {object} userData - User registration data
   * @returns {Promise} Response with user data and tokens
   */
  register: async (userData) => {
    const response = await api.post('/api/users/register/', userData);
    return response.data;
  },

  /**
   * Verify token
   * @param {string} token - Access token to verify
   * @returns {Promise} Verification result
   */
  verifyToken: async (token) => {
    const response = await api.post('/api/auth/verify/', { token });
    return response.data;
  },

  /**
   * Refresh access token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise} New access token
   */
  refreshToken: async (refreshToken) => {
    const response = await api.post('/api/auth/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  },

  /**
   * Get current user profile
   * @returns {Promise} User profile data
   */
  getCurrentUser: async () => {
    const response = await api.get('/api/users/me/');
    return response.data;
  },
};

