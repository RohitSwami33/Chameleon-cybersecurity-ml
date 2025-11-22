import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Handle 401 errors and redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);


export const submitInput = async (inputData) => {
  try {
    const response = await api.post('/api/trap/submit', inputData);
    return response.data;
  } catch (error) {
    // For trap submissions, even "errors" (500, 403, etc.) are deceptive responses
    // We should return the deception message, not throw an error
    if (error.response && error.response.data) {
      // This is a deceptive response from the honeypot
      return error.response.data;
    }
    throw error;
  }
};

export const getDashboardStats = async () => {
  try {
    const token = localStorage.getItem('authToken');
    console.log('Token exists:', !!token);
    console.log('Making request to /api/dashboard/stats');
    const response = await api.get('/api/dashboard/stats');
    console.log('Dashboard stats received:', response.data);
    return response.data;
  } catch (error) {
    console.error('Dashboard stats error:', error);
    console.error('Error response:', error.response);
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
