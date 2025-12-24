// src/pages/Home.jsx
import {
  Container,
  Typography,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  Stack,
  Chip,
} from "@mui/material";
import {
  Code,
  Bolt,
  TrendingUp,
  EmojiEvents,
  PlayArrow,
  Security,
  Speed,
} from "@mui/icons-material";
import { Link } from "react-router-dom";
import Layout from "../components/layout/Layout";

function Home() {
  const frameworks = [
    {
      name: "React",
      color: "#61DAFB",
      icon: <Code />,
      description: "Master components, hooks, and state management",
    },
    {
      name: "Django",
      color: "#092E20",
      icon: <Security />,
      description: "Build robust backends with models and serializers",
    },
    {
      name: "Angular",
      color: "#DD0031",
      icon: <Bolt />,
      description: "Master components, services, and dependency injection",
    },
    {
      name: "Express",
      color: "#000000",
      icon: <Speed />,
      description: "Create efficient APIs with middleware and routing",
    },
  ];

  const features = [
    {
      icon: <Bolt sx={{ fontSize: 40 }} />,
      title: "Instant Validation",
      description:
        "Get real-time feedback with our AST-powered validation engine. No waiting for code execution.",
    },
    {
      icon: <TrendingUp sx={{ fontSize: 40 }} />,
      title: "Progress Tracking",
      description:
        "Watch your skills grow with detailed analytics and milestone achievements.",
    },
    {
      icon: <EmojiEvents sx={{ fontSize: 40 }} />,
      title: "Compete & Learn",
      description:
        "Climb leaderboards while mastering industry-standard framework patterns.",
    },
  ];

  return (
    <Layout>
      <style>{`
        @keyframes particleFloat {
          0% { 
            transform: translateY(0) translateX(0);
            opacity: 0;
          }
          10% {
            opacity: 0.6;
          }
          90% {
            opacity: 0.6;
          }
          100% { 
            transform: translateY(-100vh) translateX(var(--float-x, 0));
            opacity: 0;
          }
        }
        
        @keyframes gradientMorph {
          0%, 100% { 
            border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
            transform: translate(0, 0) scale(1);
          }
          25% {
            border-radius: 40% 60% 70% 30% / 40% 70% 30% 60%;
            transform: translate(5%, -5%) scale(1.05);
          }
          50% { 
            border-radius: 70% 30% 50% 50% / 30% 60% 40% 70%;
            transform: translate(-5%, 5%) scale(0.95);
          }
          75% {
            border-radius: 50% 50% 30% 70% / 50% 40% 60% 50%;
            transform: translate(5%, 5%) scale(1.02);
          }
        }
        
        @keyframes fadeInUp {
          from { transform: translateY(30px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        
        @keyframes titleFadeIn {
          from { 
            transform: translateY(20px) scale(0.95); 
            opacity: 0; 
          }
          to { 
            transform: translateY(0) scale(1); 
            opacity: 1; 
          }
        }
        
        @keyframes buttonGlow {
          0%, 100% { 
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
          }
          50% { 
            box-shadow: 0 4px 30px rgba(59, 130, 246, 0.6);
          }
        }
        
        @keyframes scaleInOut {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.2); }
        }
        
        @keyframes wave {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(5deg); }
        }
        
        .animate-particle-float {
          animation: particleFloat linear infinite;
        }
        
        .animate-gradient-morph {
          animation: gradientMorph 20s ease-in-out infinite;
        }
        
        .animate-fade-in-up {
          animation: fadeInUp 0.8s ease-out forwards;
        }
        
        .animate-title {
          animation: titleFadeIn 1s ease-out forwards;
        }
        
        .animate-button-glow {
          animation: buttonGlow 3s ease-in-out infinite;
        }
        
        .animate-scale {
          animation: scaleInOut 3s ease-in-out infinite;
        }
        
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
      `}</style>

      {/* Hero Section */}
      <Box
        sx={{
          background:
            "linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%)",
          color: "white",
          py: { xs: 10, md: 15 },
          textAlign: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Animated Background Elements */}
        <Box
          sx={{ position: "absolute", inset: 0, overflow: "hidden", zIndex: 0 }}
        >
          {/* Floating circles */}
          <Box
            className="animate-float"
            sx={{
              position: "absolute",
              top: "5rem",
              left: "2.5rem",
              width: "16rem",
              height: "16rem",
              background: "#3B82F6",
              borderRadius: "50%",
              opacity: 0.2,
              filter: "blur(60px)",
            }}
          />
          <Box
            className="animate-float-slow"
            sx={{
              position: "absolute",
              top: "10rem",
              right: "5rem",
              width: "24rem",
              height: "24rem",
              background: "#A855F7",
              borderRadius: "50%",
              opacity: 0.15,
              filter: "blur(60px)",
              animationDelay: "2s",
            }}
          />
          <Box
            className="animate-pulse-custom"
            sx={{
              position: "absolute",
              bottom: "5rem",
              left: "25%",
              width: "20rem",
              height: "20rem",
              background: "#06B6D4",
              borderRadius: "50%",
              opacity: 0.1,
              filter: "blur(60px)",
            }}
          />

          {/* Rotating geometric shapes */}
          <Box
            className="animate-rotate"
            sx={{
              position: "absolute",
              top: "25%",
              right: "33%",
              width: "8rem",
              height: "8rem",
              border: "4px solid #60A5FA",
              opacity: 0.2,
            }}
          />
          <Box
            className="animate-rotate"
            sx={{
              position: "absolute",
              bottom: "33%",
              left: "25%",
              width: "6rem",
              height: "6rem",
              border: "4px solid #C084FC",
              opacity: 0.15,
              animationDelay: "5s",
              animationDuration: "15s",
            }}
          />

          {/* Additional floating shapes */}
          <Box
            className="animate-float"
            sx={{
              position: "absolute",
              top: "50%",
              left: "2.5rem",
              width: "4rem",
              height: "4rem",
              border: "2px solid #22D3EE",
              opacity: 0.2,
              animationDelay: "3s",
            }}
          />
          <Box
            className="animate-float-slow"
            sx={{
              position: "absolute",
              bottom: "25%",
              right: "25%",
              width: "5rem",
              height: "5rem",
              border: "2px solid #C084FC",
              opacity: 0.15,
            }}
          />

          {/* Grid pattern */}
          <Box
            sx={{
              position: "absolute",
              inset: 0,
              opacity: 0.05,
              backgroundImage:
                "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
              backgroundSize: "50px 50px",
            }}
          />

          {/* Animated gradient overlay */}
          <Box
            className="animate-gradient"
            sx={{
              position: "absolute",
              inset: 0,
              background:
                "linear-gradient(90deg, rgba(59, 130, 246, 0.1), rgba(168, 85, 247, 0.1), rgba(6, 182, 212, 0.1))",
            }}
          />
        </Box>

        <Container maxWidth="lg" sx={{ position: "relative", zIndex: 1 }}>
          <Box className="animate-fade-in-up">
            <Box sx={{ position: "relative", display: "inline-block" }}>
              <Typography
                variant="h1"
                component="h1"
                gutterBottom
                className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold animate-gradient"
                sx={{
                  background:
                    "linear-gradient(90deg, #60A5FA, #C084FC, #22D3EE)",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  color: "transparent",
                }}
              >
                GAGOFORGE
              </Typography>
              <Box
                className="animate-shimmer"
                sx={{ position: "absolute", inset: 0 }}
              />
            </Box>

            <Typography
              variant="h4"
              className="text-lg sm:text-xl md:text-2xl lg:text-3xl mb-4 opacity-90"
              sx={{
                color: "#E2E8F0",
                animation: "fadeInUp 0.8s ease-out forwards",
                animationDelay: "0.2s",
                opacity: 0,
              }}
            >
              CRACK THE CODE. MASTER FRAMEWORKS.
            </Typography>

            <Typography
              variant="h6"
              className="text-base sm:text-lg md:text-xl mb-12 opacity-80 max-w-2xl mx-auto px-4"
              sx={{
                color: "#CBD5E1",
                animation: "fadeInUp 0.8s ease-out forwards",
                animationDelay: "0.4s",
                opacity: 0,
              }}
            >
              Level up your framework skills through gamified challenges. Go
              from beginner to veteran with our AI-powered validation system.
            </Typography>

            {/* BUTTONS SECTION */}
            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={3}
              justifyContent="center"
              alignItems="center"
              className="mt-12"
              sx={{
                animation: "fadeInUp 0.8s ease-out forwards",
                animationDelay: "0.6s",
                opacity: 0,
              }}
            >
              <Button
                component={Link}
                to="/problems"
                variant="contained"
                size="large"
                className="px-6 sm:px-8 py-3 text-base sm:text-lg font-bold rounded-lg transition-all duration-300 hover:scale-105 w-full sm:w-auto"
                sx={{
                  background: "#3B82F6",
                  boxShadow: "0 4px 20px rgba(59, 130, 246, 0.4)",
                  position: "relative",
                  overflow: "hidden",
                  "&:hover": {
                    background: "#2563EB",
                    boxShadow: "0 6px 28px rgba(59, 130, 246, 0.5)",
                  },
                }}
                startIcon={<PlayArrow />}
              >
                <Box
                  className="animate-shimmer"
                  sx={{ position: "absolute", inset: 0 }}
                />
                <Box component="span" sx={{ position: "relative", zIndex: 1 }}>
                  START CHALLENGES
                </Box>
              </Button>

              <Button
                component={Link}
                to="/register"
                variant="outlined"
                size="large"
                className="px-6 sm:px-8 py-3 text-base sm:text-lg font-bold rounded-lg transition-all duration-300 hover:scale-105 w-full sm:w-auto"
                sx={{
                  borderColor: "rgba(255, 255, 255, 0.5)",
                  color: "white",
                  borderWidth: "2px",
                  backgroundColor: "rgba(255, 255, 255, 0.05)",
                  backdropFilter: "blur(10px)",
                  position: "relative",
                  overflow: "hidden",
                  "&:hover": {
                    borderColor: "rgba(255, 255, 255, 0.8)",
                    backgroundColor: "rgba(255, 255, 255, 0.15)",
                    borderWidth: "2px",
                  },
                }}
              >
                CREATE ACCOUNT
              </Button>
            </Stack>
          </Box>
        </Container>
      </Box>

      {/* Frameworks Section */}
      <Container
        maxWidth="lg"
        className="py-12 md:py-16"
        sx={{ position: "relative" }}
      >
        {/* Subtle background animation */}
        <Box sx={{ position: "absolute", inset: 0, opacity: 0.05, zIndex: 0 }}>
          <Box
            className="animate-pulse-custom"
            sx={{
              position: "absolute",
              top: 0,
              left: "25%",
              width: "16rem",
              height: "16rem",
              background: "#93C5FD",
              borderRadius: "50%",
              filter: "blur(60px)",
            }}
          />
          <Box
            className="animate-pulse-custom"
            sx={{
              position: "absolute",
              bottom: 0,
              right: "25%",
              width: "16rem",
              height: "16rem",
              background: "#C084FC",
              borderRadius: "50%",
              filter: "blur(60px)",
              animationDelay: "2s",
            }}
          />
        </Box>

        <Box
          className="text-center mb-8 md:mb-12 px-4"
          sx={{ position: "relative", zIndex: 1 }}
        >
          <Typography
            variant="h3"
            component="h2"
            className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4"
            sx={{ color: "#0F172A" }}
          >
            MASTER POPULAR FRAMEWORKS
          </Typography>

          <Typography
            variant="h6"
            className="text-base sm:text-lg max-w-2xl mx-auto"
            sx={{ color: "#64748B" }}
          >
            Choose your weapon and start cracking challenges
          </Typography>
        </Box>

        <Grid
          container
          spacing={{ xs: 2, sm: 3, md: 4 }}
          justifyContent="center"
          alignItems="stretch"
          sx={{ position: "relative", zIndex: 1 }}
        >
          {frameworks.map((framework, index) => (
            <Grid
              key={framework.name}
              size={{
                xs: 12,
                sm: 10,
                md: 6,
                lg: 5,
                xl: 3,
              }}
              sx={{
                display: "flex",
              }}
            >
              <Card
                className="w-full rounded-2xl transition-all duration-500 ease-out group overflow-hidden flex flex-col animate-fade-in-up"
                sx={{
                  background: "#FFFFFF",
                  border: "1px solid #E2E8F0",
                  cursor: "pointer",
                  display: "flex",
                  flexDirection: "column",
                  flex: 1,
                  position: "relative",
                  opacity: 0,
                  animation: "fadeInUp 0.8s ease-out forwards",
                  animationDelay: `${index * 0.1}s`,
                  "&:hover": {
                    boxShadow: "0 25px 50px rgba(0, 0, 0, 0.1)",
                    border: "1px solid #CBD5E1",
                    transform: "translateY(-8px) scale(1.02)",
                  },
                }}
              >
                <Box
                  sx={{
                    position: "absolute",
                    inset: 0,
                    background: `linear-gradient(45deg, ${framework.color}10, transparent)`,
                    opacity: 0,
                    transition: "opacity 0.5s",
                    ".MuiCard-root:hover &": {
                      opacity: 1,
                    },
                  }}
                />

                <Box
                  className="animate-shimmer"
                  sx={{
                    position: "absolute",
                    inset: 0,
                    opacity: 0,
                    ".MuiCard-root:hover &": {
                      opacity: 1,
                    },
                  }}
                />

                <CardContent className="text-center p-6 sm:p-8 relative z-10 flex flex-col flex-grow">
                  <Box
                    className="text-4xl sm:text-5xl mb-4 transition-transform duration-500 animate-float"
                    sx={{
                      color: framework.color,
                      ".MuiCard-root:hover &": {
                        transform: "scale(1.1) rotate(12deg)",
                      },
                    }}
                  >
                    {framework.icon}
                  </Box>

                  <Typography
                    variant="h5"
                    component="h3"
                    className="font-bold mb-3 transition-colors duration-300"
                    sx={{ color: "#0F172A" }}
                  >
                    {framework.name}
                  </Typography>

                  <Typography
                    variant="body2"
                    className="text-gray-600 mb-6 min-h-12 transition-colors duration-300 leading-relaxed flex-grow"
                    sx={{ color: "#64748B" }}
                  >
                    {framework.description}
                  </Typography>

                  <Box className="mt-auto">
                    <Chip
                      label={'Challenges'}
                      variant="outlined"
                      className="transition-all duration-300"
                      sx={{
                        borderColor: framework.color,
                        color: framework.color,
                        fontWeight: "bold",
                        backgroundColor: `${framework.color}08`,
                        "&:hover": {
                          backgroundColor: `${framework.color}15`,
                          boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                        },
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Features Section */}
      <Box
        sx={{
          background: "#F8FAFC",
          py: { xs: 8, md: 12 },
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Animated background elements */}
        <Box
          sx={{
            position: "absolute",
            inset: 0,
            overflow: "hidden",
            opacity: 0.3,
            zIndex: 0,
          }}
        >
          <Box
            className="animate-pulse-custom"
            sx={{
              position: "absolute",
              top: "2.5rem",
              left: "2.5rem",
              width: "10rem",
              height: "10rem",
              background: "#93C5FD",
              borderRadius: "50%",
              filter: "blur(40px)",
            }}
          />
          <Box
            className="animate-pulse-custom"
            sx={{
              position: "absolute",
              bottom: "2.5rem",
              right: "2.5rem",
              width: "15rem",
              height: "15rem",
              background: "#C084FC",
              borderRadius: "50%",
              filter: "blur(40px)",
              animationDelay: "2s",
            }}
          />
          <Box
            className="animate-float-slow"
            sx={{
              position: "absolute",
              top: "50%",
              left: "50%",
              width: "20rem",
              height: "20rem",
              background: "#22D3EE",
              borderRadius: "50%",
              filter: "blur(60px)",
              transform: "translate(-50%, -50%)",
            }}
          />
        </Box>

        <Container maxWidth="lg" sx={{ position: "relative", zIndex: 1 }}>
          <Box className="text-center mb-8 md:mb-12 px-4">
            <Typography
              variant="h3"
              component="h2"
              className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4"
              sx={{ color: "#0F172A" }}
            >
              WHY CHOOSE GAGOFORGE?
            </Typography>
          </Box>

          <Grid container spacing={6} justifyContent="center">
            {features.map((feature, index) => (
              <Grid
                key={feature.title}
                size={{
                  xs: 12,
                  md: 8,
                  lg: 4,
                }}
              >
                <Box
                  className="text-center p-4 sm:p-6 animate-fade-in-up"
                  sx={{
                    background: "rgba(255, 255, 255, 0.5)",
                    backdropFilter: "blur(10px)",
                    borderRadius: "1rem",
                    transition: "all 0.3s",
                    opacity: 0,
                    animation: "fadeInUp 0.8s ease-out forwards",
                    animationDelay: `${index * 0.2}s`,
                    "&:hover": {
                      background: "rgba(255, 255, 255, 1)",
                      boxShadow: "0 10px 40px rgba(0,0,0,0.1)",
                      transform: "translateY(-5px)",
                    },
                  }}
                >
                  <Box
                    className="mb-4 sm:mb-6 animate-scale"
                    sx={{ color: "#3B82F6" }}
                  >
                    {feature.icon}
                  </Box>

                  <Typography
                    variant="h5"
                    component="h3"
                    className="font-bold mb-3 sm:mb-4 text-lg sm:text-xl"
                    sx={{ color: "#0F172A" }}
                  >
                    {feature.title}
                  </Typography>

                  <Typography
                    variant="body1"
                    className="text-sm sm:text-base"
                    sx={{ color: "#64748B" }}
                  >
                    {feature.description}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box
        className="animate-gradient"
        sx={{
          background: "linear-gradient(90deg, #2563EB, #3B82F6, #A855F7)",
          color: "white",
          py: { xs: 12, md: 16 },
          textAlign: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Animated elements */}
        <Box
          sx={{ position: "absolute", inset: 0, overflow: "hidden", zIndex: 0 }}
        >
          {/* Floating particles */}
          <Box
            sx={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              opacity: 0.2,
            }}
          >
            {[...Array(30)].map((_, i) => (
              <Box
                key={i}
                className="animate-float"
                sx={{
                  position: "absolute",
                  background: "white",
                  borderRadius: "50%",
                  width: `${Math.random() * 4 + 2}px`,
                  height: `${Math.random() * 4 + 2}px`,
                  top: `${Math.random() * 100}%`,
                  left: `${Math.random() * 100}%`,
                  animationDuration: `${Math.random() * 5 + 5}s`,
                  animationDelay: `${Math.random() * 5}s`,
                }}
              />
            ))}
          </Box>

          {/* Wave effect */}
          <Box sx={{ position: "absolute", inset: 0, opacity: 0.1 }}>
            <Box
              sx={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                background:
                  "linear-gradient(90deg, transparent, rgba(255,255,255,1), transparent)",
                animation: "wave 3s ease-in-out infinite",
              }}
            />
          </Box>
        </Box>

        <Container maxWidth="md" sx={{ position: "relative", zIndex: 1 }}>
          <Box className="px-4">
            <Typography
              variant="h3"
              component="h2"
              className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4"
            >
              READY TO LEVEL UP?
            </Typography>

            <Typography
              variant="h6"
              className="mb-6 sm:mb-8 opacity-90 text-base sm:text-lg"
              sx={{ color: "#E2E8F0" }}
            >
              Join thousands of developers mastering frameworks through gamified
              challenges
            </Typography>

            <Button
              component={Link}
              to="/register"
              variant="contained"
              size="large"
              className="px-8 sm:px-12 py-3 text-lg sm:text-xl font-bold rounded-lg transition-all duration-300 hover:scale-105 w-full sm:w-auto"
              sx={{
                background: "rgba(255, 255, 255, 0.95)",
                color: "#3B82F6",
                boxShadow: "0 4px 20px rgba(0, 0, 0, 0.2)",
                position: "relative",
                overflow: "hidden",
                "&:hover": {
                  background: "rgba(255, 255, 255, 1)",
                  boxShadow: "0 6px 28px rgba(0, 0, 0, 0.25)",
                },
              }}
            >
              <Box
                className="animate-shimmer"
                sx={{
                  position: "absolute",
                  inset: 0,
                  background:
                    "linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.2), transparent)",
                  backgroundSize: "1000px 100%",
                }}
              />
              <Box component="span" sx={{ position: "relative", zIndex: 1 }}>
                GET STARTED FREE
              </Box>
            </Button>
          </Box>
        </Container>
      </Box>
    </Layout>
  );
}

export default Home;
