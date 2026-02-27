import { useState, useEffect, useCallback } from 'react';
import { Box, CircularProgress, Paper, Typography, Switch, FormControlLabel } from '@mui/material';
import { toast } from 'react-toastify';
import Navbar from '../components/Navbar';
import AttackGlobeSimple from '../components/AttackGlobeSimple';
import { getAttackLogs } from '../services/api';

const AttackGlobePage = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(new Date());
    const [useMockGeo, setUseMockGeo] = useState(true);
    const [selectedAttack, setSelectedAttack] = useState(null);

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
    ];

    const logsWithGeo = useMockGeo ? logs.map((log, index) => {
        if (!log.geo_location || !log.geo_location.latitude) {
            const mockGeo = mockGeoLocations[index % mockGeoLocations.length];
            return {
                ...log,
                geo_location: mockGeo
            };
        }
        return log;
    }) : logs;

    const fetchData = useCallback(async () => {
        try {
            const logsData = await getAttackLogs(0, 100);
            setLogs(logsData);
            setLastUpdated(new Date());
        } catch (error) {
            console.error('Error fetching attack logs:', error);
            toast.error('Failed to fetch attack data');
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

    const handleAttackClick = (attack) => {
        setSelectedAttack(attack);
        toast.info(`Selected attack from ${attack.ip_address}`);
    };

    if (loading && logs.length === 0) {
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
                <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        Global Attack Visualization
                    </Typography>
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
                </Box>

                <AttackGlobeSimple
                    attacks={logsWithGeo}
                    serverLocation={{ lat: 37.7749, lon: -122.4194 }}
                    onAttackClick={handleAttackClick}
                    maxArcs={100}
                />

                {selectedAttack && (
                    <Paper sx={{ mt: 2, p: 3, bgcolor: '#1e1e1e' }}>
                        <Typography variant="h6" gutterBottom>Selected Attack Details</Typography>
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
                        </Box>
                    </Paper>
                )}
            </Box>
        </Box>
    );
};

export default AttackGlobePage;
