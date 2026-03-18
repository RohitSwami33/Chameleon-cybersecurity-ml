import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Activity, Clock, Zap } from 'lucide-react';

/**
 * TCPSOTarpitMonitor Component
 * 
 * Visualizes the Threat-Calibrated Particle Swarm Optimization algorithm
 * in real-time, showing tarpit delay convergence and particle swarm behavior.
 * 
 * @param {string} className - Additional CSS classes
 * @param {string} statsEndpoint - API endpoint for TC-PSO statistics
 */
const TCPSOTarpitMonitor = ({ className = '', statsEndpoint = '/api/meta-heuristics/stats' }) => {
  const [data, setData] = useState([]);
  const [stats, setStats] = useState({
    globalBestDelay: 0,
    currentInertia: 0,
    avgDwellTime: 0,
    activeSessions: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  // Fetch TC-PSO statistics
  const fetchStats = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch(statsEndpoint);
      // const data = await response.json();
      
      // Mock data for demonstration
      const mockStats = {
        pso: {
          SQLI: {
            global_best_delay: 4.5,
            dynamic_inertia: 0.42,
            iterations: 47
          }
        }
      };
      
      setStats({
        globalBestDelay: mockStats.pso.SQLI?.global_best_delay || 0,
        currentInertia: mockStats.pso.SQLI?.dynamic_inertia || 0,
        avgDwellTime: (mockStats.pso.SQLI?.global_best_delay || 0) * 2.5,
        activeSessions: Math.floor(Math.random() * 10) + 5
      });

      // Generate mock time series data
      const now = new Date();
      const newData = Array.from({ length: 20 }, (_, i) => ({
        time: new Date(now.getTime() - (19 - i) * 10000).toLocaleTimeString(),
        delay: 3.0 + Math.random() * 2.5,
        inertia: 0.35 + Math.random() * 0.4,
        anomaly: 0.5 + Math.random() * 0.5
      }));
      
      setData(newData);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching PSO stats:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 3000); // Poll every 3 seconds
    return () => clearInterval(interval);
  }, [statsEndpoint]);

  const StatCard = ({ icon: Icon, label, value, subtext, color }) => (
    <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${color}`} />
        <span className="text-xs text-slate-400">{label}</span>
      </div>
      <div className="text-2xl font-bold text-slate-100 font-mono">{value}</div>
      {subtext && <div className="text-xs text-slate-500 mt-1">{subtext}</div>}
    </div>
  );

  return (
    <div className={`space-y-4 ${className}`}>
      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Activity}
          label="Global Best Delay"
          value={`${stats.globalBestDelay.toFixed(2)}s`}
          subtext="Optimal tarpit duration"
          color="text-cyan-400"
        />
        <StatCard
          icon={Zap}
          label="Current Inertia"
          value={stats.currentInertia.toFixed(3)}
          subtext="Dynamic weight scaling"
          color="text-purple-400"
        />
        <StatCard
          icon={Clock}
          label="Avg Dwell Time"
          value={`${stats.avgDwellTime.toFixed(1)}s`}
          subtext="Time wasted per attacker"
          color="text-green-400"
        />
        <StatCard
          icon={Activity}
          label="Active Sessions"
          value={stats.activeSessions}
          subtext="Current tarpit victims"
          color="text-orange-400"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Delay Convergence Chart */}
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-slate-200 mb-4">Delay Convergence</h4>
          <div className="h-48">
            {isLoading ? (
              <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                Loading...
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="delayGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis 
                    dataKey="time" 
                    stroke="#475569" 
                    fontSize={10}
                    tick={{ fontFamily: 'monospace' }}
                  />
                  <YAxis 
                    stroke="#475569" 
                    fontSize={10}
                    tick={{ fontFamily: 'monospace' }}
                    domain={[0, 8]}
                  />
                  <Tooltip
                    contentStyle={{ 
                      backgroundColor: '#0f172a', 
                      border: '1px solid #1e293b',
                      fontFamily: 'monospace',
                      fontSize: '11px'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="delay" 
                    stroke="#06b6d4" 
                    strokeWidth={2}
                    fill="url(#delayGradient)"
                    name="Delay (s)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Inertia Weight Chart */}
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-slate-200 mb-4">Dynamic Inertia Weight</h4>
          <div className="h-48">
            {isLoading ? (
              <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                Loading...
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis 
                    dataKey="time" 
                    stroke="#475569" 
                    fontSize={10}
                    tick={{ fontFamily: 'monospace' }}
                  />
                  <YAxis 
                    stroke="#475569" 
                    fontSize={10}
                    tick={{ fontFamily: 'monospace' }}
                    domain={[0.2, 0.8]}
                  />
                  <Tooltip
                    contentStyle={{ 
                      backgroundColor: '#0f172a', 
                      border: '1px solid #1e293b',
                      fontFamily: 'monospace',
                      fontSize: '11px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="inertia" 
                    stroke="#a855f7" 
                    strokeWidth={2}
                    dot={false}
                    name="Inertia"
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Algorithm Info */}
      <div className="bg-slate-900/30 border border-slate-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Activity className="w-5 h-5 text-cyan-400 mt-0.5" />
          <div>
            <h5 className="text-sm font-semibold text-slate-200 mb-1">
              TC-PSO: Threat-Calibrated Particle Swarm Optimization
            </h5>
            <p className="text-xs text-slate-400 font-mono">
              w(t) = w_base · max(σ_min, 1 - α · A(t))
            </p>
            <p className="text-xs text-slate-500 mt-2">
              Dynamic inertia scaling based on BiLSTM anomaly scores. Higher threats trigger faster convergence to optimal delays.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TCPSOTarpitMonitor;
