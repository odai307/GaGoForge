// src/components/layout/Header.jsx
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  IconButton,
} from "@mui/material";
import {
  Code,
  AccountCircle,
  KeyboardArrowDown,
  Notifications,
  Leaderboard,
} from "@mui/icons-material";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";

function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isLoggedIn, user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const navItems = [
    {
      path: "/problems",
      label: "Challenges",
      icon: <Code sx={{ fontSize: 18 }} />,
    },
    {
      path: "/leaderboard",
      label: "Leaderboard",
      icon: <Leaderboard sx={{ fontSize: 18 }} />,
    },
  ];

  return (
    <AppBar
      position="sticky"
      sx={{
        background: "#0F172A",
        boxShadow: "none",
        borderBottom: "1px solid #1E293B",
        backdropFilter: "blur(10px)",
        backgroundColor: "rgba(15, 23, 42, 0.95)",
      }}
    >
      <Toolbar sx={{ py: 1 }}>
        {/* Logo */}
        <Box
          component={Link}
          to="/"
          sx={{
            display: "flex",
            alignItems: "center",
            textDecoration: "none",
            color: "inherit",
            mr: 4,
          }}
        >
          <Code
            sx={{
              fontSize: 32,
              mr: 1,
              color: "#3B82F6",
            }}
          />
          <Typography
            variant="h5"
            component="div"
            sx={{
              fontWeight: "bold",
              color: "#FFFFFF",
            }}
          >
            GaGoForge
          </Typography>
          <Chip
            label="Beta"
            size="small"
            sx={{
              ml: 1,
              height: 20,
              fontSize: "0.7rem",
              fontWeight: "bold",
              background: "#3B82F6",
              color: "white",
            }}
          />
        </Box>

        {/* Navigation Links */}
        <Box sx={{ display: { xs: "none", md: "flex" }, gap: 1, flexGrow: 1 }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              component={Link}
              to={item.path}
              startIcon={item.icon}
              sx={{
                color: "#E2E8F0",
                fontWeight: location.pathname === item.path ? "bold" : "normal",
                background:
                  location.pathname === item.path
                    ? "rgba(59, 130, 246, 0.2)"
                    : "transparent",
                borderRadius: 2,
                px: 2,
                py: 1,
                border:
                  location.pathname === item.path
                    ? "1px solid rgba(59, 130, 246, 0.3)"
                    : "1px solid transparent",
                "&:hover": {
                  background: "rgba(59, 130, 246, 0.15)",
                  border: "1px solid rgba(59, 130, 246, 0.4)",
                  transform: "translateY(-1px)",
                },
                transition: "all 0.2s ease",
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        {/* Right Side - Auth/Avatar */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          {isLoggedIn ? (
            <>
              <IconButton
                color="inherit"
                sx={{
                  background: "rgba(59, 130, 246, 0.1)",
                  border: "1px solid rgba(59, 130, 246, 0.3)",
                  color: "#E2E8F0",
                  "&:hover": {
                    background: "rgba(59, 130, 246, 0.2)",
                    transform: "translateY(-1px)",
                  },
                  transition: "all 0.2s ease",
                }}
              >
                <Notifications />
              </IconButton>

              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    background: "#3B82F6",
                    fontSize: "0.8rem",
                    fontWeight: "bold",
                  }}
                >
                  {user?.username?.charAt(0).toUpperCase() || "U"}
                </Avatar>
                <Button
                  color="inherit"
                  endIcon={<KeyboardArrowDown />}
                  onClick={handleMenu}
                  sx={{
                    textTransform: "none",
                    fontWeight: "medium",
                    color: "#E2E8F0",
                  }}
                >
                  {user?.username || "User"}
                </Button>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleClose}
                  PaperProps={{
                    sx: {
                      mt: 1,
                      background: "#0F172A",
                      color: "#E2E8F0",
                      border: "1px solid #1E293B",
                    },
                  }}
                >
                  <MenuItem
                    onClick={() => {
                      navigate("/profile");
                      handleClose();
                    }}
                    sx={{
                      "&:hover": {
                        background: "#1E293B",
                      },
                    }}
                  >
                    <AccountCircle sx={{ mr: 1 }} /> Profile
                  </MenuItem>
                  <MenuItem
                    onClick={() => {
                      logout();
                      handleClose();
                      navigate("/");
                    }}
                    sx={{
                      "&:hover": {
                        background: "#1E293B",
                      },
                    }}
                  >
                    Logout
                  </MenuItem>
                </Menu>
              </Box>
            </>
          ) : (
            <Box sx={{ display: "flex", gap: 1 }}>
              <Button
                component={Link}
                to="/login"
                color="inherit"
                sx={{
                  color: "#E2E8F0",
                  borderRadius: 2,
                  px: 3,
                  border: "1px solid #475569",
                  "&:hover": {
                    background: "#1E293B",
                    border: "1px solid #64748B",
                    transform: "translateY(-1px)",
                  },
                  transition: "all 0.2s ease",
                }}
              >
                Login
              </Button>
              <Button
                component={Link}
                to="/register"
                variant="contained"
                sx={{
                  background: "#3B82F6",
                  borderRadius: 2,
                  px: 3,
                  boxShadow: "0 4px 15px rgba(59, 130, 246, 0.4)",
                  border: "1px solid rgba(59, 130, 246, 0.3)",
                  "&:hover": {
                    background: "#2563EB",
                    boxShadow: "0 6px 20px rgba(59, 130, 246, 0.5)",
                    transform: "translateY(-2px)",
                  },
                  transition: "all 0.3s ease",
                }}
              >
                Sign Up Free
              </Button>
            </Box>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
