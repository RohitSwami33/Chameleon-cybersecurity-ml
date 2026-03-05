import React from 'react';
import { motion } from 'framer-motion';
import { Box } from '@mui/material';
import { useMagneticTilt } from '../hooks/useMagneticTilt';

function TiltCard({ children, strength = 12, glowColor = '#00d4ff', style = {}, sx = {}, ...props }) {
    const { ref, transform, handleMouseMove, handleMouseLeave, glarePosition } = useMagneticTilt(strength);

    return (
        <Box
            component={motion.div}
            ref={ref}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            sx={{
                ...sx,
                '&:hover': {
                    boxShadow: `0 20px 60px ${glowColor}22, 0 0 0 1px ${glowColor}33`,
                    zIndex: 10,
                    ...(sx['&:hover'] || {})
                }
            }}
            style={{
                ...style,
                position: 'relative',
                transform,
                transition: 'transform 0.15s ease-out, box-shadow 0.15s ease-out',
                transformStyle: 'preserve-3d',
                willChange: 'transform',
                borderRadius: '12px',
            }}
            {...props}
        >
            {/* The child card goes here, raised above the glare visually if needed */}
            {children}

            {/* Glare overlay */}
            <Box style={{
                position: 'absolute',
                inset: 0,
                borderRadius: 'inherit',
                background: `radial-gradient(circle at ${glarePosition.x}% ${glarePosition.y}%, rgba(255,255,255,0.06) 0%, transparent 40%)`,
                opacity: glarePosition.opacity,
                pointerEvents: 'none',
                zIndex: 10,
                transition: 'opacity 0.2s',
            }} />
        </Box>
    );
}

export default TiltCard;
