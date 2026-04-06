import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Box, Typography, Chip, Tooltip } from '@mui/material';
import Navbar from '../components/Navbar';

/* ── Helpers ──────────────────────────────────────── */
const fmtTime = (ts) => {
    try { return new Date(ts).toLocaleTimeString(); }
    catch { return ts || '—'; }
};

const fmtRelative = (ts) => {
    try {
        const diff = Date.now() - new Date(ts).getTime();
        const s = Math.floor(diff / 1000);
        if (s < 60) return `${s}s ago`;
        if (s < 3600) return `${Math.floor(s / 60)}m ago`;
        return `${Math.floor(s / 3600)}h ago`;
    } catch { return '—'; }
};

const EVENT_ICONS = {
    PAGE_VISIT: '🌐',
    LOGIN_ATTEMPT: '🔑',
    MFA_ATTEMPT: '📱',
    RETRY_ATTEMPT: '↺',
    DASHBOARD_INTERACTION: '🖱',
    FILE_SYSTEM_ACCESS: '📁',
    SESSION_TERMINATED: '💀',
    UNKNOWN: '❓',
};

const EVENT_COLORS = {
    PAGE_VISIT: '#00c8ff',
    LOGIN_ATTEMPT: '#ffaa00',
    MFA_ATTEMPT: '#7c43ff',
    RETRY_ATTEMPT: '#ff8800',
    DASHBOARD_INTERACTION: '#00e676',
    FILE_SYSTEM_ACCESS: '#ff3344',
    SESSION_TERMINATED: '#ff3344',
    UNKNOWN: '#7a9bbf',
};

const sev = (type) => {
    if (['SESSION_TERMINATED', 'FILE_SYSTEM_ACCESS'].includes(type)) return 'error';
    if (['LOGIN_ATTEMPT', 'MFA_ATTEMPT'].includes(type)) return 'warning';
    return 'info';
};

/* ── Reusable styled card ─────────────────────────── */
const Panel = ({ title, icon, tag, children, sx = {} }) => (
    <Box sx={{
        background: 'rgba(10, 15, 30, 0.85)',
        border: '1px solid rgba(0, 200, 255, 0.08)',
        borderRadius: '12px',
        overflow: 'hidden',
        ...sx,
    }}>
        <Box sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '12px 16px',
            borderBottom: '1px solid rgba(0, 200, 255, 0.06)',
            background: 'rgba(255,255,255,0.01)',
        }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {icon && <Typography sx={{ fontSize: '1rem' }}>{icon}</Typography>}
                <Typography sx={{
                    fontFamily: '"IBM Plex Mono", monospace',
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    letterSpacing: '0.1em',
                    textTransform: 'uppercase',
                    color: '#e8f4fd',
                }}>
                    {title}
                </Typography>
            </Box>
            {tag && (
                <Chip label={tag} size="small" sx={{
                    fontFamily: '"IBM Plex Mono", monospace',
                    fontSize: '9px',
                    height: '18px',
                    background: 'rgba(0, 200, 255, 0.08)',
                    color: '#00c8ff',
                    border: '1px solid rgba(0, 200, 255, 0.2)',
                }} />
            )}
        </Box>
        <Box sx={{ padding: '16px' }}>
            {children}
        </Box>
    </Box>
);

/* ── Scrolling Timeline ───────────────────────────── */
function EventTimeline({ events }) {
    if (!events.length) return (
        <Box sx={{ textAlign: 'center', py: 4, color: 'rgba(122,155,191,0.5)', fontFamily: '"IBM Plex Mono", monospace', fontSize: '12px' }}>
            No events recorded yet
        </Box>
    );

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, maxHeight: 340, overflowY: 'auto' }}>
            {events.map((evt, i) => {
                const type = evt.honeypot_event || 'UNKNOWN';
                const color = EVENT_COLORS[type] || EVENT_COLORS.UNKNOWN;
                const icon  = EVENT_ICONS[type]  || EVENT_ICONS.UNKNOWN;
                const fp = evt.fingerprint_data || {};

                return (
                    <Box key={i} sx={{
                        display: 'flex',
                        gap: 2,
                        padding: '10px 12px',
                        background: 'rgba(255,255,255,0.02)',
                        borderRadius: '8px',
                        borderLeft: `3px solid ${color}`,
                        position: 'relative',
                        transition: 'background 0.15s',
                        '&:hover': { background: 'rgba(0,200,255,0.04)' },
                    }}>
                        {/* Icon */}
                        <Typography sx={{ fontSize: '18px', flexShrink: 0, lineHeight: 1.2 }}>{icon}</Typography>

                        {/* Content */}
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5, flexWrap: 'wrap' }}>
                                <Typography sx={{
                                    fontFamily: '"IBM Plex Mono", monospace',
                                    fontSize: '11px',
                                    fontWeight: 700,
                                    color,
                                }}>
                                    {type}
                                </Typography>
                                {fp.path && (
                                    <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '10px', color: '#ff3344' }}>
                                        {fp.path}
                                    </Typography>
                                )}
                                {fp.item && (
                                    <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '10px', color: '#00e676' }}>
                                        → {fp.item}
                                    </Typography>
                                )}
                            </Box>
                            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                                {fp.username && (
                                    <Typography sx={{ fontSize: '11px', color: '#7a9bbf' }}>
                                        user: <strong style={{ color: '#e8f4fd' }}>{fp.username}</strong>
                                    </Typography>
                                )}
                                {fp.passwordLength && (
                                    <Typography sx={{ fontSize: '11px', color: '#7a9bbf' }}>
                                        pwd len: <strong style={{ color: '#ffaa00' }}>{fp.passwordLength}</strong>
                                    </Typography>
                                )}
                                {fp.passwordPattern && (
                                    <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '10px', color: '#7c43ff' }}>
                                        {fp.passwordPattern}
                                    </Typography>
                                )}
                                {fp.incidentId && (
                                    <Typography sx={{ fontSize: '11px', color: '#ff3344' }}>
                                        incident: <strong>{fp.incidentId}</strong>
                                    </Typography>
                                )}
                            </Box>
                        </Box>

                        {/* Time */}
                        <Typography sx={{
                            fontFamily: '"IBM Plex Mono", monospace',
                            fontSize: '10px',
                            color: 'rgba(122,155,191,0.5)',
                            flexShrink: 0,
                        }}>
                            {fmtTime(fp.timestamp || evt.created_at)}
                        </Typography>
                    </Box>
                );
            })}
        </Box>
    );
}

/* ── Browser Fingerprint Card ─────────────────────── */
function FingerprintCard({ fp }) {
    const rows = [
        ['User Agent', fp.userAgent?.slice(0, 60)],
        ['Platform', fp.platform],
        ['Language', fp.language],
        ['Screen', fp.screenRes],
        ['Color Depth', fp.colorDepth ? `${fp.colorDepth}-bit` : null],
        ['Timezone', fp.timezone],
        ['Cookies', fp.cookiesEnabled ? 'Enabled' : 'Disabled'],
        ['GPU', fp.gpuRenderer?.slice(0, 50)],
        ['Canvas Hash', fp.canvasHash],
        ['Fonts Detected', fp.fontsDetected?.join(', ')?.slice(0, 60)],
        ['Referrer', fp.referrer || '(direct)'],
    ].filter(([, v]) => v);

    if (!rows.length) return (
        <Typography sx={{ color: 'rgba(122,155,191,0.5)', fontSize: '12px', textAlign: 'center', py: 2 }}>
            No fingerprint data captured yet
        </Typography>
    );

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            {rows.map(([k, v]) => (
                <Box key={k} sx={{ display: 'flex', gap: 2, alignItems: 'flex-start', py: 0.6, borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                    <Typography sx={{
                        fontFamily: '"IBM Plex Mono", monospace',
                        fontSize: '10px',
                        color: '#7a9bbf',
                        minWidth: 100,
                        flexShrink: 0,
                    }}>
                        {k}
                    </Typography>
                    <Typography sx={{
                        fontFamily: '"IBM Plex Mono", monospace',
                        fontSize: '10px',
                        color: '#e8f4fd',
                        wordBreak: 'break-all',
                        lineHeight: 1.5,
                    }}>
                        {v}
                    </Typography>
                </Box>
            ))}
        </Box>
    );
}

/* ── File Navigation Tree ─────────────────────────── */
function FileNavTree({ paths }) {
    if (!paths.length) return (
        <Typography sx={{ color: 'rgba(122,155,191,0.5)', fontSize: '12px', textAlign: 'center', py: 2 }}>
            No filesystem access recorded
        </Typography>
    );

    // Build frequency map
    const freq = {};
    paths.forEach(p => { freq[p] = (freq[p] || 0) + 1; });
    const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]);

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, maxHeight: 240, overflowY: 'auto' }}>
            {sorted.map(([path, count]) => {
                const pct = Math.min(100, (count / sorted[0][1]) * 100);
                return (
                    <Box key={path} sx={{ position: 'relative' }}>
                        {/* Background heat bar */}
                        <Box sx={{
                            position: 'absolute',
                            left: 0, top: 0, bottom: 0,
                            width: `${pct}%`,
                            background: count > 3
                                ? 'rgba(255,51,68,0.06)'
                                : count > 1
                                    ? 'rgba(255,170,0,0.05)'
                                    : 'rgba(0,200,255,0.03)',
                            borderRadius: '6px',
                            pointerEvents: 'none',
                        }} />
                        <Box sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                            padding: '5px 10px',
                            position: 'relative',
                        }}>
                            <Typography sx={{ fontSize: '12px', flexShrink: 0 }}>
                                {path.includes('.') ? '📄' : '📁'}
                            </Typography>
                            <Typography sx={{
                                fontFamily: '"IBM Plex Mono", monospace',
                                fontSize: '10px',
                                color: count > 3 ? '#ff3344' : count > 1 ? '#ffaa00' : '#00c8ff',
                                flex: 1,
                                wordBreak: 'break-all',
                                lineHeight: 1.5,
                            }}>
                                {path}
                            </Typography>
                            <Chip
                                label={`×${count}`}
                                size="small"
                                sx={{
                                    fontFamily: '"IBM Plex Mono", monospace',
                                    fontSize: '9px',
                                    height: '16px',
                                    background: count > 3
                                        ? 'rgba(255,51,68,0.15)'
                                        : 'rgba(0,200,255,0.08)',
                                    color: count > 3 ? '#ff3344' : '#00c8ff',
                                    border: 'none',
                                    flexShrink: 0,
                                }}
                            />
                        </Box>
                    </Box>
                );
            })}
        </Box>
    );
}

/* ── Interaction Heatmap ──────────────────────────── */
function InteractionHeatmap({ interactions }) {
    if (!interactions.length) return (
        <Typography sx={{ color: 'rgba(122,155,191,0.5)', fontSize: '12px', textAlign: 'center', py: 2 }}>
            No dashboard interactions captured
        </Typography>
    );

    const freq = {};
    interactions.forEach(i => { freq[i] = (freq[i] || 0) + 1; });
    const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 10);
    const max = sorted[0]?.[1] || 1;

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {sorted.map(([item, count]) => (
                <Box key={item} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography sx={{
                        fontFamily: '"IBM Plex Mono", monospace',
                        fontSize: '11px',
                        color: '#7a9bbf',
                        minWidth: 140,
                        flexShrink: 0,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                    }}>
                        {item}
                    </Typography>
                    <Box sx={{ flex: 1, height: 8, background: 'rgba(255,255,255,0.04)', borderRadius: '99px', overflow: 'hidden' }}>
                        <Box sx={{
                            height: '100%',
                            width: `${(count / max) * 100}%`,
                            background: count === max
                                ? 'linear-gradient(90deg, #ff3344, #ff8800)'
                                : 'linear-gradient(90deg, #00c8ff, #7c43ff)',
                            borderRadius: '99px',
                            transition: 'width 0.5s ease',
                        }} />
                    </Box>
                    <Typography sx={{
                        fontFamily: '"IBM Plex Mono", monospace',
                        fontSize: '11px',
                        color: '#e8f4fd',
                        minWidth: 24,
                        textAlign: 'right',
                        flexShrink: 0,
                    }}>
                        {count}
                    </Typography>
                </Box>
            ))}
        </Box>
    );
}

/* ── Event Type Breakdown ─────────────────────────── */
function EventBreakdown({ events }) {
    const counts = {};
    events.forEach(e => {
        const t = e.honeypot_event || 'UNKNOWN';
        counts[t] = (counts[t] || 0) + 1;
    });

    const total = events.length || 1;

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            {Object.entries(counts).map(([type, count]) => {
                const color = EVENT_COLORS[type] || '#7a9bbf';
                const icon  = EVENT_ICONS[type]  || '❓';
                const pct   = Math.round((count / total) * 100);
                return (
                    <Box key={type}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography sx={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: 0.8, color: '#e8f4fd' }}>
                                {icon} {type}
                            </Typography>
                            <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '11px', color }}>
                                {count} ({pct}%)
                            </Typography>
                        </Box>
                        <Box sx={{ height: 5, background: 'rgba(255,255,255,0.04)', borderRadius: '99px', overflow: 'hidden' }}>
                            <Box sx={{
                                height: '100%', width: `${pct}%`,
                                background: color, borderRadius: '99px',
                                transition: 'width 0.6s ease',
                                boxShadow: `0 0 6px ${color}60`,
                            }} />
                        </Box>
                    </Box>
                );
            })}
            {!events.length && (
                <Typography sx={{ color: 'rgba(122,155,191,0.5)', fontSize: '12px', textAlign: 'center' }}>
                    No events recorded
                </Typography>
            )}
        </Box>
    );
}

/* ── Password Pattern Mosaic ──────────────────────── */
function PasswordPatternMosaic({ patterns }) {
    if (!patterns.length) return (
        <Typography sx={{ color: 'rgba(122,155,191,0.5)', fontSize: '12px', textAlign: 'center', py: 2 }}>
            No password patterns recorded
        </Typography>
    );

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Typography sx={{ fontSize: '11px', color: '#7a9bbf', mb: 1 }}>
                Pattern key: <code style={{ color: '#00c8ff' }}>x</code>=letter,{' '}
                <code style={{ color: '#ffaa00' }}>n</code>=digit,{' '}
                <code style={{ color: '#ff3344' }}>s</code>=symbol
            </Typography>
            {patterns.map((p, i) => (
                <Box key={i} sx={{
                    fontFamily: '"IBM Plex Mono", monospace',
                    fontSize: '14px',
                    letterSpacing: '0.15em',
                    padding: '8px 12px',
                    background: 'rgba(255,255,255,0.02)',
                    borderRadius: '6px',
                    border: '1px solid rgba(255,255,255,0.04)',
                }}>
                    {p.split('').map((c, j) => (
                        <span key={j} style={{
                            color: c === 'x' ? '#00c8ff' : c === 'n' ? '#ffaa00' : '#ff3344',
                        }}>
                            {c}
                        </span>
                    ))}
                </Box>
            ))}
        </Box>
    );
}

/* ─────────────────────────────────────────────────────────────
   MAIN PAGE
─────────────────────────────────────────────────────────────── */
export default function AttackerFootprintPage() {
    const [events, setEvents]     = useState([]);
    const [loading, setLoading]   = useState(true);
    const [error, setError]       = useState(null);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(new Date());
    const [selectedIP, setSelectedIP] = useState('All');

    const fetchEvents = useCallback(async () => {
        try {
            const res = await fetch('/api/honeypot/logs?limit=200', {
                headers: { Authorization: `Bearer ${localStorage.getItem('authToken')}` },
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setEvents(data.logs || data || []);
            setLastUpdated(new Date());
            setError(null);
        } catch (e) {
            // If endpoint doesn't exist, show demo data
            setEvents([]);
            setError(`Could not fetch logs: ${e.message}`);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchEvents();
    }, [fetchEvents]);

    useEffect(() => {
        if (!autoRefresh) return;
        const t = setInterval(fetchEvents, 8000);
        return () => clearInterval(t);
    }, [autoRefresh, fetchEvents]);

    /* ── Derived data ─────────────────────── */
    const allIPs = ['All', ...new Set(events.map(e => e.attacker_ip).filter(Boolean))];
    const filtered = selectedIP === 'All' ? events : events.filter(e => e.attacker_ip === selectedIP);

    const pageVisit   = filtered.find(e => e.honeypot_event === 'PAGE_VISIT');
    const fingerprint = pageVisit?.fingerprint_data || {};

    const filePaths   = filtered
        .filter(e => e.honeypot_event === 'FILE_SYSTEM_ACCESS')
        .map(e => e.fingerprint_data?.path)
        .filter(Boolean);

    const interactions = filtered
        .filter(e => e.honeypot_event === 'DASHBOARD_INTERACTION')
        .map(e => e.fingerprint_data?.item)
        .filter(Boolean);

    const passPatterns = filtered
        .filter(e => e.honeypot_event === 'LOGIN_ATTEMPT' && e.fingerprint_data?.passwordPattern)
        .map(e => e.fingerprint_data.passwordPattern);

    const totalSessions = events.filter(e => e.honeypot_event === 'SESSION_TERMINATED').length;
    const uniqueIPs     = new Set(events.map(e => e.attacker_ip).filter(Boolean)).size;
    const totalFileHits = events.filter(e => e.honeypot_event === 'FILE_SYSTEM_ACCESS').length;
    const totalLogins   = events.filter(e => e.honeypot_event === 'LOGIN_ATTEMPT').length;

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#050810', position: 'relative', zIndex: 2 }}>
            <Navbar
                lastUpdated={lastUpdated}
                autoRefresh={autoRefresh}
                setAutoRefresh={setAutoRefresh}
                onRefresh={fetchEvents}
            />

            <Box sx={{ px: 2, py: 3, maxWidth: 1600, mx: 'auto' }}>
                {/* Header */}
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h4" sx={{
                        color: '#ff3344',
                        fontFamily: '"Orbitron", sans-serif',
                        fontWeight: 700,
                        mb: 0.5,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1.5,
                    }}>
                        👣 ATTACKER DIGITAL FOOTPRINT
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#7a9bbf' }}>
                        Live forensic trail of attackers interacting with the honeypot deception layer
                    </Typography>
                </Box>

                {/* Error banner */}
                {error && (
                    <Box sx={{
                        mb: 2,
                        p: 2,
                        background: 'rgba(255,51,68,0.08)',
                        border: '1px solid rgba(255,51,68,0.2)',
                        borderRadius: '8px',
                        fontFamily: '"IBM Plex Mono", monospace',
                        fontSize: '12px',
                        color: '#ff3344',
                    }}>
                        ⚠ {error} — Make sure the backend `/api/honeypot/logs` endpoint is available.
                    </Box>
                )}

                {/* IP filter */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    <Typography sx={{ fontSize: '12px', color: '#7a9bbf' }}>Filter by IP:</Typography>
                    {allIPs.map(ip => (
                        <Chip
                            key={ip}
                            label={ip}
                            size="small"
                            onClick={() => setSelectedIP(ip)}
                            sx={{
                                fontFamily: '"IBM Plex Mono", monospace',
                                fontSize: '10px',
                                cursor: 'pointer',
                                background: selectedIP === ip ? 'rgba(0,200,255,0.18)' : 'rgba(255,255,255,0.04)',
                                color: selectedIP === ip ? '#00c8ff' : '#7a9bbf',
                                border: selectedIP === ip ? '1px solid rgba(0,200,255,0.3)' : '1px solid rgba(255,255,255,0.06)',
                            }}
                        />
                    ))}
                </Box>

                {/* KPI Row */}
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 2, mb: 2 }}>
                    {[
                        ['Total Events', filtered.length, '#00c8ff', '📊'],
                        ['Login Attempts', totalLogins, '#ffaa00', '🔑'],
                        ['File System Hits', totalFileHits, '#ff3344', '📁'],
                        ['Sessions Terminated', totalSessions, '#7c43ff', '💀'],
                    ].map(([label, value, color, icon]) => (
                        <Box key={label} sx={{
                            background: 'rgba(10,15,30,0.85)',
                            border: `1px solid ${color}22`,
                            borderRadius: '12px',
                            padding: '16px',
                        }}>
                            <Typography sx={{ fontSize: '1.5rem', mb: 0.5 }}>{icon}</Typography>
                            <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '24px', fontWeight: 700, color }}>
                                {value}
                            </Typography>
                            <Typography sx={{ fontSize: '11px', color: '#7a9bbf', mt: 0.5 }}>{label}</Typography>
                        </Box>
                    ))}
                </Box>

                {/* Main grid */}
                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 2, mb: 2 }}>
                    {/* Event timeline */}
                    <Panel title="Event Timeline" icon="⏱" tag={`${filtered.length} events`}>
                        {loading
                            ? <Typography sx={{ color: '#7a9bbf', fontSize: '12px', textAlign: 'center', py: 2 }}>Loading…</Typography>
                            : <EventTimeline events={filtered.slice().reverse()} />
                        }
                    </Panel>

                    {/* Right column */}
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {/* Browser fingerprint */}
                        <Panel title="Browser Fingerprint" icon="🔬" tag={fingerprint.canvasHash ? 'CAPTURED' : 'PENDING'}>
                            <FingerprintCard fp={fingerprint} />
                        </Panel>

                        {/* Event breakdown */}
                        <Panel title="Event Type Breakdown" icon="📊">
                            <EventBreakdown events={filtered} />
                        </Panel>
                    </Box>
                </Box>

                {/* Bottom grid */}
                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr 1fr' }, gap: 2 }}>
                    {/* File navigation */}
                    <Panel title="File System Navigation" icon="📁" tag="S-RRT Paths">
                        <FileNavTree paths={filePaths} />
                    </Panel>

                    {/* Dashboard interaction heatmap */}
                    <Panel title="Dashboard Interaction Heatmap" icon="🖱" tag="Click Frequency">
                        <InteractionHeatmap interactions={interactions} />
                    </Panel>

                    {/* Password patterns */}
                    <Panel title="Password Patterns" icon="🔑" tag="Behavioral Analysis">
                        <PasswordPatternMosaic patterns={passPatterns} />
                        {passPatterns.length > 0 && (
                            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(255,255,255,0.04)' }}>
                                <Typography sx={{ fontSize: '11px', color: '#7a9bbf', mb: 1 }}>Password lengths:</Typography>
                                {filtered
                                    .filter(e => e.honeypot_event === 'LOGIN_ATTEMPT' && e.fingerprint_data?.passwordLength)
                                    .map((e, i) => (
                                        <Chip
                                            key={i}
                                            label={`${e.fingerprint_data.passwordLength} chars`}
                                            size="small"
                                            sx={{
                                                mr: 0.5, mb: 0.5,
                                                fontFamily: '"IBM Plex Mono", monospace',
                                                fontSize: '10px',
                                                background: 'rgba(255,170,0,0.08)',
                                                color: '#ffaa00',
                                                border: '1px solid rgba(255,170,0,0.15)',
                                            }}
                                        />
                                    ))
                                }
                            </Box>
                        )}
                    </Panel>
                </Box>
            </Box>
        </Box>
    );
}
