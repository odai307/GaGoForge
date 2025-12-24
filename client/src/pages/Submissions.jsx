// src/pages/Submissions.jsx
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
  IconButton,
  Collapse,
  LinearProgress,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress as MuiCircularProgress,
} from "@mui/material";
import {
  Search,
  FilterList,
  ExpandMore,
  ExpandLess,
  Code,
  CheckCircle,
  Warning,
  Error,
  Schedule,
  Refresh,
  Visibility,
  Close,
  Bolt,
  Flag,
  KeyboardArrowRight,
  Info,
  ClearAll,
} from "@mui/icons-material";
import { useState, useMemo, useCallback, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Layout from "../components/layout/Layout";
import { submissionsAPI } from "../services/submissions";
import { problemsAPI } from "../services/problems";
import { useAuth } from "../contexts/AuthContext";
import { styled } from "@mui/material/styles";
import { CircularProgress } from "@mui/material";

function Submissions() {
  const { isLoggedIn } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  // State management
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingStats, setLoadingStats] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  // Problem slug mapping state
  const [problemSlugMap, setProblemSlugMap] = useState({});
  const [loadingProblems, setLoadingProblems] = useState(false);

  // Filter and pagination state
  const [selectedVerdict, setSelectedVerdict] = useState(
    searchParams.get("verdict") || "all"
  );
  const [searchTerm, setSearchTerm] = useState(
    searchParams.get("search") || ""
  );
  const [ordering, setOrdering] = useState(
    searchParams.get("ordering") || "-submitted_at"
  );
  const [currentPage, setCurrentPage] = useState(
    parseInt(searchParams.get("page")) || 1
  );

  // Expanded submissions (for details)
  const [expandedSubmission, setExpandedSubmission] = useState(null);

  // Dispute modal
  const [disputeModalOpen, setDisputeModalOpen] = useState(false);
  const [selectedDisputeSubmission, setSelectedDisputeSubmission] =
    useState(null);
  const [disputeReason, setDisputeReason] = useState("");
  const [disputing, setDisputing] = useState(false);

  // Details modal
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [selectedSubmissionDetails, setSelectedSubmissionDetails] =
    useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  // Active tab (for stats vs list view)
  const [activeTab, setActiveTab] = useState(0);

  const SUBMISSIONS_PER_PAGE = 10;

  // Filter configurations
  const VERDICT_OPTIONS = useMemo(
    () => [
      { value: "all", label: "All Verdicts", color: "default", icon: <Code /> },
      {
        value: "accepted",
        label: "Accepted",
        color: "success",
        icon: <CheckCircle />,
      },
      {
        value: "partially_passed",
        label: "Partially Passed",
        color: "warning",
        icon: <Bolt />,
      },
      { value: "failed", label: "Failed", color: "error", icon: <Error /> },
      {
        value: "syntax_error",
        label: "Syntax Error",
        color: "error",
        icon: <Warning />,
      },
      { value: "pending", label: "Pending", color: "info", icon: <Schedule /> },
    ],
    []
  );

  const ORDERING_OPTIONS = useMemo(
    () => [
      { value: "-submitted_at", label: "Newest First" },
      { value: "submitted_at", label: "Oldest First" },
      { value: "-score", label: "Highest Score" },
      { value: "score", label: "Lowest Score" },
      { value: "problem__title", label: "Problem Name A-Z" },
      { value: "-problem__title", label: "Problem Name Z-A" },
    ],
    []
  );

  // Fetch problems for slug mapping
  const fetchProblemsForSlugMapping = useCallback(async () => {
    if (!isLoggedIn || submissions.length === 0) return;

    setLoadingProblems(true);
    try {
      // Get unique problem IDs from submissions
      const uniqueProblemIds = [...new Set(submissions.map((s) => s.problem))];
      if (uniqueProblemIds.length === 0) return;

      // Fetch problems
      const problemsData = await problemsAPI.getProblems({
        limit: 100, // Adjust based on your needs
      });

      // Create mapping {problem_id: slug}
      const slugMap = {};
      const problemsList = problemsData.results || problemsData;

      if (Array.isArray(problemsList)) {
        problemsList.forEach((problem) => {
          if (problem.id && problem.slug) {
            slugMap[problem.id] = problem.slug;
          }
        });
      }

      setProblemSlugMap(slugMap);
    } catch (err) {
      console.warn("Could not fetch problems for slug mapping:", err);
    } finally {
      setLoadingProblems(false);
    }
  }, [isLoggedIn, submissions]);

  // Fetch submissions and data
  useEffect(() => {
    if (!isLoggedIn) return;

    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Build filters
        const filters = {};
        if (selectedVerdict !== "all") filters.verdict = selectedVerdict;
        if (searchTerm) filters.search = searchTerm;
        filters.ordering = ordering;

        // Update URL params
        const params = new URLSearchParams();
        if (selectedVerdict !== "all") params.set("verdict", selectedVerdict);
        if (searchTerm) params.set("search", searchTerm);
        params.set("ordering", ordering);
        params.set("page", currentPage.toString());
        setSearchParams(params);

        // Fetch submissions
        const submissionsData = await submissionsAPI.getSubmissions(filters);

        // Handle paginated response
        if (submissionsData.results) {
          setSubmissions(submissionsData.results);
        } else if (Array.isArray(submissionsData)) {
          setSubmissions(submissionsData);
        } else {
          setSubmissions([]);
        }
      } catch (err) {
        console.error("Error fetching submissions:", err);
        setError("Failed to load submissions. Please try again.");
        setSubmissions([]);
      } finally {
        setLoading(false);
      }
    };

    const fetchStats = async () => {
      if (!isLoggedIn) return;

      setLoadingStats(true);
      try {
        const statsData = await submissionsAPI.getStatistics();
        setStats(statsData);
      } catch (err) {
        console.warn("Could not fetch submission statistics:", err);
      } finally {
        setLoadingStats(false);
      }
    };

    fetchData();
    fetchStats();
  }, [
    isLoggedIn,
    selectedVerdict,
    searchTerm,
    ordering,
    currentPage,
    setSearchParams,
  ]);

  // Fetch problem slugs when submissions change
  useEffect(() => {
    if (submissions.length > 0) {
      fetchProblemsForSlugMapping();
    }
  }, [submissions, fetchProblemsForSlugMapping]);

  // Utility functions
  const getVerdictConfig = useCallback(
    (verdict) => {
      const config = VERDICT_OPTIONS.find((v) => v.value === verdict);
      return config || { label: verdict, color: "default", icon: <Code /> };
    },
    [VERDICT_OPTIONS]
  );

  // Get problem URL - uses slug mapping with fallback to problem_id
  const getProblemUrl = useCallback(
    (submission) => {
      const slug = problemSlugMap[submission.problem];
      return `/problems/${slug || submission.problem_id || submission.problem}`;
    },
    [problemSlugMap]
  );

  // Filter submissions client-side for search (if needed)
  const filteredSubmissions = useMemo(() => {
    if (!searchTerm) return submissions;

    const term = searchTerm.toLowerCase();
    return submissions.filter(
      (sub) =>
        sub.problem_title?.toLowerCase().includes(term) ||
        sub.framework?.toLowerCase().includes(term) ||
        sub.verdict?.toLowerCase().includes(term)
    );
  }, [submissions, searchTerm]);

  // Pagination calculations
  const totalPages = Math.ceil(
    filteredSubmissions.length / SUBMISSIONS_PER_PAGE
  );
  const paginatedSubmissions = useMemo(() => {
    const startIndex = (currentPage - 1) * SUBMISSIONS_PER_PAGE;
    return filteredSubmissions.slice(
      startIndex,
      startIndex + SUBMISSIONS_PER_PAGE
    );
  }, [filteredSubmissions, currentPage]);

  // Event handlers
  const handleVerdictChange = useCallback((event) => {
    setSelectedVerdict(event.target.value);
    setCurrentPage(1);
  }, []);

  const handleSearchChange = useCallback((event) => {
    setSearchTerm(event.target.value);
    setCurrentPage(1);
  }, []);

  const handleOrderingChange = useCallback((event) => {
    setOrdering(event.target.value);
    setCurrentPage(1);
  }, []);

  const handleClearFilters = useCallback(() => {
    setSelectedVerdict("all");
    setSearchTerm("");
    setOrdering("-submitted_at");
    setCurrentPage(1);
    setSearchParams({});
  }, [setSearchParams]);

  const handlePageChange = useCallback((event, value) => {
    setCurrentPage(value);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  const handleExpandSubmission = useCallback(
    (submissionId) => {
      setExpandedSubmission(
        expandedSubmission === submissionId ? null : submissionId
      );
    },
    [expandedSubmission]
  );

  const handleOpenDisputeModal = useCallback((submission) => {
    if (submission.verdict === "accepted") {
      setError("Cannot dispute accepted submissions");
      return;
    }
    setSelectedDisputeSubmission(submission);
    setDisputeReason("");
    setDisputeModalOpen(true);
  }, []);

  const handleCloseDisputeModal = useCallback(() => {
    if (!disputing) {
      setDisputeModalOpen(false);
      setSelectedDisputeSubmission(null);
      setDisputeReason("");
    }
  }, [disputing]);

  const handleSubmitDispute = useCallback(async () => {
    if (!selectedDisputeSubmission || !disputeReason.trim()) return;

    setDisputing(true);
    try {
      await submissionsAPI.disputeSubmission(
        selectedDisputeSubmission.submission_id,
        disputeReason
      );

      // Update local submission state
      setSubmissions((prev) =>
        prev.map((sub) =>
          sub.submission_id === selectedDisputeSubmission.submission_id
            ? { ...sub, is_disputed: true, dispute_reason: disputeReason }
            : sub
        )
      );

      setDisputeModalOpen(false);
      setSelectedDisputeSubmission(null);
      setDisputeReason("");

      // Show success message
      setError(null);
      alert("Dispute submitted successfully! Our team will review it shortly.");
    } catch (err) {
      setError("Failed to submit dispute. Please try again.");
      console.error("Dispute error:", err);
    } finally {
      setDisputing(false);
    }
  }, [selectedDisputeSubmission, disputeReason]);

  const handleOpenDetailsModal = useCallback(async (submissionId) => {
    setSelectedSubmissionDetails(null);
    setDetailsModalOpen(true);
    setLoadingDetails(true);

    try {
      const submissionDetails = await submissionsAPI.getSubmission(
        submissionId
      );
      setSelectedSubmissionDetails(submissionDetails);
    } catch (err) {
      console.error("Error loading submission details:", err);
      setError("Failed to load submission details");
    } finally {
      setLoadingDetails(false);
    }
  }, []);

  const handleCloseDetailsModal = useCallback(() => {
    setDetailsModalOpen(false);
    setSelectedSubmissionDetails(null);
  }, []);

  const handleTabChange = useCallback((event, newValue) => {
    setActiveTab(newValue);
  }, []);

  // Check if any filters are active
  const hasActiveFilters = useMemo(() => {
    return (
      selectedVerdict !== "all" || searchTerm || ordering !== "-submitted_at"
    );
  }, [selectedVerdict, searchTerm, ordering]);

  // Calculate statistics - FIXED to handle NaN issues
  const calculateStats = useMemo(() => {
    if (!stats && filteredSubmissions.length === 0) {
      return {
        successRate: 0,
        totalScore: 0,
        totalSubmissions: 0,
        acceptanceRate: 0,
        accepted: 0,
        partiallyPassed: 0,
        failed: 0,
        syntaxErrors: 0,
      };
    }

    const accepted = filteredSubmissions.filter(
      (s) => s.verdict === "accepted"
    ).length;
    const partiallyPassed = filteredSubmissions.filter(
      (s) => s.verdict === "partially_passed"
    ).length;
    const totalSubmissions = filteredSubmissions.length;

    // Calculate success rate safely
    const successRate =
      totalSubmissions > 0
        ? Math.round(((accepted + partiallyPassed) / totalSubmissions) * 100)
        : 0;

    // Calculate total score safely
    const totalScore = filteredSubmissions.reduce((sum, s) => {
      const score = parseFloat(s.score) || 0;
      return sum + (isNaN(score) ? 0 : score);
    }, 0);

    // Calculate acceptance rate safely
    const acceptanceRate =
      totalSubmissions > 0
        ? Math.round((accepted / totalSubmissions) * 100)
        : 0;

    return {
      successRate,
      totalScore: Math.round(totalScore),
      acceptanceRate,
      accepted,
      partiallyPassed,
      failed: filteredSubmissions.filter((s) => s.verdict === "failed").length,
      syntaxErrors: filteredSubmissions.filter(
        (s) => s.verdict === "syntax_error"
      ).length,
      totalSubmissions,
    };
  }, [filteredSubmissions, stats]);

  // Styled components
  const VerdictChip = styled(Chip)(({ verdict }) => ({
    fontWeight: 600,
    backgroundColor:
      verdict === "accepted"
        ? "#DCFCE7"
        : verdict === "partially_passed"
        ? "#FEF3C7"
        : verdict === "failed"
        ? "#FEE2E2"
        : verdict === "syntax_error"
        ? "#FEE2E2"
        : "#E2E8F0",
    color:
      verdict === "accepted"
        ? "#15803D"
        : verdict === "partially_passed"
        ? "#92400E"
        : verdict === "failed"
        ? "#991B1B"
        : verdict === "syntax_error"
        ? "#991B1B"
        : "#64748B",
  }));

  // Render loading state
  if (!isLoggedIn) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ py: { xs: 3, md: 5 } }}>
          <Alert
            severity="warning"
            sx={{
              mb: 3,
              borderRadius: 2,
            }}
            action={
              <Button component={Link} to="/login" color="inherit" size="small">
                Login
              </Button>
            }
          >
            Please log in to view your submissions.
          </Alert>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ py: { xs: 3, md: 5 } }}>
        {/* Header */}
        <Box sx={{ mb: 5 }}>
          <Stack
            direction="row"
            alignItems="center"
            justifyContent="space-between"
            sx={{ mb: 2 }}
          >
            <Typography
              variant="h3"
              component="h1"
              sx={{
                fontWeight: 800,
                color: "#0F172A",
                fontSize: { xs: "2rem", md: "2.5rem" },
              }}
            >
              My Submissions
            </Typography>
            <Button
              startIcon={<Refresh />}
              onClick={() => window.location.reload()}
              variant="outlined"
              size="small"
              sx={{ textTransform: "none" }}
            >
              Refresh
            </Button>
          </Stack>

          <Typography
            variant="body1"
            sx={{
              color: "#64748B",
              fontSize: "1.125rem",
              maxWidth: "700px",
              lineHeight: 1.7,
            }}
          >
            Track your code submissions, view feedback, and monitor your
            progress across all challenges.
          </Typography>
        </Box>

        {/* Tabs */}
        <Box sx={{ mb: 4 }}>
          <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
            <Tab label="All Submissions" />
            <Tab label="Statistics" />
          </Tabs>
        </Box>

        {/* Statistics Tab */}
        {activeTab === 1 && (
          <Card sx={{ border: "1px solid #E2E8F0", borderRadius: 3, mb: 4 }}>
            <CardContent sx={{ p: 4 }}>
              {loadingStats ? (
                <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <>
                  <Typography
                    variant="h5"
                    sx={{ fontWeight: 600, color: "#0F172A", mb: 3 }}
                  >
                    Submission Statistics
                  </Typography>

                  <Grid container spacing={3} sx={{ mb: 4 }}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card
                        sx={{
                          border: "1px solid #E2E8F0",
                          borderRadius: 2,
                          backgroundColor: "#F0FDF4",
                        }}
                      >
                        <CardContent sx={{ p: 3, textAlign: "center" }}>
                          <Typography
                            variant="h3"
                            sx={{ fontWeight: 800, color: "#15803D", mb: 1 }}
                          >
                            {calculateStats.successRate}%
                          </Typography>
                          <Typography variant="body2" sx={{ color: "#64748B" }}>
                            Success Rate
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{ color: "#94A3B8" }}
                          >
                            Accepted + Partially Passed
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>

                    <Grid item xs={12} sm={6} md={3}>
                      <Card
                        sx={{
                          border: "1px solid #E2E8F0",
                          borderRadius: 2,
                          backgroundColor: "#FEF3C7",
                        }}
                      >
                        <CardContent sx={{ p: 3, textAlign: "center" }}>
                          <Typography
                            variant="h3"
                            sx={{ fontWeight: 800, color: "#92400E", mb: 1 }}
                          >
                            {calculateStats.totalScore}
                          </Typography>
                          <Typography variant="body2" sx={{ color: "#64748B" }}>
                            Total Score
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{ color: "#94A3B8" }}
                          >
                            Across all submissions
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>

                    <Grid item xs={12} sm={6} md={3}>
                      <Card
                        sx={{
                          border: "1px solid #E2E8F0",
                          borderRadius: 2,
                          backgroundColor: "#E0E7FF",
                        }}
                      >
                        <CardContent sx={{ p: 3, textAlign: "center" }}>
                          <Typography
                            variant="h3"
                            sx={{ fontWeight: 800, color: "#3730A3", mb: 1 }}
                          >
                            {calculateStats.totalSubmissions}
                          </Typography>
                          <Typography variant="body2" sx={{ color: "#64748B" }}>
                            Total Submissions
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{ color: "#94A3B8" }}
                          >
                            All attempts
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>

                    <Grid item xs={12} sm={6} md={3}>
                      <Card
                        sx={{
                          border: "1px solid #E2E8F0",
                          borderRadius: 2,
                          backgroundColor: "#DCFCE7",
                        }}
                      >
                        <CardContent sx={{ p: 3, textAlign: "center" }}>
                          <Typography
                            variant="h3"
                            sx={{ fontWeight: 800, color: "#15803D", mb: 1 }}
                          >
                            {calculateStats.acceptanceRate}%
                          </Typography>
                          <Typography variant="body2" sx={{ color: "#64748B" }}>
                            Acceptance Rate
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{ color: "#94A3B8" }}
                          >
                            Fully accepted only
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>

                  {/* Detailed Stats Table */}
                  <Typography
                    variant="h6"
                    sx={{ fontWeight: 600, color: "#0F172A", mb: 2 }}
                  >
                    Breakdown by Verdict
                  </Typography>

                  <TableContainer
                    component={Paper}
                    variant="outlined"
                    sx={{ borderRadius: 2 }}
                  >
                    <Table>
                      <TableHead sx={{ backgroundColor: "#F8FAFC" }}>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600 }}>
                            Verdict
                          </TableCell>
                          <TableCell sx={{ fontWeight: 600 }} align="right">
                            Count
                          </TableCell>
                          <TableCell sx={{ fontWeight: 600 }} align="right">
                            Percentage
                          </TableCell>
                          <TableCell sx={{ fontWeight: 600 }} align="right">
                            Total Score
                          </TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {VERDICT_OPTIONS.filter(
                          (v) => v.value !== "all" && v.value !== "pending"
                        ).map((verdict) => {
                          const count = submissions.filter(
                            (s) => s.verdict === verdict.value
                          ).length;
                          const percentage =
                            calculateStats.totalSubmissions > 0
                              ? Math.round(
                                  (count / calculateStats.totalSubmissions) *
                                    100
                                )
                              : 0;
                          const totalScore = submissions
                            .filter((s) => s.verdict === verdict.value)
                            .reduce((sum, s) => {
                              const score = parseFloat(s.score) || 0;
                              return sum + (isNaN(score) ? 0 : score);
                            }, 0);

                          return (
                            <TableRow key={verdict.value}>
                              <TableCell>
                                <Stack
                                  direction="row"
                                  alignItems="center"
                                  spacing={1}
                                >
                                  {verdict.icon}
                                  <Typography>{verdict.label}</Typography>
                                </Stack>
                              </TableCell>
                              <TableCell align="right">
                                <Typography fontWeight={600}>
                                  {count}
                                </Typography>
                              </TableCell>
                              <TableCell align="right">
                                <Typography fontWeight={600}>
                                  {percentage}%
                                </Typography>
                              </TableCell>
                              <TableCell align="right">
                                <Typography fontWeight={600}>
                                  {Math.round(totalScore)}
                                </Typography>
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>

                  {/* Progress Bars */}
                  <Box sx={{ mt: 4 }}>
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 600, color: "#0F172A", mb: 2 }}
                    >
                      Performance Distribution
                    </Typography>

                    <Stack spacing={2}>
                      {VERDICT_OPTIONS.filter(
                        (v) => v.value !== "all" && v.value !== "pending"
                      ).map((verdict) => {
                        const count = submissions.filter(
                          (s) => s.verdict === verdict.value
                        ).length;
                        const percentage =
                          calculateStats.totalSubmissions > 0
                            ? (count / calculateStats.totalSubmissions) * 100
                            : 0;

                        return (
                          <Box key={verdict.value}>
                            <Stack
                              direction="row"
                              justifyContent="space-between"
                              sx={{ mb: 0.5 }}
                            >
                              <Stack
                                direction="row"
                                alignItems="center"
                                spacing={1}
                              >
                                {verdict.icon}
                                <Typography variant="body2" fontWeight={600}>
                                  {verdict.label}
                                </Typography>
                              </Stack>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                {count} ({percentage.toFixed(1)}%)
                              </Typography>
                            </Stack>
                            <LinearProgress
                              variant="determinate"
                              value={percentage}
                              sx={{
                                height: 8,
                                borderRadius: 4,
                                backgroundColor: "#E2E8F0",
                                "& .MuiLinearProgress-bar": {
                                  backgroundColor:
                                    verdict.color === "success"
                                      ? "#10B981"
                                      : verdict.color === "warning"
                                      ? "#F59E0B"
                                      : verdict.color === "error"
                                      ? "#EF4444"
                                      : "#64748B",
                                  borderRadius: 4,
                                },
                              }}
                            />
                          </Box>
                        );
                      })}
                    </Stack>
                  </Box>
                </>
              )}
            </CardContent>
          </Card>
        )}

        {/* Filters Card */}
        {activeTab === 0 && (
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
                      Filter Submissions
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
                    placeholder="Search by problem name or verdict..."
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
                        "&:hover fieldset": { borderColor: "#3B82F6" },
                        "&.Mui-focused": { backgroundColor: "white" },
                      },
                    }}
                  />

                  <FormControl sx={{ minWidth: { xs: "100%", md: 180 } }}>
                    <InputLabel id="verdict-label">Verdict</InputLabel>
                    <Select
                      labelId="verdict-label"
                      value={selectedVerdict}
                      label="Verdict"
                      onChange={handleVerdictChange}
                      sx={{ backgroundColor: "#F8FAFC" }}
                    >
                      {VERDICT_OPTIONS.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          <Stack
                            direction="row"
                            alignItems="center"
                            spacing={1}
                          >
                            {option.icon}
                            <Typography>{option.label}</Typography>
                          </Stack>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        )}

        {/* Error state */}
        {error && (
          <Alert
            severity="error"
            sx={{ mb: 4, borderRadius: 2 }}
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}

        {/* Loading state */}
        {loading && activeTab === 0 && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Empty state */}
        {!loading &&
          !error &&
          filteredSubmissions.length === 0 &&
          activeTab === 0 && (
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
                No submissions found
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {hasActiveFilters
                  ? "Try adjusting your filters to find what you're looking for."
                  : "You haven't submitted any code yet. Try solving your first challenge!"}
              </Typography>
              {!hasActiveFilters && (
                <Button
                  component={Link}
                  to="/problems"
                  variant="contained"
                  size="small"
                  startIcon={<Code />}
                >
                  Browse Challenges
                </Button>
              )}
            </Alert>
          )}

        {/* Results info */}
        {!loading &&
          !error &&
          filteredSubmissions.length > 0 &&
          activeTab === 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography
                variant="body2"
                sx={{ color: "#64748B", fontWeight: 500 }}
              >
                Showing {paginatedSubmissions.length} of{" "}
                {filteredSubmissions.length} submission
                {filteredSubmissions.length !== 1 ? "s" : ""}
                {hasActiveFilters && " (filtered)"}
              </Typography>
            </Box>
          )}

        {/* Submissions List */}
        {!loading &&
          !error &&
          filteredSubmissions.length > 0 &&
          activeTab === 0 && (
            <Stack spacing={2}>
              {paginatedSubmissions.map((submission) => {
                const verdictConfig = getVerdictConfig(submission.verdict);
                const isExpanded =
                  expandedSubmission === submission.submission_id;
                const problemUrl = getProblemUrl(submission);

                return (
                  <Card
                    key={submission.submission_id}
                    sx={{
                      border: "1px solid",
                      borderColor:
                        submission.verdict === "accepted"
                          ? "#10B98140"
                          : "#E2E8F0",
                      borderRadius: 3,
                      transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                      "&:hover": {
                        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)",
                        borderColor:
                          submission.verdict === "accepted"
                            ? "#10B981"
                            : "#3B82F6",
                      },
                    }}
                  >
                    <CardContent sx={{ p: 3 }}>
                      {/* Submission Header */}
                      <Stack
                        direction="row"
                        alignItems="center"
                        justifyContent="space-between"
                        sx={{ mb: 2 }}
                      >
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Box sx={{ display: "flex", alignItems: "center" }}>
                            {verdictConfig.icon}
                            <VerdictChip
                              label={verdictConfig.label}
                              size="small"
                              verdict={submission.verdict}
                              sx={{ ml: 1 }}
                            />
                          </Box>

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
                            {new Date(submission.submitted_at).toLocaleString()}
                          </Typography>

                          {submission.is_disputed && (
                            <Chip
                              icon={<Flag />}
                              label="Disputed"
                              size="small"
                              color="warning"
                              variant="outlined"
                            />
                          )}
                        </Stack>

                        <Stack direction="row" alignItems="center" spacing={1}>
                          <IconButton
                            size="small"
                            onClick={() =>
                              handleExpandSubmission(submission.submission_id)
                            }
                            aria-label={
                              isExpanded ? "Collapse details" : "Expand details"
                            }
                          >
                            {isExpanded ? <ExpandLess /> : <ExpandMore />}
                          </IconButton>
                        </Stack>
                      </Stack>

                      {/* Submission Body */}
                      <Stack spacing={2}>
                        {/* Problem Info */}
                        <Box>
                          <Typography
                            variant="h6"
                            sx={{
                              fontWeight: 600,
                              color: "#0F172A",
                              mb: 1,
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "space-between",
                            }}
                          >
                            <Link
                              to={problemUrl}
                              style={{
                                textDecoration: "none",
                                color: "inherit",
                                flexGrow: 1,
                              }}
                            >
                              {submission.problem_title || "Unknown Problem"}
                              <KeyboardArrowRight
                                sx={{ verticalAlign: "middle", ml: 0.5 }}
                              />
                            </Link>

                            <Typography
                              variant="h5"
                              sx={{
                                fontWeight: 700,
                                color:
                                  submission.score >= 80
                                    ? "#10B981"
                                    : submission.score >= 50
                                    ? "#F59E0B"
                                    : "#EF4444",
                              }}
                            >
                              {submission.score || 0}%
                            </Typography>
                          </Typography>

                          <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
                            {submission.framework && (
                              <Chip
                                label={submission.framework}
                                size="small"
                                sx={{
                                  backgroundColor: "#E0E7FF",
                                  color: "#4338CA",
                                  fontWeight: 600,
                                  fontSize: "0.75rem",
                                }}
                              />
                            )}

                            <Chip
                              label={`Attempt #${submission.attempt_number}`}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: "0.75rem" }}
                            />

                            {submission.execution_time_ms > 0 && (
                              <Chip
                                label={`${submission.execution_time_ms}ms`}
                                size="small"
                                variant="outlined"
                                sx={{ fontSize: "0.75rem" }}
                              />
                            )}
                          </Stack>
                        </Box>

                        {/* Score Progress Bar */}
                        <Box sx={{ width: "100%" }}>
                          <LinearProgress
                            variant="determinate"
                            value={submission.score || 0}
                            sx={{
                              height: 8,
                              borderRadius: 4,
                              backgroundColor: "#E2E8F0",
                              "& .MuiLinearProgress-bar": {
                                backgroundColor:
                                  (submission.score || 0) >= 80
                                    ? "#10B981"
                                    : (submission.score || 0) >= 50
                                    ? "#F59E0B"
                                    : "#EF4444",
                                borderRadius: 4,
                              },
                            }}
                          />
                        </Box>

                        {/* Expandable Details */}
                        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                          <Divider sx={{ my: 2 }} />

                          <Stack spacing={2}>
                            {/* Quick Actions */}
                            <Stack direction="row" spacing={1}>
                              <Button
                                size="small"
                                startIcon={<Visibility />}
                                onClick={() =>
                                  handleOpenDetailsModal(
                                    submission.submission_id
                                  )
                                }
                                variant="outlined"
                                sx={{ textTransform: "none" }}
                              >
                                View Details
                              </Button>

                              <Button
                                size="small"
                                startIcon={<Code />}
                                component={Link}
                                to={problemUrl}
                                variant="outlined"
                                sx={{ textTransform: "none" }}
                              >
                                Try Again
                              </Button>

                              {submission.verdict !== "accepted" &&
                                !submission.is_disputed && (
                                  <Button
                                    size="small"
                                    startIcon={<Flag />}
                                    onClick={() =>
                                      handleOpenDisputeModal(submission)
                                    }
                                    variant="outlined"
                                    color="warning"
                                    sx={{ textTransform: "none" }}
                                  >
                                    Dispute
                                  </Button>
                                )}
                            </Stack>

                            {/* Quick Stats */}
                            <Grid container spacing={2}>
                              <Grid item xs={6} sm={4}>
                                <Typography
                                  variant="caption"
                                  sx={{ color: "#64748B" }}
                                >
                                  Framework
                                </Typography>
                                <Typography variant="body2" fontWeight={600}>
                                  {submission.framework || "N/A"}
                                </Typography>
                              </Grid>
                              <Grid item xs={6} sm={4}>
                                <Typography
                                  variant="caption"
                                  sx={{ color: "#64748B" }}
                                >
                                  Language
                                </Typography>
                                <Typography variant="body2" fontWeight={600}>
                                  {submission.language || "N/A"}
                                </Typography>
                              </Grid>
                              <Grid item xs={6} sm={4}>
                                <Typography
                                  variant="caption"
                                  sx={{ color: "#64748B" }}
                                >
                                  Attempt
                                </Typography>
                                <Typography variant="body2" fontWeight={600}>
                                  #{submission.attempt_number}
                                </Typography>
                              </Grid>
                            </Grid>

                            {/* Feedback Preview */}
                            {submission.feedback &&
                              submission.feedback.length > 0 && (
                                <Box>
                                  <Typography
                                    variant="subtitle2"
                                    sx={{
                                      fontWeight: 600,
                                      color: "#0F172A",
                                      mb: 1,
                                    }}
                                  >
                                    Feedback
                                  </Typography>
                                  <Box
                                    sx={{
                                      maxHeight: 150,
                                      overflowY: "auto",
                                      p: 1,
                                      bgcolor: "#F8FAFC",
                                      borderRadius: 1,
                                    }}
                                  >
                                    {submission.feedback
                                      .slice(0, 3)
                                      .map((fb, idx) => (
                                        <Typography
                                          key={idx}
                                          variant="body2"
                                          sx={{
                                            color:
                                              fb.type === "error"
                                                ? "#EF4444"
                                                : fb.type === "warning"
                                                ? "#F59E0B"
                                                : "#10B981",
                                            mb: 0.5,
                                            fontFamily: "monospace",
                                            fontSize: "0.875rem",
                                          }}
                                        >
                                          {fb.line && `Line ${fb.line}: `}
                                          {fb.message}
                                        </Typography>
                                      ))}
                                    {submission.feedback.length > 3 && (
                                      <Typography
                                        variant="caption"
                                        sx={{
                                          color: "#64748B",
                                          fontStyle: "italic",
                                        }}
                                      >
                                        ...and {submission.feedback.length - 3}{" "}
                                        more feedback items
                                      </Typography>
                                    )}
                                  </Box>
                                </Box>
                              )}
                          </Stack>
                        </Collapse>
                      </Stack>
                    </CardContent>
                  </Card>
                );
              })}
            </Stack>
          )}

        {/* Pagination */}
        {!loading &&
          !error &&
          filteredSubmissions.length > 0 &&
          totalPages > 1 &&
          activeTab === 0 && (
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

        {/* Summary Stats (only when we have submissions) - SIMPLIFIED */}
        {!loading &&
          !error &&
          filteredSubmissions.length > 0 &&
          activeTab === 0 && (
            <Card sx={{ border: "1px solid #E2E8F0", borderRadius: 3, mt: 4 }}>
              <CardContent sx={{ p: 3 }}>
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 600, color: "#0F172A", mb: 2 }}
                >
                  Current Filter Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" sx={{ color: "#64748B" }}>
                      Success Rate
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{ fontWeight: 700, color: "#10B981" }}
                    >
                      {calculateStats.successRate}%
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" sx={{ color: "#64748B" }}>
                      Total Score
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{ fontWeight: 700, color: "#3B82F6" }}
                    >
                      {calculateStats.totalScore}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" sx={{ color: "#64748B" }}>
                      Total Submissions
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{ fontWeight: 700, color: "#8B5CF6" }}
                    >
                      {calculateStats.totalSubmissions}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}
      </Container>

      {/* Submission Details Modal */}
      <Dialog
        open={detailsModalOpen}
        onClose={handleCloseDetailsModal}
        maxWidth="lg"
        fullWidth
        scroll="paper"
      >
        <DialogTitle>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Submission Details
            </Typography>
            <IconButton onClick={handleCloseDetailsModal} size="small">
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent dividers>
          {loadingDetails ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
              <CircularProgress />
            </Box>
          ) : selectedSubmissionDetails ? (
            <Stack spacing={3}>
              {/* Header Info */}
              <Box>
                <Typography
                  variant="h5"
                  sx={{ fontWeight: 700, color: "#0F172A", mb: 1 }}
                >
                  {selectedSubmissionDetails.problem?.title ||
                    "Unknown Problem"}
                </Typography>

                <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
                  <VerdictChip
                    label={
                      getVerdictConfig(selectedSubmissionDetails.verdict).label
                    }
                    verdict={selectedSubmissionDetails.verdict}
                  />
                  <Chip
                    label={`Score: ${selectedSubmissionDetails.score || 0}%`}
                    size="small"
                    sx={{
                      backgroundColor:
                        (selectedSubmissionDetails.score || 0) >= 80
                          ? "#DCFCE7"
                          : (selectedSubmissionDetails.score || 0) >= 50
                          ? "#FEF3C7"
                          : "#FEE2E2",
                      color:
                        (selectedSubmissionDetails.score || 0) >= 80
                          ? "#15803D"
                          : (selectedSubmissionDetails.score || 0) >= 50
                          ? "#92400E"
                          : "#991B1B",
                      fontWeight: 600,
                    }}
                  />
                  <Chip
                    label={`Attempt #${selectedSubmissionDetails.attempt_number}`}
                    size="small"
                    variant="outlined"
                  />
                </Stack>

                <Grid container spacing={2}>
                  <Grid item xs={6} sm={4}>
                    <Typography
                      variant="caption"
                      sx={{ color: "#64748B", display: "block" }}
                    >
                      Framework
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                      {selectedSubmissionDetails.problem?.framework?.name ||
                        selectedSubmissionDetails.framework ||
                        "N/A"}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Typography
                      variant="caption"
                      sx={{ color: "#64748B", display: "block" }}
                    >
                      Difficulty
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                      {selectedSubmissionDetails.problem?.difficulty || "N/A"}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Typography
                      variant="caption"
                      sx={{ color: "#64748B", display: "block" }}
                    >
                      Language
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                      {selectedSubmissionDetails.language}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <Typography
                      variant="caption"
                      sx={{ color: "#64748B", display: "block" }}
                    >
                      Submitted
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                      {new Date(
                        selectedSubmissionDetails.submitted_at
                      ).toLocaleString()}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>

              {/* Code Viewer */}
              <Box>
                <Typography
                  variant="subtitle1"
                  sx={{ fontWeight: 600, color: "#0F172A", mb: 2 }}
                >
                  Submitted Code
                </Typography>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    backgroundColor: "#1E293B",
                    color: "#E2E8F0",
                    fontFamily: "monospace",
                    fontSize: "0.875rem",
                    maxHeight: 400,
                    overflow: "auto",
                    borderRadius: 2,
                  }}
                >
                  <pre
                    style={{
                      margin: 0,
                      whiteSpace: "pre-wrap",
                      wordWrap: "break-word",
                    }}
                  >
                    {selectedSubmissionDetails.code}
                  </pre>
                </Paper>
              </Box>

              {/* Validation Results */}
              {selectedSubmissionDetails.validation_results &&
                Object.keys(selectedSubmissionDetails.validation_results)
                  .length > 0 && (
                  <Box>
                    <Typography
                      variant="subtitle1"
                      sx={{ fontWeight: 600, color: "#0F172A", mb: 2 }}
                    >
                      Validation Results
                    </Typography>
                    <Grid container spacing={2}>
                      {Object.entries(
                        selectedSubmissionDetails.validation_results
                      ).map(([key, value]) => (
                        <Grid item xs={12} sm={6} md={4} key={key}>
                          <Card variant="outlined" sx={{ height: "100%" }}>
                            <CardContent sx={{ p: 2 }}>
                              <Typography
                                variant="caption"
                                sx={{
                                  color: "#64748B",
                                  textTransform: "uppercase",
                                  letterSpacing: 0.5,
                                  display: "block",
                                  mb: 1,
                                }}
                              >
                                {key.replace(/_/g, " ")}
                              </Typography>
                              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                                {typeof value === "number"
                                  ? `${value.toFixed(1)}%`
                                  : value}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                )}

              {/* Feedback */}
              {selectedSubmissionDetails.feedback &&
                selectedSubmissionDetails.feedback.length > 0 && (
                  <Box>
                    <Typography
                      variant="subtitle1"
                      sx={{ fontWeight: 600, color: "#0F172A", mb: 2 }}
                    >
                      Feedback
                    </Typography>
                    <Stack spacing={1}>
                      {selectedSubmissionDetails.feedback.map((fb, idx) => (
                        <Paper
                          key={idx}
                          variant="outlined"
                          sx={{
                            p: 2,
                            backgroundColor:
                              fb.type === "error"
                                ? "#FEF2F2"
                                : fb.type === "warning"
                                ? "#FFFBEB"
                                : "#F0FDF4",
                            borderColor:
                              fb.type === "error"
                                ? "#FECACA"
                                : fb.type === "warning"
                                ? "#FDE68A"
                                : "#BBF7D0",
                          }}
                        >
                          <Stack
                            direction="row"
                            alignItems="flex-start"
                            spacing={1}
                          >
                            {fb.type === "error" ? (
                              <Error sx={{ color: "#DC2626", mt: 0.5 }} />
                            ) : fb.type === "warning" ? (
                              <Warning sx={{ color: "#D97706", mt: 0.5 }} />
                            ) : (
                              <CheckCircle sx={{ color: "#059669", mt: 0.5 }} />
                            )}
                            <Box sx={{ flexGrow: 1 }}>
                              <Typography
                                variant="body2"
                                sx={{
                                  color:
                                    fb.type === "error"
                                      ? "#DC2626"
                                      : fb.type === "warning"
                                      ? "#D97706"
                                      : "#059669",
                                  fontWeight: 600,
                                  mb: 0.5,
                                }}
                              >
                                {fb.type?.charAt(0).toUpperCase() +
                                  fb.type?.slice(1)}
                                {fb.line && ` at line ${fb.line}`}
                                {fb.column && `, column ${fb.column}`}
                              </Typography>
                              <Typography
                                variant="body2"
                                sx={{ color: "#374151" }}
                              >
                                {fb.message}
                              </Typography>
                              {fb.suggestion && (
                                <Typography
                                  variant="body2"
                                  sx={{
                                    color: "#6B7280",
                                    mt: 1,
                                    fontStyle: "italic",
                                  }}
                                >
                                  <strong>Suggestion:</strong> {fb.suggestion}
                                </Typography>
                              )}
                            </Box>
                          </Stack>
                        </Paper>
                      ))}
                    </Stack>
                  </Box>
                )}

              {/* Dispute Info */}
              {selectedSubmissionDetails.is_disputed && (
                <Box>
                  <Typography
                    variant="subtitle1"
                    sx={{ fontWeight: 600, color: "#0F172A", mb: 2 }}
                  >
                    Dispute Information
                  </Typography>
                  <Paper
                    variant="outlined"
                    sx={{ p: 2, backgroundColor: "#FFFBEB" }}
                  >
                    <Stack spacing={1}>
                      <Typography
                        variant="body2"
                        sx={{ fontWeight: 600, color: "#92400E" }}
                      >
                        Status:{" "}
                        {selectedSubmissionDetails.dispute_resolved
                          ? "Resolved"
                          : "Pending Review"}
                      </Typography>
                      <Typography variant="body2" sx={{ color: "#92400E" }}>
                        <strong>Reason:</strong>{" "}
                        {selectedSubmissionDetails.dispute_reason}
                      </Typography>
                    </Stack>
                  </Paper>
                </Box>
              )}
            </Stack>
          ) : (
            <Alert severity="error">Failed to load submission details.</Alert>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 2 }}>
          <Button
            onClick={handleCloseDetailsModal}
            sx={{ color: "text.secondary" }}
          >
            Close
          </Button>
          {selectedSubmissionDetails && (
            <>
              <Button
                component={Link}
                to={getProblemUrl(selectedSubmissionDetails)}
                variant="outlined"
                sx={{ textTransform: "none" }}
              >
                Try Again
              </Button>
              {!selectedSubmissionDetails.is_disputed &&
                selectedSubmissionDetails.verdict !== "accepted" && (
                  <Button
                    variant="contained"
                    startIcon={<Flag />}
                    onClick={() => {
                      handleCloseDetailsModal();
                      handleOpenDisputeModal(selectedSubmissionDetails);
                    }}
                    sx={{ textTransform: "none" }}
                  >
                    Dispute Verdict
                  </Button>
                )}
            </>
          )}
        </DialogActions>
      </Dialog>

      {/* Dispute Modal */}
      <Dialog
        open={disputeModalOpen}
        onClose={handleCloseDisputeModal}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Dispute Submission
            </Typography>
            <IconButton
              onClick={handleCloseDisputeModal}
              disabled={disputing}
              size="small"
            >
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <Alert severity="info">
              Please explain why you believe this verdict is incorrect. Our team
              will review your dispute.
            </Alert>
            {selectedDisputeSubmission && (
              <Box>
                <Typography variant="body2" sx={{ color: "#64748B", mb: 0.5 }}>
                  Problem:{" "}
                  <strong>{selectedDisputeSubmission.problem_title}</strong>
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748B", mb: 0.5 }}>
                  Verdict:{" "}
                  <strong>
                    {getVerdictConfig(selectedDisputeSubmission.verdict).label}
                  </strong>
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748B" }}>
                  Score:{" "}
                  <strong>{selectedDisputeSubmission.score || 0}%</strong>
                </Typography>
              </Box>
            )}
            <TextField
              label="Reason for dispute"
              value={disputeReason}
              onChange={(e) => setDisputeReason(e.target.value)}
              multiline
              rows={4}
              fullWidth
              disabled={disputing}
              placeholder="Explain why you think the verdict should be changed..."
              helperText="Be specific about what you think was incorrect in the validation"
            />
          </Stack>
        </DialogContent>

        <DialogActions sx={{ p: 2 }}>
          <Button
            onClick={handleCloseDisputeModal}
            disabled={disputing}
            sx={{ color: "text.secondary" }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmitDispute}
            variant="contained"
            disabled={!disputeReason.trim() || disputing}
            startIcon={disputing ? <MuiCircularProgress size={20} /> : <Flag />}
          >
            {disputing ? "Submitting..." : "Submit Dispute"}
          </Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
}

export default Submissions;
