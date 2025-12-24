// src/pages/Profile.jsx
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Button,
  Stack,
  Grid,
  Avatar,
  LinearProgress,
  Divider,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Snackbar,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormHelperText,
  Switch,
  FormControlLabel,
} from "@mui/material";
import {
  Person,
  Edit,
  Share,
  CheckCircle,
  TrendingUp,
  EmojiEvents,
  Schedule,
  Code,
  CalendarToday,
  Star,
  Bolt,
  Lock,
  GitHub,
  LinkedIn,
  Twitter,
  Refresh,
  Close,
  Save,
  Language,
  Palette,
  Email,
  Language as LanguageIcon,
  Palette as PaletteIcon,
  Email as EmailIcon,
  AccountCircle,
  Link as LinkIcon,
} from "@mui/icons-material";
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/layout/Layout";
import { useAuth } from "../contexts/AuthContext";
import { profileService } from "../services/profile";
import { progressAPI } from "../services/progress";
import { submissionsAPI } from "../services/submissions";

function Profile() {
  const { user: authUser, logout } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Edit modal states
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  // Form state - ALL editable fields
  const [formData, setFormData] = useState({
    // User fields (nested under 'user')
    first_name: "",
    last_name: "",
    // Profile fields
    preferred_language: "python",
    theme: "dark",
    email_notifications: true,
    bio: "",
    github_username: "",
    website_url: "",
  });

  // Real data from APIs
  const [userData, setUserData] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [userProgress, setUserProgress] = useState([]);
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [frameworkStats, setFrameworkStats] = useState([]);
  const [difficultyStats, setDifficultyStats] = useState([]);

  // Available options for selects
  const [availableOptions, setAvailableOptions] = useState({
    themes: ["light", "dark"],
    languages: [
      "python",
      "javascript",
      "typescript",
      "java",
      "c++",
      "go",
      "rust",
    ],
  });

  useEffect(() => {
    if (authUser) {
      fetchProfileData();
    }
  }, [authUser]);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      setError(null);

      // FIXED: Get full profile data
      const profileRes = await profileService.getUserProfile();
      const profileData = profileRes.data;

      // Get editable fields info
      try {
        const editableRes = await profileService.getEditableFields();
        if (editableRes.data?.available_options) {
          setAvailableOptions(editableRes.data.available_options);
        }
      } catch (editableError) {
        console.warn("Could not fetch editable options:", editableError);
      }

      // Set user data with ALL profile fields
      setUserData({
        username: profileData.username || authUser?.username || "User",
        first_name: profileData.first_name || "",
        last_name: profileData.last_name || "",
        name:
          `${profileData.first_name || ""} ${
            profileData.last_name || ""
          }`.trim() ||
          profileData.username ||
          "User",
        email: profileData.email || "",
        bio: profileData.bio || "",
        join_date: profileData.created_at,
        preferred_language: profileData.preferred_language || "python",
        theme: profileData.theme || "dark",
        email_notifications: profileData.email_notifications !== false,
        github_username: profileData.github_username || "",
        website_url: profileData.website_url || "",
      });

      // Initialize form data
      setFormData({
        first_name: profileData.first_name || "",
        last_name: profileData.last_name || "",
        preferred_language: profileData.preferred_language || "python",
        theme: profileData.theme || "dark",
        email_notifications: profileData.email_notifications !== false,
        bio: profileData.bio || "",
        github_username: profileData.github_username || "",
        website_url: profileData.website_url || "",
      });

      // FIXED: Get comprehensive stats with totals
      let statsData = {
        overview: {
          total_problems_solved: 0,
          total_problems_attempted: 0,
          total_submissions: 0,
          total_score: 0,
        },
        frameworks: {},
        difficulties: {},
        streaks: {
          current: 0,
          longest: 0,
          last_activity: null,
        },
      };

      try {
        const statsRes = await profileService.getStatsSummary();
        if (statsRes.data) {
          statsData = statsRes.data;
        }
      } catch (statsError) {
        console.warn("Could not fetch stats summary:", statsError);
        // Fallback to old endpoint
        try {
          const oldStatsRes = await profileService.getUserStats();
          if (oldStatsRes.data) {
            statsData = {
              overview: {
                total_problems_solved: oldStatsRes.data.total_problems_solved || 0,
                total_problems_attempted: oldStatsRes.data.total_problems_attempted || 0,
                total_submissions: oldStatsRes.data.total_submissions || 0,
                total_score: oldStatsRes.data.total_score || 0,
              },
              frameworks: {},
              difficulties: {},
              streaks: oldStatsRes.data.streaks || {
                current: 0,
                longest: 0,
                last_activity: null,
              },
            };
          }
        } catch (fallbackError) {
          console.warn("Could not fetch fallback stats:", fallbackError);
        }
      }

      // Set stats state
      setUserStats(statsData);

      // FIXED: Get recent activity from new endpoint
      let recentActivityData = [];
      try {
        const activityRes = await profileService.getRecentActivity();
        if (activityRes.data?.recent_submissions) {
          recentActivityData = activityRes.data.recent_submissions;
        }
      } catch (activityError) {
        console.warn("Could not fetch recent activity:", activityError);
        // Fallback to old method
        try {
          const submissionsRes = await submissionsAPI.getSubmissions({
            ordering: "-submitted_at",
            limit: 10,
          });
          if (submissionsRes.data?.results) {
            recentActivityData = submissionsRes.data.results;
          } else if (Array.isArray(submissionsRes.data)) {
            recentActivityData = submissionsRes.data;
          }
        } catch (submissionsError) {
          console.warn("Could not fetch submissions:", submissionsError);
        }
      }

      // FIXED: Get progress for framework calculations
      let progressData = [];
      try {
        const progressRes = await progressAPI.getProgress();
        if (progressRes.results) {
          progressData = progressRes.results;
        } else if (Array.isArray(progressRes)) {
          progressData = progressRes;
        }
      } catch (progressError) {
        console.warn("Could not fetch progress:", progressError);
      }

      // Update state
      setUserStats(statsData);
      setRecentSubmissions(recentActivityData);
      setUserProgress(progressData);

      // FIXED: Use backend-calculated framework stats
      if (statsData.frameworks && Object.keys(statsData.frameworks).length > 0) {
        const frameworkArray = Object.values(statsData.frameworks).map((fw) => ({
          name: fw.name,
          solved: fw.solved,
          total: fw.total,
          proficiency: fw.proficiency,
          remaining: fw.remaining,
        }));
        setFrameworkStats(frameworkArray);
      } else {
        setFrameworkStats([]);
      }

      // FIXED: Use backend-calculated difficulty stats
      if (statsData.difficulties && Object.keys(statsData.difficulties).length > 0) {
        const difficultyArray = Object.values(statsData.difficulties).map((diff) => ({
          level: diff.level,
          solved: diff.solved,
          total: diff.total,
          percentage: diff.percentage,
          remaining: diff.remaining,
          color: diff.color,
        }));
        setDifficultyStats(difficultyArray);
      } else {
        setDifficultyStats([]);
      }

    } catch (err) {
      console.error("Error in fetchProfileData:", err);
      setError("Failed to load profile data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleEditClick = () => {
    setEditModalOpen(true);
  };

  const handleCloseModal = () => {
    if (!saving) {
      setEditModalOpen(false);
    }
  };

  const handleFormChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);

      // FIXED: Send data at top level, NOT nested under 'user'
      const updateData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        preferred_language: formData.preferred_language,
        theme: formData.theme,
        email_notifications: formData.email_notifications,
        bio: formData.bio,
        github_username: formData.github_username,
        website_url: formData.website_url,
      };

      console.log("Sending update data:", updateData);

      // Call the update API
      const response = await profileService.updateProfile(updateData);
      console.log("Update successful:", response.data);

      // Update local user data
      const updatedUserData = {
        ...userData,
        first_name: formData.first_name,
        last_name: formData.last_name,
        name:
          `${formData.first_name || ""} ${formData.last_name || ""}`.trim() ||
          userData?.username,
        preferred_language: formData.preferred_language,
        theme: formData.theme,
        email_notifications: formData.email_notifications,
        bio: formData.bio,
        github_username: formData.github_username,
        website_url: formData.website_url,
      };
      setUserData(updatedUserData);

      // Close modal
      setEditModalOpen(false);

      // Show success message
      setSnackbar({
        open: true,
        message: "Profile updated successfully!",
        severity: "success",
      });

      // Refresh profile data
      fetchProfileData();
    } catch (error) {
      console.error("Update error:", error);

      let errorMessage = "Failed to update profile. Please try again.";
      if (error.response?.data) {
        const errorData = error.response.data;
        if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        } else if (typeof errorData === "object") {
          // Handle field-specific errors
          const fieldErrors = Object.entries(errorData)
            .map(
              ([field, errors]) =>
                `${field}: ${
                  Array.isArray(errors) ? errors.join(", ") : errors
                }`
            )
            .join("; ");
          errorMessage = fieldErrors || errorMessage;
        }
      }

      setSnackbar({
        open: true,
        message: errorMessage,
        severity: "error",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case "beginner":
        return "success";
      case "intermediate":
        return "warning";
      case "pro":
        return "error";
      case "veteran":
        return "error";
      default:
        return "default";
    }
  };

  const getFrameworkColor = (framework) => {
    switch (framework.toLowerCase()) {
      case "react":
        return "#61DAFB";
      case "django":
        return "#092E20";
      case "angular":
        return "#DD0031";
      case "express":
        return "#000000";
      case "nodejs":
        return "#68A063";
      default:
        return "#6B7280";
    }
  };

  const getStatusIcon = (status) => {
    return status === "accepted" ? (
      <CheckCircle sx={{ color: "#10B981" }} />
    ) : (
      <Bolt sx={{ color: "#F59E0B" }} />
    );
  };

  const calculateStats = () => {
    if (!userStats) {
      return {
        totalSolved: 0,
        totalProblems: 0,
        streak: 0,
        longestStreak: 0,
        rank: 0,
        experience: 0,
        level: 1,
        solvedPercentage: 0,
      };
    }

    // Use overview data from new endpoint or fallback to old structure
    const overview = userStats.overview || userStats;
    
    const totalSolved = overview.total_problems_solved || 0;
    const totalProblems = overview.total_problems_attempted || totalSolved;
    const streak = userStats.streaks?.current || 0;
    const longestStreak = userStats.streaks?.longest || streak;
    const rank = overview.global_rank || 0;
    const experience = overview.total_score || totalSolved * 100;
    const level = Math.floor(experience / 1000) + 1;
    const solvedPercentage =
      totalProblems > 0 ? Math.round((totalSolved / totalProblems) * 100) : 0;

    return {
      totalSolved,
      totalProblems,
      streak,
      longestStreak,
      rank,
      experience,
      level,
      solvedPercentage,
    };
  };

  const stats = calculateStats();
  const levelProgress = (stats.experience % 1000) / 10;

  if (loading) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ py: { xs: 2, md: 3 } }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              minHeight: "60vh",
            }}
          >
            <CircularProgress />
          </Box>
        </Container>
      </Layout>
    );
  }

  if (!authUser) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ py: { xs: 2, md: 3 } }}>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Please log in to view your profile.
          </Alert>
          <Button component={Link} to="/login" variant="contained">
            Login
          </Button>
        </Container>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ py: { xs: 2, md: 3 } }}>
          <Alert
            severity="error"
            sx={{ mb: 2 }}
            action={
              <Button color="inherit" size="small" onClick={fetchProfileData}>
                Retry
              </Button>
            }
          >
            {error}
          </Alert>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ py: { xs: 2, md: 3 } }}>
        {/* Header Section */}
        <Card sx={{ border: "1px solid #E2E8F0", borderRadius: 3, mb: 4 }}>
          <CardContent sx={{ p: 4 }}>
            <Stack
              direction={{ xs: "column", md: "row" }}
              spacing={4}
              alignItems="flex-start"
            >
              {/* Avatar and Basic Info */}
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                }}
              >
                <Avatar
                  sx={{
                    width: 120,
                    height: 120,
                    bgcolor: "#3B82F6",
                    fontSize: "2.5rem",
                    fontWeight: 700,
                    mb: 2,
                  }}
                >
                  {authUser?.username?.charAt(0).toUpperCase() || "U"}
                </Avatar>
                <Stack direction="row" spacing={1}>
                  <Tooltip title="Edit Profile">
                    <IconButton
                      sx={{ border: "1px solid #E2E8F0" }}
                      onClick={handleEditClick}
                    >
                      <Edit />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Refresh Data">
                    <IconButton
                      sx={{ border: "1px solid #E2E8F0" }}
                      onClick={fetchProfileData}
                    >
                      <Refresh />
                    </IconButton>
                  </Tooltip>
                </Stack>
              </Box>

              {/* User Details */}
              <Box sx={{ flexGrow: 1 }}>
                <Stack
                  direction="row"
                  alignItems="center"
                  spacing={2}
                  sx={{ mb: 2 }}
                >
                  <Typography
                    variant="h4"
                    sx={{ fontWeight: 800, color: "#0F172A" }}
                  >
                    {userData?.name || authUser?.username || "User"}
                  </Typography>
                  <Chip
                    label={`Level ${stats.level}`}
                    color="primary"
                    sx={{ fontWeight: 600 }}
                  />
                </Stack>

                <Typography
                  variant="body1"
                  sx={{ color: "#64748B", mb: 3, lineHeight: 1.6 }}
                >
                  {userData?.bio || "No bio available. Click edit to add one!"}
                </Typography>

                {/* User Info */}
                <Stack direction="row" spacing={3} sx={{ mb: 3 }}>
                  <Typography
                    variant="body2"
                    sx={{
                      color: "#64748B",
                      display: "flex",
                      alignItems: "center",
                      gap: 0.5,
                    }}
                  >
                    <Person sx={{ fontSize: 16 }} />@{authUser?.username}
                  </Typography>
                  {userData?.join_date && (
                    <Typography
                      variant="body2"
                      sx={{
                        color: "#64748B",
                        display: "flex",
                        alignItems: "center",
                        gap: 0.5,
                      }}
                    >
                      <CalendarToday sx={{ fontSize: 16 }} />
                      Joined {new Date(userData.join_date).toLocaleDateString()}
                    </Typography>
                  )}
                  {userData?.preferred_language && (
                    <Typography
                      variant="body2"
                      sx={{
                        color: "#64748B",
                        display: "flex",
                        alignItems: "center",
                        gap: 0.5,
                      }}
                    >
                      <LanguageIcon sx={{ fontSize: 16 }} />
                      {userData.preferred_language}
                    </Typography>
                  )}
                </Stack>

                {/* Profile Details */}
                <Grid container spacing={2}>
                  {userData?.github_username && (
                    <Grid item>
                      <Chip
                        icon={<GitHub />}
                        label={`GitHub: ${userData.github_username}`}
                        variant="outlined"
                        size="small"
                      />
                    </Grid>
                  )}
                  {userData?.website_url && (
                    <Grid item>
                      <Chip
                        icon={<LinkIcon />}
                        label="Website"
                        variant="outlined"
                        size="small"
                        component="a"
                        href={userData.website_url}
                        target="_blank"
                        clickable
                      />
                    </Grid>
                  )}
                  <Grid item>
                    <Chip
                      icon={<PaletteIcon />}
                      label={`Theme: ${userData?.theme || "dark"}`}
                      variant="outlined"
                      size="small"
                    />
                  </Grid>
                  <Grid item>
                    <Chip
                      icon={<EmailIcon />}
                      label={`Notifications: ${
                        userData?.email_notifications ? "On" : "Off"
                      }`}
                      variant="outlined"
                      size="small"
                    />
                  </Grid>
                </Grid>
              </Box>

              {/* Level Progress */}
              <Box sx={{ minWidth: 200 }}>
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 600, color: "#0F172A", mb: 1 }}
                >
                  Level Progress
                </Typography>
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 2, mb: 1 }}
                >
                  <LinearProgress
                    variant="determinate"
                    value={levelProgress}
                    sx={{
                      flexGrow: 1,
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: "#E2E8F0",
                      "& .MuiLinearProgress-bar": {
                        backgroundColor: "#8B5CF6",
                        borderRadius: 4,
                      },
                    }}
                  />
                  <Typography
                    variant="body2"
                    sx={{ color: "#64748B", fontWeight: 600, minWidth: 60 }}
                  >
                    {levelProgress.toFixed(0)}%
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: "#64748B" }}>
                  {stats.experience % 1000}/1000 XP to Level {stats.level + 1}
                </Typography>
              </Box>
            </Stack>
          </CardContent>
        </Card>
        {/* Stats Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                border: "1px solid #E2E8F0",
                borderRadius: 3,
                height: "100%",
              }}
            >
              <CardContent sx={{ p: 3, textAlign: "center" }}>
                <CheckCircle sx={{ fontSize: 40, color: "#10B981", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: 800, color: "#0F172A", mb: 0.5 }}
                >
                  {stats.totalSolved}
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748B" }}>
                  Problems Solved
                </Typography>
                <Typography variant="caption" sx={{ color: "#94A3B8" }}>
                  of {stats.totalProblems} total ({stats.solvedPercentage}%)
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                border: "1px solid #E2E8F0",
                borderRadius: 3,
                height: "100%",
              }}
            >
              <CardContent sx={{ p: 3, textAlign: "center" }}>
                <TrendingUp sx={{ fontSize: 40, color: "#3B82F6", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: 800, color: "#0F172A", mb: 0.5 }}
                >
                  #{stats.rank || "N/A"}
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748B" }}>
                  Global Rank
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                border: "1px solid #E2E8F0",
                borderRadius: 3,
                height: "100%",
              }}
            >
              <CardContent sx={{ p: 3, textAlign: "center" }}>
                <EmojiEvents sx={{ fontSize: 40, color: "#F59E0B", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: 800, color: "#0F172A", mb: 0.5 }}
                >
                  {stats.streak}
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748B" }}>
                  Day Streak
                </Typography>
                <Typography variant="caption" sx={{ color: "#94A3B8" }}>
                  Best: {stats.longestStreak}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                border: "1px solid #E2E8F0",
                borderRadius: 3,
                height: "100%",
              }}
            >
              <CardContent sx={{ p: 3, textAlign: "center" }}>
                <Star sx={{ fontSize: 40, color: "#8B5CF6", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: 800, color: "#0F172A", mb: 0.5 }}
                >
                  {stats.experience}
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748B" }}>
                  Total Score
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        {/* Main Content Tabs - Simplified for now */}
        {/* Main Content Tabs */}
        <Card sx={{ border: "1px solid #E2E8F0", borderRadius: 3 }}>
          <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab label="Recent Activity" />
              <Tab label="Framework Stats" />
            </Tabs>
          </Box>

          <CardContent sx={{ p: 3 }}>
            {/* Recent Activity Tab */}
            {activeTab === 0 && (
              <Box>
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 600, color: "#0F172A", mb: 3 }}
                >
                  Recent Submissions
                </Typography>
                {recentSubmissions && recentSubmissions.length > 0 ? (
                  <List sx={{ width: "100%" }}>
                    {recentSubmissions.map((submission, index) => (
                      <ListItem
                        key={submission.submission_id || index}
                        sx={{
                          border: "1px solid #E2E8F0",
                          borderRadius: 2,
                          mb: 2,
                          "&:hover": { backgroundColor: "#F8FAFC" },
                          flexDirection: "column",
                          alignItems: "stretch",
                        }}
                      >
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            width: "100%",
                            gap: 2,
                          }}
                        >
                          <ListItemIcon sx={{ minWidth: "auto" }}>
                            {getStatusIcon(submission.verdict)}
                          </ListItemIcon>
                          
                          <Box sx={{ flexGrow: 1 }}>
                            <ListItemText
                              primary={
                                <Stack
                                  direction="row"
                                  alignItems="center"
                                  spacing={2}
                                  sx={{ mb: 0.5 }}
                                >
                                  <Typography
                                    variant="body1"
                                    sx={{ fontWeight: 600, color: "#0F172A" }}
                                  >
                                    {submission.problem_title || "Unknown Problem"}
                                  </Typography>
                                  <Chip
                                    label={submission.framework || "Unknown"}
                                    size="small"
                                    sx={{
                                      textTransform: "capitalize",
                                      bgcolor: "#E0E7FF",
                                      color: "#4338CA",
                                      fontWeight: 600,
                                    }}
                                  />
                                </Stack>
                              }
                              secondary={
                                <Stack
                                  direction={{ xs: "column", sm: "row" }}
                                  spacing={2}
                                  sx={{ mt: 0.5 }}
                                >
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      color: "#64748B",
                                      display: "flex",
                                      alignItems: "center",
                                      gap: 0.5,
                                    }}
                                  >
                                    <Schedule sx={{ fontSize: 16 }} />
                                    {new Date(
                                      submission.submitted_at
                                    ).toLocaleString()}
                                  </Typography>
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      color:
                                        submission.verdict === "accepted"
                                          ? "#10B981"
                                          : submission.verdict === "partially_passed"
                                          ? "#F59E0B"
                                          : "#EF4444",
                                      fontWeight: 600,
                                      textTransform: "capitalize",
                                    }}
                                  >
                                    {submission.verdict?.replace("_", " ") || "Unknown"} 
                                    {submission.score !== undefined && ` (${submission.score}%)`}
                                  </Typography>
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      color: "#64748B",
                                      fontStyle: "italic",
                                    }}
                                  >
                                    Attempt #{submission.attempt_number || 1}
                                  </Typography>
                                </Stack>
                              }
                            />
                          </Box>

                          {submission.problem_id && (
                            <Button
                              component={Link}
                              to={`/problems/${submission.problem_id}`}
                              size="small"
                              variant="outlined"
                              sx={{ textTransform: "none", whiteSpace: "nowrap" }}
                            >
                              View Problem
                            </Button>
                          )}
                        </Box>
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    No submissions yet. Try solving your first challenge!
                    <Button
                      component={Link}
                      to="/problems"
                      variant="contained"
                      size="small"
                      sx={{ ml: 2 }}
                    >
                      Browse Problems
                    </Button>
                  </Alert>
                )}

                {/* Show total submissions count */}
                {recentSubmissions && recentSubmissions.length > 0 && (
                  <Box sx={{ mt: 3, textAlign: "center" }}>
                    <Typography variant="body2" sx={{ color: "#64748B", mb: 2 }}>
                      Showing {recentSubmissions.length} most recent submissions
                      {userStats?.total_submissions > recentSubmissions.length &&
                        ` of ${userStats.total_submissions} total`}
                    </Typography>
                    <Button
                      component={Link}
                      to="/submissions"
                      variant="outlined"
                      size="small"
                    >
                      View All Submissions
                    </Button>
                  </Box>
                )}
              </Box>
            )}

            {/* Framework Stats Tab */}
            {activeTab === 1 && (
              <Box>
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 600, color: "#0F172A", mb: 3 }}
                >
                  Framework Proficiency
                </Typography>

                {frameworkStats.length > 0 ? (
                  <Grid container spacing={3}>
                    {frameworkStats.map((framework) => (
                      <Grid item xs={12} sm={6} md={4} key={framework.name}>
                        <Card
                          sx={{
                            border: "1px solid #E2E8F0",
                            borderRadius: 2,
                            height: "100%",
                            transition: "all 0.3s ease",
                            "&:hover": {
                              boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                              transform: "translateY(-2px)",
                            },
                          }}
                        >
                          <CardContent sx={{ p: 3 }}>
                            <Stack spacing={2}>
                              {/* Framework Header */}
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "space-between",
                                }}
                              >
                                <Box
                                  sx={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 1,
                                  }}
                                >
                                  <Code
                                    sx={{
                                      color: getFrameworkColor(framework.name),
                                      fontSize: 28,
                                    }}
                                  />
                                  <Typography
                                    variant="h6"
                                    sx={{
                                      fontWeight: 700,
                                      color: "#0F172A",
                                      textTransform: "capitalize",
                                    }}
                                  >
                                    {framework.name}
                                  </Typography>
                                </Box>
                                <Chip
                                  label={`${framework.proficiency}%`}
                                  size="small"
                                  sx={{
                                    fontWeight: 700,
                                    bgcolor:
                                      framework.proficiency >= 80
                                        ? "#DCFCE7"
                                        : framework.proficiency >= 50
                                        ? "#FEF3C7"
                                        : "#FEE2E2",
                                    color:
                                      framework.proficiency >= 80
                                        ? "#15803D"
                                        : framework.proficiency >= 50
                                        ? "#92400E"
                                        : "#991B1B",
                                  }}
                                />
                              </Box>

                              {/* Progress Bar */}
                              <Box>
                                <LinearProgress
                                  variant="determinate"
                                  value={framework.proficiency}
                                  sx={{
                                    height: 10,
                                    borderRadius: 5,
                                    backgroundColor: "#E2E8F0",
                                    "& .MuiLinearProgress-bar": {
                                      backgroundColor: getFrameworkColor(
                                        framework.name
                                      ),
                                      borderRadius: 5,
                                    },
                                  }}
                                />
                              </Box>

                              {/* Stats */}
                              <Box
                                sx={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  pt: 1,
                                }}
                              >
                                <Box>
                                  <Typography
                                    variant="h5"
                                    sx={{ fontWeight: 700, color: "#10B981" }}
                                  >
                                    {framework.solved}
                                  </Typography>
                                  <Typography
                                    variant="caption"
                                    sx={{ color: "#64748B" }}
                                  >
                                    Solved
                                  </Typography>
                                </Box>
                                <Box>
                                  <Typography
                                    variant="h5"
                                    sx={{ fontWeight: 700, color: "#64748B" }}
                                  >
                                    {framework.total}
                                  </Typography>
                                  <Typography
                                    variant="caption"
                                    sx={{ color: "#64748B" }}
                                  >
                                    Total
                                  </Typography>
                                </Box>
                                <Box>
                                  <Typography
                                    variant="h5"
                                    sx={{ fontWeight: 700, color: "#EF4444" }}
                                  >
                                    {framework.total - framework.solved}
                                  </Typography>
                                  <Typography
                                    variant="caption"
                                    sx={{ color: "#64748B" }}
                                  >
                                    Remaining
                                  </Typography>
                                </Box>
                              </Box>

                              {/* Proficiency Level */}
                              <Divider />
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 1,
                                }}
                              >
                                <Star
                                  sx={{
                                    color:
                                      framework.proficiency >= 80
                                        ? "#F59E0B"
                                        : "#CBD5E1",
                                    fontSize: 20,
                                  }}
                                />
                                <Typography
                                  variant="body2"
                                  sx={{
                                    color: "#64748B",
                                    fontWeight: 600,
                                  }}
                                >
                                  {framework.proficiency >= 80
                                    ? "Expert"
                                    : framework.proficiency >= 50
                                    ? "Intermediate"
                                    : "Beginner"}
                                </Typography>
                              </Box>
                            </Stack>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Alert severity="info">
                    No framework data yet. Start solving problems to see your
                    framework statistics!
                  </Alert>
                )}

                {/* Difficulty Breakdown */}
                {difficultyStats.length > 0 && (
                  <Box sx={{ mt: 5 }}>
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 600, color: "#0F172A", mb: 3 }}
                    >
                      Difficulty Breakdown
                    </Typography>
                    <Grid container spacing={3}>
                      {difficultyStats.map((difficulty) => (
                        <Grid item xs={12} sm={6} md={3} key={difficulty.level}>
                          <Card
                            sx={{
                              border: "1px solid #E2E8F0",
                              borderRadius: 2,
                              bgcolor: `${difficulty.color}10`,
                            }}
                          >
                            <CardContent sx={{ p: 3, textAlign: "center" }}>
                              <Chip
                                label={difficulty.level}
                                size="small"
                                color={getDifficultyColor(
                                  difficulty.level.toLowerCase()
                                )}
                                sx={{ mb: 2, fontWeight: 600 }}
                              />
                              <Typography
                                variant="h4"
                                sx={{
                                  fontWeight: 800,
                                  color: difficulty.color,
                                  mb: 1,
                                }}
                              >
                                {difficulty.solved}/{difficulty.total}
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={
                                  difficulty.total > 0
                                    ? (difficulty.solved / difficulty.total) * 100
                                    : 0
                                }
                                sx={{
                                  height: 6,
                                  borderRadius: 3,
                                  backgroundColor: "#E2E8F0",
                                  "& .MuiLinearProgress-bar": {
                                    backgroundColor: difficulty.color,
                                    borderRadius: 3,
                                  },
                                }}
                              />

                              <LinearProgress
                                variant="determinate"
                                value={
                                  difficulty.total > 0
                                    ? (difficulty.solved / difficulty.total) *
                                      100
                                    : 0
                                }
                                sx={{
                                  height: 6,
                                  borderRadius: 3,
                                  backgroundColor: "#E2E8F0",
                                  "& .MuiLinearProgress-bar": {
                                    backgroundColor: difficulty.color,
                                    borderRadius: 3,
                                  },
                                }}
                              />
                              <Typography
                                variant="caption"
                                sx={{
                                  color: "#64748B",
                                  mt: 1,
                                  display: "block",
                                }}
                              >
                                {difficulty.total > 0
                                  ? Math.round(
                                      (difficulty.solved / difficulty.total) *
                                        100
                                    )
                                  : 0}
                                % Complete
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                )}
              </Box>
            )}
          </CardContent>
        </Card>
        {/* Quick Actions */}
        <Box sx={{ mt: 4, display: "flex", gap: 2, justifyContent: "center" }}>
          <Button
            variant="contained"
            component={Link}
            to="/problems"
            startIcon={<Code />}
          >
            Browse Challenges
          </Button>
          <Button
            variant="outlined"
            component={Link}
            to="/submissions"
            startIcon={<TrendingUp />}
          >
            View All Submissions
          </Button>
          <Button variant="outlined" color="error" onClick={logout}>
            Logout
          </Button>
        </Box>
      </Container>

      {/* EDIT PROFILE MODAL */}
      <Dialog
        open={editModalOpen}
        onClose={handleCloseModal}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Edit Profile
            </Typography>
            <IconButton
              onClick={handleCloseModal}
              disabled={saving}
              size="small"
            >
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            {/* Personal Information */}
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 600,
                color: "text.primary",
                borderBottom: "1px solid #E2E8F0",
                pb: 1,
              }}
            >
              <AccountCircle sx={{ mr: 1, verticalAlign: "middle" }} />
              Personal Information
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="First Name"
                  value={formData.first_name}
                  onChange={(e) =>
                    handleFormChange("first_name", e.target.value)
                  }
                  fullWidth
                  disabled={saving}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Last Name"
                  value={formData.last_name}
                  onChange={(e) =>
                    handleFormChange("last_name", e.target.value)
                  }
                  fullWidth
                  disabled={saving}
                />
              </Grid>
            </Grid>

            {/* Bio */}
            <TextField
              label="Bio"
              value={formData.bio}
              onChange={(e) => handleFormChange("bio", e.target.value)}
              fullWidth
              multiline
              rows={3}
              disabled={saving}
              helperText="Tell others about yourself (max 500 characters)"
              inputProps={{ maxLength: 500 }}
              placeholder="What do you want to share about yourself?"
            />

            {/* Preferences */}
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 600,
                color: "text.primary",
                borderBottom: "1px solid #E2E8F0",
                pb: 1,
              }}
            >
              <PaletteIcon sx={{ mr: 1, verticalAlign: "middle" }} />
              Preferences
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Preferred Language</InputLabel>
                  <Select
                    value={formData.preferred_language}
                    onChange={(e) =>
                      handleFormChange("preferred_language", e.target.value)
                    }
                    label="Preferred Language"
                    disabled={saving}
                  >
                    {availableOptions.languages.map((lang) => (
                      <MenuItem key={lang} value={lang}>
                        {lang.charAt(0).toUpperCase() + lang.slice(1)}
                      </MenuItem>
                    ))}
                  </Select>
                  <FormHelperText>
                    Your preferred programming language
                  </FormHelperText>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Theme</InputLabel>
                  <Select
                    value={formData.theme}
                    onChange={(e) => handleFormChange("theme", e.target.value)}
                    label="Theme"
                    disabled={saving}
                  >
                    {availableOptions.themes.map((theme) => (
                      <MenuItem key={theme} value={theme}>
                        {theme.charAt(0).toUpperCase() + theme.slice(1)}
                      </MenuItem>
                    ))}
                  </Select>
                  <FormHelperText>Choose light or dark mode</FormHelperText>
                </FormControl>
              </Grid>
            </Grid>

            {/* Email Notifications */}
            <FormControlLabel
              control={
                <Switch
                  checked={formData.email_notifications}
                  onChange={(e) =>
                    handleFormChange("email_notifications", e.target.checked)
                  }
                  disabled={saving}
                />
              }
              label={
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <EmailIcon sx={{ mr: 1 }} />
                  <Typography>Email Notifications</Typography>
                </Box>
              }
            />

            {/* Social Links */}
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 600,
                color: "text.primary",
                borderBottom: "1px solid #E2E8F0",
                pb: 1,
              }}
            >
              <LinkIcon sx={{ mr: 1, verticalAlign: "middle" }} />
              Social Links
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  label="GitHub Username"
                  value={formData.github_username}
                  onChange={(e) =>
                    handleFormChange("github_username", e.target.value)
                  }
                  fullWidth
                  disabled={saving}
                  helperText="Only alphanumeric, hyphens, and underscores allowed"
                  InputProps={{
                    startAdornment: (
                      <GitHub sx={{ mr: 1, color: "text.secondary" }} />
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Website URL"
                  value={formData.website_url}
                  onChange={(e) =>
                    handleFormChange("website_url", e.target.value)
                  }
                  fullWidth
                  disabled={saving}
                  helperText="Your personal website or portfolio"
                  InputProps={{
                    startAdornment: (
                      <LinkIcon sx={{ mr: 1, color: "text.secondary" }} />
                    ),
                  }}
                />
              </Grid>
            </Grid>

            {/* Preview Section */}
            <Box>
              <Typography
                variant="body2"
                sx={{ color: "text.secondary", mb: 1, fontWeight: 600 }}
              >
                Profile Preview
              </Typography>
              <Card variant="outlined" sx={{ p: 2, bgcolor: "grey.50" }}>
                <Typography
                  variant="body2"
                  sx={{ color: "text.secondary", mb: 1 }}
                >
                  <strong>Name:</strong> {formData.first_name}{" "}
                  {formData.last_name}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ color: "text.secondary", mb: 1 }}
                >
                  <strong>Bio:</strong>{" "}
                  {formData.bio || "Your bio will appear here..."}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ color: "text.secondary", mb: 1 }}
                >
                  <strong>Language:</strong> {formData.preferred_language} |{" "}
                  <strong>Theme:</strong> {formData.theme}
                </Typography>
                <Typography variant="body2" sx={{ color: "text.secondary" }}>
                  <strong>Email Notifications:</strong>{" "}
                  {formData.email_notifications ? "On" : "Off"}
                </Typography>
              </Card>
            </Box>
          </Stack>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button
            onClick={handleCloseModal}
            disabled={saving}
            sx={{ color: "text.secondary" }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSaveProfile}
            variant="contained"
            disabled={saving}
            startIcon={saving ? <CircularProgress size={20} /> : <Save />}
          >
            {saving ? "Saving..." : "Save All Changes"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* SNACKBAR */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Layout>
  );
}

export default Profile;
