import React, { useState, useEffect } from 'react';
import { Cpu, MemoryStick, Thermometer, Activity, Server, Zap } from 'lucide-react';

/**
 * SystemEdgeNodeStatus Component
 *
 * Displays LIVE status of the local Apple MLX framework,
 * VRAM usage, and active tarpit sessions — fetched from /api/system/status.
 */
const SystemEdgeNodeStatus = ({ className = '' }) => {
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/system/status');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setStatus(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch system status:', err);
      setError('Could not reach backend');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (s) => {
    switch (s) {
      case 'HOT':     return 'text-red-400 bg-red-900/20 border-red-700';
      case 'WARM':    return 'text-orange-400 bg-orange-900/20 border-orange-700';
      case 'NORMAL':  return 'text-green-400 bg-green-900/20 border-green-700';
      case 'OFFLINE': return 'text-slate-400 bg-slate-900/20 border-slate-700';
      default:        return 'text-slate-400 bg-slate-900/20 border-slate-700';
    }
  };

  const getPressureColor = (p) => {
    switch (p) {
      case 'high':   return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low':    return 'text-green-400';
      default:       return 'text-slate-400';
    }
  };

  const StatCard = ({ icon: Icon, label, value, subtext, badge }) => (
    <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4 hover:border-slate-700 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-5 h-5 text-cyan-400" />
        {badge && (
          <span className={`text-xs px-2 py-0.5 rounded border font-mono ${getStatusColor(badge)}`}>
            {badge}
          </span>
        )}
      </div>
      <div className="text-2xl font-bold text-slate-100 font-mono">{value}</div>
      <div className="text-xs text-slate-400 mt-1">{label}</div>
      {subtext && (
        <div className={`text-xs mt-1 ${getPressureColor(subtext)}`}>{subtext}</div>
      )}
    </div>
  );

  const ProgressBar = ({ value, max, label, color = 'bg-cyan-500' }) => (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-300 font-mono">{value.toFixed(1)} / {max.toFixed(0)} GB</span>
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-500`}
          style={{ width: `${Math.min((value / max) * 100, 100)}%` }}
        />
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="text-slate-500 text-sm animate-pulse">Loading system status…</div>
      </div>
    );
  }

  if (error || !status) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="text-red-400 text-sm">{error || 'No data'}</div>
      </div>
    );
  }

  const modelWeightsGb = (status.vram_used_gb * 0.45).toFixed(1); // rough estimate: model ≈45% of used
  const availableGb    = (status.vram_total_gb - status.vram_used_gb).toFixed(1);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* ── Status Cards ──────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Cpu}
          label="Qwen 3.5 0.8B Status"
          value={status.qwen_status}
          badge={status.qwen_status}
        />
        <StatCard
          icon={MemoryStick}
          label="VRAM Usage"
          value={`${status.vram_used_gb.toFixed(1)} GB`}
          subtext={status.memory_pressure}
        />
        <StatCard
          icon={Zap}
          label="Inference Latency"
          value={`${status.inference_latency_ms.toFixed(1)} ms`}
          subtext="Apple MLX"
        />
        <StatCard
          icon={Activity}
          label="Active Tarpits"
          value={status.active_tarpits}
          subtext="TC-PSO sessions"
        />
      </div>

      {/* ── Resource Gauges ───────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* VRAM */}
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <MemoryStick className="w-5 h-5 text-cyan-400" />
            <h4 className="text-sm font-semibold text-slate-200">VRAM Allocation</h4>
          </div>
          <ProgressBar
            value={status.vram_used_gb}
            max={status.vram_total_gb}
            label="Unified Memory"
            color="bg-cyan-500"
          />
          <div className="mt-4 grid grid-cols-2 gap-4 text-xs">
            <div>
              <div className="text-slate-500 mb-1">Model Weights</div>
              <div className="text-slate-300 font-mono">~{modelWeightsGb} GB</div>
            </div>
            <div>
              <div className="text-slate-500 mb-1">Available</div>
              <div className="text-slate-300 font-mono">{availableGb} GB</div>
            </div>
          </div>
        </div>

        {/* MLX Framework */}
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <Server className="w-5 h-5 text-purple-400" />
            <h4 className="text-sm font-semibold text-slate-200">MLX Framework</h4>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Status</span>
              <span className={`text-xs font-mono flex items-center gap-1 ${status.model_loaded ? 'text-green-400' : 'text-red-400'}`}>
                <div className={`w-2 h-2 rounded-full ${status.model_loaded ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                {status.model_loaded ? 'Active' : 'Offline'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Backend</span>
              <span className="text-xs text-slate-300 font-mono">{status.mlx_backend}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Precision</span>
              <span className="text-xs text-slate-300 font-mono">{status.precision}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Blocked IPs</span>
              <span className="text-xs text-slate-300 font-mono">{status.blocked_ips}</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── System Info ───────────────────────────────────────────── */}
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
                <div className="text-slate-300 font-mono">{status.platform || 'arm64'}</div>
              </div>
              <div>
                <div className="text-slate-500 mb-1">Unified Memory</div>
                <div className="text-slate-300 font-mono">{status.vram_total_gb.toFixed(0)} GB</div>
              </div>
              <div>
                <div className="text-slate-500 mb-1">MLX Version</div>
                <div className="text-slate-300 font-mono">{status.mlx_version}</div>
              </div>
              <div>
                <div className="text-slate-500 mb-1">Uptime</div>
                <div className="text-slate-300 font-mono">{status.uptime}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemEdgeNodeStatus;
