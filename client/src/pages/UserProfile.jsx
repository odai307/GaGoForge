// src/pages/UserProfile.jsx
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Stack,
  Grid,
  Avatar,
  Tabs,
  Tab,
  LinearProgress,
  Divider,
} from "@mui/material";
import {
  EmojiEvents,
  TrendingUp,
  Code,
  Schedule,
  CalendarToday,
} from "@mui/icons-material";
import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import Layout from "../components/layout/Layout";

function UserProfile() {
  const { username } = useParams();
  const [activeTab, setActiveTab] = useState(0);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mock API call - Replace with actual API
  useEffect(() => {
    const fetchUserData = async () => {
      setLoading(true);
      // Simulate API call
      setTimeout(() => {
        const userData = getUserByUsername(username);
        setUser(userData);
        setLoading(false);
      }, 500);
    };

    fetchUserData();
  }, [username]);

  // Mock data function - Replace with actual API
  const getUserByUsername = (username) => {
    const users = {
      codeMaster: {
        username: "codeMaster",
        name: "Sarah Chen",
        bio: "Senior Full-Stack Developer | React Expert | Open Source Contributor",
        joinDate: "2023-11-20",
        stats: {
          totalSolved: 98,
          totalProblems: 110,
          streak: 42,
          rank: 1,
          experience: 2840,
          level: 5,
        },
        frameworkStats: [
          { name: "React", solved: 35, total: 35, proficiency: 100 },
          { name: "Django", solved: 28, total: 32, proficiency: 88 },
          { name: "Angular", solved: 20, total: 25, proficiency: 80 },
          { name: "Express", solved: 15, total: 18, proficiency: 83 },
        ],
        difficultyStats: [
          { level: "Beginner", solved: 40, total: 40, color: "#10B981" },
          { level: "Intermediate", solved: 38, total: 45, color: "#F59E0B" },
          { level: "Advanced", solved: 20, total: 25, color: "#EF4444" },
        ],
        achievements: [
          {
            id: 1,
            name: "React Master",
            description: "Complete all React challenges",
            icon: "⚛️",
            earned: true,
          },
          {
            id: 2,
            name: "Perfect Streak",
            description: "30-day coding streak",
            icon: "🔥",
            earned: true,
          },
          {
            id: 3,
            name: "Speed Demon",
            description: "Solve 10 challenges under 10min",
            icon: "⚡",
            earned: true,
          },
        ],
      },
      devWizard: {
        username: "devWizard",
        name: "Marcus Rodriguez",
        bio: "Backend Specialist | Django & Express | System Architecture",
        joinDate: "2023-12-15",
        stats: {
          totalSolved: 94,
          totalProblems: 110,
          streak: 35,
          rank: 2,
          experience: 2750,
          level: 5,
        },
        frameworkStats: [
          { name: "React", solved: 30, total: 35, proficiency: 86 },
          { name: "Django", solved: 32, total: 32, proficiency: 100 },
          { name: "Angular", solved: 18, total: 25, proficiency: 72 },
          { name: "Express", solved: 14, total: 18, proficiency: 78 },
        ],
        difficultyStats: [
          { level: "Beginner", solved: 40, total: 40, color: "#10B981" },
          { level: "Intermediate", solved: 36, total: 45, color: "#F59E0B" },
          { level: "Advanced", solved: 18, total: 25, color: "#EF4444" },
        ],
        achievements: [
          {
            id: 1,
            name: "Django Expert",
            description: "Complete all Django challenges",
            icon: "🐍",
            earned: true,
          },
          {
            id: 2,
            name: "Week Warrior",
            description: "7-day coding streak",
            icon: "🔥",
            earned: true,
          },
        ],
      },
    };

    return users[username] || null;
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
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
      default:
        return "#6B7280";
    }
  };

  const calculateLevelProgress = () => {
    if (!user) return 0;
    const currentLevelExp = user.stats.experience % 1000;
    return (currentLevelExp / 1000) * 100;
  };

  if (loading) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ py: 4, textAlign: "center" }}>
          <Typography variant="h6" sx={{ color: "#64748B" }}>
            Loading profile...
          </Typography>
        </Container>
      </Layout>
    );
  }

  if (!user) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ py: 4, textAlign: "center" }}>
          <Typography variant="h4" sx={{ color: "#64748B", mb: 2 }}>
            User not found
          </Typography>
          <Typography variant="body1" sx={{ color: "#94A3B8" }}>
            The user @{username} doesn't exist or hasn't joined yet.
          </Typography>
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
                  {user.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </Avatar>
                <Chip
                  label={`Rank #${user.stats.rank}`}
                  color="primary"
                  sx={{ fontWeight: 600 }}
                />
              </Box>

              {/* User Details */}
              <Box sx={{ flexGrow: 1 }}>
                <Typography
                  variant="h4"
                  sx={{ fontWeight: 800, color: "#0F172A", mb: 1 }}
                >
                  {user.name}
                </Typography>
                <Typography
                  variant="body1"
                  sx={{ color: "#64748B", mb: 2, fontWeight: 600 }}
                >
                  @{user.username}
                </Typography>

                <Typography
                  variant="body1"
                  sx={{ color: "#64748B", mb: 3, lineHeight: 1.6 }}
                >
                  {user.bio}
                </Typography>

                {/* Join Date */}
                <Typography
                  variant="body2"
                  sx={{
                    color: "#94A3B8",
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                  }}
                >
                  <CalendarToday sx={{ fontSize: 16 }} />
                  Joined{" "}
                  {new Date(user.joinDate).toLocaleDateString("en-US", {
                    month: "long",
                    year: "numeric",
                  })}
                </Typography>
              </Box>

              {/* Level Progress */}
              <Box sx={{ minWidth: 200 }}>
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 600, color: "#0F172A", mb: 1 }}
                >
                  Level {user.stats.level}
                </Typography>
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 2, mb: 1 }}
                >
                  <LinearProgress
                    variant="determinate"
                    value={calculateLevelProgress()}
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
                    {calculateLevelProgress().toFixed(0)}%
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: "#64748B" }}>
                  {user.stats.experience} Total XP
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
                <EmojiEvents sx={{ fontSize: 40, color: "#10B981", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: 800, color: "#0F172A", mb: 0.5 }}
                >
                  {user.stats.totalSolved}
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748B" }}>
                  Problems Solved
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
                  #{user.stats.rank}
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
                <Code sx={{ fontSize: 40, color: "#F59E0B", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: 800, color: "#0F172A", mb: 0.5 }}
                >
                  {user.stats.streak}
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748B" }}>
                  Day Streak
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
                <Schedule sx={{ fontSize: 40, color: "#8B5CF6", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: 800, color: "#0F172A", mb: 0.5 }}
                >
                  {user.frameworkStats.length}
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748B" }}>
                  Frameworks
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Main Content Tabs */}
        <Card sx={{ border: "1px solid #E2E8F0", borderRadius: 3 }}>
          <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab label="Skills & Progress" />
              <Tab label="Achievements" />
            </Tabs>
          </Box>

          <CardContent sx={{ p: 3 }}>
            {/* Skills & Progress Tab */}
            {activeTab === 0 && (
              <Box>
                <Grid container spacing={4}>
                  {/* Framework Proficiency */}
                  <Grid item xs={12} md={6}>
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 600, color: "#0F172A", mb: 3 }}
                    >
                      Framework Mastery
                    </Typography>
                    <Stack spacing={3}>
                      {user.frameworkStats.map((framework) => (
                        <Box key={framework.name}>
                          <Stack
                            direction="row"
                            justifyContent="space-between"
                            sx={{ mb: 1 }}
                          >
                            <Typography
                              variant="body2"
                              sx={{ fontWeight: 600, color: "#0F172A" }}
                            >
                              {framework.name}
                            </Typography>
                            <Typography
                              variant="body2"
                              sx={{ color: "#64748B", fontWeight: 600 }}
                            >
                              {framework.solved}/{framework.total} (
                              {framework.proficiency}%)
                            </Typography>
                          </Stack>
                          <LinearProgress
                            variant="determinate"
                            value={framework.proficiency}
                            sx={{
                              height: 8,
                              borderRadius: 4,
                              backgroundColor: "#E2E8F0",
                              "& .MuiLinearProgress-bar": {
                                backgroundColor: getFrameworkColor(
                                  framework.name
                                ),
                                borderRadius: 4,
                              },
                            }}
                          />
                        </Box>
                      ))}
                    </Stack>
                  </Grid>

                  {/* Difficulty Distribution */}
                  <Grid item xs={12} md={6}>
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 600, color: "#0F172A", mb: 3 }}
                    >
                      Challenge Progress
                    </Typography>
                    <Stack spacing={3}>
                      {user.difficultyStats.map((difficulty) => (
                        <Box key={difficulty.level}>
                          <Stack
                            direction="row"
                            justifyContent="space-between"
                            sx={{ mb: 1 }}
                          >
                            <Chip
                              label={difficulty.level}
                              size="small"
                              sx={{
                                backgroundColor: `${difficulty.color}15`,
                                color: difficulty.color,
                                fontWeight: 600,
                              }}
                            />
                            <Typography
                              variant="body2"
                              sx={{ color: "#64748B", fontWeight: 600 }}
                            >
                              {difficulty.solved}/{difficulty.total}
                            </Typography>
                          </Stack>
                          <LinearProgress
                            variant="determinate"
                            value={(difficulty.solved / difficulty.total) * 100}
                            sx={{
                              height: 8,
                              borderRadius: 4,
                              backgroundColor: "#E2E8F0",
                              "& .MuiLinearProgress-bar": {
                                backgroundColor: difficulty.color,
                                borderRadius: 4,
                              },
                            }}
                          />
                        </Box>
                      ))}
                    </Stack>
                  </Grid>
                </Grid>
              </Box>
            )}

            {/* Achievements Tab */}
            {activeTab === 1 && (
              <Box>
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 600, color: "#0F172A", mb: 3 }}
                >
                  Earned Achievements
                </Typography>
                <Grid container spacing={2}>
                  {user.achievements.map((achievement) => (
                    <Grid item xs={12} sm={6} md={4} key={achievement.id}>
                      <Card
                        sx={{
                          border: "1px solid #E2E8F0",
                          borderRadius: 3,
                        }}
                      >
                        <CardContent sx={{ p: 2.5, textAlign: "center" }}>
                          <Typography variant="h4" sx={{ mb: 1 }}>
                            {achievement.icon}
                          </Typography>
                          <Typography
                            variant="body1"
                            sx={{ fontWeight: 600, color: "#0F172A", mb: 1 }}
                          >
                            {achievement.name}
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{
                              color: "#64748B",
                              fontSize: "0.8rem",
                              lineHeight: 1.3,
                            }}
                          >
                            {achievement.description}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </CardContent>
        </Card>
      </Container>
    </Layout>
  );
}

export default UserProfile;
