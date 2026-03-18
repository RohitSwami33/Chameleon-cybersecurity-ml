import api from './api';

/**
 * Dashboard API Services
 * 
 * Centralized API calls for dashboard data fetching.
 * All endpoints are configurable via environment variables.
 */

const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * Fetch live threat data from BiLSTM + Qwen pipeline
 * @param {number} limit - Number of records to fetch
 * @param {number} skip - Pagination offset
 */
export const getThreatFeed = async (limit = 50, skip = 0) => {
  try {
    const response = await api.get(`${API_BASE}/api/dashboard/logs`, {
      params: { limit, skip }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching threat feed:', error);
    throw error;
  }
};

/**
 * Fetch dashboard statistics
 */
export const getDashboardStats = async () => {
  try {
    const response = await api.get(`${API_BASE}/api/dashboard/stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    throw error;
  }
};

/**
 * Fetch meta-heuristics statistics (TC-PSO & S-RRT)
 */
export const getMetaHeuristicsStats = async () => {
  try {
    const response = await api.get(`${API_BASE}/api/meta-heuristics/stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching meta-heuristics stats:', error);
    throw error;
  }
};

/**
 * Fetch S-RRT deception schema
 */
export const getDeceptionSchema = async () => {
  try {
    const response = await api.get(`${API_BASE}/api/meta-heuristics/rrt/schema`);
    return response.data;
  } catch (error) {
    console.error('Error fetching deception schema:', error);
    throw error;
  }
};

/**
 * Fetch system health status
 */
export const getSystemHealth = async () => {
  try {
    const response = await api.get(`${API_BASE}/api/health`);
    return response.data;
  } catch (error) {
    console.error('Error fetching system health:', error);
    throw error;
  }
};

/**
 * Fetch TC-PSO specific statistics
 */
export const getTCPSOStats = async (category = 'SQLI') => {
  try {
    const stats = await getMetaHeuristicsStats();
    return stats.pso?.[category] || null;
  } catch (error) {
    console.error('Error fetching TC-PSO stats:', error);
    throw error;
  }
};

/**
 * Fetch S-RRT specific statistics
 */
export const getSRTStats = async () => {
  try {
    const stats = await getMetaHeuristicsStats();
    return stats.rrt || null;
  } catch (error) {
    console.error('Error fetching S-RRT stats:', error);
    throw error;
  }
};

export default {
  getThreatFeed,
  getDashboardStats,
  getMetaHeuristicsStats,
  getDeceptionSchema,
  getSystemHealth,
  getTCPSOStats,
  getSRTStats
};
