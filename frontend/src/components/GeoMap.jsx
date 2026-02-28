import React from 'react';
import { Paper, Typography, Box, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import PublicIcon from '@mui/icons-material/Public';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import TiltCard from './TiltCard';

/**
 * GeoMap — List mode: scrollable attack origin cards
 * @see Section 3 — WorldMap/GeoMap Rules (List Mode)
 */
const GeoMap = ({ geoLocations }) => {
    const topLocations = geoLocations.slice(0, 10);

    return (
        <TiltCard
            glowColor="#00d4ff"
            sx={{
                p: '20px',
                height: '100%',
                backgroundColor: 'rgba(10, 15, 30, 0.85)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(0, 212, 255, 0.08)',
                borderRadius: '12px',
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PublicIcon sx={{ mr: 1, color: '#00d4ff', fontSize: 22 }} />
                <Typography variant="h6" component="h2" sx={{ fontWeight: 600, fontSize: '0.95rem', color: '#e8f4fd' }}>
                    Attack Origins
                </Typography>
            </Box>

            {topLocations.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
                    <Typography variant="body2" sx={{ color: '#3d5a7a' }}>
                        No geographic data available
                    </Typography>
                </Box>
            ) : (
                <Box sx={{ flexGrow: 1, overflowY: 'auto', pr: 0.5 }}>
                    {topLocations.map((location, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.05 }}
                        >
                            <Box
                                sx={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    py: 1.2,
                                    px: 1.5,
                                    mb: 0.8,
                                    borderRadius: '8px',
                                    backgroundColor: 'rgba(10, 15, 30, 0.5)',
                                    border: '1px solid rgba(0, 212, 255, 0.04)',
                                    transition: 'all 0.2s',
                                    '&:hover': {
                                        backgroundColor: 'rgba(0, 212, 255, 0.04)',
                                        borderColor: 'rgba(0, 212, 255, 0.15)',
                                    },
                                }}
                            >
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                                    <LocationOnIcon sx={{ color: '#ff3d71', fontSize: 18 }} />
                                    <Box>
                                        <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.8rem', color: '#e8f4fd' }}>
                                            {location.city || 'Unknown City'}, {location.country || 'Unknown'}
                                        </Typography>
                                        {location.latitude && location.longitude && (
                                            <Typography variant="caption" sx={{
                                                color: '#3d5a7a',
                                                fontFamily: '"IBM Plex Mono", monospace',
                                                fontSize: '0.65rem',
                                            }}>
                                                {location.latitude.toFixed(2)}°, {location.longitude.toFixed(2)}°
                                            </Typography>
                                        )}
                                    </Box>
                                </Box>
                                <Chip
                                    label={`${location.count}`}
                                    size="small"
                                    sx={{
                                        backgroundColor: 'rgba(255, 61, 113, 0.12)',
                                        color: '#ff3d71',
                                        fontWeight: 700,
                                        fontFamily: '"Rajdhani", sans-serif',
                                        fontSize: '0.8rem',
                                        border: '1px solid rgba(255, 61, 113, 0.2)',
                                        minWidth: 36,
                                        height: 24,
                                        borderRadius: '12px',
                                    }}
                                />
                            </Box>
                        </motion.div>
                    ))}
                </Box>
            )}

            {topLocations.length > 0 && (
                <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px solid rgba(0, 212, 255, 0.06)' }}>
                    <Typography variant="caption" sx={{ color: '#3d5a7a', fontSize: '0.7rem' }}>
                        Showing top {topLocations.length} attack locations
                    </Typography>
                </Box>
            )}
        </TiltCard>
    );
};

export default GeoMap;
