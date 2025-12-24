import api from "./api";

export const leaderboardService = {
  getGlobalLeaderboard: (params = {}) => {
    return api.get("/api/leaderboard/global/", { params });
  },

  getWeeklyLeaderboard: (params = {}) => {
    return api.get("/api/leaderboard/weekly/", { params });
  },

  getFrameworkLeaderboard: (framework, params = {}) => {
    return api.get(`/api/leaderboard/frameworks/${framework}/`, { params });
  },

  getCurrentUserRank: () => {
    return api.get("/api/leaderboard/current-user/");
  },
};
