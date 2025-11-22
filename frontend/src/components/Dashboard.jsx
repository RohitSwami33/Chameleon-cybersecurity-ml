import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Grid,
    Typography,
    Button,
    CircularProgress,
    Switch,
    FormControlLabel,
    AppBar,
    Toolbar,
    useTheme
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import SecurityIcon from '@mui/icons-material/Security';
import LogoutIcon from '@mui/icons-material/Logout';
import LinkIcon from '@mui/icons-material/Link';
import { toast } from 'react-toastify';
import StatsCards from './StatsCards';
import AttackChart from './AttackChart';
import AttackLogs from './AttackLogs';
import GeoMap from './GeoMap';
import ThreatScorePanel from './ThreatScorePanel';
import { getDashboardStats, getAttackLogs, generateReport } from '../services/api';
import { downloadPDF } from '../utils/helpers';

const Dashboard = () => {
    const [stats, setStats] = useState({
        total_attempts: 0,
        malicious_attempts: 0,
        benign_attempts: 0,
        merkle_root: null,
        attack_distribution: {},
        geo_locations: [],
        flagged_ips_count: 0,
        top_threats: []
    });
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(new Date());

    const theme = useTheme();
    const navigate = useNavigate();

    const fetchData = useCallback(async () => {
        try {
            // Check if token exists
            const token = localStorage.getItem('authToken');
            if (!token) {
                toast.error('Please login to access dashboard');
                navigate('/login');
                return;
            }

            const [statsData, logsData] = await Promise.all([
                getDashboardStats(),
                getAttackLogs(0, 100) // Fetch last 100 logs
            ]);

            setStats(statsData);
            setLogs(logsData);
            setLastUpdated(new Date());
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            
            // Check if it's an auth error
            if (error.response && error.response.status === 401) {
                toast.error('Session expired. Please login again.');
                localStorage.removeItem('authToken');
                navigate('/login');
            } else {
                toast.error('Failed to fetch dashboard data');
                // Stop auto-refresh on error to prevent spamming
                setAutoRefresh(false);
            }
        } finally {
            setLoading(false);
        }
    }, [navigate]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    useEffect(() => {
        let interval;
        if (autoRefresh) {
            interval = setInterval(() => {
                fetchData();
            }, 10000); // 10 seconds
        }
        return () => clearInterval(interval);
    }, [autoRefresh, fetchData]);

    const handleRefresh = () => {
        setLoading(true);
        fetchData();
    };

    const handleGenerateReport = async (ipAddress) => {
        try {
            toast.info(`Generating report for ${ipAddress}...`);
            const blob = await generateReport(ipAddress);
            downloadPDF(blob, `incident_report_${ipAddress}.pdf`);
            toast.success('Report generated successfully');
        } catch (error) {
            console.error('Error generating report:', error);
            toast.error('Failed to generate report');
        }
    };

    const handleViewDetails = (logId) => {
        // In a real app, this might open a dedicated page or a more detailed modal
        // For now, the expandable row in AttackLogs handles most details
        console.log('View details for log:', logId);
    };

    const handleLogout = () => {
        localStorage.removeItem('authToken');
        toast.info('Logged out successfully');
        navigate('/login');
    };

    return (
        <Box sx={{ 
            flexGrow: 1, 
            backgroundColor: 'background.default', 
            minHeight: '100vh',
            width: '100vw',
            overflow: 'hidden'
        }}>
            <AppBar position="static" color="transparent" elevation={0} sx={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <Toolbar sx={{ px: 2 }}>
                    <SecurityIcon sx={{ mr: 2, color: 'primary.main', fontSize: 32 }} />
                    <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 700, letterSpacing: 1 }}>
                        CHAMELEON <Typography component="span" variant="h5" color="primary" sx={{ fontWeight: 700 }}>FORENSICS</Typography>
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ display: { xs: 'none', sm: 'block' } }}>
                            Last updated: {lastUpdated.toLocaleTimeString()}
                        </Typography>

                        <FormControlLabel
                            control={
                                <Switch
                                    checked={autoRefresh}
                                    onChange={(e) => setAutoRefresh(e.target.checked)}
                                    color="primary"
                                    size="small"
                                />
                            }
                            label={<Typography variant="body2">Live Updates</Typography>}
                        />

                        <Button
                            variant="outlined"
                            startIcon={<RefreshIcon />}
                            onClick={handleRefresh}
                            size="small"
                        >
                            Refresh
                        </Button>

                        <Button
                            variant="outlined"
                            color="primary"
                            startIcon={<LinkIcon />}
                            onClick={() => navigate('/blockchain')}
                            size="small"
                        >
                            Blockchain
                        </Button>

                        <Button
                            variant="outlined"
                            color="error"
                            startIcon={<LogoutIcon />}
                            onClick={handleLogout}
                            size="small"
                        >
                            Logout
                        </Button>
                    </Box>
                </Toolbar>
            </AppBar>

            <Box sx={{ px: 2, py: 2, width: '100%', boxSizing: 'border-box' }}>
                {loading && !stats.total_attempts ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <>
                        <StatsCards stats={stats} />

                        <Grid container spacing={2} sx={{ mb: 2 }}>
                            <Grid item xs={12} md={4}>
                                {/* Attack Distribution Chart */}
                                <Box sx={{ height: 400 }}>
                                    <AttackChart attackDistribution={stats.attack_distribution} />
                                </Box>
                            </Grid>
                            <Grid item xs={12} md={4}>
                                {/* Geographic Attack Origins */}
                                <Box sx={{ height: 400 }}>
                                    <GeoMap geoLocations={stats.geo_locations || []} />
                                </Box>
                            </Grid>
                            <Grid item xs={12} md={4}>
                                {/* Threat Score Panel */}
                                <Box sx={{ height: 400 }}>
                                    <ThreatScorePanel 
                                        topThreats={stats.top_threats || []} 
                                        flaggedCount={stats.flagged_ips_count || 0}
                                    />
                                </Box>
                            </Grid>
                        </Grid>

                        <Grid container spacing={2} sx={{ mb: 2 }}>
                            <Grid item xs={12}>
                                <Box sx={{ p: 2, bgcolor: '#1e1e1e', borderRadius: 1, border: '1px solid #333' }}>
                                    <Typography variant="h6" gutterBottom>System Health</Typography>
                                    <Grid container spacing={2}>
                                        <Grid item xs={12} sm={4}>
                                            <Typography variant="body2" color="text.secondary">Deception Engine</Typography>
                                            <Typography variant="body1" color="success.main" sx={{ fontWeight: 600 }}>Active • Low Latency</Typography>
                                        </Grid>
                                        <Grid item xs={12} sm={4}>
                                            <Typography variant="body2" color="text.secondary">Blockchain Node</Typography>
                                            <Typography variant="body1" color="success.main" sx={{ fontWeight: 600 }}>Synced • Height: {stats.total_attempts}</Typography>
                                        </Grid>
                                        <Grid item xs={12} sm={4}>
                                            <Typography variant="body2" color="text.secondary">Tarpit Status</Typography>
                                            <Typography variant="body1" color="warning.main" sx={{ fontWeight: 600 }}>Engaged (Adaptive)</Typography>
                                        </Grid>
                                    </Grid>
                                </Box>
                            </Grid>
                        </Grid>

                        <AttackLogs
                            logs={logs}
                            onViewDetails={handleViewDetails}
                            onGenerateReport={handleGenerateReport}
                        />
                    </>
                )}
            </Box>
        </Box>
    );
};

export default Dashboard;
