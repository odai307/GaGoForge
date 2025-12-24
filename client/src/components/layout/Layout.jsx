// src/components/Layout/Layout.jsx
import { Box } from "@mui/material";
import Header from "./Header";

function Layout({ children }) {
  return (
    <Box sx={{ minHeight: "100vh", backgroundColor: "background.default" }}>
      <Header />
      <Box component="main">{children}</Box>
    </Box>
  );
}

export default Layout;
