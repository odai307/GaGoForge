import api from "./api";

export const profileService = {
  // Get current user basic info
  getCurrentUser: () => {
    return api.get("/api/users/me/");
  },

  getUserProfile: () => {
    return api.get("/api/users/profiles/me/");
  },

  // Get detailed user statistics
  getUserStats: () => {
    return api.get("/api/users/profiles/stats/");
  },

  // Get user submissions
  getUserSubmissions: (params = {}) => {
    return api.get("/api/submissions/", { params });
  },

  // Update user profile preferences
  updateProfile: (data) => {
    return api.patch("/api/users/profiles/update_preferences/", data);
  },

  // Get editable fields info
  getEditableFields: () => {
    return api.get("/api/users/profiles/editable_fields/");
  },

  // Get user's recent activity
  getRecentActivity: () => {
    return api.get("/api/users/profiles/recent_activity/");
  },

  // Get comprehensive stats summary
  getStatsSummary: () => {
    return api.get("/api/users/profiles/stats_summary/");
  },
};
