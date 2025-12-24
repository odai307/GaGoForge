import api from "./api";

/**
 * Submissions API endpoints
 */
export const submissionsAPI = {
  /**
   * Submit code for a problem
   * @param {object} submissionData - Submission data (problem, code, language, hints_used, etc.)
   * @returns {Promise} Submission result with validation
   */
  submitCode: async (submissionData) => {
    const data = {
      ...submissionData,
      problem: submissionData.problem, // Keep as UUID - backend should handle this
    };

    const response = await api.post("/api/submissions/", data);
    return response.data;
  },

  /**
   * Get user's submissions
   * @param {object} filters - Filter options (problem, verdict, etc.)
   * @returns {Promise} List of submissions
   */
  getSubmissions: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.problem) params.append("problem", filters.problem);
    if (filters.verdict) params.append("verdict", filters.verdict);
    if (filters.ordering) params.append("ordering", filters.ordering);

    const response = await api.get(`/api/submissions/?${params.toString()}`);
    return response.data;
  },

  /**
   * Get single submission by ID
   * @param {string} submissionId - Submission UUID
   * @returns {Promise} Submission details
   */
  getSubmission: async (submissionId) => {
    const response = await api.get(`/api/submissions/${submissionId}/`);
    return response.data;
  },

  /**
   * Get recent submissions
   * @param {number} limit - Number of recent submissions to fetch
   * @returns {Promise} Recent submissions
   */
  getRecentSubmissions: async (limit = 10) => {
    const response = await api.get(`/api/submissions/recent/?limit=${limit}`);
    return response.data;
  },

  /**
   * Get submission statistics
   * @returns {Promise} Submission statistics
   */
  getStatistics: async () => {
    const response = await api.get("/api/submissions/statistics/");
    return response.data;
  },

  /**
   * Dispute a submission
   * @param {string} submissionId - Submission UUID
   * @param {string} reason - Reason for dispute
   * @returns {Promise} Dispute result
   */
  disputeSubmission: async (submissionId, reason) => {
    const response = await api.post(
      `/api/submissions/${submissionId}/dispute/`,
      {
        dispute_reason: reason,
      }
    );
    return response.data;
  },
};
