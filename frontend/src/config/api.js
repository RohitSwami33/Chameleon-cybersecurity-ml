// API configuration
const isDevelopment = import.meta.env.DEV;

export const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8000'  // Local development
  : '';  // Production: same origin (backend serves frontend)

export default API_BASE_URL;
