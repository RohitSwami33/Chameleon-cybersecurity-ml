import React from 'react';
import { Paper, Typography, Box, Chip } from '@mui/material';
import PublicIcon from '@mui/icons-material/Public';
import LocationOnIcon from '@mui/icons-material/LocationOn';

const WorldMap = ({ geoLocations }) => {
    // Calculate total attacks
    const totalAttacks = geoLocations.reduce((sum, loc) => sum + loc.count, 0);
    
    // Get country-wise stats
    const countryStats = {};
    geoLocations.forEach(loc => {
        const country = loc.country || 'Unknown';
        if (!countryStats[country]) {
            countryStats[country] = {
                count: 0,
                cities: new Set()
            };
        }
        countryStats[country].count += loc.count;
        if (loc.city) {
            countryStats[country].cities.add(loc.city);
        }
    });

    const topCountries = Object.entries(countryStats)
        .map(([country, data]) => ({
            country,
            count: data.count,
            cities: Array.from(data.cities)
        }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);

    return (
        <Paper
            sx={{
                p: 3,
                backgroundColor: '#1e1e1e',
                backgroundImage: 'none',
                border: '1px solid #333',
                borderRadius: 2,
            }}
        >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <PublicIcon sx={{ mr: 1, color: 'primary.main', fontSize: 28 }} />
                    <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
                        Global Attack Map
                    </Typography>
                </Box>
                <Chip 
                    label={`${totalAttacks} Total Attacks`}
                    sx={{ 
                        backgroundColor: 'rgba(244, 67, 54, 0.2)',
                        color: '#f44336',
                        fontWeight: 600,
                        border: '1px solid rgba(244, 67, 54, 0.3)',
                    }}
                />
            </Box>

            {geoLocations.length === 0 ? (
                <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'center', 
                    alignItems: 'center', 
                    minHeight: 300,
                    border: '2px dashed #333',
                    borderRadius: 2
                }}>
                    <Box sx={{ textAlign: 'center' }}>
                        <PublicIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h6" color="text.secondary">
                            No Geographic Data Available
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            Attack locations will appear here once detected
                        </Typography>
                    </Box>
                </Box>
            ) : (
                <Box>
                    {/* World Map Visualization */}
                    <Box sx={{ 
                        position: 'relative',
                        minHeight: 400,
                        backgroundColor: '#0a1929',
                        borderRadius: 2,
                        border: '1px solid #1e3a5f',
                        overflow: 'hidden',
                        mb: 3
                    }}>
                        {/* Map Background */}
                        <Box sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(25, 118, 210, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(244, 67, 54, 0.1) 0%, transparent 50%)',
                        }} />
                        
                        {/* Attack Markers */}
                        <Box sx={{ position: 'relative', height: 400, p: 3 }}>
                            {geoLocations.slice(0, 20).map((location, index) => {
                                // Simple positioning based on lat/long (simplified projection)
                                const x = location.longitude ? ((location.longitude + 180) / 360) * 100 : Math.random() * 100;
                                const y = location.latitude ? ((90 - location.latitude) / 180) * 100 : Math.random() * 100;
                                
                                return (
                                    <Box
                                        key={index}
                                        sx={{
                                            position: 'absolute',
                                            left: `${x}%`,
                                            top: `${y}%`,
                                            transform: 'translate(-50%, -50%)',
                                            animation: `pulse 2s ease-in-out infinite ${index * 0.1}s`,
                                            '@keyframes pulse': {
                                                '0%, 100%': {
                                                    opacity: 0.6,
                                                    transform: 'translate(-50%, -50%) scale(1)',
                                                },
                                                '50%': {
                                                    opacity: 1,
                                                    transform: 'translate(-50%, -50%) scale(1.2)',
                                                },
                                            },
                                        }}
                                    >
                                        <Box
                                            sx={{
                                                width: Math.min(20 + location.count * 2, 40),
                                                height: Math.min(20 + location.count * 2, 40),
                                                borderRadius: '50%',
                                                backgroundColor: 'rgba(244, 67, 54, 0.6)',
                                                border: '2px solid #f44336',
                                                boxShadow: '0 0 20px rgba(244, 67, 54, 0.8)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                cursor: 'pointer',
                                                '&:hover': {
                                                    backgroundColor: 'rgba(244, 67, 54, 0.9)',
                                                    transform: 'scale(1.3)',
                                                    zIndex: 10,
                                                },
                                            }}
                                            title={`${location.city || 'Unknown'}, ${location.country || 'Unknown'} - ${location.count} attacks`}
                                        >
                                            <Typography variant="caption" sx={{ fontWeight: 700, color: 'white', fontSize: '0.7rem' }}>
                                                {location.count}
                                            </Typography>
                                        </Box>
                                    </Box>
                                );
                            })}
                        </Box>
                    </Box>

                    {/* Country Statistics */}
                    <Box>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                            Top Attack Sources by Country
                        </Typography>
                        <Box sx={{ 
                            display: 'grid', 
                            gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                            gap: 2
                        }}>
                            {topCountries.map((country, index) => (
                                <Box
                                    key={index}
                                    sx={{
                                        p: 2,
                                        borderRadius: 1,
                                        backgroundColor: 'rgba(255, 255, 255, 0.03)',
                                        border: '1px solid rgba(255, 255, 255, 0.05)',
                                        transition: 'all 0.2s',
                                        '&:hover': {
                                            backgroundColor: 'rgba(255, 255, 255, 0.05)',
                                            border: '1px solid rgba(244, 67, 54, 0.3)',
                                            transform: 'translateY(-2px)',
                                        },
                                    }}
                                >
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <LocationOnIcon sx={{ color: '#f44336', fontSize: 20 }} />
                                            <Typography variant="body1" sx={{ fontWeight: 600 }}>
                                                {country.country}
                                            </Typography>
                                        </Box>
                                        <Chip
                                            label={country.count}
                                            size="small"
                                            sx={{
                                                backgroundColor: 'rgba(244, 67, 54, 0.2)',
                                                color: '#f44336',
                                                fontWeight: 700,
                                                minWidth: 45,
                                            }}
                                        />
                                    </Box>
                                    {country.cities.length > 0 && (
                                        <Typography variant="caption" color="text.secondary">
                                            Cities: {country.cities.slice(0, 3).join(', ')}
                                            {country.cities.length > 3 && ` +${country.cities.length - 3} more`}
                                        </Typography>
                                    )}
                                </Box>
                            ))}
                        </Box>
                    </Box>
                </Box>
            )}
        </Paper>
    );
};

export default WorldMap;
