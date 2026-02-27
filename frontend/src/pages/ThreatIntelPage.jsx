import { useState, useEffect, useCallback } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { toast } from 'react-toastify';
import Navbar from '../components/Navbar';
import ThreatIntelFeed from '../components/ThreatIntelFeed';

const ThreatIntelPage = () => {
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(new Date());
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const handleRefresh = () => {
        setRefreshTrigger(prev => prev + 1);
        setLastUpdated(new Date());
        toast.info('Refreshing threat intelligence...');
    };

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
                    Threat Intelligence Feed
                </Typography>

                <ThreatIntelFeed key={refreshTrigger} />
            </Box>
        </Box>
    );
};

export default ThreatIntelPage;
