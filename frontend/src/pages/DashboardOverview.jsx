import { useState, useEffect, useCallback, useMemo } from 'react';
import { Box, CircularProgress } from '@mui/material';
import { toast } from 'react-toastify';
import StatsCards from '../components/StatsCards';
import AttackChart from '../components/AttackChart';
import GeoMap from '../components/GeoMap';
import ThreatScorePanel from '../components/ThreatScorePanel';
<<<<<<< HEAD
import AttackLogs from '../components/AttackLogs';
=======
import TelemetryTable from '../components/TelemetryTable';
>>>>>>> 5035a73d50efbedccaead6fb1e12408899a269ef
import Navbar from '../components/Navbar';
import FilterBadges from '../components/ui/FilterBadges';
import useAttackStore from '../stores/useAttackStore';
import { getDashboardStats, getAttackLogs, generateReport } from '../services/api';
import { downloadPDF } from '../utils/helpers';

const DashboardOverview = () => {
    const [stats, setStats] = useState({
        total_attempts: 0, malicious_attempts: 0, benign_attempts: 0,
        merkle_root: null, attack_distribution: {}, geo_locations: [],
        flagged_ips_count: 0, top_threats: []
    });
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(new Date());
    const [useMockGeo, setUseMockGeo] = useState(true);

    const { setAttacks, getFilteredAttacks, filters } = useAttackStore();

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

    const filteredLogs = useMemo(() => getFilteredAttacks(), [logs, filters, getFilteredAttacks]);

    const logsWithGeo = useMemo(() => {
        if (!useMockGeo) return filteredLogs;
        return filteredLogs.map((log, index) => {
            if (!log.geo_location || !log.geo_location.latitude) {
                return { ...log, geo_location: mockGeoLocations[index % mockGeoLocations.length] };
            }
            return log;
        });
    }, [filteredLogs, useMockGeo]);

    const filteredStats = useMemo(() => {
        const malicious = logsWithGeo.filter(log => log.classification?.attack_type !== 'BENIGN').length;
        const benign = logsWithGeo.filter(log => log.classification?.attack_type === 'BENIGN').length;
        const distribution = {};
        logsWithGeo.forEach(log => {
            const type = log.classification?.attack_type || 'UNKNOWN';
            distribution[type] = (distribution[type] || 0) + 1;
        });
        const geoMap = {};
        logsWithGeo.forEach(log => {
            if (log.geo_location?.country) {
                const key = `${log.geo_location.country}-${log.geo_location.city}`;
                if (!geoMap[key]) geoMap[key] = { ...log.geo_location, count: 0 };
                geoMap[key].count++;
            }
        });
        return {
            ...stats,
            total_attempts: logsWithGeo.length,
            malicious_attempts: malicious,
            benign_attempts: benign,
            attack_distribution: distribution,
            geo_locations: Object.values(geoMap).sort((a, b) => b.count - a.count)
        };
    }, [logsWithGeo, stats]);

    const fetchData = useCallback(async () => {
        try {
            const [statsData, logsData] = await Promise.all([
                getDashboardStats(),
                getAttackLogs(0, 100)
            ]);
            setStats(statsData);
            setLogs(logsData);
            setAttacks(logsData);
            setLastUpdated(new Date());
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            toast.error('Failed to fetch dashboard data');
            setAutoRefresh(false);
        } finally {
            setLoading(false);
        }
    }, [setAttacks]);

    useEffect(() => { fetchData(); }, [fetchData]);

    useEffect(() => {
        if (autoRefresh) {
            const interval = setInterval(fetchData, 10000);
            return () => clearInterval(interval);
        }
    }, [autoRefresh, fetchData]);

    const handleRefresh = () => { setLoading(true); fetchData(); };

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

    if (loading && !stats.total_attempts) {
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
                useMockGeo={useMockGeo}
                setUseMockGeo={setUseMockGeo}
            />

            <Box sx={{ px: 2, py: 3 }}>
                <FilterBadges />
                <StatsCards stats={filteredStats} />

                <Box sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' },
                    gap: '16px',
                    mb: 2,
                }}>
                    <Box sx={{ minHeight: 350 }}>
                        <AttackChart attackDistribution={filteredStats.attack_distribution} />
                    </Box>
                    <Box sx={{ minHeight: 350 }}>
                        <GeoMap geoLocations={filteredStats.geo_locations || []} />
                    </Box>
                    <Box sx={{ minHeight: 350 }}>
                        <ThreatScorePanel
                            topThreats={stats.top_threats || []}
                            flaggedCount={stats.flagged_ips_count || 0}
                        />
                    </Box>
                </Box>

<<<<<<< HEAD
                <AttackLogs
                    logs={filteredLogs}
                    onGenerateReport={handleGenerateReport}
=======
                <TelemetryTable
                    logs={filteredLogs}
                    onRefresh={handleRefresh}
                    loading={loading}
>>>>>>> 5035a73d50efbedccaead6fb1e12408899a269ef
                />
            </Box>
        </Box>
    );
};

export default DashboardOverview;
