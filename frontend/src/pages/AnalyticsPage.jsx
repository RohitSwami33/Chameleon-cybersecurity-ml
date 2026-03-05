import { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import { Box, CircularProgress, Paper, Typography, Button, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import SecurityIcon from '@mui/icons-material/Security';
import LinkIcon from '@mui/icons-material/Link';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { getDashboardStats } from '../services/api';

const AttackTerrainMap = lazy(() => import('../components/AttackTerrainMap'));
const MerkleTree3D = lazy(() => import('../components/MerkleTree3D'));
const ServerRack3D = lazy(() => import('../components/ServerRack3D'));

const LoadingSkeleton = ({ width = '100%', height = 300 }) => (
    <Box sx={{ width, height, background: 'rgba(0,212,255,0.03)', border: '1px solid rgba(0,212,255,0.08)', borderRadius: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress size={24} sx={{ color: '#00d4ff' }} />
    </Box>
);

const AnalyticsPage = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(new Date());
    const navigate = useNavigate();

    const fetchData = useCallback(async () => {
        try {
            const statsData = await getDashboardStats();
            setStats(statsData);
            setLastUpdated(new Date());
        } catch (error) {
            console.error('Error fetching stats:', error);
            toast.error('Failed to fetch analytics data');
            setAutoRefresh(false);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    useEffect(() => {
        if (autoRefresh) {
            const interval = setInterval(fetchData, 10000);
            return () => clearInterval(interval);
        }
    }, [autoRefresh, fetchData]);

    const handleRefresh = () => { setLoading(true); fetchData(); };

    if (loading && !stats) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <CircularProgress sx={{ color: '#00d4ff' }} />
            </Box>
        );
    }

    return (
        <Box sx={{ flexGrow: 1, minHeight: '100vh', position: 'relative', zIndex: 2 }}>
            <Navbar
                lastUpdated={lastUpdated}
                autoRefresh={autoRefresh}
                setAutoRefresh={setAutoRefresh}
                onRefresh={handleRefresh}
            />

            <Box sx={{ px: 2, py: 3 }}>
                <Typography variant="h4" sx={{
                    fontWeight: 700, mb: 3,
                    fontFamily: '"Rajdhani", sans-serif',
                    color: '#e8f4fd',
                    fontSize: 'clamp(1.5rem, 3vw, 2rem)',
                }}>
                    System Analytics
                </Typography>

                {/* Hero Visualization */}
                <Suspense fallback={<LoadingSkeleton height={420} />}>
                    <AttackTerrainMap />
                </Suspense>

                {/* System Health */}
                <Paper sx={{ p: 3, mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, fontSize: '0.95rem', color: '#e8f4fd' }}>System Health</Typography>
                    <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap', justifyContent: 'space-between' }}>

                        <Box sx={{ flex: 1, minWidth: 260, display: 'flex', flexDirection: 'column', justifyContent: 'space-around', gap: 2 }}>
                            {[
                                { label: 'Deception Engine', status: 'Active • Low Latency', color: '#00e676' },
                                { label: 'Blockchain Node', status: `Synced • Height: ${stats?.total_attempts || 0}`, color: '#00e676' },
                                { label: 'Tarpit Status', status: 'Engaged (Adaptive)', color: '#ffab00' },
                            ].map((item, i) => (
                                <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                                    <Box sx={{ padding: '12px 20px', background: 'rgba(5, 8, 16, 0.4)', borderRadius: '8px', border: '1px solid rgba(0,212,255,0.08)' }}>
                                        <Typography variant="body2" sx={{ color: '#7a9bbf', fontSize: '0.8rem', mb: 0.5 }}>{item.label}</Typography>
                                        <Typography variant="body1" sx={{ color: item.color, fontWeight: 600, fontFamily: '"DM Sans", sans-serif' }}>
                                            {item.status}
                                        </Typography>
                                    </Box>
                                </motion.div>
                            ))}
                        </Box>

                        <Box sx={{ flex: '0 0 auto', display: 'flex', justifyContent: 'center', alignItems: 'center', width: { xs: '100%', md: 'auto' } }}>
                            <Suspense fallback={<LoadingSkeleton width={350} height={380} />}>
                                <ServerRack3D />
                            </Suspense>
                        </Box>

                    </Box>
                </Paper>

                {/* Merkle Root */}
                <Paper sx={{
                    p: 3, mb: 2,
                    borderLeft: '3px solid',
                    borderLeftColor: stats?.merkle_root ? '#00e676' : '#ffab00',
                }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600, fontSize: '0.95rem', color: '#e8f4fd' }}>
                            <SecurityIcon sx={{ color: '#00e676' }} />
                            Forensic Evidence Integrity
                        </Typography>
                        <Chip
                            label={stats?.merkle_root ? 'VERIFIED' : 'PENDING'}
                            size="small"
                            sx={{
                                backgroundColor: stats?.merkle_root ? 'rgba(0, 230, 118, 0.12)' : 'rgba(255, 171, 0, 0.12)',
                                color: stats?.merkle_root ? '#00e676' : '#ffab00',
                                fontWeight: 700, fontSize: '0.65rem',
                                border: `1px solid ${stats?.merkle_root ? 'rgba(0, 230, 118, 0.3)' : 'rgba(255, 171, 0, 0.3)'}`,
                            }}
                        />
                    </Box>

                    <Typography variant="body2" sx={{ color: '#7a9bbf', mb: 2, fontSize: '0.8rem' }}>
                        The Merkle Root cryptographically proves that forensic evidence is immutable and hasn't been tampered with.
                    </Typography>

                    <Box sx={{
                        bgcolor: '#050810', p: 2, borderRadius: '8px',
                        border: '1px solid rgba(0, 212, 255, 0.08)',
                    }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="caption" sx={{ color: '#3d5a7a', textTransform: 'uppercase', letterSpacing: 1, fontWeight: 600, fontSize: '0.6rem' }}>
                                Merkle Root Hash
                            </Typography>
                            {stats?.merkle_root && (
                                <Button size="small" variant="outlined" startIcon={<ContentCopyIcon sx={{ fontSize: 12 }} />}
                                    onClick={() => { navigator.clipboard.writeText(stats.merkle_root); toast.success('Merkle root copied'); }}
                                    sx={{ fontSize: '0.65rem', py: 0.3, color: '#00d4ff', borderColor: 'rgba(0, 212, 255, 0.25)' }}>
                                    Copy
                                </Button>
                            )}
                        </Box>
                        <Typography variant="body2" sx={{
                            color: stats?.merkle_root ? '#00e676' : '#3d5a7a',
                            wordBreak: 'break-all', fontSize: '0.8rem', lineHeight: 1.6,
                            fontFamily: '"IBM Plex Mono", monospace',
                        }}>
                            {stats?.merkle_root || 'No data available — waiting for attack logs…'}
                        </Typography>
                    </Box>

                    {/* Interactive 3D Tree */}
                    <Box sx={{ mt: 3, mb: 1 }}>
                        <Suspense fallback={<LoadingSkeleton height={340} />}>
                            <MerkleTree3D lastUpdated={lastUpdated} recordsCount={stats?.total_attempts || 0} />
                        </Suspense>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2, mt: 2, justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
                        {[
                            { label: 'Evidence Records', value: stats?.total_attempts?.toLocaleString() || 0 },
                            { label: 'Chain Integrity', value: stats?.merkle_root ? '100%' : 'N/A', color: '#00e676' },
                            { label: 'Last Verification', value: lastUpdated.toLocaleTimeString() },
                        ].map((item, i) => (
                            <Box key={i} sx={{ flex: 1, minWidth: 150 }}>
                                <Typography variant="caption" sx={{ color: '#3d5a7a', fontSize: '0.7rem' }}>{item.label}</Typography>
                                <Typography variant="body1" sx={{ fontWeight: 600, color: item.color || '#e8f4fd', fontFamily: '"Rajdhani", sans-serif' }}>
                                    {item.value}
                                </Typography>
                            </Box>
                        ))}
                        <Box sx={{ flex: 1, minWidth: 150, textAlign: 'right' }}>
                            <Button variant="outlined" size="small" startIcon={<LinkIcon />}
                                onClick={() => navigate('/blockchain')}
                                sx={{ fontSize: '0.75rem', color: '#00d4ff', borderColor: 'rgba(0, 212, 255, 0.25)', '&:hover': { borderColor: '#00d4ff', backgroundColor: 'rgba(0, 212, 255, 0.06)' } }}>
                                View Blockchain
                            </Button>
                        </Box>
                    </Box>
                </Paper>
            </Box>
        </Box>
    );
};

export default AnalyticsPage;
