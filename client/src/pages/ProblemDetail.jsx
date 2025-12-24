// src/pages/ProblemDetail.jsx
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Button,
  Stack,
  Alert,
  Divider,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  LinearProgress,
  Fade,
  CircularProgress,
  Grid,
  AppBar,
  Toolbar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import {
  PlayArrow,
  CheckCircle,
  Lock,
  TrendingUp,
  Schedule,
  Lightbulb,
  Report,
  Share,
  Bookmark,
  Code as CodeIcon,
  ArrowBack,
  ArrowForward,
  Refresh,
  Visibility,
  Error,
  Warning,
  Info,
  Edit,
  Code,
  Description,
  ContentCopy,
} from "@mui/icons-material";
import { useState, useCallback, useEffect, useRef } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import Layout from "../components/layout/Layout";
import { problemsAPI } from "../services/problems";
import { submissionsAPI } from "../services/submissions";
import { useAuth } from "../contexts/AuthContext";
import MonacoEditor from "../components/code/MonacoEditor";

function ProblemDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  // State for problem data
  const [problem, setProblem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // State for all problems (for navigation)
  const [allProblems, setAllProblems] = useState([]);

  // State for tabs
  const [activeTab, setActiveTab] = useState(0);

  // State for code
  const [starterCode, setStarterCode] = useState("");
  const [solutionCode, setSolutionCode] = useState("");
  const [language, setLanguage] = useState("javascript");

  // State for submission
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);

  // State for hints
  const [hintsUsed, setHintsUsed] = useState(0);
  const [expandedHints, setExpandedHints] = useState([]);

  // Refs for editors
  const starterEditorRef = useRef(null);
  const solutionEditorRef = useRef(null);

  // Fetch problem data
  useEffect(() => {
    const fetchProblem = async () => {
      // RESET ALL SUBMISSION-RELATED STATES FIRST
      setSubmissionResult(null);
      setSolutionCode("");
      setHintsUsed(0);
      setExpandedHints([]);

      // Reset active tab to problem description for new problem
      setActiveTab(0);

      setLoading(true);
      setError(null);

      try {
        const problemData = await problemsAPI.getProblem(id);
        setProblem(problemData);

        // Determine language based on framework
        const framework = problemData.framework?.name || problemData.framework;
        const lang = framework === "django" ? "python" : "javascript";
        setLanguage(lang);

        // Fetch starter code data
        const starterData = await problemsAPI.getStarterCode(id);
        const contextCode = starterData.context_code || "";
        const starterCodeContent = starterData.starter_code || "";

        // For Starter Code editor: Show everything
        const fullStarterCode =
          `${contextCode}\n\n${starterCodeContent}`.trim();
        setStarterCode(fullStarterCode);

        // For Solution editor: Start completely empty
        setSolutionCode("");
      } catch (err) {
        console.error("Error fetching problem:", err);
        setError(
          err.response?.data?.detail ||
            "Failed to load problem. Please try again."
        );
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchProblem();
    }

    // Cleanup function when component unmounts or id changes
    return () => {
      // Optional: Clear any pending states
      setSubmissionResult(null);
      setSolutionCode("");
    };
  }, [id]);

  // Fetch all problems for navigation - Modified to filter by current framework
  useEffect(() => {
    const fetchAllProblems = async () => {
      try {
        // Get the framework from the current problem
        const framework = problem?.framework?.name || problem?.framework;

        if (framework) {
          // Pass framework as filter parameter to get only problems in this framework
          const data = await problemsAPI.getProblems({
            framework__name: framework,
          });
          setAllProblems(data.results || data || []);
        }
      } catch (err) {
        console.error("Error fetching all problems:", err);
      }
    };

    // Only fetch if problem is loaded
    if (problem) {
      fetchAllProblems();
    }
  }, [problem]);

  // Calculate filtered problems by framework
  const filteredProblems = problem
    ? allProblems.filter((p) => {
        const pFramework = p.framework?.name || p.framework;
        const currentFramework = problem.framework?.name || problem.framework;
        return pFramework === currentFramework;
      })
    : [];

  // Calculate current problem position within filtered problems
  const currentProblemIndex =
    problem && filteredProblems.length > 0
      ? filteredProblems.findIndex((p) => p.slug === problem.slug)
      : -1;
  const currentPosition =
    currentProblemIndex >= 0 ? currentProblemIndex + 1 : 0;
  const totalProblems = filteredProblems.length;
  const isFirstProblem = currentProblemIndex === 0;
  const isLastProblem = currentProblemIndex === totalProblems - 1;

  // Utility functions
  const getDifficultyConfig = useCallback((difficulty) => {
    const configs = {
      beginner: {
        color: "success",
        label: "Beginner",
        bgColor: "#D1FAE5",
        textColor: "#065F46",
      },
      intermediate: {
        color: "warning",
        label: "Intermediate",
        bgColor: "#FEF3C7",
        textColor: "#92400E",
      },
      pro: {
        color: "error",
        label: "Pro",
        bgColor: "#FEE2E2",
        textColor: "#991B1B",
      },
      veteran: {
        color: "error",
        label: "Veteran",
        bgColor: "#FECACA",
        textColor: "#7F1D1D",
      },
    };
    return (
      configs[difficulty] || {
        color: "default",
        label: difficulty,
        bgColor: "#E5E7EB",
        textColor: "#374151",
      }
    );
  }, []);

  const getFrameworkConfig = useCallback((framework) => {
    const configs = {
      react: {
        color: "#61DAFB",
        name: "React",
        bgColor: "#E0F2FE",
        textColor: "#0369A1",
      },
      django: {
        color: "#092E20",
        name: "Django",
        bgColor: "#D1FAE5",
        textColor: "#065F46",
      },
      angular: {
        color: "#DD0031",
        name: "Angular",
        bgColor: "#FEE2E2",
        textColor: "#991B1B",
      },
      express: {
        color: "#000000",
        name: "Express",
        bgColor: "#E5E7EB",
        textColor: "#374151",
      },
    };
    return (
      configs[framework] || {
        color: "#6B7280",
        name: framework,
        bgColor: "#F3F4F6",
        textColor: "#4B5563",
      }
    );
  }, []);

  // Event handlers
  const handleTabChange = useCallback((event, newValue) => {
    setActiveTab(newValue);
  }, []);

  const handleSolutionCodeChange = useCallback((value) => {
    setSolutionCode(value || "");
  }, []);

  const handleCopyImports = useCallback(() => {
    if (starterCode) {
      // Extract just the imports/context part from starterCode
      const lines = starterCode.split("\n");
      const importsOnly = lines
        .filter(
          (line) =>
            line.includes("import") ||
            line.includes("require") ||
            line.trim().startsWith("#") ||
            (language === "python" &&
              (line.includes("from ") || line.includes("import ")))
        )
        .join("\n");

      navigator.clipboard
        .writeText(importsOnly.trim() || starterCode)
        .then(() => {
          console.log("Imports copied to clipboard");
        });
    }
  }, [starterCode, language]);

  const handleSubmit = useCallback(async () => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }

    if (!problem || !solutionCode.trim()) {
      setSubmissionResult({
        success: false,
        message: "Please write some code before submitting.",
        score: 0,
        feedback: [],
      });
      return;
    }

    setIsSubmitting(true);
    setSubmissionResult(null);

    try {
      const result = await submissionsAPI.submitCode({
        problem: problem.id,
        code: solutionCode,
        language: language,
        hints_used: hintsUsed,
      });

      // Convert score to number if it's a string
      const scoreValue =
        typeof result.score === "string"
          ? parseFloat(result.score)
          : Number(result.score || 0);

      const isAccepted = result.verdict === "accepted";
      const isPassing = scoreValue >= (problem.passing_score || 80);

      setSubmissionResult({
        success: isAccepted || isPassing,
        message: isAccepted
          ? "Congratulations! Your solution passed all test cases."
          : isPassing
          ? `Your solution scored ${scoreValue.toFixed(
              1
            )}% and meets the passing threshold!`
          : `Your solution scored ${scoreValue.toFixed(1)}%. Keep trying!`,
        score: scoreValue,
        verdict: result.verdict,
        feedback: result.feedback || [],
        validationResults: result.validation_results,
        executionTime: result.execution_time_ms
          ? `${(result.execution_time_ms / 1000).toFixed(2)}s`
          : "N/A",
        matchedPatterns: result.matched_patterns || [],
      });

      // Scroll to results
      setTimeout(() => {
        const resultsElement = document.getElementById("submission-results");
        if (resultsElement) {
          resultsElement.scrollIntoView({ behavior: "smooth" });
        }
      }, 100);
    } catch (err) {
      console.error("Submission error:", err);
      setSubmissionResult({
        success: false,
        message:
          err.response?.data?.detail || "Submission failed. Please try again.",
        score: 0,
        feedback: [],
      });
    } finally {
      setIsSubmitting(false);
    }
  }, [problem, solutionCode, isLoggedIn, navigate, language, hintsUsed]);

  const handleReset = useCallback(async () => {
    // Reset solution editor to empty
    setSolutionCode("");
    setSubmissionResult(null);
    setHintsUsed(0);
    setExpandedHints([]);
  }, []);

  const handleShowSolution = useCallback(() => {
    if (problem && submissionResult?.success) {
      const primaryPattern = problem.patterns?.find((p) => p.is_primary);
      if (primaryPattern?.example_code) {
        setSolutionCode(primaryPattern.example_code);
      }
    }
  }, [problem, submissionResult]);

  const handleCopyStarterCode = useCallback(() => {
    navigator.clipboard.writeText(starterCode).then(() => {
      console.log("Starter code copied to clipboard");
    });
  }, [starterCode]);

  const handleEditorMount = useCallback(
    (editor, monaco, editorType) => {
      if (editorType === "starter") {
        starterEditorRef.current = editor;
        // Make starter editor read-only
        editor.updateOptions({ readOnly: true });
      } else {
        solutionEditorRef.current = editor;

        // Add keyboard shortcut for submission
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
          handleSubmit();
        });

        editor.focus();
      }
    },
    [handleSubmit]
  );

  const difficultyConfig = problem
    ? getDifficultyConfig(problem.difficulty)
    : { color: "default", label: "" };
  const frameworkConfig = problem
    ? getFrameworkConfig(problem.framework?.name || problem.framework)
    : { color: "#6B7280", name: "" };
  const acceptanceRateValue = problem
    ? Number(problem.acceptance_rate ?? 0)
    : 0;
  const displayAcceptanceRate = Number.isFinite(acceptanceRateValue)
    ? acceptanceRateValue.toFixed(0)
    : "0";

  // Extract errors for editor highlighting
  const editorErrors =
    submissionResult?.feedback
      ?.filter((f) => f.type === "error")
      .map((f) => ({
        line: f.line || 1,
        column: f.column || 1,
        message: f.message || "Error",
        severity: 8,
      })) || [];

  // Show loading state
  if (loading) {
    return (
      <Layout>
        <Container
          maxWidth="xl"
          sx={{
            py: { xs: 2, md: 3 },
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "60vh",
          }}
        >
          <CircularProgress />
        </Container>
      </Layout>
    );
  }

  // Show error state
  if (error || !problem) {
    return (
      <Layout>
        <Container maxWidth="xl" sx={{ py: { xs: 2, md: 3 } }}>
          <Alert
            severity="error"
            sx={{ mb: 3 }}
            action={
              <Button
                component={Link}
                to="/problems"
                variant="outlined"
                size="small"
              >
                Back to Problems
              </Button>
            }
          >
            {error || "Problem not found"}
          </Alert>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container
        maxWidth="xl"
        sx={{ py: { xs: 2, md: 3 }, px: { xs: 1, sm: 2, md: 3 } }}
      >
        {/* Header Navigation */}
        <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 4 }}>
          <Tooltip title="Back to problems">
            <IconButton
              component={Link}
              to="/problems"
              sx={{
                border: "1px solid #E2E8F0",
                "&:hover": { backgroundColor: "#F8FAFC" },
              }}
            >
              <ArrowBack />
            </IconButton>
          </Tooltip>
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="body2"
              sx={{ color: "#64748B", fontWeight: 500, mb: 0.5 }}
            >
              {frameworkConfig.name} Challenge
            </Typography>
            <Typography variant="h5" sx={{ color: "#0F172A", fontWeight: 700 }}>
              {problem.title}
            </Typography>
          </Box>
          <Stack direction="row" spacing={1}>
            <Tooltip title="Bookmark">
              <IconButton
                sx={{ color: "#64748B", border: "1px solid #E2E8F0" }}
              >
                <Bookmark />
              </IconButton>
            </Tooltip>
            <Tooltip title="Share">
              <IconButton
                sx={{ color: "#64748B", border: "1px solid #E2E8F0" }}
              >
                <Share />
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>

        {/* Challenge Progress Bar - Shows progress within current framework */}
        {filteredProblems.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Stack direction="row" alignItems="center" spacing={2}>
              <Typography
                variant="body2"
                sx={{ color: "#64748B", fontWeight: 500, minWidth: 100 }}
              >
                {frameworkConfig.name} Challenge {currentPosition} of{" "}
                {totalProblems}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(currentPosition / totalProblems) * 100}
                sx={{
                  flex: 1,
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: "#E2E8F0",
                  "& .MuiLinearProgress-bar": {
                    backgroundColor: "#3B82F6",
                    borderRadius: 4,
                  },
                }}
              />
              <Chip
                label={`${Math.round(
                  (currentPosition / totalProblems) * 100
                )}% Complete`}
                size="small"
                sx={{
                  backgroundColor: "#E0F2FE",
                  color: "#0369A1",
                  fontWeight: 600,
                }}
              />
            </Stack>
          </Box>
        )}

        {/* Main Content with Tabs */}
        <Card
          sx={{
            border: "1px solid #E2E8F0",
            borderRadius: 3,
            overflow: "hidden",
            mb: 3,
          }}
        >
          {/* Tabs Header */}
          <AppBar
            position="static"
            elevation={0}
            sx={{
              backgroundColor: "#F8FAFC",
              borderBottom: "1px solid #E2E8F0",
            }}
          >
            <Toolbar
              variant="dense"
              sx={{ minHeight: "48px !important", px: { xs: 1, sm: 2 } }}
            >
              <Tabs
                value={activeTab}
                onChange={handleTabChange}
                sx={{
                  flex: 1,
                  minWidth: 0,
                  "& .MuiTabs-indicator": {
                    backgroundColor: "#3B82F6",
                    height: 3,
                  },
                  "& .MuiTab-root": {
                    minHeight: 48,
                    fontWeight: 600,
                    textTransform: "none",
                    fontSize: "0.9rem",
                    color: "#64748B",
                    minWidth: "auto",
                    px: { xs: 1, sm: 2 },
                    "&.Mui-selected": {
                      color: "#0F172A",
                    },
                  },
                }}
              >
                <Tab
                  icon={<Description />}
                  iconPosition="start"
                  label="Problem Description"
                />
                <Tab
                  icon={<Code />}
                  iconPosition="start"
                  label="Code Workspace"
                />
              </Tabs>

              {/* Stats Badge */}
              <Stack direction="row" spacing={1} alignItems="center">
                <Chip
                  label={frameworkConfig.name}
                  size="small"
                  sx={{
                    backgroundColor: frameworkConfig.bgColor,
                    color: frameworkConfig.textColor,
                    fontWeight: 600,
                    border: `1px solid ${frameworkConfig.color}30`,
                    display: { xs: "none", sm: "flex" },
                  }}
                />
                <Chip
                  label={difficultyConfig.label}
                  size="small"
                  sx={{
                    backgroundColor: difficultyConfig.bgColor,
                    color: difficultyConfig.textColor,
                    fontWeight: 600,
                    border: `1px solid ${difficultyConfig.textColor}30`,
                  }}
                />
              </Stack>
            </Toolbar>
          </AppBar>

          {/* Tab Content */}
          <Box sx={{ p: 0 }}>
            {/* Tab 1: Problem Description */}
            {activeTab === 0 && (
              <Fade in timeout={300}>
                <Box>
                  <Grid container spacing={0}>
                    {/* Problem Content */}
                    <Grid item xs={12}>
                      <Box sx={{ p: { xs: 2, sm: 3 } }}>
                        {/* Quick Stats */}
                        <Stack
                          direction="row"
                          spacing={{ xs: 1, sm: 3 }}
                          sx={{
                            mb: 4,
                            p: 2,
                            backgroundColor: "#F8FAFC",
                            borderRadius: 2,
                            flexWrap: "wrap",
                          }}
                        >
                          <Box
                            sx={{ flex: 1, minWidth: 100, textAlign: "center" }}
                          >
                            <TrendingUp
                              sx={{ color: "#10B981", fontSize: 24, mb: 1 }}
                            />
                            <Typography
                              variant="body2"
                              sx={{ color: "#64748B", fontWeight: 500 }}
                            >
                              Success Rate
                            </Typography>
                            <Typography
                              variant="h6"
                              sx={{ color: "#0F172A", fontWeight: 700 }}
                            >
                              {displayAcceptanceRate}%
                            </Typography>
                          </Box>
                          <Divider
                            orientation="vertical"
                            flexItem
                            sx={{ display: { xs: "none", sm: "block" } }}
                          />
                          <Box
                            sx={{ flex: 1, minWidth: 100, textAlign: "center" }}
                          >
                            <Schedule
                              sx={{ color: "#3B82F6", fontSize: 24, mb: 1 }}
                            />
                            <Typography
                              variant="body2"
                              sx={{ color: "#64748B", fontWeight: 500 }}
                            >
                              Avg. Time
                            </Typography>
                            <Typography
                              variant="h6"
                              sx={{ color: "#0F172A", fontWeight: 700 }}
                            >
                              {problem.estimated_time_minutes
                                ? `${problem.estimated_time_minutes} min`
                                : "N/A"}
                            </Typography>
                          </Box>
                          <Divider
                            orientation="vertical"
                            flexItem
                            sx={{ display: { xs: "none", sm: "block" } }}
                          />
                          <Box
                            sx={{ flex: 1, minWidth: 100, textAlign: "center" }}
                          >
                            <CodeIcon
                              sx={{ color: "#8B5CF6", fontSize: 24, mb: 1 }}
                            />
                            <Typography
                              variant="body2"
                              sx={{ color: "#64748B", fontWeight: 500 }}
                            >
                              Difficulty
                            </Typography>
                            <Typography
                              variant="h6"
                              sx={{ color: "#0F172A", fontWeight: 700 }}
                            >
                              {difficultyConfig.label}
                            </Typography>
                          </Box>
                        </Stack>

                        {/* Problem Description */}
                        <Typography
                          variant="body1"
                          sx={{
                            color: "#374151",
                            lineHeight: 1.8,
                            whiteSpace: "pre-line",
                            mb: 4,
                            "& h3": {
                              color: "#0F172A",
                              mt: 3,
                              mb: 2,
                              fontSize: "1.25rem",
                              fontWeight: 600,
                            },
                            "& h4": {
                              color: "#0F172A",
                              mt: 2,
                              mb: 1,
                              fontSize: "1.1rem",
                              fontWeight: 600,
                            },
                            "& p": { mb: 2 },
                            "& ul, & ol": {
                              pl: 2,
                              mb: 2,
                              "& li": { mb: 1 },
                            },
                            "& code": {
                              backgroundColor: "#F3F4F6",
                              padding: "2px 6px",
                              borderRadius: 1,
                              fontFamily: "'Fira Code', monospace",
                              fontSize: "0.9em",
                              color: "#1F2937",
                            },
                            "& pre": {
                              backgroundColor: "#1F2937",
                              color: "white",
                              padding: 3,
                              borderRadius: 2,
                              overflow: "auto",
                              margin: "16px 0",
                              fontFamily: "'Fira Code', monospace",
                              fontSize: "0.9rem",
                              lineHeight: 1.5,
                            },
                          }}
                        >
                          {problem.description}
                        </Typography>

                        {/* Target Area */}
                        {problem.target_area && (
                          <Alert
                            severity="info"
                            icon={<Info />}
                            sx={{
                              mb: 3,
                              borderRadius: 2,
                              backgroundColor: "#E0F2FE",
                              "& .MuiAlert-icon": { color: "#0EA5E9" },
                            }}
                          >
                            <Typography
                              variant="body2"
                              sx={{ fontWeight: 600, color: "#0369A1" }}
                            >
                              Target Area:
                            </Typography>
                            <Typography
                              variant="body2"
                              sx={{ color: "#0C4A6E", mt: 0.5 }}
                            >
                              {problem.target_area}
                            </Typography>
                          </Alert>
                        )}

                        {/* Hints Section */}
                        {problem.hints?.length > 0 && (
                          <Box sx={{ mb: 3 }}>
                            <Typography
                              variant="h6"
                              sx={{ color: "#0F172A", fontWeight: 600, mb: 2 }}
                            >
                              Hints ({problem.hints.length})
                            </Typography>
                            <Stack spacing={2}>
                              {problem.hints.map((hint, index) => {
                                const isExpanded =
                                  expandedHints.includes(index);

                                const handleHintClick = () => {
                                  if (
                                    !isExpanded &&
                                    !expandedHints.includes(index)
                                  ) {
                                    setHintsUsed((prev) => prev + 1);
                                  }
                                  setExpandedHints((prev) =>
                                    isExpanded
                                      ? prev.filter((i) => i !== index)
                                      : [...prev, index]
                                  );
                                };

                                return (
                                  <Alert
                                    key={index}
                                    icon={<Lightbulb />}
                                    severity="warning"
                                    onClick={handleHintClick}
                                    sx={{
                                      borderRadius: 2,
                                      cursor: "pointer",
                                      transition: "all 0.2s",
                                      "&:hover": { backgroundColor: "#FFFBEB" },
                                    }}
                                  >
                                    <Box>
                                      <Typography
                                        variant="body2"
                                        sx={{ fontWeight: 600, mb: 0.5 }}
                                      >
                                        Hint {index + 1}
                                      </Typography>

                                      {isExpanded ? (
                                        <>
                                          <Typography
                                            variant="body2"
                                            sx={{ color: "#374151", mb: 1 }}
                                          >
                                            {hint}
                                          </Typography>
                                          <Typography
                                            variant="caption"
                                            sx={{
                                              color: "#6B7280",
                                              fontStyle: "italic",
                                            }}
                                          >
                                            Click to hide
                                          </Typography>
                                        </>
                                      ) : (
                                        <Typography
                                          variant="body2"
                                          sx={{
                                            color: "#92400E",
                                            fontStyle: "italic",
                                          }}
                                        >
                                          Click to reveal hint
                                        </Typography>
                                      )}
                                    </Box>
                                  </Alert>
                                );
                              })}
                            </Stack>
                          </Box>
                        )}

                        {/* Learning Resources */}
                        {problem.learning_resources?.length > 0 && (
                          <Box>
                            <Typography
                              variant="h6"
                              sx={{ color: "#0F172A", fontWeight: 600, mb: 2 }}
                            >
                              Learning Resources
                            </Typography>
                            <Stack spacing={1}>
                              {problem.learning_resources.map(
                                (resource, index) => (
                                  <Button
                                    key={index}
                                    href={resource.url || resource}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    sx={{
                                      justifyContent: "flex-start",
                                      textAlign: "left",
                                      color: "#3B82F6",
                                      "&:hover": { backgroundColor: "#EFF6FF" },
                                    }}
                                  >
                                    <Typography
                                      variant="body2"
                                      sx={{ fontWeight: 500 }}
                                    >
                                      {resource.title || resource}
                                    </Typography>
                                  </Button>
                                )
                              )}
                            </Stack>
                          </Box>
                        )}
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              </Fade>
            )}

            {/* Tab 2: Code Workspace */}
            {activeTab === 1 && (
              <Fade in timeout={300}>
                <Box
                  sx={{
                    height: "calc(100vh - 280px)",
                    minHeight: 600,
                    width: "100%",
                  }}
                >
                  <Grid
                    container
                    spacing={0}
                    sx={{ height: "100%", width: "100%", margin: 0 }}
                  >
                    {/* Left Panel: Starter Code */}
                    <Grid
                      item
                      xs={12}
                      md={6}
                      sx={{
                        height: "100%",
                        width: "50%",
                        borderRight: "1px solid #E2E8F0",
                        display: "flex",
                        flexDirection: "column",
                      }}
                    >
                      <Box
                        sx={{
                          height: "100%",
                          width: "100%",
                          display: "flex",
                          flexDirection: "column",
                        }}
                      >
                        {/* Starter Code Header */}
                        <Box
                          sx={{
                            p: 2,
                            borderBottom: "1px solid #E2E8F0",
                            backgroundColor: "#F8FAFC",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            width: "100%",
                          }}
                        >
                          <Typography
                            variant="subtitle1"
                            sx={{ color: "#0F172A", fontWeight: 600 }}
                          >
                            <CodeIcon
                              sx={{
                                mr: 1,
                                fontSize: 18,
                                verticalAlign: "middle",
                              }}
                            />
                            Starter Code
                          </Typography>
                          <Stack direction="row" spacing={1}>
                            <Tooltip title="Copy starter code">
                              <IconButton
                                size="small"
                                onClick={handleCopyStarterCode}
                              >
                                <ContentCopy sx={{ fontSize: 16 }} />
                              </IconButton>
                            </Tooltip>
                            <Chip
                              label="Read Only"
                              size="small"
                              sx={{
                                backgroundColor: "#E5E7EB",
                                color: "#4B5563",
                                fontWeight: 500,
                                fontSize: "0.7rem",
                              }}
                            />
                          </Stack>
                        </Box>

                        {/* Starter Code Editor */}
                        <Box
                          sx={{
                            flex: 1,
                            overflow: "hidden",
                            width: "100%",
                          }}
                        >
                          <MonacoEditor
                            value={starterCode}
                            language={language}
                            theme="vs-light"
                            onMount={(editor, monaco) =>
                              handleEditorMount(editor, monaco, "starter")
                            }
                            options={{
                              readOnly: true,
                              fontSize: 14,
                              minimap: { enabled: false },
                              scrollBeyondLastLine: false,
                              wordWrap: "on",
                              automaticLayout: true,
                              lineNumbers: "on",
                              glyphMargin: false,
                              folding: true,
                              lineDecorationsWidth: 10,
                              renderLineHighlight: "none",
                              cursorStyle: "block",
                              cursorBlinking: "solid",
                            }}
                          />
                        </Box>
                      </Box>
                    </Grid>

                    {/* Right Panel: Solution Editor */}
                    <Grid
                      item
                      xs={12}
                      md={6}
                      sx={{
                        height: "100%",
                        width: "50%",
                        display: "flex",
                        flexDirection: "column",
                      }}
                    >
                      <Box
                        sx={{
                          height: "100%",
                          width: "100%",
                          display: "flex",
                          flexDirection: "column",
                        }}
                      >
                        {/* Solution Header */}
                        <Box
                          sx={{
                            p: 2,
                            borderBottom: "1px solid #E2E8F0",
                            backgroundColor: "#F8FAFC",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            width: "100%",
                          }}
                        >
                          <Typography
                            variant="subtitle1"
                            sx={{ color: "#0F172A", fontWeight: 600 }}
                          >
                            <Edit
                              sx={{
                                mr: 1,
                                fontSize: 18,
                                verticalAlign: "middle",
                              }}
                            />
                            Your Solution
                          </Typography>
                          <Stack direction="row" spacing={1}>
                            <Button
                              size="small"
                              startIcon={<ContentCopy />}
                              onClick={handleCopyImports}
                              disabled={!starterCode}
                              sx={{ textTransform: "none" }}
                            >
                              Copy Imports
                            </Button>
                            <Button
                              size="small"
                              startIcon={<Refresh />}
                              onClick={handleReset}
                              disabled={isSubmitting}
                              sx={{ textTransform: "none" }}
                            >
                              Reset
                            </Button>
                            {submissionResult?.success && (
                              <Button
                                size="small"
                                startIcon={<Visibility />}
                                onClick={handleShowSolution}
                                disabled={isSubmitting}
                                sx={{ textTransform: "none" }}
                              >
                                Show Solution
                              </Button>
                            )}
                          </Stack>
                        </Box>

                        {/* Solution Editor */}
                        <Box
                          sx={{
                            flex: 1,
                            overflow: "hidden",
                            width: "100%",
                          }}
                        >
                          <MonacoEditor
                            value={solutionCode}
                            onChange={handleSolutionCodeChange}
                            language={language}
                            theme="vs-dark"
                            onMount={(editor, monaco) =>
                              handleEditorMount(editor, monaco, "solution")
                            }
                            errors={editorErrors}
                            options={{
                              fontSize: 14,
                              minimap: { enabled: false },
                              scrollBeyondLastLine: false,
                              wordWrap: "on",
                              automaticLayout: true,
                              formatOnPaste: true,
                              formatOnType: true,
                              suggestOnTriggerCharacters: true,
                              acceptSuggestionOnEnter: "on",
                              tabSize: 2,
                              insertSpaces: true,
                              autoIndent: "full",
                              matchBrackets: "always",
                              lineNumbers: "on",
                              glyphMargin: true,
                              folding: true,
                              lineDecorationsWidth: 10,
                              renderLineHighlight: "all",
                              cursorBlinking: "blink",
                              cursorStyle: "line",
                              cursorWidth: 2,
                            }}
                          />
                        </Box>

                        {/* Submission Panel */}
                        <Box
                          sx={{
                            borderTop: "1px solid #E2E8F0",
                            backgroundColor: "white",
                            width: "100%",
                          }}
                        >
                          <Box sx={{ p: 2, width: "100%" }}>
                            <Button
                              variant="contained"
                              fullWidth
                              size="large"
                              startIcon={isSubmitting ? null : <PlayArrow />}
                              onClick={handleSubmit}
                              disabled={
                                isSubmitting ||
                                problem.is_premium ||
                                !isLoggedIn
                              }
                              sx={{
                                py: 1.5,
                                fontWeight: 600,
                                fontSize: "1rem",
                                borderRadius: 2,
                                background: isSubmitting
                                  ? "#6B7280"
                                  : problem.is_premium
                                  ? "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)"
                                  : "linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)",
                                "&:hover": {
                                  background: problem.is_premium
                                    ? "linear-gradient(135deg, #D97706 0%, #B45309 100%)"
                                    : "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)",
                                  transform: "translateY(-1px)",
                                  boxShadow:
                                    "0 4px 12px rgba(59, 130, 246, 0.3)",
                                },
                                "&.Mui-disabled": {
                                  background: "#9CA3AF",
                                  transform: "none",
                                },
                                transition: "all 0.2s ease",
                              }}
                            >
                              {isSubmitting ? (
                                <>
                                  <CircularProgress
                                    size={20}
                                    sx={{ color: "white", mr: 1 }}
                                  />
                                  Testing Solution...
                                </>
                              ) : !isLoggedIn ? (
                                "Login to Submit"
                              ) : problem.is_premium ? (
                                <>
                                  <Lock sx={{ mr: 1 }} />
                                  Unlock Pro to Solve
                                </>
                              ) : (
                                "Submit Solution"
                              )}
                            </Button>

                            <Typography
                              variant="caption"
                              sx={{
                                color: "#9CA3AF",
                                display: "block",
                                textAlign: "center",
                                mt: 1,
                              }}
                            >
                              Press Ctrl/Cmd + Enter to submit quickly
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              </Fade>
            )}
          </Box>
        </Card>

        {/* Submission Results Card */}
        {submissionResult && (
          <Box id="submission-results" sx={{ mb: 3 }}>
            <Card
              sx={{
                border: "1px solid #E2E8F0",
                borderRadius: 3,
                transition: "all 0.3s ease",
                borderColor: submissionResult.success ? "#10B981" : "#EF4444",
                boxShadow: `0 0 0 1px ${
                  submissionResult.success ? "#10B98140" : "#EF444440"
                }`,
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Fade in timeout={500}>
                  <Box>
                    {/* Result Header */}
                    <Stack
                      direction="row"
                      alignItems="center"
                      spacing={2}
                      sx={{ mb: 3 }}
                    >
                      {submissionResult.success ? (
                        <CheckCircle sx={{ color: "#10B981", fontSize: 40 }} />
                      ) : (
                        <Error sx={{ color: "#EF4444", fontSize: 40 }} />
                      )}
                      <Box>
                        <Typography
                          variant="h5"
                          sx={{ color: "#0F172A", fontWeight: 700 }}
                        >
                          {submissionResult.success ? "Success!" : "Try Again"}
                        </Typography>
                        <Typography variant="body1" sx={{ color: "#64748B" }}>
                          {submissionResult.message}
                        </Typography>
                      </Box>
                    </Stack>

                    {/* Score & Details */}
                    <Stack direction="row" spacing={4} sx={{ mb: 3 }}>
                      <Box>
                        <Typography
                          variant="caption"
                          sx={{ color: "#64748B", display: "block" }}
                        >
                          Score
                        </Typography>
                        <Typography
                          variant="h3"
                          sx={{ color: "#0F172A", fontWeight: 800 }}
                        >
                          {submissionResult.score.toFixed(1)}%
                        </Typography>
                      </Box>
                      <Box>
                        <Typography
                          variant="caption"
                          sx={{ color: "#64748B", display: "block" }}
                        >
                          Verdict
                        </Typography>
                        <Chip
                          label={
                            submissionResult.verdict?.replace("_", " ") ||
                            "Unknown"
                          }
                          size="medium"
                          sx={{
                            backgroundColor: submissionResult.success
                              ? "#10B981"
                              : "#EF4444",
                            color: "white",
                            fontWeight: 600,
                            fontSize: "0.9rem",
                            textTransform: "capitalize",
                          }}
                        />
                      </Box>
                      {submissionResult.executionTime && (
                        <Box>
                          <Typography
                            variant="caption"
                            sx={{ color: "#64748B", display: "block" }}
                          >
                            Execution Time
                          </Typography>
                          <Typography
                            variant="h6"
                            sx={{ color: "#0F172A", fontWeight: 600 }}
                          >
                            {submissionResult.executionTime}
                          </Typography>
                        </Box>
                      )}
                    </Stack>

                    {/* Progress Bar */}
                    <Box sx={{ mb: 3 }}>
                      <LinearProgress
                        variant="determinate"
                        value={submissionResult.score}
                        sx={{
                          height: 10,
                          borderRadius: 5,
                          backgroundColor: "#E2E8F0",
                          "& .MuiLinearProgress-bar": {
                            backgroundColor: submissionResult.success
                              ? "#10B981"
                              : submissionResult.score >= 50
                              ? "#F59E0B"
                              : "#EF4444",
                            borderRadius: 5,
                          },
                        }}
                      />
                    </Box>

                    {/* Detailed Feedback */}
                    {submissionResult.feedback?.length > 0 && (
                      <Box>
                        <Typography
                          variant="subtitle1"
                          sx={{ color: "#0F172A", fontWeight: 600, mb: 2 }}
                        >
                          Detailed Feedback
                        </Typography>
                        <Stack spacing={1}>
                          {submissionResult.feedback.map((item, index) => (
                            <Alert
                              key={index}
                              severity={
                                item.type === "error"
                                  ? "error"
                                  : item.type === "warning"
                                  ? "warning"
                                  : "info"
                              }
                              icon={
                                item.type === "error" ? (
                                  <Error />
                                ) : item.type === "warning" ? (
                                  <Warning />
                                ) : (
                                  <Info />
                                )
                              }
                              sx={{
                                borderRadius: 2,
                                py: 1,
                                "& .MuiAlert-message": { py: 0.5 },
                              }}
                            >
                              <Typography
                                variant="body2"
                                sx={{ fontWeight: 500 }}
                              >
                                {item.line && `Line ${item.line}: `}
                                {item.message}
                                {item.suggestion && (
                                  <Typography
                                    variant="caption"
                                    sx={{
                                      color: "#6B7280",
                                      display: "block",
                                      mt: 0.5,
                                    }}
                                  >
                                    Suggestion: {item.suggestion}
                                  </Typography>
                                )}
                              </Typography>
                            </Alert>
                          ))}
                        </Stack>
                      </Box>
                    )}
                  </Box>
                </Fade>
              </CardContent>
            </Card>
          </Box>
        )}

        {/* Navigation Controls - Shows navigation within current framework */}
        {filteredProblems.length > 0 && problem && (
          <Card
            sx={{
              border: "1px solid #E2E8F0",
              borderRadius: 3,
              backgroundColor: "#F8FAFC",
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Stack
                direction={{ xs: "column", md: "row" }}
                spacing={3}
                alignItems="center"
                justifyContent="space-between"
              >
                {/* Progress and Jump Selector */}
                <Stack
                  direction="row"
                  alignItems="center"
                  spacing={3}
                  sx={{ flex: 1 }}
                >
                  {/* Progress Display */}
                  <Box sx={{ minWidth: 120 }}>
                    <Typography
                      variant="body2"
                      sx={{ color: "#64748B", fontWeight: 500, mb: 0.5 }}
                    >
                      Progress in {frameworkConfig.name}
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{ fontWeight: 700, color: "#0F172A" }}
                    >
                      {currentPosition} / {totalProblems}
                    </Typography>
                  </Box>

                  {/* Jump to Challenge Selector - Only shows problems in current framework */}
                  <FormControl sx={{ minWidth: 200, flex: 1 }}>
                    <InputLabel>
                      Jump to {frameworkConfig.name} Challenge
                    </InputLabel>
                    <Select
                      value={problem.slug}
                      label={`Jump to ${frameworkConfig.name} Challenge`}
                      onChange={(e) => navigate(`/problems/${e.target.value}`)}
                      sx={{
                        backgroundColor: "white",
                        "& .MuiSelect-select": {
                          py: 1.5,
                        },
                      }}
                    >
                      {filteredProblems.map((p, index) => (
                        <MenuItem key={p.slug} value={p.slug}>
                          <Stack
                            direction="row"
                            alignItems="center"
                            spacing={2}
                            sx={{ width: "100%" }}
                          >
                            <Chip
                              label={`${index + 1}`}
                              size="small"
                              sx={{
                                backgroundColor:
                                  p.slug === problem.slug
                                    ? "#3B82F6"
                                    : "#E5E7EB",
                                color:
                                  p.slug === problem.slug ? "white" : "#4B5563",
                                fontWeight: 600,
                                minWidth: 32,
                              }}
                            />
                            <Typography
                              variant="body2"
                              sx={{
                                flex: 1,
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                whiteSpace: "nowrap",
                                fontWeight: p.slug === problem.slug ? 600 : 400,
                                color:
                                  p.slug === problem.slug
                                    ? "#0F172A"
                                    : "#374151",
                              }}
                            >
                              {p.title}
                            </Typography>
                            {p.slug === problem.slug && (
                              <CheckCircle
                                sx={{ fontSize: 18, color: "#10B981" }}
                              />
                            )}
                          </Stack>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Stack>

                {/* Navigation Buttons - Navigates within current framework */}
                <Stack direction="row" spacing={2}>
                  <Button
                    variant="outlined"
                    startIcon={<ArrowBack />}
                    onClick={() => {
                      if (!isFirstProblem) {
                        // Optional: Clear submission results immediately for better UX
                        setSubmissionResult(null);
                        const prevProblem =
                          filteredProblems[currentProblemIndex - 1];
                        navigate(`/problems/${prevProblem.slug}`);
                      }
                    }}
                    disabled={isFirstProblem}
                    sx={{
                      px: 4,
                      py: 1.5,
                      borderRadius: 2,
                      textTransform: "none",
                      fontWeight: 600,
                      fontSize: "1rem",
                      borderColor: "#CBD5E1",
                      color: "#475569",
                      minWidth: 160,
                      "&:hover": {
                        backgroundColor: "#F1F5F9",
                        borderColor: "#94A3B8",
                      },
                      "&.Mui-disabled": {
                        borderColor: "#E2E8F0",
                        color: "#94A3B8",
                      },
                    }}
                  >
                    Previous Challenge
                  </Button>

                  <Button
                    variant="contained"
                    endIcon={<ArrowForward />}
                    onClick={() => {
                      if (!isLastProblem) {
                        // Optional: Clear submission results immediately for better UX
                        setSubmissionResult(null);
                        const nextProblem =
                          filteredProblems[currentProblemIndex + 1];
                        navigate(`/problems/${nextProblem.slug}`);
                      } else {
                        navigate("/problems");
                      }
                    }}
                    disabled={isLastProblem}
                    sx={{
                      px: 4,
                      py: 1.5,
                      borderRadius: 2,
                      textTransform: "none",
                      fontWeight: 600,
                      fontSize: "1rem",
                      background:
                        "linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)",
                      minWidth: 160,
                      "&:hover": {
                        background:
                          "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)",
                        transform: "translateY(-2px)",
                        boxShadow: "0 4px 12px rgba(59, 130, 246, 0.3)",
                      },
                      "&.Mui-disabled": {
                        background: "#CBD5E1",
                        transform: "none",
                        boxShadow: "none",
                      },
                    }}
                  >
                    Next Challenge
                  </Button>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        )}
      </Container>
    </Layout>
  );
}

export default ProblemDetail;
