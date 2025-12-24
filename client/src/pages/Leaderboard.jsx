// src/pages/Leaderboard.jsx
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
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from "@mui/material";
import {
  EmojiEvents,
  TrendingUp,
  Code,
  Search,
  FilterList,
  GitHub,
  LinkedIn,
  Twitter,
  Visibility,
  MilitaryTech,
  Star,
  Bolt,
  Whatshot,
  Lock,
  PersonAdd,
  Login as LoginIcon,
} from "@mui/icons-material";
import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/layout/Layout";
import { useAuth } from "../contexts/AuthContext";

function Leaderboard() {
  const { isLoggedIn, loading } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [timeFrame, setTimeFrame] = useState("all");
  const [frameworkFilter, setFrameworkFilter] = useState("all");

  // Mock leaderboard data - Replace with API call
  const leaderboardData = useMemo(
    () => ({
      global: [
        {
          rank: 1,
          username: "codeMaster",
          name: "Sarah Chen",
          avatar: "",
          score: 2840,
          problemsSolved: 98,
          streak: 42,
          frameworks: { react: 35, django: 28, angular: 20, express: 15 },
          joinDate: "2023-11-20",
          socialLinks: { github: "sarahchen", linkedin: "sarah-chen-dev" },
        },
        {
          rank: 2,
          username: "devWizard",
          name: "Marcus Rodriguez",
          avatar: "",
          score: 2750,
          problemsSolved: 94,
          streak: 35,
          frameworks: { react: 30, django: 32, angular: 18, express: 14 },
          joinDate: "2023-12-15",
          socialLinks: { github: "marcusrod", twitter: "marcus_dev" },
        },
        {
          rank: 3,
          username: "byteNinja",
          name: "Alex Thompson",
          avatar: "",
          score: 2680,
          problemsSolved: 89,
          streak: 28,
          frameworks: { react: 28, django: 25, angular: 22, express: 14 },
          joinDate: "2024-01-08",
          socialLinks: { github: "byteninja", linkedin: "alex-thompson-dev" },
        },
        {
          rank: 4,
          username: "reactGuru",
          name: "Jessica Wang",
          avatar: "",
          score: 2520,
          problemsSolved: 85,
          streak: 31,
          frameworks: { react: 40, django: 20, angular: 15, express: 10 },
          joinDate: "2024-01-22",
          socialLinks: { github: "jessw", twitter: "jessreact" },
        },
        {
          rank: 5,
          username: "pythonPro",
          name: "David Kim",
          avatar: "",
          score: 2450,
          problemsSolved: 82,
          streak: 25,
          frameworks: { react: 18, django: 38, angular: 12, express: 14 },
          joinDate: "2023-12-30",
          socialLinks: { github: "davidkim-py", linkedin: "david-kim-python" },
        },
        {
          rank: 156,
          username: "coder123",
          name: "Alex Johnson",
          avatar: "",
          score: 1240,
          problemsSolved: 42,
          streak: 7,
          frameworks: { react: 18, django: 12, angular: 8, express: 4 },
          joinDate: "2024-01-15",
          socialLinks: { github: "coder123", linkedin: "alexjohnson" },
        },
      ],
      weekly: [
        {
          rank: 1,
          username: "devWizard",
          name: "Marcus Rodriguez",
          score: 450,
          problemsSolved: 15,
          streak: 7,
          change: "+2",
        },
        {
          rank: 2,
          username: "byteNinja",
          name: "Alex Thompson",
          score: 420,
          problemsSolved: 14,
          streak: 7,
          change: "+3",
        },
        {
          rank: 3,
          username: "codeMaster",
          name: "Sarah Chen",
          score: 380,
          problemsSolved: 12,
          streak: 7,
          change: "-2",
        },
      ],
      frameworks: {
        react: [
          {
            rank: 1,
            username: "reactGuru",
            name: "Jessica Wang",
            score: 1600,
            problemsSolved: 40,
          },
          {
            rank: 2,
            username: "codeMaster",
            name: "Sarah Chen",
            score: 1400,
            problemsSolved: 35,
          },
          {
            rank: 3,
            username: "devWizard",
            name: "Marcus Rodriguez",
            score: 1200,
            problemsSolved: 30,
          },
        ],
        django: [
          {
            rank: 1,
            username: "pythonPro",
            name: "David Kim",
            score: 1520,
            problemsSolved: 38,
          },
          {
            rank: 2,
            username: "devWizard",
            name: "Marcus Rodriguez",
            score: 1280,
            problemsSolved: 32,
          },
          {
            rank: 3,
            username: "codeMaster",
            name: "Sarah Chen",
            score: 1120,
            problemsSolved: 28,
          },
        ],
        angular: [
          {
            rank: 1,
            username: "codeMaster",
            name: "Sarah Chen",
            score: 800,
            problemsSolved: 20,
          },
          {
            rank: 2,
            username: "byteNinja",
            name: "Alex Thompson",
            score: 720,
            problemsSolved: 18,
          },
          {
            rank: 3,
            username: "reactGuru",
            name: "Jessica Wang",
            score: 600,
            problemsSolved: 15,
          },
        ],
        express: [
          {
            rank: 1,
            username: "devWizard",
            name: "Marcus Rodriguez",
            score: 560,
            problemsSolved: 14,
          },
          {
            rank: 2,
            username: "codeMaster",
            name: "Sarah Chen",
            score: 520,
            problemsSolved: 13,
          },
          {
            rank: 3,
            username: "pythonPro",
            name: "David Kim",
            score: 480,
            problemsSolved: 12,
          },
        ],
      },
    }),
    []
  );

  const frameworks = [
    { value: "all", label: "All Frameworks" },
    { value: "react", label: "React" },
    { value: "django", label: "Django" },
    { value: "angular", label: "Angular" },
    { value: "express", label: "Express" },
  ];

  const timeFrames = [
    { value: "all", label: "All Time" },
    { value: "weekly", label: "This Week" },
    { value: "monthly", label: "This Month" },
  ];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getRankColor = (rank) => {
    if (rank === 1) return "#FFD700"; // Gold
    if (rank === 2) return "#C0C0C0"; // Silver
    if (rank === 3) return "#CD7F32"; // Bronze
    return "transparent";
  };

  const getRankIcon = (rank) => {
    if (rank === 1)
      return <EmojiEvents sx={{ color: "#FFD700", fontSize: 24 }} />;
    if (rank === 2)
      return <EmojiEvents sx={{ color: "#C0C0C0", fontSize: 24 }} />;
    if (rank === 3)
      return <EmojiEvents sx={{ color: "#CD7F32", fontSize: 24 }} />;
    return (
      <Typography variant="h6" sx={{ fontWeight: 700, color: "#64748B" }}>
        #{rank}
      </Typography>
    );
  };

  const getFrameworkColor = (framework) => {
    switch (framework) {
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

  const filteredData = useMemo(() => {
    let data =
      activeTab === 0
        ? leaderboardData.global
        : activeTab === 1
        ? leaderboardData.weekly
        : leaderboardData.frameworks[frameworkFilter] || [];

    if (searchTerm) {
      data = data.filter(
        (user) =>
          user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          user.username.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return data;
  }, [activeTab, frameworkFilter, searchTerm, leaderboardData]);

  const currentUser = leaderboardData.global.find(
    (user) => user.username === "coder123"
  );

  // Show loading state
  if (loading) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ py: { xs: 2, md: 3 } }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
            <Typography variant="h6" sx={{ color: "#64748B" }}>
              Loading...
            </Typography>
          </Box>
        </Container>
      </Layout>
    );
  }

  // Show authentication required message if not logged in
  if (!isLoggedIn) {
    return (
      <Layout>
        <Container maxWidth="md" sx={{ py: { xs: 4, md: 8 } }}>
          <Card
            sx={{
              border: "1px solid #E2E8F0",
              borderRadius: 3,
              boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            }}
          >
            <CardContent sx={{ p: { xs: 4, md: 6 }, textAlign: "center" }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  mx: "auto",
                  mb: 3,
                  boxShadow: "0 8px 24px rgba(102, 126, 234, 0.4)",
                }}
              >
                <Lock sx={{ fontSize: 40, color: "white" }} />
              </Box>

              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: "#0F172A",
                  mb: 2,
                }}
              >
                Authentication Required
              </Typography>

              <Typography
                variant="body1"
                sx={{
                  color: "#64748B",
                  mb: 4,
                  maxWidth: 500,
                  mx: "auto",
                  lineHeight: 1.7,
                }}
              >
                You need to be authenticated to access the leaderboard. Sign up or log in to compete with developers worldwide and see your ranking!
              </Typography>

              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={2}
                justifyContent="center"
                sx={{ mt: 4 }}
              >
                <Button
                  component={Link}
                  to="/register"
                  variant="contained"
                  size="large"
                  startIcon={<PersonAdd />}
                  sx={{
                    py: 1.5,
                    px: 4,
                    borderRadius: 2,
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    boxShadow: "0 4px 20px rgba(102, 126, 234, 0.4)",
                    fontSize: "1rem",
                    fontWeight: 600,
                    textTransform: "none",
                    "&:hover": {
                      background:
                        "linear-gradient(135deg, #5568d3 0%, #63408a 100%)",
                      boxShadow: "0 6px 28px rgba(102, 126, 234, 0.5)",
                      transform: "translateY(-2px)",
                    },
                    transition: "all 0.3s ease",
                  }}
                >
                  Create Account
                </Button>

                <Button
                  component={Link}
                  to="/login"
                  variant="outlined"
                  size="large"
                  startIcon={<LoginIcon />}
                  sx={{
                    py: 1.5,
                    px: 4,
                    borderRadius: 2,
                    borderColor: "#667eea",
                    borderWidth: 2,
                    color: "#667eea",
                    fontSize: "1rem",
                    fontWeight: 600,
                    textTransform: "none",
                    "&:hover": {
                      borderColor: "#5568d3",
                      backgroundColor: "#F8FAFC",
                      borderWidth: 2,
                      transform: "translateY(-2px)",
                    },
                    transition: "all 0.3s ease",
                  }}
                >
                  Sign In
                </Button>
              </Stack>

              <Typography
                variant="body2"
                sx={{
                  color: "#94A3B8",
                  mt: 4,
                }}
              >
                Already have an account?{" "}
                <Link
                  to="/login"
                  style={{
                    color: "#667eea",
                    fontWeight: 600,
                    textDecoration: "none",
                  }}
                >
                  Sign in here
                </Link>
                {" "}or{" "}
                <Link
                  to="/register"
                  style={{
                    color: "#667eea",
                    fontWeight: 600,
                    textDecoration: "none",
                  }}
                >
                  create a new account
                </Link>
              </Typography>
            </CardContent>
          </Card>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ py: { xs: 2, md: 3 } }}>
        {/* Header Section */}
        <Box sx={{ mb: 4 }}>
          <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
            <EmojiEvents sx={{ fontSize: 40, color: "#F59E0B" }} />
            <Box>
              <Typography
                variant="h3"
                sx={{ fontWeight: 800, color: "#0F172A" }}
              >
                Leaderboard
              </Typography>
              <Typography variant="body1" sx={{ color: "#64748B" }}>
                Compete with developers worldwide and climb the ranks
              </Typography>
            </Box>
          </Stack>

          {/* Current User Rank Card */}
          {currentUser && (
            <Card
              sx={{
                border: "2px solid #3B82F6",
                borderRadius: 3,
                background: "linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)",
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Stack
                  direction="row"
                  alignItems="center"
                  justifyContent="space-between"
                >
                  <Stack direction="row" alignItems="center" spacing={3}>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography
                        variant="h4"
                        sx={{ fontWeight: 800, color: "#1E40AF" }}
                      >
                        #{currentUser.rank}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ color: "#64748B", fontWeight: 600 }}
                      >
                        Your Rank
                      </Typography>
                    </Box>
                    <Avatar
                      sx={{
                        width: 60,
                        height: 60,
                        bgcolor: "#3B82F6",
                        fontWeight: 700,
                      }}
                    >
                      {currentUser.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </Avatar>
                    <Box>
                      <Typography
                        variant="h6"
                        sx={{ fontWeight: 700, color: "#0F172A" }}
                      >
                        {currentUser.name}
                      </Typography>
                      <Typography variant="body2" sx={{ color: "#64748B" }}>
                        @{currentUser.username}
                      </Typography>
                    </Box>
                  </Stack>
                  <Stack direction="row" spacing={4} alignItems="center">
                    <Box sx={{ textAlign: "center" }}>
                      <Typography
                        variant="h6"
                        sx={{ fontWeight: 800, color: "#0F172A" }}
                      >
                        {currentUser.score}
                      </Typography>
                      <Typography variant="body2" sx={{ color: "#64748B" }}>
                        Total Score
                      </Typography>
                    </Box>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography
                        variant="h6"
                        sx={{ fontWeight: 800, color: "#0F172A" }}
                      >
                        {currentUser.problemsSolved}
                      </Typography>
                      <Typography variant="body2" sx={{ color: "#64748B" }}>
                        Solved
                      </Typography>
                    </Box>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography
                        variant="h6"
                        sx={{ fontWeight: 800, color: "#0F172A" }}
                      >
                        {currentUser.streak}
                      </Typography>
                      <Typography variant="body2" sx={{ color: "#64748B" }}>
                        Day Streak
                      </Typography>
                    </Box>
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          )}
        </Box>

        {/* Filters and Tabs */}
        <Card sx={{ border: "1px solid #E2E8F0", borderRadius: 3, mb: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Stack spacing={3}>
              {/* Tabs */}
              <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
                <Tabs value={activeTab} onChange={handleTabChange}>
                  <Tab label="Global Rankings" />
                  <Tab label="Weekly Top" />
                  <Tab label="Framework Masters" />
                </Tabs>
              </Box>

              {/* Filters */}
              <Stack
                direction={{ xs: "column", md: "row" }}
                spacing={2}
                alignItems="center"
              >
                <TextField
                  placeholder="Search developers..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search sx={{ color: "#94A3B8" }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    flexGrow: 1,
                    "& .MuiOutlinedInput-root": {
                      backgroundColor: "#F8FAFC",
                    },
                  }}
                />

                {activeTab === 2 && (
                  <FormControl sx={{ minWidth: 200 }}>
                    <InputLabel>Framework</InputLabel>
                    <Select
                      value={frameworkFilter}
                      label="Framework"
                      onChange={(e) => setFrameworkFilter(e.target.value)}
                    >
                      {frameworks.map((framework) => (
                        <MenuItem key={framework.value} value={framework.value}>
                          {framework.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}

                {activeTab === 0 && (
                  <FormControl sx={{ minWidth: 200 }}>
                    <InputLabel>Time Frame</InputLabel>
                    <Select
                      value={timeFrame}
                      label="Time Frame"
                      onChange={(e) => setTimeFrame(e.target.value)}
                    >
                      {timeFrames.map((frame) => (
                        <MenuItem key={frame.value} value={frame.value}>
                          {frame.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              </Stack>
            </Stack>
          </CardContent>
        </Card>

        {/* Leaderboard Content */}
        <Card sx={{ border: "1px solid #E2E8F0", borderRadius: 3 }}>
          <CardContent sx={{ p: 0 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: "#F8FAFC" }}>
                    <TableCell
                      sx={{ width: 80, fontWeight: 700, color: "#0F172A" }}
                    >
                      Rank
                    </TableCell>
                    <TableCell sx={{ fontWeight: 700, color: "#0F172A" }}>
                      Developer
                    </TableCell>
                    <TableCell
                      align="center"
                      sx={{ fontWeight: 700, color: "#0F172A" }}
                    >
                      Score
                    </TableCell>
                    <TableCell
                      align="center"
                      sx={{ fontWeight: 700, color: "#0F172A" }}
                    >
                      Solved
                    </TableCell>
                    <TableCell
                      align="center"
                      sx={{ fontWeight: 700, color: "#0F172A" }}
                    >
                      Streak
                    </TableCell>
                    {activeTab === 0 && (
                      <TableCell
                        align="center"
                        sx={{ fontWeight: 700, color: "#0F172A" }}
                      >
                        Frameworks
                      </TableCell>
                    )}
                    {activeTab === 1 && (
                      <TableCell
                        align="center"
                        sx={{ fontWeight: 700, color: "#0F172A" }}
                      >
                        Change
                      </TableCell>
                    )}
                    <TableCell
                      align="center"
                      sx={{ fontWeight: 700, color: "#0F172A" }}
                    >
                      Actions
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredData.map((user) => (
                    <TableRow
                      key={user.username}
                      sx={{
                        "&:last-child td, &:last-child th": { border: 0 },
                        backgroundColor:
                          user.username === "coder123"
                            ? "#EFF6FF"
                            : "transparent",
                        "&:hover": {
                          backgroundColor:
                            user.username === "coder123"
                              ? "#E0F2FE"
                              : "#F8FAFC",
                        },
                      }}
                    >
                      {/* Rank */}
                      <TableCell>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          {getRankIcon(user.rank)}
                        </Box>
                      </TableCell>

                      {/* Developer Info */}
                      <TableCell>
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Avatar
                            sx={{
                              width: 40,
                              height: 40,
                              bgcolor: getRankColor(user.rank),
                              color: user.rank <= 3 ? "white" : "#3B82F6",
                              fontWeight: 700,
                            }}
                          >
                            {user.name
                              .split(" ")
                              .map((n) => n[0])
                              .join("")}
                          </Avatar>
                          <Box>
                            <Typography
                              variant="body1"
                              sx={{ fontWeight: 600, color: "#0F172A" }}
                            >
                              {user.name}
                            </Typography>
                            <Typography
                              variant="body2"
                              sx={{ color: "#64748B" }}
                            >
                              @{user.username}
                            </Typography>
                          </Box>
                          <Stack direction="row" spacing={0.5}>
                            {user.socialLinks?.github && (
                              <Tooltip title="GitHub">
                                <IconButton size="small">
                                  <GitHub sx={{ fontSize: 16 }} />
                                </IconButton>
                              </Tooltip>
                            )}
                            {user.socialLinks?.linkedin && (
                              <Tooltip title="LinkedIn">
                                <IconButton size="small">
                                  <LinkedIn sx={{ fontSize: 16 }} />
                                </IconButton>
                              </Tooltip>
                            )}
                            {user.socialLinks?.twitter && (
                              <Tooltip title="Twitter">
                                <IconButton size="small">
                                  <Twitter sx={{ fontSize: 16 }} />
                                </IconButton>
                              </Tooltip>
                            )}
                          </Stack>
                        </Stack>
                      </TableCell>

                      {/* Score */}
                      <TableCell align="center">
                        <Typography
                          variant="body1"
                          sx={{ fontWeight: 700, color: "#0F172A" }}
                        >
                          {user.score.toLocaleString()}
                        </Typography>
                      </TableCell>

                      {/* Problems Solved */}
                      <TableCell align="center">
                        <Typography
                          variant="body1"
                          sx={{ fontWeight: 600, color: "#0F172A" }}
                        >
                          {user.problemsSolved}
                        </Typography>
                      </TableCell>

                      {/* Streak */}
                      <TableCell align="center">
                        <Chip
                          icon={<Whatshot sx={{ color: "#EF4444" }} />}
                          label={user.streak}
                          size="small"
                          sx={{
                            backgroundColor: "#FEF2F2",
                            color: "#DC2626",
                            fontWeight: 600,
                          }}
                        />
                      </TableCell>

                      {/* Framework Progress (Global Rankings) */}
                      {activeTab === 0 && (
                        <TableCell align="center">
                          <Stack
                            direction="row"
                            spacing={1}
                            justifyContent="center"
                          >
                            {Object.entries(user.frameworks).map(
                              ([framework, count]) => (
                                <Tooltip
                                  key={framework}
                                  title={`${count} ${framework} challenges`}
                                >
                                  <Chip
                                    label={framework}
                                    size="small"
                                    sx={{
                                      backgroundColor: `${getFrameworkColor(
                                        framework
                                      )}10`,
                                      color: getFrameworkColor(framework),
                                      fontWeight: 600,
                                      fontSize: "0.7rem",
                                    }}
                                  />
                                </Tooltip>
                              )
                            )}
                          </Stack>
                        </TableCell>
                      )}

                      {/* Rank Change (Weekly) */}
                      {activeTab === 1 && (
                        <TableCell align="center">
                          <Chip
                            label={user.change}
                            size="small"
                            color={
                              user.change.startsWith("+") ? "success" : "error"
                            }
                            sx={{ fontWeight: 600 }}
                          />
                        </TableCell>
                      )}

                      {/* Actions */}
                      <TableCell align="center">
                        <Tooltip title="View Profile">
                          <IconButton
                            component={Link}
                            to={`/${user.username}`}
                            size="small"
                            sx={{ color: "#3B82F6" }}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Empty State */}
            {filteredData.length === 0 && (
              <Box sx={{ p: 8, textAlign: "center" }}>
                <EmojiEvents sx={{ fontSize: 64, color: "#E2E8F0", mb: 2 }} />
                <Typography variant="h6" sx={{ color: "#64748B", mb: 1 }}>
                  No developers found
                </Typography>
                <Typography variant="body2" sx={{ color: "#94A3B8" }}>
                  Try adjusting your search or filters
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Framework Masters Grid */}
        {activeTab === 2 && frameworkFilter === "all" && (
          <Box sx={{ mt: 4 }}>
            <Typography
              variant="h5"
              sx={{ fontWeight: 700, color: "#0F172A", mb: 3 }}
            >
              Framework Masters
            </Typography>
            <Grid container spacing={3}>
              {Object.entries(leaderboardData.frameworks).map(
                ([framework, topUsers]) => (
                  <Grid item xs={12} sm={6} md={3} key={framework}>
                    <Card sx={{ border: "1px solid #E2E8F0", borderRadius: 3 }}>
                      <CardContent sx={{ p: 3, textAlign: "center" }}>
                        <Box
                          sx={{
                            width: 60,
                            height: 60,
                            borderRadius: "50%",
                            backgroundColor: `${getFrameworkColor(
                              framework
                            )}10`,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            mx: "auto",
                            mb: 2,
                          }}
                        >
                          <Code
                            sx={{
                              fontSize: 30,
                              color: getFrameworkColor(framework),
                            }}
                          />
                        </Box>
                        <Typography
                          variant="h6"
                          sx={{
                            fontWeight: 700,
                            color: "#0F172A",
                            mb: 1,
                            textTransform: "capitalize",
                          }}
                        >
                          {framework}
                        </Typography>
                        <Stack spacing={2} sx={{ mt: 2 }}>
                          {topUsers.map((user) => (
                            <Box
                              key={user.username}
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                              }}
                            >
                              <Typography
                                variant="body2"
                                sx={{ fontWeight: 600, color: "#0F172A" }}
                              >
                                {user.name}
                              </Typography>
                              <Typography
                                variant="body2"
                                sx={{ color: "#64748B", fontWeight: 600 }}
                              >
                                {user.problemsSolved} solved
                              </Typography>
                            </Box>
                          ))}
                        </Stack>
                      </CardContent>
                    </Card>
                  </Grid>
                )
              )}
            </Grid>
          </Box>
        )}
      </Container>
    </Layout>
  );
}

export default Leaderboard;
