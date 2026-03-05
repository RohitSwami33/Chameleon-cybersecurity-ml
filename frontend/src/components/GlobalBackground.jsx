import React, { useMemo } from 'react';
import { Box } from '@mui/material';

/**
 * GlobalBackground — Atmospheric background effect
 * Includes CSS-only TRON grid, floating particles, vignette, and SVG noise
 * Renders behind all dashboard pages (z-index: 0)
 */
const GlobalBackground = () => {
    // Generate static random values for ambient particles
    const particles = useMemo(() => {
        return Array.from({ length: 30 }).map((_, i) => ({
            id: i,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDuration: `${8 + Math.random() * 12}s`,
            animationDelay: `-${Math.random() * 20}s`,
            opacity: 0.15 + Math.random() * 0.15,
        }));
    }, []);

    return (
        <Box sx={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', overflow: 'hidden' }}>
            {/* TRON Perspective Grid Floor */}
            <Box className="grid-floor" />

            {/* Ambient Particles */}
            {particles.map((p) => (
                <Box
                    key={p.id}
                    className="ambient-particle"
                    sx={{
                        left: p.left,
                        top: p.top,
                        animationDuration: p.animationDuration,
                        animationDelay: p.animationDelay,
                        opacity: p.opacity,
                    }}
                />
            ))}

            {/* Subtle Noise Texture (SVG filter) */}
            <svg style={{ position: 'absolute', width: 0, height: 0 }}>
                <filter id="noiseFilter">
                    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch" />
                </filter>
            </svg>
            <Box
                sx={{
                    position: 'absolute',
                    inset: 0,
                    opacity: 0.03,
                    mixBlendMode: 'overlay',
                    filter: 'url(#noiseFilter)',
                }}
            />

            {/* Vignette Edge Shading */}
            <Box className="vignette" />
        </Box>
    );
};

export default GlobalBackground;
