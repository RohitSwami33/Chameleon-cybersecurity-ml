import React, { useState, useEffect } from 'react';
import { Activity, Shield, Cpu, Terminal } from 'lucide-react';
import LiveThreatFeed from '../components/dashboard/LiveThreatFeed';
import TCPSOTarpitMonitor from '../components/dashboard/TCPSOTarpitMonitor';
import SRTDeceptionMap from '../components/dashboard/SRTDeceptionMap';
import SystemEdgeNodeStatus from '../components/dashboard/SystemEdgeNodeStatus';

/**
 * Main Dashboard Component
 * 
 * Central telemetry dashboard for the Chameleon honeypot system.
 * Integrates four core monitoring widgets in a responsive grid layout.
 * 
 * Features:
 * - Live threat feed from BiLSTM + Qwen LLM pipeline
 * - TC-PSO tarpit optimization monitoring
 * - S-RRT deception filesystem visualization
 * - System edge node status (Apple MLX)
 * 
 * @param {Object} props
 * @param {string} props.className - Additional CSS classes
 */
const Dashboard = ({ className = '' }) => {
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Auto-refresh dashboard data
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 10000); // Update timestamp every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setLastUpdate(new Date());
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className={`min-h-screen bg-slate-950 text-slate-100 ${className}`}>
      {/* Top Bar */}
      <header className="bg-slate-900/50 border-b border-slate-800 sticky top-0 z-10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-cyan-500 to-purple-600 p-2 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-100">Chameleon</h1>
                <p className="text-xs text-slate-400 font-mono">
                  AI-Driven Adaptive Deception System
                </p>
              </div>
            </div>

            {/* Status Bar */}
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-2 text-xs text-slate-400">
                <Activity className="w-4 h-4" />
                <span>System Online</span>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              </div>
              <div className="text-xs text-slate-500 font-mono">
                Last update: {lastUpdate.toLocaleTimeString()}
              </div>
              <button
                onClick={handleRefresh}
                className="px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded transition-colors"
                disabled={isRefreshing}
              >
                {isRefreshing ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* KPI Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-cyan-900/20 to-slate-900 border border-cyan-800/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span className="text-xs text-slate-400">Threats Detected</span>
            </div>
            <div className="text-2xl font-bold text-cyan-400 font-mono">1,247</div>
            <div className="text-xs text-green-400 mt-1">↑ 12% from last hour</div>
          </div>
          
          <div className="bg-gradient-to-br from-purple-900/20 to-slate-900 border border-purple-800/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-purple-400" />
              <span className="text-xs text-slate-400">Active Tarpits</span>
            </div>
            <div className="text-2xl font-bold text-purple-400 font-mono">7</div>
            <div className="text-xs text-slate-500 mt-1">TC-PSO optimized</div>
          </div>
          
          <div className="bg-gradient-to-br from-orange-900/20 to-slate-900 border border-orange-800/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-4 h-4 text-orange-400" />
              <span className="text-xs text-slate-400">Deception Nodes</span>
            </div>
            <div className="text-2xl font-bold text-orange-400 font-mono">24</div>
            <div className="text-xs text-slate-500 mt-1">S-RRT evolved</div>
          </div>
          
          <div className="bg-gradient-to-br from-green-900/20 to-slate-900 border border-green-800/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Cpu className="w-4 h-4 text-green-400" />
              <span className="text-xs text-slate-400">Classification</span>
            </div>
            <div className="text-2xl font-bold text-green-400 font-mono">100%</div>
            <div className="text-xs text-slate-500 mt-1">BiLSTM + Qwen</div>
          </div>
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Row 1: Live Threat Feed (Full Width) */}
          <div className="lg:col-span-2">
            <LiveThreatFeed className="h-full" />
          </div>

          {/* Row 2: TC-PSO Monitor & System Status */}
          <div className="space-y-6">
            <TCPSOTarpitMonitor />
            <SystemEdgeNodeStatus />
          </div>

          {/* Row 2: S-RRT Deception Map */}
          <div>
            <SRTDeceptionMap className="h-full" />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-8 pt-6 border-t border-slate-800 text-center text-xs text-slate-500">
          <div className="flex items-center justify-center gap-6 mb-2">
            <span className="font-mono">BiLSTM: 99.61% accuracy</span>
            <span className="font-mono">Qwen 3.5 2B: 4-bit quantized</span>
            <span className="font-mono">TC-PSO: +48.1% fitness</span>
            <span className="font-mono">S-RRT: +258.9% fitness</span>
          </div>
          <div className="font-mono">
            Chameleon v2.0.0 • Research Build • Apple MLX Optimized
          </div>
        </footer>
      </main>
    </div>
  );
};

export default Dashboard;
