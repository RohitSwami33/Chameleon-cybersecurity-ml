import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Container,
    Grid,
    Typography,
    Button,
    IconButton,
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
import { toast } from 'react-toastify';
import StatsCards from './StatsCards';
import AttackChart from './AttackChart';
import AttackLogs from './AttackLogs';
import { getDashboardStats, getAttackLogs, generateReport } from '../services/api';
import { downloadPDF } from '../utils/helpers';

const Dashboard = () => {
    const [stats, setStats] = useState({
        total_attempts: 0,
        malicious_attempts: 0,
        benign_attempts: 0,
        merkle_root: null,
        attack_distribution: {}
    });
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(new Date());

    const theme = useTheme();
    const navigate = useNavigate();

    const fetchData = useCallback(async () => {
        try {
            const [statsData, logsData] = await Promise.all([
                getDashboardStats(),
                getAttackLogs(0, 100) // Fetch last 100 logs
            ]);

            setStats(statsData);
            setLogs(logsData);
            setLastUpdated(new Date());
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            toast.error('Failed to fetch dashboard data');
            // Stop auto-refresh on error to prevent spamming
            setAutoRefresh(false);
        } finally {
            setLoading(false);
        }
    }, []);

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
        <Box sx={{ flexGrow: 1, backgroundColor: 'background.default', minHeight: '100vh' }}>
            <AppBar position="static" color="transparent" elevation={0} sx={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <Toolbar>
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

            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                {loading && !stats.total_attempts ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <>
                        <StatsCards stats={stats} />

                        <Grid container spacing={3} sx={{ mb: 3 }}>
                            <Grid item xs={12} md={8}>
                                {/* Main Chart Area */}
                                <Box sx={{ height: 400 }}>
                                    <AttackChart attackDistribution={stats.attack_distribution} />
                                </Box>
                            </Grid>
                            <Grid item xs={12} md={4}>
                                {/* Secondary Chart or Info - For now we just use the same chart component or could add another one */}
                                {/* Let's add a placeholder for GeoMap or another metric if needed, 
                    but for now let's just make the chart take full width or add a summary panel */}
                                <Box sx={{ height: 400, p: 2, bgcolor: '#1e1e1e', borderRadius: 1, border: '1px solid #333' }}>
                                    <Typography variant="h6" gutterBottom>System Health</Typography>
                                    <Box sx={{ mt: 2 }}>
                                        <Typography variant="body2" color="text.secondary">Deception Engine</Typography>
                                        <Typography variant="body1" color="success.main" sx={{ mb: 2 }}>Active • Low Latency</Typography>

                                        <Typography variant="body2" color="text.secondary">Blockchain Node</Typography>
                                        <Typography variant="body1" color="success.main" sx={{ mb: 2 }}>Synced • Height: {stats.total_attempts}</Typography>

                                        <Typography variant="body2" color="text.secondary">Tarpit Status</Typography>
                                        <Typography variant="body1" color="warning.main" sx={{ mb: 2 }}>Engaged (Adaptive)</Typography>
                                    </Box>
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
            </Container>
        </Box>
    );
};

export default Dashboard;
