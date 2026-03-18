import React, { useState, useEffect } from 'react';
import { Cpu, MemoryStick, Thermometer, Activity, Server, Zap } from 'lucide-react';

/**
 * SystemEdgeNodeStatus Component
 * 
 * Displays real-time status of the local Apple MLX framework,
 * VRAM usage, and active tarpit sessions.
 * 
 * @param {string} className - Additional CSS classes
 * @param {string} healthEndpoint - API endpoint for system health
 */
const SystemEdgeNodeStatus = ({ className = '', healthEndpoint = '/api/health' }) => {
  const [status, setStatus] = useState({
    qwensStatus: 'HOT',
    vramUsage: 0,
    vramTotal: 16,
    activeTarpits: 0,
    mlxFramework: 'active',
    inferenceLatency: 0,
    memoryPressure: 'low'
  });
  const [isLoading, setIsLoading] = useState(true);

  const fetchHealth = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch(healthEndpoint);
      // const data = await response.json();
      
      // Mock data for demonstration
      const mockStatus = {
        qwensStatus: 'HOT',
        vramUsage: 9.2,
        vramTotal: 16,
        activeTarpits: 7,
        mlxFramework: 'active',
        inferenceLatency: 1.8,
        memoryPressure: 'medium'
      };
      
      setStatus(mockStatus);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching health:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [healthEndpoint]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'HOT': return 'text-red-400 bg-red-900/20 border-red-700';
      case 'WARM': return 'text-orange-400 bg-orange-900/20 border-orange-700';
      case 'NORMAL': return 'text-green-400 bg-green-900/20 border-green-700';
      default: return 'text-slate-400 bg-slate-900/20 border-slate-700';
    }
  };

  const getMemoryPressureColor = (pressure) => {
    switch (pressure) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-slate-400';
    }
  };

  const StatCard = ({ icon: Icon, label, value, subtext, status }) => (
    <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4 hover:border-slate-700 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-5 h-5 text-cyan-400" />
        {status && (
          <span className={`text-xs px-2 py-0.5 rounded border font-mono ${getStatusColor(status)}`}>
            {status}
          </span>
        )}
      </div>
      <div className="text-2xl font-bold text-slate-100 font-mono">{value}</div>
      <div className="text-xs text-slate-400 mt-1">{label}</div>
      {subtext && <div className={`text-xs mt-1 ${getMemoryPressureColor(subtext)}`}>{subtext}</div>}
    </div>
  );

  const ProgressBar = ({ value, max, label, color = 'bg-cyan-500' }) => (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-300 font-mono">{value.toFixed(1)} / {max} GB</span>
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-500`}
          style={{ width: `${(value / max) * 100}%` }}
        />
      </div>
    </div>
  );

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Status Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Cpu}
          label="Qwen 2B Status"
          value={status.qwensStatus}
          status={status.qwensStatus}
        />
        <StatCard
          icon={MemoryStick}
          label="VRAM Usage"
          value={`${status.vramUsage.toFixed(1)} GB`}
          subtext={status.memoryPressure}
        />
        <StatCard
          icon={Zap}
          label="Inference Latency"
          value={`${status.inferenceLatency.toFixed(1)} ms`}
          subtext="Apple MLX"
        />
        <StatCard
          icon={Activity}
          label="Active Tarpits"
          value={status.activeTarpits}
          subtext="TC-PSO sessions"
        />
      </div>

      {/* Resource Gauges */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* VRAM Usage */}
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <MemoryStick className="w-5 h-5 text-cyan-400" />
            <h4 className="text-sm font-semibold text-slate-200">VRAM Allocation</h4>
          </div>
          <ProgressBar
            value={status.vramUsage}
            max={status.vramTotal}
            label="Unified Memory"
            color="bg-cyan-500"
          />
          <div className="mt-4 grid grid-cols-2 gap-4 text-xs">
            <div>
              <div className="text-slate-500 mb-1">Model Weights</div>
              <div className="text-slate-300 font-mono">~4.2 GB</div>
            </div>
            <div>
              <div className="text-slate-500 mb-1">Available</div>
              <div className="text-slate-300 font-mono">{(status.vramTotal - status.vramUsage).toFixed(1)} GB</div>
            </div>
          </div>
        </div>

        {/* MLX Framework Status */}
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <Server className="w-5 h-5 text-purple-400" />
            <h4 className="text-sm font-semibold text-slate-200">MLX Framework</h4>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Status</span>
              <span className="text-xs text-green-400 font-mono flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                Active
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Backend</span>
              <span className="text-xs text-slate-300 font-mono">Metal GPU</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Precision</span>
              <span className="text-xs text-slate-300 font-mono">4-bit Quantized</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Throughput</span>
              <span className="text-xs text-slate-300 font-mono">~70 tok/s</span>
            </div>
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="bg-slate-900/30 border border-slate-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Thermometer className="w-5 h-5 text-cyan-400 mt-0.5" />
          <div className="flex-1">
            <h5 className="text-sm font-semibold text-slate-200 mb-2">
              Apple Silicon Edge Node
            </h5>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
              <div>
                <div className="text-slate-500 mb-1">Platform</div>
                <div className="text-slate-300 font-mono">Apple M4</div>
              </div>
              <div>
                <div className="text-slate-500 mb-1">Unified Memory</div>
                <div className="text-slate-300 font-mono">16 GB</div>
              </div>
              <div>
                <div className="text-slate-500 mb-1">MLX Version</div>
                <div className="text-slate-300 font-mono">0.31.0</div>
              </div>
              <div>
                <div className="text-slate-500 mb-1">Uptime</div>
                <div className="text-slate-300 font-mono">2h 34m</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemEdgeNodeStatus;
