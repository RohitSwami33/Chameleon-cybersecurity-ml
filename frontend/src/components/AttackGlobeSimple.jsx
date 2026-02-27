import { useMemo, useState } from 'react';
import { Box, Card, CardContent, Typography } from '@mui/material';

/**
 * Maps attack classification types to hex color codes
 */
const getAttackColor = (attackType) => {
    const colorMap = {
        'SQLI': '#ff4444',
        'XSS': '#ffaa00',
        'BRUTE_FORCE': '#ff8800',
        'SSI': '#4444ff',
        'BENIGN': '#888888'
    };
    return colorMap[attackType] || '#ffffff';
};

/**
 * Simple 2D Attack Map Component
 * A reliable alternative to the 3D globe using react-simple-maps
 */
const AttackGlobeSimple = ({
    attacks = [],
    serverLocation = { lat: 37.7749, lon: -122.4194 },
    onAttackClick,
    maxArcs = 100
}) => {
    // State for hover coordinates
    const [hoverCoords, setHoverCoords] = useState(null);

    // Process attacks
    const processedAttacks = useMemo(() => {
        return attacks
            .filter(attack => 
                attack.geo_location && 
                attack.geo_location.latitude && 
                attack.geo_location.longitude
            )
            .slice(0, maxArcs);
    }, [attacks, maxArcs]);

    const handleMarkerClick = (attack) => {
        if (typeof onAttackClick === 'function') {
            onAttackClick(attack);
        }
    };

    // Convert SVG coordinates to lat/lon
    const handleMouseMove = (e) => {
        const svg = e.currentTarget;
        const rect = svg.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Convert to viewBox coordinates
        const viewBoxX = (x / rect.width) * 1000;
        const viewBoxY = (y / rect.height) * 500;
        
        // Convert to lat/lon
        const lon = (viewBoxX / 1000) * 360 - 180;
        const lat = 90 - (viewBoxY / 500) * 180;
        
        setHoverCoords({ lat: lat.toFixed(2), lon: lon.toFixed(2) });
    };

    const handleMouseLeave = () => {
        setHoverCoords(null);
    };

    return (
        <Card sx={{ 
            bgcolor: '#1e1e1e', 
            borderRadius: 1, 
            border: '1px solid #333',
            mb: 2
        }}>
            <CardContent>
                <Box sx={{ mb: 2 }}>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                        Attack Map
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Real-time visualization of attack origins • {processedAttacks.length} active threats
                    </Typography>
                </Box>
                
                <Box sx={{ 
                    width: '100%', 
                    height: { xs: 400, sm: 500, md: 600 },
                    bgcolor: '#0a0a0a',
                    borderRadius: 1,
                    overflow: 'hidden',
                    position: 'relative'
                }}>
                    <svg
                        width="100%"
                        height="100%"
                        viewBox="0 0 1000 500"
                        style={{ background: 'radial-gradient(circle at 50% 50%, #1a2332 0%, #0a0a0a 100%)' }}
                        onMouseMove={handleMouseMove}
                        onMouseLeave={handleMouseLeave}
                    >
                        {/* Real World Map as background */}
                        <image
                            href="https://upload.wikimedia.org/wikipedia/commons/8/83/Equirectangular_projection_SW.jpg"
                            x="0"
                            y="0"
                            width="1000"
                            height="500"
                            opacity="0.3"
                            preserveAspectRatio="xMidYMid slice"
                        />
                        
                        {/* Filters */}
                        <defs>
                            <filter id="glow">
                                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                                <feMerge>
                                    <feMergeNode in="coloredBlur"/>
                                    <feMergeNode in="SourceGraphic"/>
                                </feMerge>
                            </filter>
                            <filter id="textGlow">
                                <feGaussianBlur stdDeviation="1" result="coloredBlur"/>
                                <feMerge>
                                    <feMergeNode in="coloredBlur"/>
                                    <feMergeNode in="SourceGraphic"/>
                                </feMerge>
                            </filter>
                        </defs>

                        {/* Hover coordinates display */}
                        {hoverCoords && (
                            <g>
                                <rect
                                    x="10"
                                    y="10"
                                    width="180"
                                    height="50"
                                    fill="rgba(0, 0, 0, 0.8)"
                                    stroke="#3a8fd9"
                                    strokeWidth="2"
                                    rx="5"
                                />
                                <text
                                    x="100"
                                    y="30"
                                    fill="#ffffff"
                                    fontSize="14"
                                    fontWeight="bold"
                                    textAnchor="middle"
                                >
                                    Latitude: {hoverCoords.lat}°
                                </text>
                                <text
                                    x="100"
                                    y="50"
                                    fill="#ffffff"
                                    fontSize="14"
                                    fontWeight="bold"
                                    textAnchor="middle"
                                >
                                    Longitude: {hoverCoords.lon}°
                                </text>
                            </g>
                        )}



                        {/* Grid lines */}
                        {[...Array(11)].map((_, i) => (
                            <line
                                key={`h-${i}`}
                                x1="0"
                                y1={i * 50}
                                x2="1000"
                                y2={i * 50}
                                stroke="#1a4d7a"
                                strokeWidth="0.5"
                                opacity="0.2"
                            />
                        ))}
                        {[...Array(21)].map((_, i) => (
                            <line
                                key={`v-${i}`}
                                x1={i * 50}
                                y1="0"
                                x2={i * 50}
                                y2="500"
                                stroke="#1a4d7a"
                                strokeWidth="0.5"
                                opacity="0.2"
                            />
                        ))}

                        {/* Convert lat/lon to SVG coordinates */}
                        {processedAttacks.map((attack, index) => {
                            const attackX = ((attack.geo_location.longitude + 180) / 360) * 1000;
                            const attackY = ((90 - attack.geo_location.latitude) / 180) * 500;
                            const serverX = ((serverLocation.lon + 180) / 360) * 1000;
                            const serverY = ((90 - serverLocation.lat) / 180) * 500;
                            const color = getAttackColor(attack.classification?.attack_type);

                            return (
                                <g key={`attack-${index}`}>
                                    {/* Animated line from attack to server */}
                                    <line
                                        x1={attackX}
                                        y1={attackY}
                                        x2={serverX}
                                        y2={serverY}
                                        stroke={color}
                                        strokeWidth="3"
                                        opacity="0.6"
                                        strokeDasharray="8,4"
                                        filter="url(#glow)"
                                    >
                                        <animate
                                            attributeName="stroke-dashoffset"
                                            from="0"
                                            to="12"
                                            dur="0.8s"
                                            repeatCount="indefinite"
                                        />
                                        <animate
                                            attributeName="opacity"
                                            values="0.3;0.8;0.3"
                                            dur="2s"
                                            repeatCount="indefinite"
                                        />
                                    </line>
                                    
                                    {/* Outer pulse ring */}
                                    <circle
                                        cx={attackX}
                                        cy={attackY}
                                        r="5"
                                        fill="none"
                                        stroke={color}
                                        strokeWidth="2"
                                        opacity="0"
                                    >
                                        <animate
                                            attributeName="r"
                                            values="5;15;25"
                                            dur="2s"
                                            repeatCount="indefinite"
                                        />
                                        <animate
                                            attributeName="opacity"
                                            values="0.8;0.4;0"
                                            dur="2s"
                                            repeatCount="indefinite"
                                        />
                                    </circle>
                                    
                                    {/* Attack marker */}
                                    <circle
                                        cx={attackX}
                                        cy={attackY}
                                        r="6"
                                        fill={color}
                                        stroke="#fff"
                                        strokeWidth="2"
                                        style={{ cursor: 'pointer' }}
                                        onClick={() => handleMarkerClick(attack)}
                                        filter="url(#glow)"
                                    >
                                        <title>
                                            {`${attack.geo_location.city}, ${attack.geo_location.country} - ${attack.classification?.attack_type}`}
                                        </title>
                                        <animate
                                            attributeName="r"
                                            values="6;8;6"
                                            dur="1.5s"
                                            repeatCount="indefinite"
                                        />
                                    </circle>
                                    
                                    {/* Country label - NO FILTER for clarity */}
                                    <text
                                        x={attackX}
                                        y={attackY - 18}
                                        fill="#ffffff"
                                        fontSize="12"
                                        fontWeight="bold"
                                        textAnchor="middle"
                                        style={{ 
                                            pointerEvents: 'none',
                                            textShadow: '1px 1px 3px #000, -1px -1px 3px #000',
                                            paintOrder: 'stroke fill'
                                        }}
                                        stroke="#000"
                                        strokeWidth="3"
                                        strokeLinejoin="round"
                                    >
                                        {attack.geo_location.country}
                                    </text>
                                </g>
                            );
                        })}

                        {/* Server marker with enhanced animations */}
                        <g>
                            {/* Outer rotating ring */}
                            <circle
                                cx={((serverLocation.lon + 180) / 360) * 1000}
                                cy={((90 - serverLocation.lat) / 180) * 500}
                                r="20"
                                fill="none"
                                stroke="#4a90e2"
                                strokeWidth="2"
                                strokeDasharray="4,4"
                                opacity="0.5"
                            >
                                <animateTransform
                                    attributeName="transform"
                                    type="rotate"
                                    from={`0 ${((serverLocation.lon + 180) / 360) * 1000} ${((90 - serverLocation.lat) / 180) * 500}`}
                                    to={`360 ${((serverLocation.lon + 180) / 360) * 1000} ${((90 - serverLocation.lat) / 180) * 500}`}
                                    dur="4s"
                                    repeatCount="indefinite"
                                />
                            </circle>
                            
                            {/* Pulse ring */}
                            <circle
                                cx={((serverLocation.lon + 180) / 360) * 1000}
                                cy={((90 - serverLocation.lat) / 180) * 500}
                                r="10"
                                fill="none"
                                stroke="#4a90e2"
                                strokeWidth="3"
                                opacity="0"
                            >
                                <animate
                                    attributeName="r"
                                    values="10;25;35"
                                    dur="2.5s"
                                    repeatCount="indefinite"
                                />
                                <animate
                                    attributeName="opacity"
                                    values="0.9;0.5;0"
                                    dur="2.5s"
                                    repeatCount="indefinite"
                                />
                            </circle>
                            
                            {/* Main server marker */}
                            <circle
                                cx={((serverLocation.lon + 180) / 360) * 1000}
                                cy={((90 - serverLocation.lat) / 180) * 500}
                                r="10"
                                fill="#4a90e2"
                                stroke="#fff"
                                strokeWidth="3"
                                filter="url(#glow)"
                            >
                                <animate
                                    attributeName="r"
                                    values="10;12;10"
                                    dur="2s"
                                    repeatCount="indefinite"
                                />
                            </circle>
                            
                            {/* Server label - Clear and bold */}
                            <text
                                x={((serverLocation.lon + 180) / 360) * 1000}
                                y={((90 - serverLocation.lat) / 180) * 500 + 35}
                                fill="#ffffff"
                                fontSize="14"
                                fontWeight="bold"
                                textAnchor="middle"
                                style={{ 
                                    textShadow: '2px 2px 4px #000',
                                    paintOrder: 'stroke fill'
                                }}
                                stroke="#000"
                                strokeWidth="3"
                                strokeLinejoin="round"
                            >
                                SERVER (SF)
                            </text>
                        </g>
                    </svg>
                </Box>

                <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1, textAlign: 'center' }}>
                        Showing attack origins and paths to server (San Francisco)
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ width: 12, height: 12, bgcolor: '#ff4444', borderRadius: '50%' }} />
                            <Typography variant="caption">SQL Injection</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ width: 12, height: 12, bgcolor: '#ffaa00', borderRadius: '50%' }} />
                            <Typography variant="caption">XSS</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ width: 12, height: 12, bgcolor: '#ff8800', borderRadius: '50%' }} />
                            <Typography variant="caption">Brute Force</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ width: 12, height: 12, bgcolor: '#4444ff', borderRadius: '50%' }} />
                            <Typography variant="caption">SSI</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ width: 12, height: 12, bgcolor: '#888888', borderRadius: '50%' }} />
                            <Typography variant="caption">Benign</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ width: 12, height: 12, bgcolor: '#4a90e2', borderRadius: '50%' }} />
                            <Typography variant="caption">Server (SF)</Typography>
                        </Box>
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );
};

export default AttackGlobeSimple;
