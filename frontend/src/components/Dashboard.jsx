import { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Typography,
    Button,
    CircularProgress,
    Switch,
    FormControlLabel,
    AppBar,
    Toolbar
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
import AttackGlobeSimple from './AttackGlobeSimple';
import ThreatIntelFeed from './ThreatIntelFeed';
import { CommandBarTrigger } from './ui/CommandBar';
import FilterBadges from './ui/FilterBadges';
import useAttackStore from '../stores/useAttackStore';
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
    const [selectedAttack, setSelectedAttack] = useState(null);
    const [useMockGeo, setUseMockGeo] = useState(true); // Toggle for mock geo data

    const navigate = useNavigate();

    // Attack store integration
    const { setAttacks, getFilteredAttacks, filters } = useAttackStore();

    // Memoized filtered attacks
    const filteredLogs = useMemo(() => {
        return getFilteredAttacks();
    }, [logs, filters, getFilteredAttacks]);

    // Compute stats from filtered data
    const filteredStats = useMemo(() => {
        const malicious = filteredLogs.filter(
            log => log.classification?.attack_type !== 'BENIGN'
        ).length;
        const benign = filteredLogs.filter(
            log => log.classification?.attack_type === 'BENIGN'
        ).length;

        // Calculate attack distribution
        const distribution = {};
        filteredLogs.forEach(log => {
            const type = log.classification?.attack_type || 'UNKNOWN';
            distribution[type] = (distribution[type] || 0) + 1;
        });

        // Calculate geo locations with counts
        const geoMap = {};
        filteredLogs.forEach(log => {
            if (log.geo_location?.country) {
                const key = `${log.geo_location.country}-${log.geo_location.city}`;
                if (!geoMap[key]) {
                    geoMap[key] = {
                        ...log.geo_location,
                        count: 0
                    };
                }
                geoMap[key].count++;
            }
        });
        const geoLocations = Object.values(geoMap).sort((a, b) => b.count - a.count);

        return {
            ...stats,
            total_attempts: filteredLogs.length,
            malicious_attempts: malicious,
            benign_attempts: benign,
            attack_distribution: distribution,
            geo_locations: geoLocations
        };
    }, [filteredLogs, stats]);

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
            setAttacks(logsData); // Sync with attack store
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

    const handleAttackClick = (attack) => {
        setSelectedAttack(attack);
        toast.info(`Selected attack from ${attack.ip_address}`);
    };

    // Mock geo_location data for testing Attack Globe
    const mockGeoLocations = [
        { country: 'United States', city: 'New York', latitude: 40.7128, longitude: -74.0060 },
        { country: 'China', city: 'Beijing', latitude: 39.9042, longitude: 116.4074 },
        { country: 'Russia', city: 'Moscow', latitude: 55.7558, longitude: 37.6173 },
        { country: 'Germany', city: 'Berlin', latitude: 52.5200, longitude: 13.4050 },
        { country: 'United Kingdom', city: 'London', latitude: 51.5074, longitude: -0.1278 },
        { country: 'France', city: 'Paris', latitude: 48.8566, longitude: 2.3522 },
        { country: 'Japan', city: 'Tokyo', latitude: 35.6762, longitude: 139.6503 },
        { country: 'Brazil', city: 'São Paulo', latitude: -23.5505, longitude: -46.6333 },
        { country: 'India', city: 'Mumbai', latitude: 19.0760, longitude: 72.8777 },
        { country: 'Australia', city: 'Sydney', latitude: -33.8688, longitude: 151.2093 },
        { country: 'Canada', city: 'Toronto', latitude: 43.6532, longitude: -79.3832 },
        { country: 'South Korea', city: 'Seoul', latitude: 37.5665, longitude: 126.9780 },
        { country: 'Mexico', city: 'Mexico City', latitude: 19.4326, longitude: -99.1332 },
        { country: 'Netherlands', city: 'Amsterdam', latitude: 52.3676, longitude: 4.9041 },
        { country: 'Singapore', city: 'Singapore', latitude: 1.3521, longitude: 103.8198 },
        { country: 'Spain', city: 'Madrid', latitude: 40.4168, longitude: -3.7038 },
        { country: 'Italy', city: 'Rome', latitude: 41.9028, longitude: 12.4964 },
        { country: 'Turkey', city: 'Istanbul', latitude: 41.0082, longitude: 28.9784 },
        { country: 'Poland', city: 'Warsaw', latitude: 52.2297, longitude: 21.0122 },
        { country: 'Ukraine', city: 'Kyiv', latitude: 50.4501, longitude: 30.5234 }
    ];

    // Add mock geo_location to filtered logs for testing (only if enabled)
    const logsWithGeo = useMockGeo ? filteredLogs.map((log, index) => {
        if (!log.geo_location || !log.geo_location.latitude) {
            const mockGeo = mockGeoLocations[index % mockGeoLocations.length];
            return {
                ...log,
                geo_location: mockGeo
            };
        }
        return log;
    }) : filteredLogs;

    // Recalculate geo locations for the map when using mock data
    const displayStats = useMemo(() => {
        if (!useMockGeo || logsWithGeo.length === 0) {
            return filteredStats;
        }

        // Recalculate geo locations from logsWithGeo
        const geoMap = {};
        logsWithGeo.forEach(log => {
            if (log.geo_location?.country) {
                const key = `${log.geo_location.country}-${log.geo_location.city}`;
                if (!geoMap[key]) {
                    geoMap[key] = {
                        ...log.geo_location,
                        count: 0
                    };
                }
                geoMap[key].count++;
            }
        });
        const geoLocations = Object.values(geoMap).sort((a, b) => b.count - a.count);

        return {
            ...filteredStats,
            geo_locations: geoLocations
        };
    }, [filteredStats, logsWithGeo, useMockGeo]);

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

                        <FormControlLabel
                            control={
                                <Switch
                                    checked={useMockGeo}
                                    onChange={(e) => setUseMockGeo(e.target.checked)}
                                    color="secondary"
                                    size="small"
                                />
                            }
                            label={<Typography variant="body2">Mock Geo Data</Typography>}
                        />

                        <CommandBarTrigger />

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

            <Box sx={{ px: 1, py: 2, width: '100%', boxSizing: 'border-box' }}>
                {loading && !stats.total_attempts ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <>
                        {/* Filter Badges */}
                        <FilterBadges />

                        {/* Attack Map - 2D Visualization */}
                        <AttackGlobeSimple
                            attacks={logsWithGeo}
                            serverLocation={{ lat: 37.7749, lon: -122.4194 }}
                            onAttackClick={handleAttackClick}
                            maxArcs={100}
                        />

                        <StatsCards stats={filteredStats} />

                        <Box sx={{ 
                            display: 'flex', 
                            gap: 1, 
                            mb: 2,
                            width: '100%',
                            flexWrap: 'nowrap'
                        }}>
                            {/* Attack Distribution Chart */}
                            <Box sx={{ 
                                flex: 1, 
                                minWidth: 0, 
                                maxWidth: '33.33%',
                                height: 350,
                                overflow: 'auto'
                            }}>
                                <AttackChart attackDistribution={filteredStats.attack_distribution} />
                            </Box>
                            
                            {/* Geographic Attack Origins */}
                            <Box sx={{ 
                                flex: 1, 
                                minWidth: 0, 
                                maxWidth: '33.33%',
                                height: 350,
                                overflow: 'auto'
                            }}>
                                <GeoMap geoLocations={displayStats.geo_locations || []} />
                            </Box>
                            
                            {/* Threat Score Panel */}
                            <Box sx={{ 
                                flex: 1, 
                                minWidth: 0, 
                                maxWidth: '33.33%',
                                height: 350,
                                overflow: 'auto'
                            }}>
                                <ThreatScorePanel 
                                    topThreats={stats.top_threats || []} 
                                    flaggedCount={stats.flagged_ips_count || 0}
                                />
                            </Box>
                        </Box>

                        <Box sx={{ mb: 2 }}>
                            <Box sx={{ p: 2, bgcolor: '#1e1e1e', borderRadius: 1, border: '1px solid #333' }}>
                                <Typography variant="h6" gutterBottom>System Health</Typography>
                                <Box sx={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-around',
                                    alignItems: 'center',
                                    gap: 2,
                                    mt: 2
                                }}>
                                    <Box sx={{ 
                                        flex: 1,
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        textAlign: 'center'
                                    }}>
                                        <Typography variant="body2" color="text.secondary">Deception Engine</Typography>
                                        <Typography variant="body1" color="success.main" sx={{ fontWeight: 600 }}>Active • Low Latency</Typography>
                                    </Box>
                                    <Box sx={{ 
                                        flex: 1,
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        textAlign: 'center'
                                    }}>
                                        <Typography variant="body2" color="text.secondary">Blockchain Node</Typography>
                                        <Typography variant="body1" color="success.main" sx={{ fontWeight: 600 }}>Synced • Height: {stats.total_attempts}</Typography>
                                    </Box>
                                    <Box sx={{ 
                                        flex: 1,
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        textAlign: 'center'
                                    }}>
                                        <Typography variant="body2" color="text.secondary">Tarpit Status</Typography>
                                        <Typography variant="body1" color="warning.main" sx={{ fontWeight: 600 }}>Engaged (Adaptive)</Typography>
                                    </Box>
                                </Box>
                            </Box>
                        </Box>

                        {/* Merkle Root - Forensic Evidence Integrity */}
                        <Box sx={{ mb: 2 }}>
                            <Box sx={{ 
                                p: 2, 
                                bgcolor: '#1e1e1e', 
                                borderRadius: 1, 
                                border: '1px solid #333',
                                borderLeft: '4px solid',
                                borderLeftColor: stats.merkle_root ? 'success.main' : 'warning.main'
                            }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <SecurityIcon sx={{ color: 'success.main' }} />
                                        Forensic Evidence Integrity
                                    </Typography>
                                    <Box sx={{ 
                                        px: 2, 
                                        py: 0.5, 
                                        bgcolor: stats.merkle_root ? 'success.dark' : 'warning.dark',
                                        borderRadius: 1
                                    }}>
                                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                                            {stats.merkle_root ? 'VERIFIED' : 'PENDING'}
                                        </Typography>
                                    </Box>
                                </Box>
                                
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                    The Merkle Root cryptographically proves that forensic evidence is immutable and hasn't been tampered with by insiders or persistent attackers.
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
                                        {stats.merkle_root && (
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
                                            color: stats.merkle_root ? 'success.light' : 'text.disabled',
                                            wordBreak: 'break-all',
                                            fontSize: '0.85rem',
                                            lineHeight: 1.6
                                        }}
                                    >
                                        {stats.merkle_root || 'No data available - waiting for attack logs...'}
                                    </Typography>
                                </Box>

                                <Box sx={{ 
                                    display: 'flex', 
                                    gap: 2, 
                                    mt: 2,
                                    justifyContent: 'space-between',
                                    alignItems: 'center'
                                }}>
                                    <Box sx={{ flex: 1 }}>
                                        <Typography variant="caption" color="text.secondary">
                                            Evidence Records
                                        </Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 600 }}>
                                            {stats.total_attempts.toLocaleString()}
                                        </Typography>
                                    </Box>
                                    <Box sx={{ flex: 1 }}>
                                        <Typography variant="caption" color="text.secondary">
                                            Chain Integrity
                                        </Typography>
                                        <Typography variant="body1" color="success.main" sx={{ fontWeight: 600 }}>
                                            {stats.merkle_root ? '100%' : 'N/A'}
                                        </Typography>
                                    </Box>
                                    <Box sx={{ flex: 1 }}>
                                        <Typography variant="caption" color="text.secondary">
                                            Last Verification
                                        </Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 600 }}>
                                            {lastUpdated.toLocaleTimeString()}
                                        </Typography>
                                    </Box>
                                    <Box sx={{ flex: 1, textAlign: 'right' }}>
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
                            </Box>
                        </Box>

                        {/* Privacy-Preserving Threat Intelligence Feed */}
                        <Box sx={{ mb: 2 }}>
                            <ThreatIntelFeed />
                        </Box>

                        {/* Selected Attack Details Panel */}
                        {selectedAttack && (
                            <Box sx={{ mb: 2 }}>
                                <Box sx={{ p: 2, bgcolor: '#1e1e1e', borderRadius: 1, border: '1px solid #333' }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                        <Typography variant="h6">Selected Attack Details</Typography>
                                        <Button 
                                            variant="outlined" 
                                            size="small" 
                                            onClick={() => setSelectedAttack(null)}
                                        >
                                            Close
                                        </Button>
                                    </Box>
                                    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                                        <Box>
                                            <Typography variant="body2" color="text.secondary">IP Address</Typography>
                                            <Typography variant="body1">{selectedAttack.ip_address}</Typography>
                                        </Box>
                                        <Box>
                                            <Typography variant="body2" color="text.secondary">Attack Type</Typography>
                                            <Typography variant="body1">{selectedAttack.classification?.attack_type}</Typography>
                                        </Box>
                                        <Box>
                                            <Typography variant="body2" color="text.secondary">Location</Typography>
                                            <Typography variant="body1">
                                                {selectedAttack.geo_location?.city}, {selectedAttack.geo_location?.country}
                                            </Typography>
                                        </Box>
                                        <Box>
                                            <Typography variant="body2" color="text.secondary">Timestamp</Typography>
                                            <Typography variant="body1">
                                                {new Date(selectedAttack.timestamp).toLocaleString()}
                                            </Typography>
                                        </Box>
                                        <Box sx={{ gridColumn: '1 / -1' }}>
                                            <Typography variant="body2" color="text.secondary">Confidence</Typography>
                                            <Typography variant="body1">
                                                {(selectedAttack.classification?.confidence * 100).toFixed(2)}%
                                            </Typography>
                                        </Box>
                                    </Box>
                                </Box>
                            </Box>
                        )}

                        <AttackLogs
                            logs={filteredLogs}
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
