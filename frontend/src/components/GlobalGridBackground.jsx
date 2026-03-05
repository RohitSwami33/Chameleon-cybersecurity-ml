import { Box } from '@mui/material';

/**
 * GlobalGridBackground — subtle background grid
 * Placed behind all content, adding a cyber-forensics texture
 */
const GlobalGridBackground = () => (
    <Box
        sx={{
            position: 'fixed',
            inset: 0,
            zIndex: 1,
            pointerEvents: 'none',
            backgroundImage: `
                linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
            backgroundPosition: 'center center',
            maskImage: 'radial-gradient(ellipse at center, rgba(0,0,0,1) 10%, rgba(0,0,0,0) 80%)',
            WebkitMaskImage: 'radial-gradient(ellipse at center, rgba(0,0,0,1) 10%, rgba(0,0,0,0) 80%)',
        }}
    />
);

export default GlobalGridBackground;
