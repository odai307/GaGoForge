import api from './api';

/**
 * User Progress API endpoints
 */
export const progressAPI = {
  /**
   * Get user's progress on problems
   * @param {object} filters - Filter options (is_solved, is_attempted, framework, difficulty)
   * @returns {Promise} List of progress records
   */
  getProgress: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.is_solved !== undefined) params.append('is_solved', filters.is_solved);
    if (filters.is_attempted !== undefined) params.append('is_attempted', filters.is_attempted);
    if (filters.framework) params.append('problem__framework__name', filters.framework);
    if (filters.difficulty) params.append('problem__difficulty', filters.difficulty);
    if (filters.ordering) params.append('ordering', filters.ordering);
    
    const response = await api.get(`/api/progress/?${params.toString()}`);
    return response.data;
  },

  /**
   * Get progress summary
   * @returns {Promise} Progress summary statistics
   */
  getSummary: async () => {
    const response = await api.get('/api/progress/summary/');
    return response.data;
  },

  /**
   * Get recent activity
   * @returns {Promise} Recent activity data
   */
  getRecentActivity: async () => {
    const response = await api.get('/api/progress/recent_activity/');
    return response.data;
  },
};

