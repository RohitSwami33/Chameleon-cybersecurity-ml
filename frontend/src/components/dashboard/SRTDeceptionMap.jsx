import React, { useState, useEffect } from 'react';
import { Folder, FolderOpen, File, FileText, Lock, Database, Shield } from 'lucide-react';

/**
 * SRTDeceptionMap Component
 * 
 * Visualizes the Semantic Deception Rapidly-exploring Random Tree filesystem
 * with pheromone-based heat mapping to show attacker interaction patterns.
 * 
 * @param {string} className - Additional CSS classes
 * @param {string} schemaEndpoint - API endpoint for S-RRT schema data
 */
const SRTDeceptionMap = ({ className = '', schemaEndpoint = '/api/meta-heuristics/rrt/schema' }) => {
  const [filesystem, setFilesystem] = useState([]);
  const [expandedNodes, setExpandedNodes] = useState(['/etc', '/var', '/var/www', '/home']);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({ totalFiles: 0, hotFiles: 0, totalInteractions: 0 });

  // Fetch S-RRT schema from backend API
  const fetchSchema = async () => {
    try {
      const response = await fetch(schemaEndpoint);
      if (!response.ok) throw new Error('Failed to fetch schema');

      const data = await response.json();

      // Convert flat schema array to nested tree structure
      const treeData = convertFlatSchemaToTree(data.schema || []);
      setFilesystem(treeData);

      // Update stats
      setStats({
        totalFiles: data.schema?.length || 0,
        hotFiles: (data.schema || []).filter(f => f.pheromone_level >= 0.8).length,
        totalInteractions: (data.schema || []).reduce((sum, f) => sum + (f.interaction_count || 0), 0)
      });

      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching S-RRT schema:', error);
      setIsLoading(false);
    }
  };

  // Convert flat schema array from API to nested tree structure
  const convertFlatSchemaToTree = (flatSchema) => {
    if (!flatSchema || flatSchema.length === 0) return [];

    const root = {};

    flatSchema.forEach(file => {
      const parts = file.path.split('/').filter(p => p);
      let current = root;

      parts.forEach((part, index) => {
        const isLast = index === parts.length - 1;
        const fullPath = '/' + parts.slice(0, index + 1).join('/');

        if (!current[part]) {
          current[part] = {
            path: fullPath,
            name: part,
            type: isLast ? 'file' : 'folder',
            children: {},
            pheromoneLevel: isLast ? file.pheromone_level : 0,
            interactionCount: isLast ? (file.interaction_count || 0) : 0
          };
        }

        current = current[part].children;
      });
    });

    // Convert root object to array of top-level nodes
    return Object.keys(root).map(key => {
      const node = root[key];
      return convertNodeToTree(node);
    });
  };

  // Recursively convert node children
  const convertNodeToTree = (node) => {
    const children = Object.keys(node.children || {}).map(key =>
      convertNodeToTree(node.children[key])
    );

    return {
      path: node.path,
      name: node.name,
      type: node.type,
      children: children.length > 0 ? children : undefined,
      pheromoneLevel: node.pheromoneLevel,
      interactionCount: node.interactionCount
    };
  };

  useEffect(() => {
    fetchSchema();
    const interval = setInterval(fetchSchema, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [schemaEndpoint]);

  const toggleNode = (path) => {
    setExpandedNodes(prev =>
      prev.includes(path)
        ? prev.filter(p => p !== path)
        : [...prev, path]
    );
  };

  const getPheromoneColor = (level) => {
    if (level >= 0.8) return 'text-red-500';
    if (level >= 0.6) return 'text-orange-500';
    if (level >= 0.4) return 'text-yellow-500';
    return 'text-slate-400';
  };

  const getPheromoneHeat = (level) => {
    const opacity = 0.3 + (level * 0.7);
    return `rgba(239, 68, 68, ${opacity})`;
  };

  const getFileIcon = (iconName) => {
    const icons = {
      FileText: FileText,
      Lock: Lock,
      Database: Database,
      File: File
    };
    const Icon = icons[iconName] || File;
    return <Icon className="w-4 h-4" />;
  };

  const renderNode = (node, depth = 0) => {
    const isExpanded = expandedNodes.includes(node.path);
    const hasChildren = node.children && node.children.length > 0;
    const isFolder = node.type === 'folder';

    return (
      <div key={node.path} className="select-none">
        <div
          className={`flex items-center gap-2 py-1.5 px-2 rounded hover:bg-slate-800/50 cursor-pointer transition-colors ${
            node.pheromoneLevel ? 'border-l-2 border-red-500/50' : ''
          }`}
          style={node.pheromoneLevel ? {
            background: `linear-gradient(90deg, ${getPheromoneHeat(node.pheromoneLevel)} 0%, transparent 100%)`
          } : {}}
          onClick={() => isFolder && toggleNode(node.path)}
        >
          {/* Expand/Collapse */}
          {hasChildren ? (
            <span className="text-slate-500 text-xs w-4">
              {isExpanded ? '▼' : '▶'}
            </span>
          ) : (
            <span className="w-4" />
          )}

          {/* Icon */}
          <span className={node.pheromoneLevel ? getPheromoneColor(node.pheromoneLevel) : 'text-slate-400'}>
            {isFolder ? (
              isExpanded ? (
                <FolderOpen className="w-4 h-4" />
              ) : (
                <Folder className="w-4 h-4" />
              )
            ) : (
              getFileIcon(node.icon?.name || 'File')
            )}
          </span>

          {/* Name */}
          <span className={`text-sm font-mono ${
            node.pheromoneLevel ? getPheromoneColor(node.pheromoneLevel) : 'text-slate-300'
          }`}>
            {node.name}
          </span>

          {/* Interaction Count Badge */}
          {node.interactionCount && (
            <span className="ml-auto text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
              {node.interactionCount} hits
            </span>
          )}

          {/* Pheromone Level */}
          {node.pheromoneLevel && (
            <span className={`text-xs font-mono ${getPheromoneColor(node.pheromoneLevel)}`}>
              {(node.pheromoneLevel * 100).toFixed(0)}%
            </span>
          )}
        </div>

        {/* Children */}
        {hasChildren && isExpanded && (
          <div className="ml-4 border-l border-slate-800">
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`bg-slate-950 border border-slate-800 rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-slate-900/50 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-orange-400" />
          <h3 className="text-sm font-semibold text-slate-200">S-RRT Deception Map</h3>
        </div>
        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 bg-red-500 rounded-full" />
            High Heat (≥80%)
          </span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 bg-orange-500 rounded-full" />
            Medium (60-80%)
          </span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 bg-yellow-500 rounded-full" />
            Low (40-60%)
          </span>
        </div>
      </div>

      {/* Filesystem Tree */}
      <div className="p-4 max-h-96 overflow-y-auto font-mono">
        {isLoading ? (
          <div className="text-center text-slate-500 text-sm py-8">
            Loading deception schema...
          </div>
        ) : (
          filesystem.map(node => renderNode(node))
        )}
      </div>

      {/* Footer Stats */}
      <div className="bg-slate-900/30 px-4 py-3 border-t border-slate-800">
        <div className="grid grid-cols-3 gap-4 text-xs">
          <div>
            <div className="text-slate-500 mb-1">Total Files</div>
            <div className="text-lg font-bold text-slate-200 font-mono">{stats.totalFiles}</div>
          </div>
          <div>
            <div className="text-slate-500 mb-1">Hot Files</div>
            <div className="text-lg font-bold text-red-400 font-mono">{stats.hotFiles}</div>
          </div>
          <div>
            <div className="text-slate-500 mb-1">Total Interactions</div>
            <div className="text-lg font-bold text-slate-200 font-mono">{stats.totalInteractions}</div>
          </div>
        </div>
      </div>

      {/* Algorithm Info */}
      <div className="bg-slate-900/30 border-t border-slate-800 px-4 py-3">
        <div className="flex items-start gap-3">
          <Shield className="w-5 h-5 text-orange-400 mt-0.5" />
          <div>
            <h5 className="text-xs font-semibold text-slate-200 mb-1">
              S-RRT: Semantic Deception RRT
            </h5>
            <p className="text-xs text-slate-400 font-mono">
              Δτ' = Δτ · exp(Ψ - 1)
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Exponential pheromone weighting based on payload severity. Heat indicates high-value attacker targets.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SRTDeceptionMap;
