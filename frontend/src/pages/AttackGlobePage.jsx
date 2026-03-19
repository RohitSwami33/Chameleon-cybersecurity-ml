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
        { country: 'Canada', city: 'Toronto', latitude: 43.6532, longitude: -79.3832 },
        { country: 'South Korea', city: 'Seoul', latitude: 37.5665, longitude: 126.9780 },
        { country: 'Netherlands', city: 'Amsterdam', latitude: 52.3676, longitude: 4.9041 },
        { country: 'Singapore', city: 'Singapore', latitude: 1.3521, longitude: 103.8198 },
        { country: 'Turkey', city: 'Istanbul', latitude: 41.0082, longitude: 28.9784 },
    ];

    const logsWithGeo = useMockGeo ? logs.map((log, index) => {
        if (!log.geo_location || !log.geo_location.latitude) {
            return { ...log, geo_location: mockGeoLocations[index % mockGeoLocations.length] };
        }
        return log;
    }) : logs;

    // Generate synthetic attacks when DB is empty so the globe isn't blank
    const displayAttacks = logsWithGeo.length > 0 ? logsWithGeo : mockGeoLocations.map((geo, i) => ({
        id: `mock-${i}`,
        timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
        ip_address: `${Math.floor(Math.random()*255)}.${Math.floor(Math.random()*255)}.${Math.floor(Math.random()*255)}.${Math.floor(Math.random()*255)}`,
        geo_location: geo,
        classification: {
            attack_type: ['SQLI', 'XSS', 'SSI', 'BRUTE_FORCE', 'BENIGN'][Math.floor(Math.random() * 5)],
            confidence: Math.random(),
            is_malicious: Math.random() > 0.3,
        }
    }));

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

    return (
        <Box sx={{ 
            flexGrow: 1, 
            minHeight: '100vh', 
            display: 'flex', 
            flexDirection: 'column', 
            backgroundColor: '#050810' 
        }}>
            <Box sx={{ zIndex: 20, flexShrink: 0 }}>
                <Navbar
                    lastUpdated={lastUpdated}
                    autoRefresh={autoRefresh}
                    setAutoRefresh={setAutoRefresh}
                    onRefresh={handleRefresh}
                    useMockGeo={useMockGeo}
                    setUseMockGeo={setUseMockGeo}
                />
            </Box>

            {/* Globe container — must have explicit height for the SVG to render */}
            <Box sx={{ 
                flexGrow: 1, 
                position: 'relative', 
                height: 'calc(100vh - 76px)',   /* navbar height ~76px with padding */
                minHeight: 500,
            }}>
                {loading && logs.length === 0 ? (
                    <Box sx={{ 
                        display: 'flex', 
                        justifyContent: 'center', 
                        alignItems: 'center', 
                        height: '100%' 
                    }}>
                        <CircularProgress sx={{ color: '#ff2a2a' }} />
                    </Box>
                ) : (
                    <AttackGlobeSimple
                        attacks={displayAttacks}
                        serverLocation={{ lat: 37.7749, lon: -122.4194 }}
                    />
                )}

                <Box sx={{ position: 'absolute', bottom: 24, left: 24, zIndex: 10 }}>
                    <FormControlLabel
                        control={
                            <Switch checked={useMockGeo} onChange={(e) => setUseMockGeo(e.target.checked)} size="small"
                                sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color: '#ff2a2a' }, '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#ff2a2a' } }} />
                        }
                        label={<Typography variant="body2" sx={{ color: '#7a9bbf', fontSize: '0.8rem', fontWeight: 600 }}>USE MOCK GEO-DATA</Typography>}
                    />
                </Box>
            </Box>
        </Box>
    );
};

export default AttackGlobePage;
