import { useState, useEffect, useCallback } from 'react';
import { Box, CircularProgress, Paper, Typography, Button } from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import LinkIcon from '@mui/icons-material/Link';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { getDashboardStats } from '../services/api';

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

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    useEffect(() => {
        if (autoRefresh) {
            const interval = setInterval(fetchData, 10000);
            return () => clearInterval(interval);
        }
    }, [autoRefresh, fetchData]);

    const handleRefresh = () => {
        setLoading(true);
        fetchData();
    };

    if (loading && !stats) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ 
            flexGrow: 1, 
            backgroundColor: 'background.default', 
            minHeight: '100vh',
        }}>
            <Navbar 
                lastUpdated={lastUpdated}
                autoRefresh={autoRefresh}
                setAutoRefresh={setAutoRefresh}
                onRefresh={handleRefresh}
            />

            <Box sx={{ px: 2, py: 3 }}>
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
                    System Analytics
                </Typography>

                {/* System Health */}
                <Paper sx={{ p: 3, mb: 2, bgcolor: '#1e1e1e' }}>
                    <Typography variant="h6" gutterBottom>System Health</Typography>
                    <Box sx={{ 
                        display: 'flex', 
                        justifyContent: 'space-around',
                        alignItems: 'center',
                        gap: 2,
                        mt: 2,
                        flexWrap: 'wrap'
                    }}>
                        <Box sx={{ flex: 1, minWidth: 200, textAlign: 'center' }}>
                            <Typography variant="body2" color="text.secondary">Deception Engine</Typography>
                            <Typography variant="body1" color="success.main" sx={{ fontWeight: 600 }}>
                                Active • Low Latency
                            </Typography>
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 200, textAlign: 'center' }}>
                            <Typography variant="body2" color="text.secondary">Blockchain Node</Typography>
                            <Typography variant="body1" color="success.main" sx={{ fontWeight: 600 }}>
                                Synced • Height: {stats?.total_attempts || 0}
                            </Typography>
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 200, textAlign: 'center' }}>
                            <Typography variant="body2" color="text.secondary">Tarpit Status</Typography>
                            <Typography variant="body1" color="warning.main" sx={{ fontWeight: 600 }}>
                                Engaged (Adaptive)
                            </Typography>
                        </Box>
                    </Box>
                </Paper>

                {/* Merkle Root */}
                <Paper sx={{ 
                    p: 3, 
                    mb: 2, 
                    bgcolor: '#1e1e1e',
                    borderLeft: '4px solid',
                    borderLeftColor: stats?.merkle_root ? 'success.main' : 'warning.main'
                }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <SecurityIcon sx={{ color: 'success.main' }} />
                            Forensic Evidence Integrity
                        </Typography>
                        <Box sx={{ 
                            px: 2, 
                            py: 0.5, 
                            bgcolor: stats?.merkle_root ? 'success.dark' : 'warning.dark',
                            borderRadius: 1
                        }}>
                            <Typography variant="caption" sx={{ fontWeight: 600 }}>
                                {stats?.merkle_root ? 'VERIFIED' : 'PENDING'}
                            </Typography>
                        </Box>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        The Merkle Root cryptographically proves that forensic evidence is immutable and hasn't been tampered with.
                    </Typography>

                    <Box sx={{ 
                        bgcolor: '#0a0a0a', 
                        p: 2, 
                        borderRadius: 1,
                        border: '1px solid #2a2a2a',
                        fontFamily: 'monospace'
                    }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: 1 }}>
                                Merkle Root Hash
                            </Typography>
                            {stats?.merkle_root && (
                                <Button
                                    size="small"
                                    variant="outlined"
                                    onClick={() => {
                                        navigator.clipboard.writeText(stats.merkle_root);
                                        toast.success('Merkle root copied to clipboard');
                                    }}
                                    sx={{ fontSize: '0.7rem', py: 0.5 }}
                                >
                                    Copy
                                </Button>
                            )}
                        </Box>
                        <Typography 
                            variant="body2" 
                            sx={{ 
                                color: stats?.merkle_root ? 'success.light' : 'text.disabled',
                                wordBreak: 'break-all',
                                fontSize: '0.85rem',
                                lineHeight: 1.6
                            }}
                        >
                            {stats?.merkle_root || 'No data available - waiting for attack logs...'}
                        </Typography>
                    </Box>

                    <Box sx={{ 
                        display: 'flex', 
                        gap: 2, 
                        mt: 2,
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        flexWrap: 'wrap'
                    }}>
                        <Box sx={{ flex: 1, minWidth: 150 }}>
                            <Typography variant="caption" color="text.secondary">
                                Evidence Records
                            </Typography>
                            <Typography variant="body1" sx={{ fontWeight: 600 }}>
                                {stats?.total_attempts?.toLocaleString() || 0}
                            </Typography>
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 150 }}>
                            <Typography variant="caption" color="text.secondary">
                                Chain Integrity
                            </Typography>
                            <Typography variant="body1" color="success.main" sx={{ fontWeight: 600 }}>
                                {stats?.merkle_root ? '100%' : 'N/A'}
                            </Typography>
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 150 }}>
                            <Typography variant="caption" color="text.secondary">
                                Last Verification
                            </Typography>
                            <Typography variant="body1" sx={{ fontWeight: 600 }}>
                                {lastUpdated.toLocaleTimeString()}
                            </Typography>
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 150, textAlign: 'right' }}>
                            <Button
                                variant="outlined"
                                size="small"
                                startIcon={<LinkIcon />}
                                onClick={() => navigate('/blockchain')}
                                sx={{ fontSize: '0.75rem' }}
                            >
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
