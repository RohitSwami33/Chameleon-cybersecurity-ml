import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { AnimatePresence } from 'framer-motion';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';
import PageTransition from './components/PageTransition';

// Components
import TrapInterface from './components/TrapInterface';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
import BlockchainExplorer from './components/BlockchainExplorer';
import { CommandBarProvider } from './components/ui/CommandBar';
import DepthLayers from './components/DepthLayers';
import GlobalBackground from './components/GlobalBackground';

// Pages
import DashboardOverview from './pages/DashboardOverview';
import AttackGlobePage from './pages/AttackGlobePage';
import AnalyticsPage from './pages/AnalyticsPage';
import ThreatIntelPage from './pages/ThreatIntelPage';
import ChatbotPage from './pages/ChatbotPage';

/**
 * Chameleon Forensics — MUI Dark Theme
 * All colors from design system tokens in Section 2
 */
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00d4ff',
      light: '#33ddff',
      dark: '#009abb',
    },
    secondary: {
      main: '#ff3d71',
      light: '#ff6b94',
      dark: '#cc2e59',
    },
    error: {
      main: '#ff3d71',
    },
    success: {
      main: '#00e676',
      light: '#33eb91',
      dark: '#00b35e',
    },
    warning: {
      main: '#ffab00',
      light: '#ffbc33',
      dark: '#cc8900',
    },
    info: {
      main: '#7c4dff',
      light: '#9670ff',
      dark: '#6339cc',
    },
    background: {
      default: '#050810',
      paper: '#0a0f1e',
    },
    text: {
      primary: '#e8f4fd',
      secondary: '#7a9bbf',
      disabled: '#3d5a7a',
    },
    divider: 'rgba(0, 212, 255, 0.08)',
  },
  typography: {
    fontFamily: '"DM Sans", "Space Mono", sans-serif',
    h1: {
      fontFamily: '"Orbitron", "Rajdhani", sans-serif',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontFamily: '"Orbitron", "Rajdhani", sans-serif',
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontFamily: '"Rajdhani", "Orbitron", sans-serif',
      fontWeight: 700,
      fontSize: 'clamp(2rem, 4vw, 3.5rem)',
      letterSpacing: '-0.02em',
    },
    h4: {
      fontFamily: '"Rajdhani", sans-serif',
      fontWeight: 700,
    },
    h5: {
      fontFamily: '"Rajdhani", sans-serif',
      fontWeight: 600,
    },
    h6: {
      fontFamily: '"DM Sans", sans-serif',
      fontWeight: 600,
    },
    body1: {
      fontFamily: '"DM Sans", sans-serif',
    },
    body2: {
      fontFamily: '"DM Sans", sans-serif',
    },
    caption: {
      fontFamily: '"DM Sans", sans-serif',
    },
    button: {
      fontFamily: '"DM Sans", sans-serif',
      fontWeight: 600,
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#050810',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
          fontFamily: '"DM Sans", sans-serif',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          backgroundImage: 'none',
          backgroundColor: 'rgba(10, 15, 30, 0.85)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(0, 212, 255, 0.08)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#0a0f1e',
          border: '1px solid rgba(0, 212, 255, 0.08)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontFamily: '"DM Sans", sans-serif',
          fontWeight: 600,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(0, 212, 255, 0.06)',
        },
        head: {
          fontWeight: 700,
          fontFamily: '"DM Sans", sans-serif',
          color: '#7a9bbf',
          backgroundColor: '#0a0f1e',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: 'rgba(0, 212, 255, 0.15)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(0, 212, 255, 0.3)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#00d4ff',
            },
          },
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        switchBase: {
          '&.Mui-checked': {
            color: '#00d4ff',
          },
          '&.Mui-checked + .MuiSwitch-track': {
            backgroundColor: '#00d4ff',
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: '#0a0f1e',
          border: '1px solid rgba(0, 212, 255, 0.15)',
          backgroundImage: 'none',
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: '#0f1628',
          border: '1px solid rgba(0, 212, 255, 0.15)',
          fontSize: '0.75rem',
          fontFamily: '"IBM Plex Mono", monospace',
        },
      },
    },
  },
});

function AnimatedRoutes() {
  const location = useLocation();
  const isTrapPage = location.pathname === '/' || location.pathname === '/trap';

  useEffect(() => {
    if (isTrapPage) {
      document.documentElement.style.setProperty('--app-bg', '#f0f2f5');
      document.body.style.backgroundColor = '#f0f2f5';
    } else {
      document.documentElement.style.removeProperty('--app-bg');
      document.body.style.backgroundColor = '#050810';
    }

    return () => {
      document.documentElement.style.removeProperty('--app-bg');
      document.body.style.backgroundColor = '#050810';
    };
  }, [isTrapPage]);

  return (
    <>
      {!isTrapPage && (
        <>
          <DepthLayers />
          <GlobalBackground />
        </>
      )}
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<TrapInterface />} />
          <Route path="/trap" element={<TrapInterface />} />
          <Route path="/login" element={<Login />} />

          {/* Dashboard Routes with Page Transitions */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <PageTransition>
                  <DashboardOverview />
                </PageTransition>
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/globe"
            element={
              <ProtectedRoute>
                <PageTransition>
                  <AttackGlobePage />
                </PageTransition>
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/analytics"
            element={
              <ProtectedRoute>
                <PageTransition>
                  <AnalyticsPage />
                </PageTransition>
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/threat-intel"
            element={
              <ProtectedRoute>
                <PageTransition>
                  <ThreatIntelPage />
                </PageTransition>
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/chatbot"
            element={
              <ProtectedRoute>
                <PageTransition>
                  <ChatbotPage />
                </PageTransition>
              </ProtectedRoute>
            }
          />
          <Route
            path="/blockchain"
            element={
              <ProtectedRoute>
                <PageTransition>
                  <BlockchainExplorer />
                </PageTransition>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AnimatePresence>
    </>
  );
}

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <CommandBarProvider>
        <Router>
          <div className="app-container">
            <AnimatedRoutes />
          </div>
          <ToastContainer
            position="bottom-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="dark"
          />
        </Router>
      </CommandBarProvider>
    </ThemeProvider>
  );
}

export default App;
