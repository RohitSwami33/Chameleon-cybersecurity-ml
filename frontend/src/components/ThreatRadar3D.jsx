import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography } from '@mui/material';

const ThreatRadar3D = ({ feed = [] }) => {
    const [pings, setPings] = useState([]);
    const prevFeedRef = useRef([]);

    useEffect(() => {
        // Find newly added items
        const newItems = feed.filter(f => !prevFeedRef.current.some(p => p.pattern_hash === f.pattern_hash));
        prevFeedRef.current = feed;

        // Take up to 5 items to spawn immediately
        const itemsToPing = newItems.length > 0 ? newItems.slice(0, 5) : feed.slice(0, 3);

        if (itemsToPing.length > 0) {
            const addedPings = itemsToPing.map((threat, idx) => {
                let color = '#00d4ff';
                if (threat.attack_type === 'SQLI' || threat.severity === 'CRITICAL') color = '#ff3d71';
                else if (threat.attack_type === 'XSS' || threat.severity === 'MEDIUM') color = '#ffab00';
                else if (threat.severity === 'HIGH') color = '#ff6584';
                else if (threat.severity === 'LOW') color = '#00e676';

                const angle = Math.random() * Math.PI * 2;
                const r = Math.random() * 50 + 10; // 10 to 60 radius
                const top = 80 + Math.sin(angle) * r;
                const left = 80 + Math.cos(angle) * r;

                return {
                    id: (threat.pattern_hash || '') + Date.now() + Math.random(),
                    top, left, color,
                    delay: idx * 800
                };
            });

            addedPings.forEach(p => {
                setTimeout(() => {
                    setPings(prev => [...prev, p]);
                    setTimeout(() => {
                        setPings(prev => prev.filter(x => x.id !== p.id));
                    }, 8000); // persis for 8s
                }, p.delay);
            });
        }
    }, [feed]);

    // Secondary effect: spawn ambient random pings periodically based on feed volume to look alive
    useEffect(() => {
        if (feed.length === 0) return;
        const interval = setInterval(() => {
            const threat = feed[Math.floor(Math.random() * feed.length)];
            let color = '#00d4ff'; // default dim
            if (threat.attack_type === 'SQLI' || threat.severity === 'CRITICAL') color = '#ff3d71';
            else if (threat.attack_type === 'XSS' || threat.severity === 'MEDIUM') color = '#ffab00';
            else if (threat.severity === 'HIGH') color = '#ff6584'; // bright
            else if (threat.severity === 'LOW') color = '#206b4b'; // dim

            const angle = Math.random() * Math.PI * 2;
            const r = Math.random() * 60 + 10;
            const top = 80 + Math.sin(angle) * r;
            const left = 80 + Math.cos(angle) * r;

            const p = { id: Date.now() + Math.random(), top, left, color };
            setPings(prev => [...prev, p]);
            setTimeout(() => {
                setPings(prev => prev.filter(x => x.id !== p.id));
            }, 8000);
        }, 2500);
        return () => clearInterval(interval);
    }, [feed]);

    return (
        <Box sx={{ width: 180, height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <style>{`
                @keyframes radarSweep { 
                    from { transform: rotate(0deg); } 
                    to { transform: rotate(360deg); } 
                }
                @keyframes radarPingRipple { 
                    0% { transform: scale(1); opacity: 1; } 
                    100% { transform: scale(3); opacity: 0; } 
                }
                @keyframes radarFadeInOut { 
                    0% { opacity: 0; } 
                    5% { opacity: 1; } 
                    90% { opacity: 1; } 
                    100% { opacity: 0; } 
                }
            `}</style>

            <Box sx={{
                width: 160, height: 160,
                borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(0,212,255,0.05) 0%, transparent 70%)',
                border: '1px solid rgba(0,212,255,0.2)',
                position: 'relative',
                overflow: 'hidden'
            }}>
                <Box sx={{
                    position: 'absolute',
                    width: '50%', height: '50%',
                    top: '50%', left: '50%',
                    transformOrigin: '0% 0%',
                    background: 'conic-gradient(from 0deg, transparent 300deg, rgba(0,212,255,0.4) 360deg)',
                    borderRadius: '0 100% 0 0',
                    animation: 'radarSweep 3s linear infinite'
                }} />

                {/* Rings */}
                {[33, 66, 100].map(pct => (
                    <Box key={pct} sx={{
                        position: 'absolute',
                        top: `${50 - pct / 2}%`, left: `${50 - pct / 2}%`,
                        width: `${pct}%`, height: `${pct}%`,
                        borderRadius: '50%',
                        border: '1px dashed rgba(0,212,255,0.15)',
                        pointerEvents: 'none'
                    }} />
                ))}

                {/* Center dot */}
                <Box sx={{
                    position: 'absolute', top: '50%', left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: 4, height: 4, backgroundColor: '#00d4ff',
                    borderRadius: '50%', zIndex: 10
                }} />

                {/* Counter Badge */}
                <Box sx={{
                    position: 'absolute', top: '50%', left: '50%',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 11, mt: 2.5
                }}>
                    <Typography sx={{
                        fontFamily: '"Orbitron", sans-serif', fontWeight: 700,
                        color: '#00d4ff', fontSize: '0.9rem',
                        textShadow: '0 0 8px rgba(0,212,255,0.8)'
                    }}>
                        {feed.length}
                    </Typography>
                </Box>

                {/* Pings */}
                {pings.map(ping => (
                    <Box key={ping.id} sx={{
                        position: 'absolute',
                        top: ping.top, left: ping.left,
                        width: 6, height: 6,
                        backgroundColor: ping.color,
                        borderRadius: '50%',
                        transform: 'translate(-50%, -50%)',
                        boxShadow: `0 0 6px ${ping.color}`,
                        animation: 'radarFadeInOut 8s ease-in-out forwards',
                        zIndex: 5
                    }}>
                        <Box sx={{
                            position: 'absolute',
                            top: -2, left: -2, width: 10, height: 10,
                            borderRadius: '50%',
                            border: `2px solid ${ping.color}`,
                            animation: 'radarPingRipple 1s ease-out infinite'
                        }} />
                    </Box>
                ))}
            </Box>
        </Box>
    );
};
export default ThreatRadar3D;
