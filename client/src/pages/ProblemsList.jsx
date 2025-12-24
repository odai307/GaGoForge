// src/pages/ProblemsList.jsx
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Button,
  Stack,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  Alert,
  Tooltip,
  Divider,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import {
  Search,
  FilterList,
  Code,
  PlayArrow,
  CheckCircle,
  Lock,
  TrendingUp,
  Schedule,
  ClearAll,
  Info,
  Check,
  Close,
  Help,
  HourglassEmpty,
} from "@mui/icons-material";
import { useState, useMemo, useCallback, useEffect } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/layout/Layout";
import { problemsAPI } from "../services/problems";
import { progressAPI } from "../services/progress";
import { CircularProgress } from "@mui/material";
import { useAuth } from "../contexts/AuthContext";

function ProblemsList() {
  // State management
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFramework, setSelectedFramework] = useState("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState("all");
  const [progressFilter, setProgressFilter] = useState("all"); // "all", "solved", "attempted", "unattempted"
  const [currentPage, setCurrentPage] = useState(1);
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    total: 0,
    by_difficulty: {},
    by_framework: {},
  });
  const [userProgress, setUserProgress] = useState(new Map());
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
  });
  const PROBLEMS_PER_PAGE = 9;
  const { isLoggedIn } = useAuth();

  // Fetch problems and user progress
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const filters = {};
        if (selectedFramework !== "all") filters.framework = selectedFramework;
        if (selectedDifficulty !== "all") filters.difficulty = selectedDifficulty;
        if (searchTerm) filters.search = searchTerm;

        // Add pagination parameter - use 9 per page to match your frontend display
        const [problemsData, statsData] = await Promise.all([
          problemsAPI.getProblems(filters, currentPage, 9), // ← ADD THIS
          problemsAPI.getStats(),
        ]);

        if (problemsData.results) {
          setProblems(problemsData.results);
          setPagination({
            count: problemsData.count || problemsData.results.length,
            next: problemsData.next,
            previous: problemsData.previous,
          });
        } else if (Array.isArray(problemsData)) {
          setProblems(problemsData);
          setPagination({
            count: problemsData.length,
            next: null,
            previous: null,
          });
        } else {
          setProblems([]);
          setPagination({ count: 0, next: null, previous: null });
        }

        setStats(statsData);

        if (isLoggedIn) {
          try {
            const progressData = await progressAPI.getProgress();
            if (progressData.results) {
              const progressMap = new Map();
              progressData.results.forEach((progress) => {
                let problemKey = null;

                if (
                  typeof progress.problem === "object" &&
                  progress.problem !== null
                ) {
                  problemKey =
                    progress.problem.slug || progress.problem.id?.toString();
                } else if (progress.problem) {
                  problemKey = progress.problem.toString();
                }

                if (problemKey) {
                  progressMap.set(problemKey, progress);
                }
              });
              setUserProgress(progressMap);
            }
          } catch (progressErr) {
            console.error("Error fetching progress:", progressErr);
            setUserProgress(new Map());
          }
        } else {
          setUserProgress(new Map());
        }
      } catch (err) {
        console.error("Error fetching problems:", err);
        setError("Failed to load problems. Please try again later.");
        setProblems([]);
        setUserProgress(new Map());
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedFramework, selectedDifficulty, searchTerm, isLoggedIn, currentPage]);

  // Filter configurations
  const FRAMEWORKS = useMemo(
    () => [
      { value: "all", label: "All Frameworks" },
      { value: "react", label: "React" },
      { value: "django", label: "Django" },
      { value: "angular", label: "Angular" },
      { value: "express", label: "Express" },
    ],
    []
  );

  const DIFFICULTIES = useMemo(
    () => [
      { value: "all", label: "All Levels" },
      { value: "beginner", label: "Beginner" },
      { value: "intermediate", label: "Intermediate" },
      { value: "pro", label: "Pro" },
      { value: "veteran", label: "Veteran" },
    ],
    []
  );

  const PROGRESS_FILTERS = useMemo(
    () => [
      { value: "all", label: "All Problems", icon: <Help />, color: "default" },
      { value: "solved", label: "Solved", icon: <Check />, color: "success" },
      {
        value: "attempted",
        label: "Attempted",
        icon: <HourglassEmpty />,
        color: "warning",
      },
      {
        value: "unattempted",
        label: "Unattempted",
        icon: <Close />,
        color: "error",
      },
    ],
    []
  );

  // Utility functions
  const getDifficultyConfig = useCallback((difficulty) => {
    const configs = {
      beginner: { color: "success", label: "Beginner" },
      intermediate: { color: "warning", label: "Intermediate" },
      pro: { color: "error", label: "Pro" },
      veteran: { color: "error", label: "Veteran" },
    };
    return configs[difficulty] || { color: "default", label: difficulty };
  }, []);

  const getFrameworkConfig = useCallback((framework) => {
    const configs = {
      react: { color: "#61DAFB", name: "React" },
      django: { color: "#092E20", name: "Django" },
      angular: { color: "#DD0031", name: "Angular" },
      express: { color: "#000000", name: "Express" },
    };
    return configs[framework] || { color: "#6B7280", name: framework };
  }, []);

  // Function to check if problem is solved
  const getProblemProgress = useCallback(
    (problem) => {
      if (!isLoggedIn)
        return {
          isSolved: false,
          bestScore: 0,
          totalAttempts: 0,
          isAttempted: false,
        };

      const progress =
        userProgress.get(problem.slug) ||
        userProgress.get(problem.id?.toString()) ||
        userProgress.get(problem.problem_id?.toString());

      const isSolved = progress?.is_solved || false;
      const totalAttempts = progress?.total_attempts || 0;
      const isAttempted = totalAttempts > 0;

      return {
        isSolved,
        bestScore: progress?.best_score || 0,
        totalAttempts,
        isAttempted,
      };
    },
    [userProgress, isLoggedIn]
  );

  // Filter problems based on progress filter
  const filteredProblems = useMemo(() => {
    if (!isLoggedIn || progressFilter === "all") {
      return problems;
    }

    return problems.filter((problem) => {
      const { isSolved, isAttempted } = getProblemProgress(problem);

      switch (progressFilter) {
        case "solved":
          return isSolved;
        case "attempted":
          return isAttempted && !isSolved;
        case "unattempted":
          return !isAttempted;
        default:
          return true;
      }
    });
  }, [problems, progressFilter, isLoggedIn, getProblemProgress]);

  

// Calculate total pages from backend count
  const totalPages = Math.ceil(pagination.count / PROBLEMS_PER_PAGE); // Use backend count



  const averageAcceptance = useMemo(() => {
    if (problems.length === 0) return 0;
    const total = problems.reduce((sum, p) => {
      const value = Number(p.acceptance_rate ?? 0);
      return sum + (Number.isFinite(value) ? value : 0);
    }, 0);
    return Math.round(total / problems.length);
  }, [problems]);

  // Calculate progress statistics
  const progressStats = useMemo(() => {
    if (!isLoggedIn)
      return { solved: 0, attempted: 0, unattempted: problems.length };

    let solved = 0;
    let attempted = 0;
    let unattempted = 0;

    problems.forEach((problem) => {
      const { isSolved, isAttempted } = getProblemProgress(problem);
      if (isSolved) {
        solved++;
      } else if (isAttempted) {
        attempted++;
      } else {
        unattempted++;
      }
    });

    return { solved, attempted, unattempted };
  }, [problems, isLoggedIn, getProblemProgress]);

  // Event handlers
  const handleSearchChange = useCallback((event) => {
    setSearchTerm(event.target.value);
    setCurrentPage(1);
  }, []);

  const handleFrameworkChange = useCallback((event) => {
    setSelectedFramework(event.target.value);
    setCurrentPage(1);
  }, []);

  const handleDifficultyChange = useCallback((event) => {
    setSelectedDifficulty(event.target.value);
    setCurrentPage(1);
  }, []);

  const handleProgressFilterChange = useCallback((event, newFilter) => {
    if (newFilter !== null) {
      setProgressFilter(newFilter);
      setCurrentPage(1);
    }
  }, []);

  const handleClearFilters = useCallback(() => {
    setSearchTerm("");
    setSelectedFramework("all");
    setSelectedDifficulty("all");
    setProgressFilter("all");
    setCurrentPage(1);
  }, []);

  const handlePageChange = useCallback((event, value) => {
    setCurrentPage(value);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  const hasActiveFilters =
    searchTerm ||
    selectedFramework !== "all" ||
    selectedDifficulty !== "all" ||
    progressFilter !== "all";

  // Render stat card
  const StatCard = ({ icon, value, label, color }) => (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 2,
        p: 2,
        borderRadius: 2,
        backgroundColor: "#F8FAFC",
        minWidth: 180,
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          width: 48,
          height: 48,
          borderRadius: 2,
          backgroundColor: `${color}15`,
        }}
      >
        {icon}
      </Box>
      <Box>
        <Typography
          variant="h5"
          sx={{ fontWeight: 700, color: "#1A202C", lineHeight: 1 }}
        >
          {value}
        </Typography>
        <Typography variant="body2" sx={{ color: "#64748B", mt: 0.5 }}>
          {label}
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ py: { xs: 3, md: 5 } }}>
        {/* Header */}
        <Box sx={{ mb: 5 }}>
          <Typography
            variant="h3"
            component="h1"
            sx={{
              fontWeight: 800,
              color: "#0F172A",
              mb: 1.5,
              fontSize: { xs: "2rem", md: "2.5rem" },
            }}
          >
            Coding Challenges
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: "#64748B",
              fontSize: "1.125rem",
              maxWidth: "700px",
              lineHeight: 1.7,
            }}
          >
            Master modern frameworks through hands-on challenges. Practice
            real-world scenarios and improve your development skills.
          </Typography>
        </Box>

        {/* Stats Overview */}
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={2}
          sx={{ mb: 4, flexWrap: "wrap" }}
        >
          <StatCard
            icon={<Code sx={{ color: "#3B82F6", fontSize: 24 }} />}
            value={pagination.count || stats.total || problems.length}
            label="Total Challenges"
            color="#3B82F6"
          />
          <StatCard
            icon={<TrendingUp sx={{ color: "#10B981", fontSize: 24 }} />}
            value={`${averageAcceptance}%`}
            label="Avg Success Rate"
            color="#10B981"
          />
          {isLoggedIn && (
            <StatCard
              icon={<CheckCircle sx={{ color: "#8B5CF6", fontSize: 24 }} />}
              value={progressStats.solved}
              label="You Solved"
              color="#8B5CF6"
            />
          )}
        </Stack>

        {/* Filters */}
        <Card
          sx={{
            mb: 4,
            border: "1px solid #E2E8F0",
            borderRadius: 3,
            boxShadow: "0 1px 3px rgba(0, 0, 0, 0.05)",
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Stack spacing={2.5}>
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
              >
                <Stack direction="row" alignItems="center" spacing={1}>
                  <FilterList sx={{ color: "#64748B" }} />
                  <Typography
                    variant="h6"
                    sx={{ fontWeight: 600, color: "#0F172A" }}
                  >
                    Filter Challenges
                  </Typography>
                </Stack>
                {hasActiveFilters && (
                  <Button
                    size="small"
                    startIcon={<ClearAll />}
                    onClick={handleClearFilters}
                    sx={{
                      textTransform: "none",
                      color: "#64748B",
                      "&:hover": { backgroundColor: "#F1F5F9" },
                    }}
                  >
                    Clear all
                  </Button>
                )}
              </Stack>

              <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                <TextField
                  fullWidth
                  placeholder="Search by title, description, or tags..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search sx={{ color: "#94A3B8" }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      backgroundColor: "#F8FAFC",
                      "&:hover fieldset": {
                        borderColor: "#3B82F6",
                      },
                      "&.Mui-focused": {
                        backgroundColor: "white",
                      },
                    },
                  }}
                />

                <FormControl sx={{ minWidth: { xs: "100%", md: 200 } }}>
                  <InputLabel id="framework-label">Framework</InputLabel>
                  <Select
                    labelId="framework-label"
                    value={selectedFramework}
                    label="Framework"
                    onChange={handleFrameworkChange}
                    sx={{ backgroundColor: "#F8FAFC" }}
                  >
                    {FRAMEWORKS.map((framework) => (
                      <MenuItem key={framework.value} value={framework.value}>
                        {framework.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl sx={{ minWidth: { xs: "100%", md: 200 } }}>
                  <InputLabel id="difficulty-label">Difficulty</InputLabel>
                  <Select
                    labelId="difficulty-label"
                    value={selectedDifficulty}
                    label="Difficulty"
                    onChange={handleDifficultyChange}
                    sx={{ backgroundColor: "#F8FAFC" }}
                  >
                    {DIFFICULTIES.map((difficulty) => (
                      <MenuItem key={difficulty.value} value={difficulty.value}>
                        {difficulty.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Stack>

              {/* Progress Filter - Only show if logged in */}
              {isLoggedIn && (
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{
                      color: "#64748B",
                      fontWeight: 600,
                      mb: 1,
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                    }}
                  >
                    <CheckCircle sx={{ fontSize: 18 }} />
                    Filter by Your Progress
                  </Typography>
                  <ToggleButtonGroup
                    value={progressFilter}
                    exclusive
                    onChange={handleProgressFilterChange}
                    aria-label="progress filter"
                    sx={{
                      width: "100%",
                      "& .MuiToggleButton-root": {
                        flex: 1,
                        py: 1,
                        textTransform: "none",
                        fontWeight: 600,
                        borderColor: "#E2E8F0",
                        "&.Mui-selected": {
                          backgroundColor: "#3B82F615",
                          color: "#1D4ED8",
                          borderColor: "#3B82F6",
                          "&:hover": {
                            backgroundColor: "#3B82F620",
                          },
                        },
                        "&:not(.Mui-selected)": {
                          "&:hover": {
                            backgroundColor: "#F8FAFC",
                          },
                        },
                      },
                    }}
                  >
                    {PROGRESS_FILTERS.map((filter) => (
                      <ToggleButton
                        key={filter.value}
                        value={filter.value}
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                        }}
                      >
                        {filter.icon}
                        {filter.label}
                        {filter.value !== "all" && (
                          <Chip
                            label={
                              filter.value === "solved"
                                ? progressStats.solved
                                : filter.value === "attempted"
                                ? progressStats.attempted
                                : progressStats.unattempted
                            }
                            size="small"
                            sx={{
                              height: 20,
                              fontSize: "0.7rem",
                              fontWeight: 700,
                              backgroundColor:
                                filter.color === "success"
                                  ? "#10B98120"
                                  : filter.color === "warning"
                                  ? "#F59E0B20"
                                  : filter.color === "error"
                                  ? "#EF444420"
                                  : "#6B728020",
                              color:
                                filter.color === "success"
                                  ? "#059669"
                                  : filter.color === "warning"
                                  ? "#D97706"
                                  : filter.color === "error"
                                  ? "#DC2626"
                                  : "#4B5563",
                            }}
                          />
                        )}
                      </ToggleButton>
                    ))}
                  </ToggleButtonGroup>
                </Box>
              )}
            </Stack>
          </CardContent>
        </Card>

        {/* Loading state */}
        {loading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Error state */}
        {error && !loading && (
          <Alert
            severity="error"
            sx={{
              mb: 4,
              borderRadius: 2,
            }}
          >
            {error}
          </Alert>
        )}

        {/* Results info */}
        {!loading && !error && (
          <Box sx={{ mb: 3 }}>
            <Typography
              variant="body2"
              sx={{ color: "#64748B", fontWeight: 500 }}
            >
              Showing {problems.length} of {pagination.count}
              challenge
              {pagination.count !== 1 ? "s" : ""}
              {hasActiveFilters && " (filtered)"}
              {isLoggedIn && progressFilter !== "all" && (
                <>
                  {" • "}
                  {progressFilter === "solved" &&
                    `${progressStats.solved} solved`}
                  {progressFilter === "attempted" &&
                    `${progressStats.attempted} attempted`}
                  {progressFilter === "unattempted" &&
                    `${progressStats.unattempted} unattempted`}
                </>
              )}
            </Typography>
          </Box>
        )}

        {/* Empty state */}
        {!loading && !error && filteredProblems.length === 0 && (
          <Alert
            severity="info"
            icon={<Info />}
            sx={{
              mb: 4,
              borderRadius: 2,
              "& .MuiAlert-message": { width: "100%" },
            }}
          >
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
              No challenges found
            </Typography>
            <Typography variant="body2">
              {progressFilter !== "all" && isLoggedIn
                ? `No ${progressFilter} challenges match your filters. Try adjusting your filters.`
                : "Try adjusting your filters or search term to find what you're looking for."}
            </Typography>
          </Alert>
        )}

        {/* Problems Grid */}
        {!loading && !error && (
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "1fr",
                sm: "repeat(2, 1fr)",
                md: "repeat(3, 1fr)",
              },
              gap: 3,
              width: "100%",
            }}
          >
            {problems.map((problem) => {
              const frameworkName =
                typeof problem.framework === "string"
                  ? problem.framework
                  : problem.framework?.name || problem.framework;
              const frameworkConfig = getFrameworkConfig(frameworkName);
              const difficultyConfig = getDifficultyConfig(problem.difficulty);
              const { isSolved, bestScore, totalAttempts, isAttempted } =
                getProblemProgress(problem);
              const acceptanceRateValue = Number(problem.acceptance_rate ?? 0);
              const acceptanceRate = Number.isFinite(acceptanceRateValue)
                ? acceptanceRateValue
                : 0;
              const displayAcceptanceRate = acceptanceRate.toFixed(0);
              const estimatedTime = problem.estimated_time_minutes
                ? `${problem.estimated_time_minutes} min`
                : "N/A";

              return (
                <Card
                  key={problem.id || problem.slug}
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    border: "2px solid",
                    borderColor: isSolved
                      ? "#10B981"
                      : isAttempted
                      ? "#F59E0B"
                      : "#E2E8F0",
                    borderRadius: 3,
                    transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                    "&:hover": {
                      transform: "translateY(-4px)",
                      boxShadow: "0 12px 32px rgba(0, 0, 0, 0.1)",
                      borderColor: isSolved
                        ? "#059669"
                        : isAttempted
                        ? "#D97706"
                        : "#3B82F6",
                    },
                  }}
                >
                  <CardContent
                    sx={{
                      p: 3,
                      height: "100%",
                      display: "flex",
                      flexDirection: "column",
                      "&:last-child": { pb: 3 },
                    }}
                  >
                    {/* Header with badges */}
                    <Stack
                      direction="row"
                      spacing={1}
                      alignItems="center"
                      sx={{ mb: 2 }}
                    >
                      <Chip
                        label={frameworkConfig.name}
                        size="small"
                        sx={{
                          backgroundColor: `${frameworkConfig.color}10`,
                          color: frameworkConfig.color,
                          fontWeight: 600,
                          fontSize: "0.75rem",
                          border: `1px solid ${frameworkConfig.color}30`,
                        }}
                      />
                      <Chip
                        label={difficultyConfig.label}
                        size="small"
                        color={difficultyConfig.color}
                        sx={{ fontWeight: 600, fontSize: "0.75rem" }}
                      />
                      {problem.is_premium && (
                        <Chip
                          icon={<Lock sx={{ fontSize: 14 }} />}
                          label="PRO"
                          size="small"
                          sx={{
                            background:
                              "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)",
                            color: "white",
                            fontWeight: 700,
                            fontSize: "0.7rem",
                            "& .MuiChip-icon": { color: "white" },
                          }}
                        />
                      )}
                    </Stack>

                    {/* Title */}
                    <Typography
                      variant="h6"
                      component="h3"
                      sx={{
                        fontWeight: 700,
                        color: "#0F172A",
                        mb: 1.5,
                        lineHeight: 1.4,
                        minHeight: "44px",
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}
                    >
                      {problem.title}
                    </Typography>

                    {/* Description */}
                    <Typography
                      variant="body2"
                      sx={{
                        color: "#64748B",
                        lineHeight: 1.6,
                        mb: 2,
                        flexGrow: 1,
                        minHeight: "60px",
                        display: "-webkit-box",
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}
                    >
                      {problem.description_preview || problem.description}
                    </Typography>

                    {/* Tags */}
                    <Box
                      sx={{
                        mb: 3,
                        minHeight: "32px",
                        display: "flex",
                        flexWrap: "wrap",
                        gap: 0.75,
                      }}
                    >
                      {(problem.tags || []).slice(0, 3).map((tag) => (
                        <Chip
                          key={tag}
                          label={tag}
                          size="small"
                          variant="outlined"
                          sx={{
                            fontSize: "0.7rem",
                            height: 26,
                            backgroundColor: "#F8FAFC",
                            borderColor: "#CBD5E1",
                            color: "#475569",
                          }}
                        />
                      ))}
                    </Box>

                    <Divider sx={{ mb: 2 }} />

                    {/* User progress info */}
                    {isLoggedIn && (isSolved || isAttempted) && (
                      <Box sx={{ mb: 2 }}>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 1,
                            backgroundColor: isSolved ? "#D1FAE5" : "#FEF3C7",
                            p: 1,
                            borderRadius: 1,
                            border: `1px solid ${
                              isSolved ? "#A7F3D0" : "#FDE68A"
                            }`,
                          }}
                        >
                          {isSolved ? (
                            <CheckCircle
                              sx={{ color: "#059669", fontSize: 18 }}
                            />
                          ) : (
                            <Typography
                              variant="caption"
                              sx={{
                                color: "#92400E",
                                fontWeight: "bold",
                                minWidth: "16px",
                              }}
                            >
                              {totalAttempts}
                            </Typography>
                          )}
                          <Typography
                            variant="body2"
                            sx={{
                              color: isSolved ? "#065F46" : "#92400E",
                              fontWeight: 600,
                            }}
                          >
                            {isSolved ? "Solved" : "Attempted"} • Best score:{" "}
                            {bestScore}%
                          </Typography>
                        </Box>
                      </Box>
                    )}

                    {/* Footer with stats and action */}
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <Stack direction="row" spacing={2.5}>
                        <Tooltip title="Success rate" arrow>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 0.5,
                            }}
                          >
                            <TrendingUp
                              sx={{ fontSize: 18, color: "#10B981" }}
                            />
                            <Typography
                              variant="body2"
                              sx={{ color: "#64748B", fontWeight: 600 }}
                            >
                              {displayAcceptanceRate}%
                            </Typography>
                          </Box>
                        </Tooltip>
                        <Tooltip title="Estimated time" arrow>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 0.5,
                            }}
                          >
                            <Schedule sx={{ fontSize: 18, color: "#64748B" }} />
                            <Typography
                              variant="body2"
                              sx={{ color: "#64748B", fontWeight: 600 }}
                            >
                              {estimatedTime}
                            </Typography>
                          </Box>
                        </Tooltip>
                      </Stack>

                      <Button
                        component={Link}
                        to={`/problems/${problem.slug}`}
                        variant="contained"
                        size="small"
                        startIcon={
                          isSolved ? (
                            <CheckCircle />
                          ) : problem.is_premium ? (
                            <Lock />
                          ) : (
                            <PlayArrow />
                          )
                        }
                        disabled={problem.is_premium}
                        sx={{
                          fontWeight: 600,
                          textTransform: "none",
                          borderRadius: 2,
                          px: 2,
                          minWidth: "100px",
                          background: isSolved
                            ? "#10B981"
                            : isAttempted
                            ? "#F59E0B"
                            : problem.is_premium
                            ? "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)"
                            : "linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)",
                          boxShadow: "none",
                          "&:hover": {
                            background: isSolved
                              ? "#059669"
                              : isAttempted
                              ? "#D97706"
                              : problem.is_premium
                              ? "linear-gradient(135deg, #D97706 0%, #B45309 100%)"
                              : "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)",
                            boxShadow: "0 4px 12px rgba(59, 130, 246, 0.3)",
                          },
                        }}
                      >
                        {isSolved
                          ? "Review"
                          : problem.is_premium
                          ? "Unlock"
                          : "Start"}
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              );
            })}
          </Box>
        )}

        {/* Pagination */}
        {!loading && !error && totalPages > 1 && (
          <Box sx={{ display: "flex", justifyContent: "center", mt: 6 }}>
            <Pagination
              count={totalPages}
              page={currentPage}
              onChange={handlePageChange}
              color="primary"
              size="large"
              showFirstButton
              showLastButton
              sx={{
                "& .MuiPaginationItem-root": {
                  fontWeight: 600,
                  "&.Mui-selected": {
                    background:
                      "linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)",
                  },
                },
              }}
            />
          </Box>
        )}
      </Container>
    </Layout>
  );
}

export default ProblemsList;
