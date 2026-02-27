import React from 'react';
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

// Pages
import DashboardOverview from './pages/DashboardOverview';
import AttackGlobePage from './pages/AttackGlobePage';
import AnalyticsPage from './pages/AnalyticsPage';
import ThreatIntelPage from './pages/ThreatIntelPage';
import ChatbotPage from './pages/ChatbotPage';

// Theme Configuration
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#ffa726',
    },
    error: {
      main: '#f44336',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
    h1: {
      fontFamily: 'Montserrat, sans-serif',
      fontWeight: 700,
    },
    h2: {
      fontFamily: 'Montserrat, sans-serif',
      fontWeight: 600,
    },
    h3: {
      fontFamily: 'Montserrat, sans-serif',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          backgroundImage: 'none',
        },
      },
    },
  },
});

function AnimatedRoutes() {
  const location = useLocation();

  return (
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
