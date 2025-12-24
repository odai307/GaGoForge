import api from './api';

/**
 * Problems API endpoints
 */
export const problemsAPI = {
  /**
   * Get list of problems with filters and pagination
   * @param {object} filters - Filter options (framework, category, difficulty, search, etc.)
   * @param {number} page - Page number for pagination
   * @param {number} pageSize - Items per page
   * @returns {Promise} Paginated list of problems
   */
  getProblems: async (filters = {}, page = 1, pageSize = 20) => {
    const params = new URLSearchParams();
    
    if (filters.framework) params.append('framework__name', filters.framework);
    if (filters.category) params.append('category__name', filters.category);
    if (filters.difficulty) params.append('difficulty', filters.difficulty);
    if (filters.search) params.append('search', filters.search);
    if (filters.is_solved !== undefined) params.append('is_solved', filters.is_solved);
    if (filters.is_premium !== undefined) params.append('is_premium', filters.is_premium);
    if (filters.ordering) params.append('ordering', filters.ordering);
    
    // Add pagination parameters
    params.append('page', page);
    params.append('page_size', pageSize);
    
    const response = await api.get(`/api/problems/?${params.toString()}`);
    return response.data;
  },

  /**
   * Get single problem by slug
   * @param {string} slug - Problem slug
   * @returns {Promise} Problem details
   */
  getProblem: async (slug) => {
    const response = await api.get(`/api/problems/${slug}/`);
    return response.data;
  },

  /**
   * Get problem starter code
   * @param {string} slug - Problem slug
   * @returns {Promise} Starter code data
   */
  getStarterCode: async (slug) => {
    const response = await api.get(`/api/problems/${slug}/starter_code/`);
    return response.data;
  },

  /**
   * Get random problem
   * @param {object} filters - Optional filters
   * @returns {Promise} Random problem
   */
  getRandomProblem: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.framework) params.append('framework__name', filters.framework);
    if (filters.difficulty) params.append('difficulty', filters.difficulty);
    
    const response = await api.get(`/api/problems/random/?${params.toString()}`);
    return response.data;
  },

  /**
   * Get problem statistics
   * @returns {Promise} Problem statistics
   */
  getStats: async () => {
    const response = await api.get('/api/problems/stats/');
    return response.data;
  },
};

