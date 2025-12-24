/**
 * Token management utilities
 */

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

/**
 * Store tokens in localStorage
 * @param {string} accessToken - Access token
 * @param {string} refreshToken - Refresh token
 */
export const setTokens = (accessToken, refreshToken) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
};

/**
 * Get access token from localStorage
 * @returns {string|null} Access token or null
 */
export const getAccessToken = () => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

/**
 * Get refresh token from localStorage
 * @returns {string|null} Refresh token or null
 */
export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Remove tokens from localStorage
 */
export const removeTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

/**
 * Check if user is authenticated (has access token)
 * @returns {boolean} True if authenticated
 */
export const isAuthenticated = () => {
  return !!getAccessToken();
};

