import { useState, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    Box,
    Typography,
    IconButton,
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Switch,
    FormControlLabel,
    Divider,
    Tooltip,
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PublicIcon from '@mui/icons-material/Public';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SecurityIcon from '@mui/icons-material/Security';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import LinkIcon from '@mui/icons-material/Link';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import { CommandBarTrigger } from './ui/CommandBar';
import { toast } from 'react-toastify';

/* ─── Shield SVG brand icon ─────────────────────────────────────────────── */
const ShieldSVG = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ filter: 'drop-shadow(0 0 6px rgba(0,212,255,0.7))' }}
    >
        <path
            d="M12 2L3 6v6c0 5.25 3.75 10.15 9 11.25C17.25 22.15 21 17.25 21 12V6L12 2z"
            fill="rgba(0,212,255,0.15)"
            stroke="#00d4ff"
            strokeWidth="1.5"
            strokeLinejoin="round"
        />
        <path
            d="M9 12l2 2 4-4"
            stroke="#00d4ff"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
        />
    </svg>
);

/* ─── Nav item definitions ───────────────────────────────────────────────── */
const NAV_ITEMS = [
    { path: '/dashboard', label: 'Overview', Icon: DashboardIcon },
    { path: '/dashboard/globe', label: 'Attack Globe', Icon: PublicIcon },
    { path: '/dashboard/analytics', label: 'Analytics', Icon: AssessmentIcon },
    { path: '/dashboard/threat-intel', label: 'Threat Intel', Icon: SecurityIcon },
    { path: '/dashboard/chatbot', label: 'AI Assistant', Icon: SmartToyIcon },
    { path: '/blockchain', label: 'Blockchain', Icon: LinkIcon },
];

/* ─── Shared style tokens ────────────────────────────────────────────────── */
const NAV_FONT = '"IBM Plex Mono", monospace';
const BRAND_FONT = '"Orbitron", sans-serif';
const CYAN = '#00d4ff';
const AMBER = '#ffab00';
const MUTED = 'rgba(232, 244, 253, 0.7)';

/* ════════════════════════════════════════════════════════════════════════════
   NAVBAR COMPONENT
   ════════════════════════════════════════════════════════════════════════════ */
const Navbar = ({
    lastUpdated,
    autoRefresh,
    setAutoRefresh,
    onRefresh,
    useMockGeo,
    setUseMockGeo,
}) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [drawerOpen, setDrawerOpen] = useState(false);

    const isActive = (path) => {
        if (path === '/dashboard') return location.pathname === '/dashboard';
        return location.pathname === path || location.pathname.startsWith(path + '/');
    };

    const handleLogout = () => {
        localStorage.removeItem('authToken');
        toast.info('Session terminated');
        navigate('/login');
    };

    /* ── Framer Motion variants ── */
    const navbarVariants = {
        hidden: { opacity: 0, y: -20 },
        visible: {
            opacity: 1,
            y: 0,
            transition: { duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] },
        },
    };

    return (
        <>
            {/* ── Floating pill wrapper ─────────────────────────────────── */}
            <Box
                sx={{
                    position: 'sticky',
                    top: 0,
                    zIndex: 1300,
                    /* give a little breathing room above so the pill floats */
                    pt: '12px',
                    px: '12px',
                    pb: 0,
                    pointerEvents: 'none',   /* let clicks pass through the gutter */
                }}
            >
                <motion.div
                    variants={navbarVariants}
                    initial="hidden"
                    animate="visible"
                    style={{ pointerEvents: 'auto' }}
                >
                    <Box
                        sx={{
                            maxWidth: 960,
                            mx: 'auto',
                            height: 52,
                            borderRadius: '999px',
                            background: 'rgba(8, 14, 28, 0.75)',
                            backdropFilter: 'blur(24px) saturate(180%)',
                            WebkitBackdropFilter: 'blur(24px) saturate(180%)',
                            border: '1px solid rgba(0, 212, 255, 0.12)',
                            boxShadow: '0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(0,212,255,0.05)',
                            display: 'flex',
                            alignItems: 'center',
                            px: '24px',
                            gap: 1.5,
                        }}
                    >
                        {/* ── BRAND ─────────────────────────────────────── */}
                        <Box
                            onClick={() => navigate('/dashboard')}
                            sx={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                cursor: 'pointer',
                                flexShrink: 0,
                                userSelect: 'none',
                            }}
                        >
                            <ShieldSVG />
                            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: '4px', whiteSpace: 'nowrap' }}>
                                <Typography
                                    sx={{
                                        fontFamily: BRAND_FONT,
                                        fontWeight: 700,
                                        fontSize: '13px',
                                        lineHeight: 1,
                                        color: '#ffffff',
                                        letterSpacing: '0.06em',
                                    }}
                                >
                                    CHAMELEON
                                </Typography>
                                <Typography
                                    sx={{
                                        fontFamily: BRAND_FONT,
                                        fontWeight: 400,
                                        fontSize: '13px',
                                        lineHeight: 1,
                                        color: CYAN,
                                        letterSpacing: '0.06em',
                                    }}
                                >
                                    FORENSICS
                                </Typography>
                            </Box>
                        </Box>

                        {/* ── ALWAYS-VISIBLE HAMBURGER (all screen sizes) ── */}
                        <Box
                            sx={{
                                display: 'flex',
                                ml: 'auto',
                                alignItems: 'center',
                                gap: '8px',
                            }}
                        >
                            <IconButton
                                onClick={() => setDrawerOpen(prev => !prev)}
                                size="small"
                                sx={{
                                    color: CYAN,
                                    border: `1px solid rgba(0,212,255,0.2)`,
                                    borderRadius: '999px',
                                    width: 32,
                                    height: 32,
                                    transition: 'background-color 0.2s, transform 0.2s',
                                    transform: drawerOpen ? 'rotate(90deg)' : 'rotate(0deg)',
                                    '&:hover': { backgroundColor: 'rgba(0,212,255,0.08)' },
                                }}
                            >
                                {drawerOpen
                                    ? <CloseIcon sx={{ fontSize: 18 }} />
                                    : <MenuIcon sx={{ fontSize: 18 }} />
                                }
                            </IconButton>
                        </Box>
                    </Box>
                </motion.div>
            </Box>

            {/* ── MOBILE DRAWER ────────────────────────────────────────────── */}
            <Drawer
                anchor="right"
                open={drawerOpen}
                onClose={() => setDrawerOpen(false)}
                PaperProps={{
                    sx: {
                        width: 280,
                        background: 'rgba(8, 14, 28, 0.95)',
                        backdropFilter: 'blur(24px) saturate(180%)',
                        WebkitBackdropFilter: 'blur(24px) saturate(180%)',
                        border: 'none',
                        borderLeft: '1px solid rgba(0,212,255,0.12)',
                        backgroundImage: 'none',
                    },
                }}
            >
                {/* Drawer header */}
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        px: 2.5,
                        py: 2,
                        borderBottom: '1px solid rgba(0,212,255,0.08)',
                    }}
                >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <ShieldSVG />
                        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
                            <Typography
                                sx={{
                                    fontFamily: BRAND_FONT,
                                    fontWeight: 700,
                                    fontSize: '13px',
                                    color: '#ffffff',
                                    letterSpacing: '0.06em',
                                }}
                            >
                                CHAMELEON
                            </Typography>
                            <Typography
                                sx={{
                                    fontFamily: BRAND_FONT,
                                    fontSize: '13px',
                                    color: CYAN,
                                    letterSpacing: '0.06em',
                                }}
                            >
                                FORENSICS
                            </Typography>
                        </Box>
                    </Box>
                    <IconButton
                        onClick={() => setDrawerOpen(false)}
                        size="small"
                        sx={{ color: MUTED, '&:hover': { color: '#fff' } }}
                    >
                        <CloseIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                </Box>

                {/* Drawer nav items */}
                <List sx={{ pt: 1 }}>
                    {NAV_ITEMS.map(({ path, label, Icon }) => {
                        const active = isActive(path);
                        return (
                            <ListItem key={path} disablePadding>
                                <ListItemButton
                                    onClick={() => { navigate(path); setDrawerOpen(false); }}
                                    sx={{
                                        mx: 1,
                                        my: 0.25,
                                        borderRadius: '12px',
                                        backgroundColor: active ? 'rgba(0,212,255,0.08)' : 'transparent',
                                        borderLeft: active ? `3px solid ${CYAN}` : '3px solid transparent',
                                        '&:hover': { backgroundColor: 'rgba(0,212,255,0.05)' },
                                    }}
                                >
                                    <ListItemIcon sx={{ color: active ? CYAN : MUTED, minWidth: 36 }}>
                                        <Icon sx={{ fontSize: 18 }} />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={label}
                                        primaryTypographyProps={{
                                            sx: {
                                                fontFamily: NAV_FONT,
                                                fontSize: '11px',
                                                letterSpacing: '0.05em',
                                                textTransform: 'uppercase',
                                                color: active ? CYAN : MUTED,
                                                fontWeight: active ? 600 : 400,
                                            },
                                        }}
                                    />
                                </ListItemButton>
                            </ListItem>
                        );
                    })}
                </List>

                <Divider sx={{ borderColor: 'rgba(0,212,255,0.08)', mx: 2, my: 1 }} />

                {/* Drawer controls */}
                <Box sx={{ px: 2.5, display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {setAutoRefresh && (
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={autoRefresh}
                                    onChange={(e) => setAutoRefresh(e.target.checked)}
                                    size="small"
                                    sx={{
                                        '& .MuiSwitch-switchBase.Mui-checked': { color: CYAN },
                                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: CYAN },
                                    }}
                                />
                            }
                            label={
                                <Typography sx={{ fontFamily: NAV_FONT, fontSize: '11px', color: MUTED, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                                    Live Updates
                                </Typography>
                            }
                        />
                    )}
                    {setUseMockGeo && (
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={useMockGeo}
                                    onChange={(e) => setUseMockGeo(e.target.checked)}
                                    size="small"
                                    sx={{
                                        '& .MuiSwitch-switchBase.Mui-checked': { color: AMBER },
                                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: AMBER },
                                    }}
                                />
                            }
                            label={
                                <Typography sx={{ fontFamily: NAV_FONT, fontSize: '11px', color: MUTED, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                                    Mock Geo
                                </Typography>
                            }
                        />
                    )}
                </Box>

                <Divider sx={{ borderColor: 'rgba(0,212,255,0.08)', mx: 2, my: 1 }} />

                {/* Logout */}
                <List>
                    <ListItem disablePadding>
                        <ListItemButton
                            onClick={handleLogout}
                            sx={{
                                mx: 1,
                                borderRadius: '12px',
                                '&:hover': { backgroundColor: 'rgba(255,61,113,0.06)' },
                            }}
                        >
                            <ListItemIcon sx={{ color: '#ff3d71', minWidth: 36 }}>
                                <LogoutIcon sx={{ fontSize: 18 }} />
                            </ListItemIcon>
                            <ListItemText
                                primary="Logout"
                                primaryTypographyProps={{
                                    sx: {
                                        fontFamily: NAV_FONT,
                                        fontSize: '11px',
                                        letterSpacing: '0.05em',
                                        textTransform: 'uppercase',
                                        color: '#ff3d71',
                                    },
                                }}
                            />
                        </ListItemButton>
                    </ListItem>
                </List>
            </Drawer>
        </>
    );
};

export default Navbar;
