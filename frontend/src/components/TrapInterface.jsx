import React, { useState, useEffect, useRef, useCallback } from 'react';
import '../trap.css';

/* ── Stage machine ──────────────────────────────────────────── */
const STAGES = {
    LOGIN: 'LOGIN',
    VERIFYING: 'VERIFYING',
    ERROR: 'ERROR',
    MFA: 'MFA',
    LOADING: 'LOADING',
    DASHBOARD: 'DASHBOARD',
    TERMINATED: 'TERMINATED',
    BENIGN: 'BENIGN',
};

/* ── Terminal log lines that appear during verification ─────── */
const VERIFY_LOG_LINES = [
    { at: 0,  text: '[SYS]  Initiating TLS 1.3 handshake → auth.nexacorp.io:8443' },
    { at: 6,  text: '[LDAP] Querying DC01.nexacorp.io... CONNECTED' },
    { at: 14, text: '[PKI]  Validating certificate chain: Chain OK (depth=3)' },
    { at: 22, text: '[MFA]  Resolving registered device registry...' },
    { at: 30, text: '[2FA]  Dispatching OTP via secure channel...' },
    { at: 40, text: '[SEC]  Cross-referencing access control list...' },
    { at: 48, text: '[WARN] Response timeout on auth-node-3 — retrying auth-node-4' },
    { at: 55, text: '[SYS]  Session token queued (48-bit ephemeral)' },
    { at: 65, text: '[WARN] Auth node experiencing elevated latency (823ms)' },
    { at: 75, text: '[SYS]  Finalizing authentication handshake...' },
];

const LOAD_LOG_LINES = [
    { at: 0,  text: 'Loading user profile & permission matrix...' },
    { at: 12, text: 'Connecting to enterprise services...' },
    { at: 28, text: 'Syncing SharePoint & Confluence data...' },
    { at: 45, text: 'Loading analytics engine modules...' },
    { at: 62, text: 'Hydrating notification service...' },
    { at: 80, text: 'Almost ready...' },
];

/* ── Browser fingerprinting helpers ─────────────────────────── */
function getCanvasFingerprint() {
    try {
        const c = document.createElement('canvas');
        const ctx = c.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillText('NexaCorp_fp_2025', 2, 2);
        return c.toDataURL().slice(-50);
    } catch { return 'unavailable'; }
}
function getWebGLRenderer() {
    try {
        const c = document.createElement('canvas');
        const gl = c.getContext('webgl');
        const ext = gl?.getExtension('WEBGL_debug_renderer_info');
        return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'unavailable';
    } catch { return 'unavailable'; }
}
function detectFonts() {
    const fonts = ['Calibri','Cambria','Consolas','Courier New','Georgia','Segoe UI','Tahoma','Trebuchet MS','Verdana'];
    const detected = [];
    const span = document.createElement('span');
    span.style.cssText = 'position:absolute;visibility:hidden;font-size:72px';
    span.innerHTML = 'mmmmmmmmmmlli';
    document.body.appendChild(span);
    const baseW = span.offsetWidth;
    fonts.forEach(f => { span.style.fontFamily = `'${f}',monospace`; if (span.offsetWidth !== baseW) detected.push(f); });
    document.body.removeChild(span);
    return detected;
}

/* ── Honeypot logger ─────────────────────────────────────────── */
function logEvent(event, data = {}) {
    fetch('/api/honeypot/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event, data: { ...data, timestamp: new Date().toISOString() } }),
    }).catch(() => {});
}

/* ─────────────────────────────────────────────────────────────
   STAGE: LOGIN
───────────────────────────────────────────────────────────────*/
function StageLogin({ onSubmit, credentials, setCredentials }) {
    const [shimmer, setShimmer] = useState(false);
    const [showPass, setShowPass] = useState(false);

    useEffect(() => {
        const t = setInterval(() => setShimmer(p => !p), 4000);
        return () => clearInterval(t);
    }, []);

    return (
        <div className="trap2-root">
            {/* Animated grid background */}
            <div className="trap2-grid-bg" />
            <div className="trap2-scanline" />

            {/* Header */}
            <header className="trap2-header">
                <div className="trap2-logo">
                    <span className="trap2-logo-icon">⬡</span>
                    <span className="trap2-logo-text">NexaCorp</span>
                    <span className="trap2-logo-tag">SECURE GATEWAY</span>
                </div>
                <div className="trap2-header-right">
                    <span className="trap2-status-dot" />
                    <span className="trap2-header-sys">AUTH NODE ONLINE</span>
                    <span className="trap2-header-sep" />
                    <span style={{ color: '#7a9bbf', fontSize: '11px' }}>Helpdesk: ext. 4400</span>
                </div>
            </header>

            {/* Card */}
            <div className="trap2-center">
                <div className={`trap2-card${shimmer ? ' trap2-card-shimmer' : ''}`}>
                    {/* Card top stripe */}
                    <div className="trap2-card-stripe" />

                    <div className="trap2-card-inner">
                        <div className="trap2-card-title-block">
                            <h2 className="trap2-card-title">Employee Login</h2>
                            <p className="trap2-card-sub">Sign in with your NexaCorp credentials</p>
                        </div>

                        <div className="trap2-notice">
                            <span className="trap2-notice-icon">⚠</span>
                            <span>Authorized personnel only. All access is monitored and logged under IT Security Policy 4.2.</span>
                        </div>

                        <div className="trap2-field">
                            <label className="trap2-label">Username</label>
                            <div className="trap2-input-wrap">
                                <span className="trap2-input-icon">@</span>
                                <input
                                    className="trap2-input"
                                    type="text"
                                    placeholder="firstname.lastname"
                                    value={credentials.username}
                                    onChange={e => setCredentials(p => ({ ...p, username: e.target.value }))}
                                    autoComplete="username"
                                />
                            </div>
                        </div>

                        <div className="trap2-field">
                            <label className="trap2-label">Password</label>
                            <div className="trap2-input-wrap">
                                <span className="trap2-input-icon">🔑</span>
                                <input
                                    className="trap2-input"
                                    type={showPass ? 'text' : 'password'}
                                    placeholder="••••••••••••"
                                    value={credentials.password}
                                    onChange={e => setCredentials(p => ({ ...p, password: e.target.value }))}
                                    autoComplete="current-password"
                                />
                                <button
                                    className="trap2-eye-btn"
                                    type="button"
                                    onClick={() => setShowPass(v => !v)}
                                    tabIndex={-1}
                                >
                                    {showPass ? '🙈' : '👁'}
                                </button>
                            </div>
                        </div>

                        <div className="trap2-row-opts">
                            <label className="trap2-check-label">
                                <input type="checkbox" className="trap2-checkbox" /> Remember this device
                            </label>
                            <a href="#" onClick={e => e.preventDefault()} className="trap2-link">Forgot password?</a>
                        </div>

                        <button
                            className="trap2-btn-primary"
                            onClick={() => {
                                logEvent('LOGIN_ATTEMPT', {
                                    username: credentials.username,
                                    passwordLength: credentials.password.length,
                                    passwordPattern: credentials.password
                                        .replace(/[a-z]/gi, 'x')
                                        .replace(/[0-9]/g, 'n')
                                        .replace(/[^xn]/g, 's'),
                                });
                                onSubmit();
                            }}
                        >
                            <span>Sign In</span>
                            <span className="trap2-btn-arrow">→</span>
                        </button>

                        <div className="trap2-divider"><span>or continue with</span></div>

                        <div className="trap2-sso-row">
                            <button className="trap2-sso-btn" onClick={e => e.preventDefault()}>
                                <span>🏢</span> SSO / Active Directory
                            </button>
                            <button className="trap2-sso-btn" onClick={e => e.preventDefault()}>
                                <span>🔐</span> Hardware Token
                            </button>
                        </div>

                        <div className="trap2-footer-links">
                            <a href="#" onClick={e => e.preventDefault()}>New Employee Setup</a>
                            <span>•</span>
                            <a href="#" onClick={e => e.preventDefault()}>VPN Instructions</a>
                            <span>•</span>
                            <a href="#" onClick={e => e.preventDefault()}>IT Support Portal</a>
                        </div>
                    </div>
                </div>

                <p className="trap2-footer-legal">
                    © 2025 NexaCorp Systems v5.1.0 — Unauthorized access is strictly prohibited and will be prosecuted.
                </p>
            </div>
        </div>
    );
}

/* ─────────────────────────────────────────────────────────────
   STAGE: VERIFYING
───────────────────────────────────────────────────────────────*/
function StageVerifying({ progress, logs }) {
    return (
        <div className="trap2-root">
            <div className="trap2-grid-bg" />
            <div className="trap2-scanline" />
            <header className="trap2-header">
                <div className="trap2-logo">
                    <span className="trap2-logo-icon">⬡</span>
                    <span className="trap2-logo-text">NexaCorp</span>
                    <span className="trap2-logo-tag">SECURE GATEWAY</span>
                </div>
            </header>
            <div className="trap2-center trap2-verify-center">
                <div className="trap2-verify-card">
                    <div className="trap2-verify-header">
                        <div className="trap2-verify-spinner" />
                        <div>
                            <h3 className="trap2-verify-title">Authenticating…</h3>
                            <p className="trap2-verify-sub">Do not close this window</p>
                        </div>
                    </div>

                    {/* Progress bar */}
                    <div className="trap2-prog-track">
                        <div className="trap2-prog-fill" style={{ width: `${progress}%` }} />
                    </div>
                    <div className="trap2-prog-row">
                        <span className="trap2-prog-pct">{Math.floor(progress)}%</span>
                        <span className="trap2-prog-label">Establishing secure session</span>
                    </div>

                    {/* Terminal */}
                    <div className="trap2-terminal">
                        <div className="trap2-terminal-bar">
                            <span className="trap2-term-dot trap2-td-r" />
                            <span className="trap2-term-dot trap2-td-y" />
                            <span className="trap2-term-dot trap2-td-g" />
                            <span className="trap2-term-title">auth-session.log</span>
                        </div>
                        <div className="trap2-terminal-body">
                            {logs.map((l, i) => (
                                <div key={i} className={`trap2-log-line ${l.startsWith('[WARN]') ? 'trap2-log-warn' : l.startsWith('[SEC]') ? 'trap2-log-sec' : ''}`}>
                                    {l}
                                </div>
                            ))}
                            <div className="trap2-cursor">█</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ─────────────────────────────────────────────────────────────
   STAGE: ERROR (deceptive auth failure to trigger MFA)
───────────────────────────────────────────────────────────────*/
function StageError({ onRetry }) {
    const errCode = 'AUTH_SRV_TIMEOUT_0x80090304';
    const traceId = Math.random().toString(36).substr(2, 16).toUpperCase();
    const incId = `INC-${Math.floor(Math.random() * 90000) + 10000}`;
    return (
        <div className="trap2-root">
            <div className="trap2-grid-bg" />
            <header className="trap2-header">
                <div className="trap2-logo">
                    <span className="trap2-logo-icon">⬡</span>
                    <span className="trap2-logo-text">NexaCorp</span>
                    <span className="trap2-logo-tag">SECURE GATEWAY</span>
                </div>
            </header>
            <div className="trap2-center">
                <div className="trap2-card trap2-err-card">
                    <div className="trap2-card-stripe trap2-stripe-red" />
                    <div className="trap2-card-inner">
                        <div className="trap2-err-icon">✕</div>
                        <h3 className="trap2-err-title">Authentication Failed</h3>
                        <div className="trap2-err-box">
                            <div className="trap2-err-row"><span>Error Code</span><code>{errCode}</code></div>
                            <div className="trap2-err-row"><span>Node</span><code>auth-node-3.nexacorp.io:8443</code></div>
                            <div className="trap2-err-row"><span>Time</span><code>{new Date().toLocaleTimeString()}</code></div>
                            <div className="trap2-err-row"><span>Trace ID</span><code style={{ fontSize: '11px' }}>{traceId}</code></div>
                        </div>
                        <p className="trap2-err-hint">
                            Your credentials may be correct. This is a temporary server-side issue.
                            The system will route you through secondary MFA verification.
                        </p>
                        <div className="trap2-btn-row">
                            <button className="trap2-btn-primary" onClick={onRetry}>↺ Retry with 2FA</button>
                            <button className="trap2-btn-ghost" onClick={e => e.preventDefault()}>Contact Support</button>
                        </div>
                        <p className="trap2-incident">Incident auto-logged. Reference: <strong>{incId}</strong></p>
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ─────────────────────────────────────────────────────────────
   STAGE: MFA
───────────────────────────────────────────────────────────────*/
function StageMFA({ mfaCode, setMfaCode, mfaError, onSubmit, setMfaError }) {
    const boxes = useRef([]);

    const handleKey = (idx, e) => {
        const val = e.target.value.replace(/\D/g, '').slice(-1);
        const arr = mfaCode.split('');
        arr[idx] = val;
        const next = arr.join('');
        setMfaCode(next);
        if (val && idx < 5) boxes.current[idx + 1]?.focus();
        if (!val && e.key === 'Backspace' && idx > 0) boxes.current[idx - 1]?.focus();
    };

    return (
        <div className="trap2-root">
            <div className="trap2-grid-bg" />
            <header className="trap2-header">
                <div className="trap2-logo">
                    <span className="trap2-logo-icon">⬡</span>
                    <span className="trap2-logo-text">NexaCorp</span>
                    <span className="trap2-logo-tag">SECURE GATEWAY</span>
                </div>
            </header>
            <div className="trap2-center">
                <div className="trap2-card">
                    <div className="trap2-card-stripe" />
                    <div className="trap2-card-inner">
                        <div className="trap2-mfa-icon-wrap">
                            <div className="trap2-mfa-icon">📱</div>
                            <div className="trap2-mfa-pulse" />
                        </div>
                        <h3 className="trap2-card-title">Two-Factor Authentication</h3>
                        <p className="trap2-card-sub">
                            A 6-digit code was sent to your registered device ending in <strong>••••7284</strong>
                        </p>

                        {/* 6-box OTP */}
                        <div className="trap2-otp-row">
                            {[0,1,2,3,4,5].map(i => (
                                <input
                                    key={i}
                                    ref={el => (boxes.current[i] = el)}
                                    className={`trap2-otp-box${mfaError ? ' trap2-otp-err' : ''}`}
                                    type="text"
                                    inputMode="numeric"
                                    maxLength={1}
                                    value={mfaCode[i] || ''}
                                    onChange={e => handleKey(i, e)}
                                    onKeyDown={e => handleKey(i, e)}
                                    autoFocus={i === 0}
                                />
                            ))}
                        </div>
                        {mfaError && <p className="trap2-otp-err-msg">Please enter a valid 6-digit code</p>}

                        <div className="trap2-mfa-hints">
                            <span>⏱ Code expires in <strong className="trap2-countdown">4:59</strong></span>
                            <span>
                                Didn't get it? <a href="#" onClick={e => e.preventDefault()}>Resend</a>
                                {' '}or <a href="#" onClick={e => e.preventDefault()}>Use backup code</a>
                            </span>
                        </div>

                        <button
                            className="trap2-btn-primary"
                            onClick={() => {
                                if (mfaCode.replace(/\D/g, '').length !== 6) { setMfaError(true); return; }
                                setMfaError(false);
                                logEvent('MFA_ATTEMPT', { code: mfaCode });
                                onSubmit();
                            }}
                        >
                            <span>Verify Code</span><span className="trap2-btn-arrow">→</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ─────────────────────────────────────────────────────────────
   STAGE: LOADING (post-MFA)
───────────────────────────────────────────────────────────────*/
function StageLoading({ progress, logs }) {
    const MODULES = ['User Authentication', 'Permission Matrix', 'Dashboard Core', 'Analytics Engine', 'Notification Service', 'Document Library'];
    return (
        <div className="trap2-root trap2-dark-bg">
            <div className="trap2-load-screen">
                <div className="trap2-load-success-banner">
                    <span>✓</span> Code accepted. Establishing secure session…
                </div>
                <div className="trap2-load-logo">⬡ NexaCorp Enterprise</div>
                <p className="trap2-load-msg">{logs[logs.length - 1] || 'Initializing…'}</p>
                <div className="trap2-prog-track trap2-prog-wide">
                    <div className="trap2-prog-fill trap2-prog-green" style={{ width: `${progress}%` }} />
                </div>
                <div className="trap2-module-list">
                    {MODULES.map((m, i) => (
                        <div key={m} className="trap2-module-item">
                            {progress > (i + 1) * 14
                                ? <span className="trap2-mod-check">✓</span>
                                : <span className="trap2-mod-spinner" />
                            }
                            <span>{m}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

/* ─────────────────────────────────────────────────────────────
   FAKE FILESYSTEM (S-RRT driven)
───────────────────────────────────────────────────────────────*/
function FakeFilesystem({ onPathClick, activeDelay }) {
    const [schema, setSchema] = useState([]);
    const [expanded, setExpanded] = useState({});
    const [selected, setSelected] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/meta-heuristics/rrt/schema')
            .then(r => r.json())
            .then(d => {
                setSchema(d.schema || []);
                setLoading(false);
            })
            .catch(() => { setLoading(false); });
    }, []);

    const handleClick = (path, heat) => {
        setSelected(path);
        logEvent('FILE_SYSTEM_ACCESS', { path, heat, method: 'click' });
        onPathClick(path);
    };

    const buildTree = (paths) => {
        const tree = {};
        paths.forEach(item => {
            const parts = item.path.replace(/^\//, '').split('/');
            let node = tree;
            parts.forEach((p, i) => {
                if (!node[p]) node[p] = { _meta: item, _children: {} };
                if (i === parts.length - 1) node[p]._meta = item;
                node = node[p]._children;
            });
        });
        return tree;
    };

    const renderTree = (node, depth = 0) => {
        return Object.entries(node).map(([name, item]) => {
            const path = item._meta?.path || name;
            const heat = item._meta?.pheromone_level || 0;
            const hasChildren = Object.keys(item._children).length > 0;
            const isExpanded = expanded[path];
            const isSelected = selected === path;

            const heatColor = heat > 0.7 ? '#ff4444' : heat > 0.4 ? '#ffaa00' : '#00e676';

            return (
                <div key={path}>
                    <div
                        className={`trap2-fs-item${isSelected ? ' trap2-fs-selected' : ''}`}
                        style={{ paddingLeft: `${8 + depth * 16}px` }}
                        onClick={() => {
                            if (hasChildren) setExpanded(p => ({ ...p, [path]: !isExpanded }));
                            handleClick(path, heat);
                        }}
                    >
                        <span className="trap2-fs-expand">{hasChildren ? (isExpanded ? '▾' : '▸') : ''}</span>
                        <span className="trap2-fs-icon">{hasChildren ? (isExpanded ? '📂' : '📁') : '📄'}</span>
                        <span className="trap2-fs-name">{name}</span>
                        <span className="trap2-fs-heat" style={{ color: heatColor, opacity: Math.max(0.3, heat) }} title={`Interest: ${Math.round(heat * 100)}%`}>
                            ●
                        </span>
                    </div>
                    {hasChildren && isExpanded && renderTree(item._children, depth + 1)}
                </div>
            );
        });
    };

    if (loading) return <div className="trap2-fs-loading">Loading filesystem…</div>;
    if (!schema.length) {
        // Fallback static tree if API fails
        const fallback = [
            { path: '/home/admin/documents', pheromone_level: 0.8 },
            { path: '/home/admin/documents/finance', pheromone_level: 0.9 },
            { path: '/home/admin/documents/finance/Q4_2025_report.xlsx', pheromone_level: 1.0 },
            { path: '/home/admin/documents/hr', pheromone_level: 0.5 },
            { path: '/home/admin/documents/hr/employees.csv', pheromone_level: 0.7 },
            { path: '/etc/passwd', pheromone_level: 0.95 },
            { path: '/etc/shadow', pheromone_level: 1.0 },
            { path: '/var/log/auth.log', pheromone_level: 0.6 },
            { path: '/home/admin/scripts/backup.sh', pheromone_level: 0.4 },
        ];
        return <div>{renderTree(buildTree(fallback))}</div>;
    }

    return <div>{renderTree(buildTree(schema))}</div>;
}

/* ─────────────────────────────────────────────────────────────
   STAGE: DASHBOARD (fake enterprise panel)
───────────────────────────────────────────────────────────────*/
function StageDashboard({ data, onItemClick, clickedItem, activeDelay, activePath, setActivePath }) {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [fileContent, setFileContent] = useState(null);

    const handlePathClick = (path) => {
        if (setActivePath) setActivePath(path);
        // Show fake "file content" for leaf files
        if (!path.endsWith('/') && path.includes('.')) {
            const fakeContents = {
                '.xlsx': '⚠ Encrypted file — requires enterprise DRM to open.',
                '.csv': 'id,name,email,dept,salary\n1,Alice Johnson,alice.j@nexacorp.io,Finance,95000\n2,Bob Martinez,bob.m@nexacorp.io,IT,87000\n3,Carol Lee,carol.l@nexacorp.io,HR,72000',
                '.sh': '#!/bin/bash\n# NexaCorp Backup\ntar -czf /backup/$(date +%F).tar.gz /home/admin/\naws s3 cp /backup/ s3://nexacorp-backup/ --recursive',
                '.log': `[2025-04-07 02:14:31] sshd: Accepted publickey for admin from 192.168.1.14\n[2025-04-07 03:11:22] sshd: Failed password for root from 45.76.88.102\n[2025-04-07 03:11:23] sshd: Failed password for root from 45.76.88.102\n[2025-04-07 03:11:24] sshd: Failed password for root from 45.76.88.102\n[2025-04-07 03:11:25] PAM: Authentication failure; logname= uid=0`,
                default: 'Access denied. This file requires elevated permissions.',
            };
            const ext = Object.keys(fakeContents).find(k => path.endsWith(k)) || 'default';
            setFileContent({ path, content: fakeContents[ext] });
        }
    };

    const SPARKDATA = Array.from({ length: 20 }, (_, i) => ({
        t: i,
        v: 30 + Math.sin(i * 0.5) * 15 + Math.random() * 10,
    }));

    return (
        <div className="trap2-dash">
            {/* Topbar */}
            <div className="trap2-dash-topbar">
                <div className="trap2-dash-logo">⬡ NexaCorp Enterprise</div>
                <div className="trap2-dash-topbar-center">
                    <div className="trap2-dash-search">
                        🔍 <input placeholder="Search systems, users, documents…" className="trap2-search-input" onClick={() => onItemClick('search')} readOnly />
                    </div>
                </div>
                <div className="trap2-dash-topbar-right">
                    <button className="trap2-dash-notif" onClick={() => onItemClick('notifications')}>
                        🔔 <span className="trap2-notif-badge">7</span>
                    </button>
                    <div className="trap2-dash-avatar">
                        <span className="trap2-avatar-ring">{data.user.name?.charAt(0)?.toUpperCase() || 'U'}</span>
                        <div>
                            <div className="trap2-avatar-name">{data.user.name}</div>
                            <div className="trap2-avatar-role">{data.user.role}</div>
                        </div>
                    </div>
                    <button className="trap2-signout" onClick={() => onItemClick('logout')}>Sign Out</button>
                </div>
            </div>

            <div className="trap2-dash-body">
                {/* Sidebar */}
                <nav className="trap2-dash-nav">
                    <div className="trap2-nav-section">MAIN</div>
                    {[
                        ['📊', 'Dashboard', 'dashboard'],
                        ['🖥', 'Devices', 'devices'],
                        ['🔒', 'Security', 'security'],
                        ['📁', 'Documents', 'documents'],
                        ['👤', 'Users', 'users'],
                    ].map(([icon, label, key]) => (
                        <button
                            key={key}
                            className={`trap2-nav-item${activeTab === key ? ' trap2-nav-active' : ''}`}
                            onClick={() => { setActiveTab(key); onItemClick(key); }}
                        >
                            <span>{icon}</span>
                            <span>{label}</span>
                            {clickedItem === key && <span className="trap2-nav-spin" />}
                        </button>
                    ))}

                    <div className="trap2-nav-section">TOOLS</div>
                    {[
                        ['📈', 'Reports', 'reports'],
                        ['🔔', 'Alerts', 'alerts'],
                        ['🌐', 'Network Map', 'network'],
                        ['⚙', 'Settings', 'settings'],
                    ].map(([icon, label, key]) => (
                        <button
                            key={key}
                            className={`trap2-nav-item${activeTab === key ? ' trap2-nav-active' : ''}`}
                            onClick={() => { setActiveTab(key); onItemClick(key); }}
                        >
                            <span>{icon}</span>
                            <span>{label}</span>
                        </button>
                    ))}

                    {/* System Health widget */}
                    <div className="trap2-nav-health">
                        <div className="trap2-health-label">System Load</div>
                        <div className="trap2-health-bar"><div className="trap2-health-fill" style={{ width: '68%' }} /></div>
                        <div className="trap2-health-label">Memory</div>
                        <div className="trap2-health-bar"><div className="trap2-health-fill trap2-health-yellow" style={{ width: '82%' }} /></div>
                        <div className="trap2-health-label">Storage</div>
                        <div className="trap2-health-bar"><div className="trap2-health-fill trap2-health-green" style={{ width: '44%' }} /></div>
                    </div>
                </nav>

                {/* Main content */}
                <main className="trap2-dash-main">
                    {/* TC-PSO delay overlay */}
                    {activeDelay > 0 && (
                        <div className="trap2-delay-overlay">
                            <div className="trap2-delay-spinner" />
                            <p>Loading {clickedItem}… <span style={{ color: '#ffaa00' }}>({activeDelay.toFixed(1)}s)</span></p>
                        </div>
                    )}

                    {/* Stats row */}
                    <div className="trap2-stats-row">
                        {data.stats.map(s => (
                            <div key={s.label} className="trap2-stat-card" onClick={() => onItemClick(s.label)}>
                                <div className="trap2-stat-value">{s.value}</div>
                                <div className="trap2-stat-label">{s.label}</div>
                                <div className={`trap2-stat-change ${s.change.startsWith('+') ? 'trap2-pos' : s.change.startsWith('-') ? 'trap2-neg' : ''}`}>
                                    {s.change}
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Two-column layout */}
                    <div className="trap2-two-col">
                        {/* Left: Alerts table */}
                        <div className="trap2-panel">
                            <div className="trap2-panel-header">
                                <span className="trap2-panel-title">🔔 Recent Security Alerts</span>
                                <button className="trap2-panel-btn" onClick={() => onItemClick('alerts')}>View All</button>
                            </div>
                            <table className="trap2-table">
                                <thead>
                                    <tr><th>Time</th><th>Event</th><th>Severity</th><th></th></tr>
                                </thead>
                                <tbody>
                                    {data.alerts.map((a, i) => (
                                        <tr key={i} className="trap2-table-row" onClick={() => onItemClick(`alert-${i}`)}>
                                            <td className="trap2-td-mono">{a.time}</td>
                                            <td>{a.msg}</td>
                                            <td><span className={`trap2-badge trap2-badge-${a.sev}`}>{a.sev}</span></td>
                                            <td>
                                                {clickedItem === `alert-${i}`
                                                    ? <span className="trap2-nav-spin" />
                                                    : <button className="trap2-action-btn">View</button>
                                                }
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Right: File explorer (S-RRT) */}
                        <div className="trap2-panel">
                            <div className="trap2-panel-header">
                                <span className="trap2-panel-title">📁 File System Explorer</span>
                                <span className="trap2-panel-tag">S-RRT</span>
                            </div>
                            {activePath && (
                                <div className="trap2-path-bar">
                                    <span className="trap2-path-icon">📍</span>
                                    <span className="trap2-path-text">{activePath}</span>
                                </div>
                            )}
                            <div className="trap2-fs-scroll">
                                <FakeFilesystem onPathClick={handlePathClick} activeDelay={activeDelay} />
                            </div>
                            {fileContent && (
                                <div className="trap2-file-viewer">
                                    <div className="trap2-file-viewer-header">
                                        <span>📄 {fileContent.path}</span>
                                        <button onClick={() => setFileContent(null)}>✕</button>
                                    </div>
                                    <pre className="trap2-file-content">{fileContent.content}</pre>
                                </div>
                            )}
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

/* ─────────────────────────────────────────────────────────────
   STAGE: TERMINATED
───────────────────────────────────────────────────────────────*/
function StageTerminated({ credentials }) {
    const incidentId = useRef(`CF-${Math.floor(Math.random() * 9000) + 1000}`);
    const traceId = useRef(Array.from({ length: 16 }, () => Math.floor(Math.random() * 16).toString(16)).join('').toUpperCase());
    const [traceStep, setTraceStep] = useState(0);

    useEffect(() => {
        logEvent('SESSION_TERMINATED', { incidentId: incidentId.current, username: credentials.username, duration: '~8 minutes' });
        const t = setInterval(() => setTraceStep(p => Math.min(p + 1, 5)), 1200);
        return () => clearInterval(t);
    }, [credentials.username]);

    const TRACE_LINES = [
        '> Tracing connection origin via BGP route analysis…',
        '✓ Origin IP geolocated and logged',
        '> Cross-referencing threat intelligence feeds…',
        '✓ Evidence package archived (SHA-256 chain intact)',
        '> Filing incident report with Security Operations…',
        '✓ Report filed — SOC team notified via PagerDuty',
    ];

    return (
        <div className="trap2-terminated">
            <div className="trap2-terminated-pulse" />
            <div className="trap2-terminated-card">
                <div className="trap2-terminated-icon">⚠</div>
                <h1 className="trap2-terminated-title">SESSION TERMINATED</h1>
                <div className="trap2-terminated-divider" />
                <p className="trap2-terminated-reason">
                    Anomalous access pattern detected. This incident has been escalated and logged.
                </p>
                <div className="trap2-terminated-details">
                    {[
                        ['Incident ID', incidentId.current],
                        ['Status', 'FILED — UNDER REVIEW'],
                        ['Timestamp', new Date().toLocaleString()],
                        ['Trace ID', traceId.current],
                        ['Action', 'Connection flagged • IP logged • Admin notified'],
                    ].map(([k, v]) => (
                        <div key={k} className="trap2-detail-row">
                            <span>{k}</span>
                            <strong className={k === 'Status' ? 'trap2-filed' : ''}>{v}</strong>
                        </div>
                    ))}
                </div>
                <div className="trap2-trace-terminal">
                    {TRACE_LINES.slice(0, traceStep + 1).map((l, i) => (
                        <div key={i} className={`trap2-trace-line${l.startsWith('✓') ? ' trap2-trace-done' : ''}`}>{l}</div>
                    ))}
                </div>
                <p className="trap2-terminated-footer">
                    If you believe this is an error, contact IT Security at security@nexacorp.io
                    with reference <strong>{incidentId.current}</strong>
                </p>
            </div>
        </div>
    );
}

/* ─────────────────────────────────────────────────────────────
   STAGE: BENIGN (real user success)
───────────────────────────────────────────────────────────────*/
function StageBenign({ credentials }) {
    useEffect(() => {
        const t = setTimeout(() => { window.location.href = '/dashboard'; }, 2000);
        return () => clearTimeout(t);
    }, []);

    return (
        <div className="trap2-root">
            <div className="trap2-grid-bg" />
            <header className="trap2-header">
                <div className="trap2-logo">
                    <span className="trap2-logo-icon">⬡</span>
                    <span className="trap2-logo-text">NexaCorp</span>
                    <span className="trap2-logo-tag">SECURE GATEWAY</span>
                </div>
            </header>
            <div className="trap2-center">
                <div className="trap2-card">
                    <div className="trap2-card-stripe trap2-stripe-green" />
                    <div className="trap2-card-inner" style={{ textAlign: 'center' }}>
                        <div className="trap2-success-check">✓</div>
                        <h3 style={{ color: '#00e676', marginBottom: '8px' }}>Authentication Successful</h3>
                        <p style={{ color: '#7a9bbf', marginBottom: '24px' }}>Welcome back, <strong style={{ color: '#e8f4fd' }}>{credentials.username || 'User'}</strong></p>
                        <p className="trap2-hint">Redirecting to dashboard…</p>
                        <a href="/dashboard" className="trap2-btn-primary" style={{ display: 'inline-flex', textDecoration: 'none', marginTop: '16px' }}>
                            Continue to Dashboard →
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ─────────────────────────────────────────────────────────────
   MAIN COMPONENT
───────────────────────────────────────────────────────────────*/
export default function TrapInterface() {
    const [stage, setStage] = useState(STAGES.LOGIN);
    const [progress, setProgress] = useState(0);
    const [verifyLogs, setVerifyLogs] = useState([]);
    const [mfaCode, setMfaCode] = useState('');
    const [mfaError, setMfaError] = useState(false);
    const [loadProgress, setLoadProgress] = useState(0);
    const [loadLogs, setLoadLogs] = useState([]);
    const [clickedItem, setClickedItem] = useState(null);
    const [credentials, setCredentials] = useState({ username: '', password: '' });
    const [activeDelay, setActiveDelay] = useState(0);
    const [activePath, setActivePath] = useState(null);
    const terminationTimerRef = useRef(null);

    /* ── Page-visit fingerprint ───────────────────────── */
    useEffect(() => {
        logEvent('PAGE_VISIT', {
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            cookiesEnabled: navigator.cookieEnabled,
            screenRes: `${window.screen.width}x${window.screen.height}`,
            colorDepth: window.screen.colorDepth,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            referrer: document.referrer,
            canvasHash: getCanvasFingerprint(),
            gpuRenderer: getWebGLRenderer(),
            fontsDetected: detectFonts(),
        });
    }, []);

    /* ── VERIFYING — ML classification + progress ────── */
    useEffect(() => {
        if (stage !== STAGES.VERIFYING) return;

        const checkUser = async () => {
            try {
                const res = await fetch('/api/trap/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        input_text: `${credentials.username} ${credentials.password}`,
                        ip_address: null,
                        user_agent: navigator.userAgent,
                    }),
                });
                const data = await res.json();

                if (data.status === 'benign' || data.is_malicious === false) {
                    // Real user — fast-track to benign
                    setTimeout(() => setStage(STAGES.BENIGN), 1200);
                    return;
                }

                // Malicious user — run full deception progress bar
                runVerifyProgress();
            } catch {
                runVerifyProgress(); // On error, still show deception
            }
        };

        const runVerifyProgress = () => {
            let current = 0;
            const addLog = (text) => setVerifyLogs(p => [...p, text]);
            const interval = setInterval(() => {
                current += 0.22;
                if (current >= 99) {
                    current = 99;
                    clearInterval(interval);
                    // Bypassing Error/MFA stages directly to Loading
                    setTimeout(() => setStage(STAGES.LOADING), 1000);
                }
                setProgress(current);
                const msg = VERIFY_LOG_LINES.filter(m => current >= m.at).pop();
                if (msg) setVerifyLogs(prev => {
                    if (prev[prev.length - 1] !== msg.text) return [...prev, msg.text];
                    return prev;
                });
            }, 100);
        };

        checkUser();
    }, [stage]); // eslint-disable-line react-hooks/exhaustive-deps

    /* ── LOADING progress ────────────────────────────── */
    useEffect(() => {
        if (stage !== STAGES.LOADING) return;
        let current = 0;
        const interval = setInterval(() => {
            current += 0.35;
            if (current >= 100) {
                current = 100;
                clearInterval(interval);
                setTimeout(() => setStage(STAGES.DASHBOARD), 400);
            }
            setLoadProgress(current);
            const msg = LOAD_LOG_LINES.filter(m => current >= m.at).pop();
            if (msg) setLoadLogs([msg.text]);
        }, 100);
        return () => clearInterval(interval);
    }, [stage]);

    /* ── DASHBOARD auto-terminate after 5 min ────────── */
    useEffect(() => {
        if (stage !== STAGES.DASHBOARD) return;
        terminationTimerRef.current = setTimeout(() => setStage(STAGES.TERMINATED), 5 * 60 * 1000);
        return () => clearTimeout(terminationTimerRef.current);
    }, [stage]);

    /* ── MFA countdown ───────────────────────────────── */
    useEffect(() => {
        if (stage !== STAGES.MFA) return;
        let secs = 299;
        const t = setInterval(() => {
            secs--;
            const el = document.querySelector('.trap2-countdown');
            if (el) el.textContent = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, '0')}`;
            if (secs <= 0) clearInterval(t);
        }, 1000);
        return () => clearInterval(t);
    }, [stage]);

    /* ── TC-PSO: apply tarpit delay before "page loads" */
    const applyTarpitDelay = useCallback(async (item) => {
        try {
            const res = await fetch('/api/meta-heuristics/stats');
            const data = await res.json();
            const delay = data?.tc_pso?.SQLI?.global_best_delay || data?.pso?.SQLI?.global_best_delay || 0;
            if (delay > 0.5) {
                // Add minor UI jitter so it doesn't look completely stuck at flat 3.0
                const displayDelay = delay === 3.0 ? delay + (Math.random() * 1.5 - 0.5) : delay;
                setActiveDelay(displayDelay);
                await new Promise(r => setTimeout(r, displayDelay * 1000));
                setActiveDelay(0);
            }
        } catch {
            setActiveDelay(0);
        }
    }, []);

    const handleItemClick = useCallback(async (item) => {
        setClickedItem(item);
        logEvent('DASHBOARD_INTERACTION', { item });
        await applyTarpitDelay(item);
        setTimeout(() => setClickedItem(null), 2000);
    }, [applyTarpitDelay]);

    const handleRetry = () => {
        logEvent('RETRY_ATTEMPT', {});
        setProgress(0);
        setVerifyLogs([]);
        setStage(STAGES.MFA);
    };

    const DECOY_DATA = {
        user: {
            name: credentials.username || 'j.morrison',
            role: 'Network Administrator',
        },
        stats: [
            { label: 'Active Sessions', value: '1,247', change: '+3%' },
            { label: 'Network Devices', value: '342', change: '+1' },
            { label: 'Security Alerts', value: '7', change: '-2' },
            { label: 'System Health', value: '98.2%', change: 'Good' },
        ],
        alerts: [
            { time: '10:42 AM', msg: 'Firewall rule updated: rule-847', sev: 'info' },
            { time: '09:15 AM', msg: 'Failed login attempt: user admin', sev: 'warn' },
            { time: '08:30 AM', msg: 'Certificate renewal: cert-prod-02', sev: 'info' },
            { time: 'Yesterday', msg: 'Patch deployed: KB5023696', sev: 'info' },
            { time: 'Yesterday', msg: 'VPN tunnel established: BR-NYC-01', sev: 'info' },
        ],
    };

    switch (stage) {
        case STAGES.LOGIN:
            return <StageLogin onSubmit={() => { setProgress(0); setVerifyLogs([]); setStage(STAGES.VERIFYING); }} credentials={credentials} setCredentials={setCredentials} />;
        case STAGES.VERIFYING:
            return <StageVerifying progress={progress} logs={verifyLogs} />;
        case STAGES.ERROR:
            return <StageError onRetry={handleRetry} />;
        case STAGES.MFA:
            return <StageMFA mfaCode={mfaCode} setMfaCode={setMfaCode} mfaError={mfaError} setMfaError={setMfaError} onSubmit={() => setStage(STAGES.LOADING)} />;
        case STAGES.LOADING:
            return <StageLoading progress={loadProgress} logs={loadLogs} />;
        case STAGES.DASHBOARD:
            return <StageDashboard data={DECOY_DATA} onItemClick={handleItemClick} clickedItem={clickedItem} activeDelay={activeDelay} activePath={activePath} setActivePath={setActivePath} />;
        case STAGES.TERMINATED:
            return <StageTerminated credentials={credentials} />;
        case STAGES.BENIGN:
            return <StageBenign credentials={credentials} />;
        default:
            return null;
    }
}
