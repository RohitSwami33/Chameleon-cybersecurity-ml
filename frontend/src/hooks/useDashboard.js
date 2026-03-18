import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * usePolling Hook
 * 
 * Generic polling hook for fetching data at regular intervals.
 * Handles loading states, errors, and automatic cleanup.
 * 
 * @param {Function} fetchFn - Async function to fetch data
 * @param {number} interval - Polling interval in milliseconds
 * @param {boolean} immediate - Fetch immediately on mount
 * @returns {Object} { data, loading, error, refresh }
 */
export const usePolling = (fetchFn, interval = 5000, immediate = true) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);
  const fetchFnRef = useRef(fetchFn);

  // Keep fetchFn reference up-to-date
  useEffect(() => {
    fetchFnRef.current = fetchFn;
  }, [fetchFn]);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchFnRef.current();
      setData(result);
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }

    intervalRef.current = setInterval(fetchData, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [interval, immediate, fetchData]);

  const refresh = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refresh };
};

/**
 * useWebSocket Hook
 * 
 * WebSocket hook for real-time data updates.
 * Falls back to polling if WebSocket is unavailable.
 * 
 * @param {string} url - WebSocket URL
 * @param {Object} options - Configuration options
 * @returns {Object} { data, loading, error, connected, sendMessage }
 */
export const useWebSocket = (url, options = {}) => {
  const {
    reconnectInterval = 3000,
    shouldReconnect = true
  } = options;

  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    if (!url) return;

    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        setConnected(true);
        setError(null);
        console.log('WebSocket connected');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setData(message);
        } catch (err) {
          setData(event.data);
        }
      };

      wsRef.current.onerror = (err) => {
        console.error('WebSocket error:', err);
        setError('WebSocket connection error');
      };

      wsRef.current.onclose = () => {
        setConnected(false);
        if (shouldReconnect) {
          reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
        }
      };
    } catch (err) {
      setError(err.message);
      if (shouldReconnect) {
        reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
      }
    }
  }, [url, reconnectInterval, shouldReconnect]);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected');
    }
  }, []);

  return { data, loading: !connected && !error, error, connected, sendMessage };
};

/**
 * useDashboardData Hook
 * 
 * Specialized hook for fetching all dashboard data.
 * Combines multiple API calls with polling.
 * 
 * @returns {Object} Dashboard data and states
 */
export const useDashboardData = () => {
  const [dashboardData, setDashboardData] = useState({
    threats: [],
    psoStats: null,
    rrtStats: null,
    systemHealth: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAllData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Import API services
      const dashboardApi = await import('../services/dashboardApi');
      
      const [threats, psoStats, rrtStats, health] = await Promise.all([
        dashboardApi.getThreatFeed().catch(() => []),
        dashboardApi.getTCPSOStats().catch(() => null),
        dashboardApi.getSRTStats().catch(() => null),
        dashboardApi.getSystemHealth().catch(() => null)
      ]);

      setDashboardData({
        threats,
        psoStats,
        rrtStats,
        systemHealth: health
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, [fetchAllData]);

  return {
    ...dashboardData,
    loading,
    error,
    refresh: fetchAllData
  };
};

export default {
  usePolling,
  useWebSocket,
  useDashboardData
};
