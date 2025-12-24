import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import Login from "./pages/Login";
import Home from "./pages/Home";
import Profile from "./pages/Profile";
import ProblemsList from "./pages/ProblemsList";
import ProblemDetail from "./pages/ProblemDetail";
import Register from "./pages/Register";
import Submissions from "./pages/Submissions";
import Leaderboard from "./pages/Leaderboard";
import UserProfile from "./pages/UserProfile";
import NotFound from "./pages/NotFound";

const theme = createTheme({
  palette: {
    primary: {
      main: "#3b82f6", // Blue from your project plan
    },
    secondary: {
      main: "#8b5cf6", // Purple for intermediate
    },
    background: {
      default: "#f8fafc", // Light gray background
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/problems" element={<ProblemsList />} />
            <Route path="/problems/:id" element={<ProblemDetail />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/submissions" element={<Submissions />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
            <Route path="/:username" element={<UserProfile />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
