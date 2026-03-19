import { useState, useEffect, useCallback } from 'react';
import { Box, Typography, Collapse, IconButton } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import Navbar from '../components/Navbar';

// Meta-Heuristic Optimization Components
import TCPSOTarpitMonitor from '../components/dashboard/TCPSOTarpitMonitor';
import SRTDeceptionMap from '../components/dashboard/SRTDeceptionMap';
import SystemEdgeNodeStatus from '../components/dashboard/SystemEdgeNodeStatus';
import LiveThreatFeed from '../components/dashboard/LiveThreatFeed';

/* ─── Collapsible Section Wrapper ───────────────────────────── */
const DashboardSection = ({ title, subtitle, icon, defaultExpanded = true, children }) => {
    const [expanded, setExpanded] = useState(defaultExpanded);

    return (
        <Box sx={{
            mb: 2,
            borderRadius: '12px',
            border: '1px solid rgba(255, 42, 42, 0.08)',
            background: 'rgba(10, 15, 30, 0.5)',
            backdropFilter: 'blur(8px)',
            overflow: 'hidden',
            transition: 'border-color 0.3s ease',
            '&:hover': { borderColor: 'rgba(255, 42, 42, 0.15)' },
        }}>
            {/* Section Header */}
            <Box
                onClick={() => setExpanded(!expanded)}
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    px: 2.5,
                    py: 1.5,
                    cursor: 'pointer',
                    borderBottom: expanded ? '1px solid rgba(255, 42, 42, 0.06)' : 'none',
                    transition: 'background-color 0.2s',
                    '&:hover': { backgroundColor: 'rgba(255, 42, 42, 0.03)' },
                }}
            >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    {icon && (
                        <Typography sx={{ fontSize: '1.1rem', lineHeight: 1 }}>{icon}</Typography>
                    )}
                    <Box>
                        <Typography sx={{
                            fontFamily: '"IBM Plex Mono", monospace',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            letterSpacing: '0.08em',
                            textTransform: 'uppercase',
                            color: '#ff2a2a',
                        }}>
                            {title}
                        </Typography>
                        {subtitle && (
                            <Typography sx={{
                                fontSize: '0.7rem',
                                color: 'rgba(232, 244, 253, 0.4)',
                                fontFamily: '"DM Sans", sans-serif',
                                mt: 0.25,
                            }}>
                                {subtitle}
                            </Typography>
                        )}
                    </Box>
                </Box>
                <IconButton size="small" sx={{ color: 'rgba(232, 244, 253, 0.5)' }}>
                    {expanded ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                </IconButton>
            </Box>

            {/* Section Content */}
            <Collapse in={expanded} timeout={300}>
                <Box sx={{ p: 2 }}>
                    {children}
                </Box>
            </Collapse>
        </Box>
    );
};

const AdvancedSystemsPage = () => {
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(new Date());

    const handleRefresh = useCallback(() => {
        setLastUpdated(new Date());
        // Since the components fetch their own data internally, updating the lastUpdated
        // state primarily serves the navbar timestamp. Components update on their own interval.
    }, []);

    useEffect(() => {
        if (autoRefresh) {
            const interval = setInterval(handleRefresh, 10000);
            return () => clearInterval(interval);
        }
    }, [autoRefresh, handleRefresh]);

    return (
        <Box sx={{ flexGrow: 1, minHeight: '100vh', position: 'relative', zIndex: 2, backgroundColor: '#050810' }}>
            <Navbar
                lastUpdated={lastUpdated}
                autoRefresh={autoRefresh}
                setAutoRefresh={setAutoRefresh}
                onRefresh={handleRefresh}
            />

            <Box sx={{ px: 2, py: 3, maxWidth: 1600, mx: 'auto' }}>
                <Box sx={{ mb: 4, mt: 1 }}>
                    <Typography variant="h4" sx={{ color: '#ff2a2a', fontFamily: '"Orbitron", sans-serif', fontWeight: 700, mb: 1 }}>
                        ADVANCED DECEPTION SYSTEMS
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#7a9bbf' }}>
                        Real-time monitoring of heuristic behavioral traps and model inference edge-nodes.
                    </Typography>
                </Box>

                {/* ── Live Threat Feed ─────────────────────────────── */}
                <DashboardSection
                    title="Live Threat Feed"
                    subtitle="Real-time BiLSTM + LLM classification pipeline"
                    icon="⚡"
                    defaultExpanded={true}
                >
                    <LiveThreatFeed />
                </DashboardSection>

                {/* ── TC-PSO Tarpit Monitor (Novel Algorithm) ───────── */}
                <DashboardSection
                    title="TC-PSO Tarpit Optimizer"
                    subtitle="Threat-Calibrated Particle Swarm Optimization — adaptive tarpit delays"
                    icon="🐝"
                    defaultExpanded={true}
                >
                    <TCPSOTarpitMonitor />
                </DashboardSection>

                {/* ── S-RRT Deception Map + System Status Side-by-Side ─ */}
                <Box sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
                    gap: '16px',
                    mb: 2,
                }}>
                    <DashboardSection
                        title="S-RRT Deception Map"
                        subtitle="Semantic RRT fake filesystem with pheromone heat mapping"
                        icon="🌳"
                        defaultExpanded={true}
                    >
                        <SRTDeceptionMap />
                    </DashboardSection>

                    <DashboardSection
                        title="Edge Node Status"
                        subtitle="ML inference engine, VRAM allocation & tarpit sessions"
                        icon="🖥️"
                        defaultExpanded={true}
                    >
                        <SystemEdgeNodeStatus />
                    </DashboardSection>
                </Box>
            </Box>
        </Box>
    );
};

export default AdvancedSystemsPage;
