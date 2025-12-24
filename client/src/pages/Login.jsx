// src/pages/Login.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Link,
  InputAdornment,
  IconButton,
  CircularProgress,
} from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import {
  Login as LoginIcon,
  Visibility,
  VisibilityOff,
  Email,
  Lock,
} from "@mui/icons-material";
import Layout from "../components/layout/Layout";
import { useAuth } from "../contexts/AuthContext";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error when user starts typing
    if (error) setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const result = await login(formData.username, formData.password);

      if (result.success) {
        // Redirect to problems page or previous location
        navigate("/problems");
      } else {
        setError(
          result.error || "Login failed. Please check your credentials."
        );
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Box
        sx={{
          minHeight: "calc(100vh - 64px)",
          background: "#F8FAFC",
          display: "flex",
          alignItems: "center",
          py: 8,
        }}
      >
        <Container component="main" maxWidth="sm">
          <Paper
            elevation={8}
            sx={{
              padding: { xs: 3, sm: 5 },
              borderRadius: 3,
              background: "#FFFFFF",
              border: "1px solid #E2E8F0",
              boxShadow:
                "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            }}
          >
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <Box
                sx={{
                  width: 64,
                  height: 64,
                  borderRadius: "50%",
                  background: "#3B82F6",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  mb: 2,
                  boxShadow: "0 8px 24px rgba(59, 130, 246, 0.4)",
                }}
              >
                <LoginIcon sx={{ fontSize: 32, color: "white" }} />
              </Box>

              <Typography
                component="h1"
                variant="h4"
                gutterBottom
                sx={{
                  fontWeight: "bold",
                  color: "#0F172A",
                }}
              >
                Welcome Back
              </Typography>

              <Typography
                variant="body1"
                color="#64748B"
                align="center"
                sx={{ mb: 4, maxWidth: 400 }}
              >
                Sign in to continue your framework mastery journey
              </Typography>
            </Box>

            {error && (
              <Alert
                severity="error"
                sx={{
                  mb: 3,
                  borderRadius: 2,
                  border: "1px solid rgba(211, 47, 47, 0.3)",
                }}
              >
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label="Username"
                name="username"
                autoComplete="username"
                autoFocus
                value={formData.username}
                onChange={handleChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email sx={{ color: "#3B82F6" }} />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    "&:hover fieldset": {
                      borderColor: "#3B82F6",
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "#3B82F6",
                    },
                  },
                  "& .MuiInputLabel-root.Mui-focused": {
                    color: "#3B82F6",
                  },
                }}
              />

              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type={showPassword ? "text" : "password"}
                id="password"
                autoComplete="current-password"
                value={formData.password}
                onChange={handleChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock sx={{ color: "#3B82F6" }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    "&:hover fieldset": {
                      borderColor: "#3B82F6",
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "#3B82F6",
                    },
                  },
                  "& .MuiInputLabel-root.Mui-focused": {
                    color: "#3B82F6",
                  },
                }}
              />

              <Box sx={{ textAlign: "right", mt: 1 }}>
                <Link
                  component={RouterLink}
                  to="/forgot-password"
                  sx={{
                    color: "#3B82F6",
                    fontSize: "0.875rem",
                    textDecoration: "none",
                    "&:hover": {
                      textDecoration: "underline",
                    },
                  }}
                >
                  Forgot password?
                </Link>
              </Box>

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{
                  mt: 4,
                  mb: 2,
                  py: 1.5,
                  borderRadius: 2,
                  background: "#3B82F6",
                  boxShadow: "0 4px 20px rgba(59, 130, 246, 0.4)",
                  fontSize: "1.1rem",
                  fontWeight: "bold",
                  textTransform: "none",
                  "&:hover": {
                    background: "#2563EB",
                    boxShadow: "0 6px 28px rgba(59, 130, 246, 0.5)",
                    transform: "translateY(-2px)",
                  },
                  "&:disabled": {
                    background: "#9CA3AF",
                  },
                  transition: "all 0.3s ease",
                }}
              >
                {loading ? (
                  <>
                    <CircularProgress
                      size={20}
                      sx={{ mr: 1, color: "white" }}
                    />
                    Signing In...
                  </>
                ) : (
                  "Sign In"
                )}
              </Button>

              <Box sx={{ textAlign: "center", mt: 2 }}>
                <Typography variant="body2" color="#64748B">
                  Don't have an account?{" "}
                  <Link
                    component={RouterLink}
                    to="/register"
                    sx={{
                      color: "#3B82F6",
                      fontWeight: "bold",
                      textDecoration: "none",
                      "&:hover": {
                        textDecoration: "underline",
                      },
                    }}
                  >
                    Create Account
                  </Link>
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Container>
      </Box>
    </Layout>
  );
}

export default Login;
