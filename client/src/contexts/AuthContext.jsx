import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/auth';
import { setTokens, removeTokens, isAuthenticated, getAccessToken } from '../utils/token';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (isAuthenticated()) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
          setIsLoggedIn(true);
        } catch (error) {
          // Token invalid or expired
          removeTokens();
          setUser(null);
          setIsLoggedIn(false);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  /**
   * Login user
   * @param {string} username - Username
   * @param {string} password - User password
   * @returns {Promise} Login result
   */
  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);
      // JWT returns { access, refresh } directly
      const { access, refresh } = response;
      
      setTokens(access, refresh);
      
      // Fetch user data after login
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      setIsLoggedIn(true);
      
      return { success: true, user: userData };
    } catch (error) {
      console.error('Login error:', error);
      let message = 'Login failed';
      
      // Handle network errors
      if (!error.response) {
        if (error.code === 'ECONNABORTED') {
          message = 'Request timeout. Please check if the backend server is running.';
        } else if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
          message = `Network error. Please ensure the backend server is running at ${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}`;
        } else {
          message = `Network error: ${error.message}. Please check if the backend server is running.`;
        }
      } else if (error.response?.data) {
        const errorData = error.response.data;
        if (errorData.detail) {
          message = errorData.detail;
        } else if (errorData.message) {
          message = errorData.message;
        } else if (typeof errorData === 'string') {
          message = errorData;
        } else if (errorData.non_field_errors) {
          message = Array.isArray(errorData.non_field_errors) 
            ? errorData.non_field_errors.join(', ') 
            : errorData.non_field_errors;
        }
      } else if (error.message) {
        message = error.message;
      }
      
      return { success: false, error: message };
    }
  };

  /**
   * Register new user
   * @param {object} userData - Registration data
   * @returns {Promise} Registration result
   */
  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      // Backend returns { user, tokens: { access, refresh } }
      const { tokens, user: newUser } = response;
      
      setTokens(tokens.access, tokens.refresh);
      setUser(newUser);
      setIsLoggedIn(true);
      
      return { success: true, user: newUser };
    } catch (error) {
      console.error('Registration error:', error);
      // Handle validation errors
      let message = 'Registration failed';
      
      // Handle network errors
      if (!error.response) {
        message = error.userMessage || error.message || 'Cannot connect to server. Please ensure the backend is running on http://localhost:8000';
      } else if (error.response?.data) {
        const errorData = error.response.data;
        if (typeof errorData === 'string') {
          message = errorData;
        } else if (errorData.detail) {
          message = errorData.detail;
        } else if (errorData.message) {
          message = errorData.message;
        } else if (errorData.error) {
          message = errorData.error;
        } else {
          // Handle field-specific errors (Django REST Framework format)
          const fieldErrors = Object.entries(errorData)
            .map(([field, errors]) => {
              const fieldName = field.replace(/_/g, ' ');
              const errorMsg = Array.isArray(errors) ? errors.join(', ') : errors;
              return `${fieldName}: ${errorMsg}`;
            })
            .join('; ');
          message = fieldErrors || message;
        }
      } else if (error.message) {
        message = error.message;
      }
      
      return { success: false, error: message };
    }
  };

  /**
   * Logout user
   */
  const logout = () => {
    removeTokens();
    setUser(null);
    setIsLoggedIn(false);
  };

  const value = {
    user,
    isLoggedIn,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

