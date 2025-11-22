import React from 'react';
import { Paper, Typography, Box, Chip } from '@mui/material';
import PublicIcon from '@mui/icons-material/Public';
import LocationOnIcon from '@mui/icons-material/LocationOn';

const GeoMap = ({ geoLocations }) => {
    // Get top 10 locations
    const topLocations = geoLocations.slice(0, 10);

    return (
        <Paper
            sx={{
                p: 3,
                height: '100%',
                backgroundColor: '#1e1e1e',
                backgroundImage: 'none',
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PublicIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
                    Attack Origins
                </Typography>
            </Box>

            {topLocations.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                        No geographic data available
                    </Typography>
                </Box>
            ) : (
                <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
                    {topLocations.map((location, index) => (
                        <Box
                            key={index}
                            sx={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                py: 1.5,
                                px: 2,
                                mb: 1,
                                borderRadius: 1,
                                backgroundColor: 'rgba(255, 255, 255, 0.03)',
                                border: '1px solid rgba(255, 255, 255, 0.05)',
                                transition: 'all 0.2s',
                                '&:hover': {
                                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                                    border: '1px solid rgba(25, 118, 210, 0.3)',
                                },
                            }}
                        >
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                                <LocationOnIcon sx={{ color: '#f44336', fontSize: 20 }} />
                                <Box>
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                        {location.city || 'Unknown City'}, {location.country || 'Unknown'}
                                    </Typography>
                                    {location.latitude && location.longitude && (
                                        <Typography variant="caption" color="text.secondary">
                                            {location.latitude.toFixed(2)}°, {location.longitude.toFixed(2)}°
                                        </Typography>
                                    )}
                                </Box>
                            </Box>
                            <Chip
                                label={`${location.count} attacks`}
                                size="small"
                                sx={{
                                    backgroundColor: 'rgba(244, 67, 54, 0.2)',
                                    color: '#f44336',
                                    fontWeight: 600,
                                    border: '1px solid rgba(244, 67, 54, 0.3)',
                                }}
                            />
                        </Box>
                    ))}
                </Box>
            )}

            {topLocations.length > 0 && (
                <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                    <Typography variant="caption" color="text.secondary">
                        Showing top {topLocations.length} attack locations
                    </Typography>
                </Box>
            )}
        </Paper>
    );
};

export default GeoMap;
