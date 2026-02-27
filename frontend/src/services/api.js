import axios from 'axios';

// In production (Render), use same origin. In development, use localhost
const isDevelopment = import.meta.env.DEV;
const API_URL = isDevelopment ? 'http://localhost:8000' : '';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Auth Interceptors ────────────────────────────────────────────────

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ========================================================================
// ★ NEW: /trap/execute — BiLSTM + DeepSeek Deception Pipeline
// ========================================================================

/**
 * Send a raw shell command to the honeypot's ML pipeline.
 *
 * POST /trap/execute
 * Payload: { "command": "ls -la", "ip_address": "optional" }
 *
 * Returns: {
 *   response: "fake terminal output",
 *   prediction_score: 0.92,
 *   is_malicious: true,
 *   hash: "a1b2c3..."
 * }
 */
export const executeCommand = async (command) => {
  try {
    const response = await api.post('/trap/execute', { command });
    return response.data;
  } catch (error) {
    // Even error responses from the honeypot contain deceptive output
    if (error.response && error.response.data) {
      return error.response.data;
    }
    throw error;
  }
};

// ========================================================================
// Dashboard & Stats
// ========================================================================

/**
 * Fetch dashboard statistics (threat scores, recent logs, metrics).
 * GET /api/dashboard/stats
 */
export const fetchDashboardStats = async () => {
  try {
    const response = await api.get('/api/dashboard/stats');
    return response.data;
  } catch (error) {
    console.error('Dashboard stats error:', error);
    throw error.response ? error.response.data : error;
  }
};

/**
 * Legacy: Submit input via the progressive deception engine.
 * POST /api/trap/submit
 */
export const submitInput = async (inputData) => {
  try {
    const response = await api.post('/api/trap/submit', inputData);
    return response.data;
  } catch (error) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    throw error;
  }
};

export const getDashboardStats = async () => {
  try {
    const token = localStorage.getItem('authToken');
    console.log('Token exists:', !!token);
    const response = await api.get('/api/dashboard/stats');
    return response.data;
  } catch (error) {
    console.error('Dashboard stats error:', error);
    throw error.response ? error.response.data : error;
  }
};

export const getAttackLogs = async (skip = 0, limit = 50) => {
  try {
    const response = await api.get(`/api/dashboard/logs?skip=${skip}&limit=${limit}`);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : error;
  }
};

export const getLogById = async (logId) => {
  try {
    const response = await api.get(`/api/dashboard/logs/${logId}`);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : error;
  }
};

export const getLogsByIp = async (ipAddress) => {
  try {
    const response = await api.get(`/api/dashboard/logs/ip/${ipAddress}`);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : error;
  }
};

export const generateReport = async (ipAddress) => {
  try {
    const response = await api.post(`/api/reports/generate/${ipAddress}`, {}, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : error;
  }
};

export const verifyBlockchain = async () => {
  try {
    const response = await api.get('/api/blockchain/verify');
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/api/health');
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : error;
  }
};

export const login = async (username, password) => {
  try {
    const response = await api.post('/api/auth/login', { username, password });
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : error;
  }
};

export default api;
