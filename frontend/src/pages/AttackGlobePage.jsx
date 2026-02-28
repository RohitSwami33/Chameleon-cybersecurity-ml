import { useState, useEffect, useCallback } from 'react';
import { Box, CircularProgress, Typography, Switch, FormControlLabel } from '@mui/material';
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
            return { ...log, geo_location: mockGeoLocations[index % mockGeoLocations.length] };
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

    if (loading && logs.length === 0) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', backgroundColor: '#050810' }}>
                <CircularProgress sx={{ color: '#00d4ff' }} />
            </Box>
        );
    }

    return (
        <Box sx={{ flexGrow: 1, minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#050810' }}>
            <Box sx={{ zIndex: 20 }}>
                <Navbar
                    lastUpdated={lastUpdated}
                    autoRefresh={autoRefresh}
                    setAutoRefresh={setAutoRefresh}
                    onRefresh={handleRefresh}
                />
            </Box>

            <Box sx={{ flexGrow: 1, position: 'relative', minHeight: 'calc(100vh - 64px)' }}>
                <AttackGlobeSimple
                    attacks={logsWithGeo}
                    serverLocation={{ lat: 37.7749, lon: -122.4194 }}
                />

                <Box sx={{ position: 'absolute', bottom: 24, left: 24, zIndex: 10 }}>
                    <FormControlLabel
                        control={
                            <Switch checked={useMockGeo} onChange={(e) => setUseMockGeo(e.target.checked)} size="small"
                                sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color: '#00d4ff' }, '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#00d4ff' } }} />
                        }
                        label={<Typography variant="body2" sx={{ color: '#7a9bbf', fontSize: '0.8rem', fontWeight: 600 }}>USE MOCK GEO-DATA</Typography>}
                    />
                </Box>
            </Box>
        </Box>
    );
};

export default AttackGlobePage;
