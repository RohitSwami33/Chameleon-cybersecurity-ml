// In production (Render), use same origin. In development, use localhost
const isDevelopment = import.meta.env.DEV;
export const API_URL = isDevelopment ? 'http://localhost:8000' : '';
