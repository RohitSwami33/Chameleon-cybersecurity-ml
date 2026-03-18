import React, { useState, useEffect } from 'react';
import { Terminal, Shield, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

/**
 * LiveThreatFeed Component
 * 
 * Displays real-time threat detection results from the BiLSTM + Qwen LLM pipeline.
 * Shows incoming payloads with anomaly scores and verdicts in a terminal-style interface.
 * 
 * @param {string} className - Additional CSS classes
 * @param {string} apiEndpoint - Backend API endpoint for threat data
 */
const LiveThreatFeed = ({ className = '', apiEndpoint = '/api/dashboard/logs?limit=50' }) => {
  const [threats, setThreats] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Mock data for development - replace with actual API call
  const fetchThreats = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch(apiEndpoint);
      // const data = await response.json();
      
      // Mock data for demonstration
      const mockThreats = [
        {
          id: 1,
          timestamp: new Date().toISOString(),
          ip: '192.168.1.105',
          payload: "' OR '1'='1",
          anomalyScore: 0.94,
          verdict: 'BLOCK',
          attackType: 'SQLi'
        },
        {
          id: 2,
          timestamp: new Date().toISOString(),
          ip: '10.0.0.42',
          payload: 'LOGIN:admin_user',
          anomalyScore: 0.12,
          verdict: 'ALLOW',
          attackType: 'BENIGN'
        },
        {
          id: 3,
          timestamp: new Date().toISOString(),
          ip: '172.16.0.88',
          payload: '<script>alert(1)</script>',
          anomalyScore: 0.89,
          verdict: 'BLOCK',
          attackType: 'XSS'
        },
        {
          id: 4,
          timestamp: new Date().toISOString(),
          ip: '192.168.1.200',
          payload: '../../../etc/passwd',
          anomalyScore: 0.87,
          verdict: 'BLOCK',
          attackType: 'Path Traversal'
        },
        {
          id: 5,
          timestamp: new Date().toISOString(),
          ip: '10.0.0.15',
          payload: 'git status',
          anomalyScore: 0.05,
          verdict: 'ALLOW',
          attackType: 'BENIGN'
        }
      ];
      
      setThreats(mockThreats);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching threats:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchThreats();
    const interval = setInterval(fetchThreats, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [apiEndpoint]);

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-red-500';
    if (score >= 0.5) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getVerdictIcon = (verdict) => {
    return verdict === 'BLOCK' ? (
      <XCircle className="w-4 h-4 text-red-500" />
    ) : (
      <CheckCircle className="w-4 h-4 text-green-500" />
    );
  };

  const getAttackTypeBadge = (type) => {
    const colors = {
      SQLi: 'bg-red-900/30 text-red-400 border-red-700',
      XSS: 'bg-orange-900/30 text-orange-400 border-orange-700',
      'Path Traversal': 'bg-purple-900/30 text-purple-400 border-purple-700',
      BENIGN: 'bg-green-900/30 text-green-400 border-green-700'
    };
    return colors[type] || 'bg-gray-900/30 text-gray-400 border-gray-700';
  };

  return (
    <div className={`bg-slate-950 border border-slate-800 rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-semibold text-slate-200">Live Threat Feed</h3>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs text-slate-400">Live</span>
        </div>
      </div>

      {/* Table Header */}
      <div className="grid grid-cols-12 gap-4 px-4 py-2 bg-slate-900/30 text-xs font-medium text-slate-400 border-b border-slate-800">
        <div className="col-span-2">Timestamp</div>
        <div className="col-span-2">IP Address</div>
        <div className="col-span-4">Payload</div>
        <div className="col-span-1">Score</div>
        <div className="col-span-2">Verdict</div>
        <div className="col-span-1">Type</div>
      </div>

      {/* Table Body */}
      <div className="max-h-96 overflow-y-auto">
        {isLoading ? (
          <div className="px-4 py-8 text-center text-slate-500 text-sm">
            Loading threat data...
          </div>
        ) : (
          threats.map((threat) => (
            <div
              key={threat.id}
              className="grid grid-cols-12 gap-4 px-4 py-3 border-b border-slate-800/50 hover:bg-slate-900/30 transition-colors font-mono text-xs"
            >
              <div className="col-span-2 text-slate-400">
                {new Date(threat.timestamp).toLocaleTimeString()}
              </div>
              <div className="col-span-2 text-cyan-400">{threat.ip}</div>
              <div className="col-span-4 text-slate-300 truncate" title={threat.payload}>
                {threat.payload}
              </div>
              <div className={`col-span-1 font-semibold ${getScoreColor(threat.anomalyScore)}`}>
                {threat.anomalyScore.toFixed(2)}
              </div>
              <div className="col-span-2 flex items-center gap-2">
                {getVerdictIcon(threat.verdict)}
                <span className={threat.verdict === 'BLOCK' ? 'text-red-400' : 'text-green-400'}>
                  {threat.verdict}
                </span>
              </div>
              <div className="col-span-1">
                <span className={`px-2 py-0.5 rounded text-xs border ${getAttackTypeBadge(threat.attackType)}`}>
                  {threat.attackType}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="bg-slate-900/30 px-4 py-2 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
        <span>Showing last {threats.length} threats</span>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <Shield className="w-3 h-3" />
            BiLSTM + Qwen LLM
          </span>
          <span>Auto-refresh: 5s</span>
        </div>
      </div>
    </div>
  );
};

export default LiveThreatFeed;
