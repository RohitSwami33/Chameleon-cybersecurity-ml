import React, { useState, useEffect, useRef } from 'react';

const STAGES = {
    LOGIN: 'LOGIN',
    VERIFYING: 'VERIFYING',
    ERROR: 'ERROR',
    MFA: 'MFA',
    LOADING: 'LOADING',
    DASHBOARD: 'DASHBOARD',
    TERMINATED: 'TERMINATED',
<<<<<<< HEAD
=======
    BENIGN: 'BENIGN',  // New stage for benign users
>>>>>>> 5035a73d50efbedccaead6fb1e12408899a269ef
};

const VERIFY_MESSAGES = [
    { at: 0, text: 'Connecting to authentication server...' },
    { at: 8, text: 'Verifying corporate credentials...' },
    { at: 18, text: 'Checking Active Directory membership...' },
    { at: 28, text: 'Validating security certificates...' },
    { at: 38, text: 'Establishing secure session...' },
    { at: 44, text: 'Finalizing authentication handshake...' },
];

const LOAD_MESSAGES = [
    { at: 0, text: 'Authenticating session token...' },
    { at: 5, text: 'Loading user profile and permissions...' },
    { at: 10, text: 'Connecting to enterprise services...' },
    { at: 16, text: 'Syncing SharePoint data...' },
    { at: 22, text: 'Loading dashboard modules...' },
    { at: 27, text: 'Almost ready...' },
];

// Reusable logic
function getCanvasFingerprint() {
    try {
        const c = document.createElement('canvas');
        const ctx = c.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillText('SecureNet_fp_2024', 2, 2);
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
    const testFonts = ['Calibri', 'Cambria', 'Consolas', 'Courier New',
        'Georgia', 'Segoe UI', 'Tahoma', 'Times New Roman',
        'Trebuchet MS', 'Verdana', 'Arial Black'];
    const detected = [];
    const span = document.createElement('span');
    span.style.cssText = 'position:absolute;visibility:hidden;font-size:72px';
    span.innerHTML = 'mmmmmmmmmmlli';
    document.body.appendChild(span);
    const baseW = span.offsetWidth;
    testFonts.forEach(font => {
        span.style.fontFamily = `'${font}', monospace`;
        if (span.offsetWidth !== baseW) detected.push(font);
    });
    document.body.removeChild(span);
    return detected;
}


// Sub-components
function StageLogin({ onSubmit, credentials, setCredentials }) {
    return (
        <div className="trap-page">
            <header className="trap-header">
                <div className="trap-logo">
                    🔒 <span>SecureNet</span> Enterprise Portal
                </div>
                <span className="trap-header-right">IT Helpdesk: ext. 4400</span>
            </header>
            <div className="trap-card">
                <div className="trap-card-header">
                    <h2>Employee Login</h2>
                    <p>Sign in with your corporate credentials</p>
                </div>
                <div className="trap-notice">
                    ⚠ This system is for authorized users only. All access is
                    monitored and logged in accordance with IT Policy 4.2.
                </div>
                <div className="trap-form">
                    <label>Username</label>
                    <input
                        type="text"
                        placeholder="firstname.lastname"
                        value={credentials.username}
                        onChange={e => setCredentials(p => ({ ...p, username: e.target.value }))}
                        autoComplete="username"
                    />
                    <label>Password</label>
                    <input
                        type="password"
                        placeholder="••••••••"
                        value={credentials.password}
                        onChange={e => setCredentials(p => ({ ...p, password: e.target.value }))}
                        autoComplete="current-password"
                    />
                    <div className="trap-form-row">
                        <label className="trap-checkbox">
                            <input type="checkbox" /> Remember this device
                        </label>
                        <a href="#" onClick={e => e.preventDefault()} className="trap-link">
                            Forgot password?
                        </a>
                    </div>
                    <button
                        className="trap-btn-primary"
                        onClick={() => {
                            fetch('/api/honeypot/log', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    event: 'LOGIN_ATTEMPT',
                                    data: {
                                        username: credentials.username,
                                        passwordLength: credentials.password.length,
                                        passwordPattern: credentials.password.replace(/[a-z]/gi, 'x')
                                            .replace(/[0-9]/g, 'n')
                                            .replace(/[^xn]/g, 's'),
                                        timestamp: new Date().toISOString(),
                                    }
                                }),
                            }).catch(() => { });
                            onSubmit();
                        }}
                    >
                        Sign In →
                    </button>
                </div>
                <div className="trap-footer-links">
                    <a href="#" onClick={e => e.preventDefault()}>New Employee Setup</a>
                    <span>•</span>
                    <a href="#" onClick={e => e.preventDefault()}>VPN Instructions</a>
                    <span>•</span>
                    <a href="#" onClick={e => e.preventDefault()}>IT Support Portal</a>
                </div>
            </div>
            <footer className="trap-footer">
<<<<<<< HEAD
                © 2024 SecureNet Enterprise Systems v4.2.1 | IT Support: ext. 4400
=======
                © 2026 SecureNet Enterprise Systems v4.2.1 | IT Support: ext. 4400
>>>>>>> 5035a73d50efbedccaead6fb1e12408899a269ef
                <br />
                <small>For technical issues contact helpdesk@securenet.internal</small>
            </footer>
        </div>
    );
}

function StageVerifying({ progress, currentMessage }) {
    return (
        <div className="trap-page">
            <header className="trap-header">
                <div className="trap-logo">🔒 <span>SecureNet</span> Enterprise Portal</div>
            </header>
            <div className="trap-card trap-card-center">
                <div className="trap-spinner" />
                <h3>Verifying Credentials</h3>
                <p className="trap-status-text">{currentMessage}</p>
                <div className="trap-progress-track">
                    <div
                        className="trap-progress-fill"
                        style={{ width: `${progress}%` }}
                    />
                </div>
                <span className="trap-progress-pct">{Math.floor(progress)}%</span>
                <p className="trap-hint">
                    Please wait. Do not close this window or press the back button.
                </p>
                <div className="trap-log-terminal">
                    <div>{'>'} SYS_AUTH: Initializing secure channel...</div>
                    {progress > 8 && <div>{'>'} LDAP: Querying DC01.securenet.internal...</div>}
                    {progress > 18 && <div>{'>'} CERT: Validating chain CA2 → CA1 → Root...</div>}
                    {progress > 28 && <div>{'>'} 2FA: Checking device trust registry...</div>}
                    {progress > 38 && <div>{'>'} SESSION: Generating ephemeral token...</div>}
                    {progress > 44 && <div className="trap-log-warn">{'>'} WARN: Response timeout on auth-node-3...</div>}
                </div>
            </div>
        </div>
    );
}

function StageError({ onRetry }) {
    return (
        <div className="trap-page">
            <header className="trap-header">
                <div className="trap-logo">🔒 <span>SecureNet</span> Enterprise Portal</div>
            </header>
            <div className="trap-card trap-card-center">
                <div className="trap-error-icon">✕</div>
                <h3 style={{ color: '#c0392b' }}>Authentication Failed</h3>
                <div className="trap-error-box">
                    <strong>Error Code:</strong> AUTH_SRV_TIMEOUT_0x80090304<br />
                    <strong>Details:</strong> Authentication server unreachable<br />
                    <strong>Node:</strong> auth-node-3.securenet.internal:8443<br />
                    <strong>Time:</strong> {new Date().toLocaleTimeString()}<br />
                    <strong>Trace ID:</strong> {Math.random().toString(36).substr(2, 16).toUpperCase()}
                </div>
                <p className="trap-hint">
                    Your credentials may be correct. This is a temporary server issue.
                    Please try again or contact IT Support at ext. 4400.
                </p>
                <div className="trap-btn-row">
                    <button className="trap-btn-primary" onClick={onRetry}>
                        ↺ Try Again
                    </button>
                    <button
                        className="trap-btn-secondary"
                        onClick={e => e.preventDefault()}
                    >
                        Contact Support
                    </button>
                </div>
                <p className="trap-incident">
                    Incident automatically logged. Reference: <strong>INC-{
                        Math.floor(Math.random() * 90000) + 10000
                    }</strong>
                </p>
            </div>
        </div>
    );
}

function StageMFA({ mfaCode, setMfaCode, mfaError, onSubmit, setMfaError }) {
    const handleInput = (e) => {
        const val = e.target.value.replace(/\D/g, '').slice(0, 6);
        setMfaCode(val);
    };

    return (
        <div className="trap-page">
            <header className="trap-header">
                <div className="trap-logo">🔒 <span>SecureNet</span> Enterprise Portal</div>
            </header>
            <div className="trap-card trap-card-center">
                <div className="trap-mfa-icon">📱</div>
                <h3>Two-Factor Authentication</h3>
                <p>
                    A 6-digit verification code has been sent to your registered
                    device ending in <strong>••••7284</strong>.
                </p>
                <div className="trap-mfa-input-group">
                    <input
                        type="text"
                        inputMode="numeric"
                        maxLength={6}
                        placeholder="000000"
                        value={mfaCode}
                        onChange={handleInput}
                        className={`trap-mfa-input ${mfaError ? 'trap-input-error' : ''}`}
                        autoFocus
                    />
                    {mfaError && (
                        <span className="trap-field-error">
                            Please enter a valid 6-digit code
                        </span>
                    )}
                </div>
                <div className="trap-mfa-hints">
                    <p>⏱ Code expires in <strong className="trap-countdown">4:59</strong></p>
                    <p>
                        Didn't receive a code?{' '}
                        <a href="#" onClick={e => e.preventDefault()}>Resend</a>
                        {' '}or{' '}
                        <a href="#" onClick={e => e.preventDefault()}>Use backup code</a>
                    </p>
                </div>
                <button
                    className="trap-btn-primary"
                    onClick={() => {
                        if (mfaCode.length !== 6) {
                            setMfaError(true);
                            return;
                        }
                        setMfaError(false);
                        fetch('/api/honeypot/log', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                event: 'MFA_ATTEMPT',
                                data: { code: mfaCode, timestamp: new Date().toISOString() }
                            }),
                        }).catch(() => { });
                        onSubmit();
                    }}
                >
                    Verify →
                </button>
            </div>
        </div>
    );
}

function StageLoading({ progress, currentMessage }) {
    return (
        <div className="trap-page trap-page-dark">
            <div className="trap-loading-screen">
                <div className="trap-success-banner">
                    ✓ Code accepted. Establishing secure session...
                </div>
                <div className="trap-loading-logo">
                    🔒 SecureNet Enterprise
                </div>
                <p className="trap-loading-msg">{currentMessage}</p>
                <div className="trap-progress-track trap-progress-wide">
                    <div
                        className="trap-progress-fill trap-progress-green"
                        style={{ width: `${progress}%` }}
                    />
                </div>
                <div className="trap-module-list">
                    {[
                        'User Authentication',
                        'Permission Matrix',
                        'Dashboard Core',
                        'Analytics Engine',
                        'Notification Service',
                        'Document Library',
                    ].map((mod, i) => (
                        <div key={mod} className="trap-module-item">
                            {progress > (i + 1) * 15
                                ? <span className="trap-check">✓</span>
                                : <span className="trap-spinner-sm" />
                            }
                            {mod}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

function StageDashboard({ data, onItemClick, clickedItem }) {
    return (
        <div className="trap-fake-dashboard">
            <div className="trap-dash-topbar">
                <div className="trap-dash-logo">🔒 SecureNet Enterprise</div>
                <div className="trap-dash-user">
                    👤 {data.user.name} | {data.user.role}
                    <button onClick={() => onItemClick('logout')}>Sign Out</button>
                </div>
            </div>
            <div className="trap-dash-body">
                <nav className="trap-dash-nav">
                    {data.navItems.map(item => (
                        <button
                            key={item}
                            className="trap-nav-item"
                            onClick={() => onItemClick(item)}
                        >
                            {item}
                            {clickedItem === item && (
                                <span className="trap-inline-spinner" />
                            )}
                        </button>
                    ))}
                </nav>
                <main className="trap-dash-main">
                    <div className="trap-stats-row">
                        {data.stats.map(s => (
                            <div
                                key={s.label}
                                className="trap-stat-card"
                                onClick={() => onItemClick(s.label)}
                            >
                                <div className="trap-stat-value">{s.value}</div>
                                <div className="trap-stat-label">{s.label}</div>
                                <div className="trap-stat-change">{s.change}</div>
                                {clickedItem === s.label && (
                                    <div className="trap-card-loading">
                                        <span className="trap-spinner-sm" /> Loading...
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                    <div className="trap-section">
                        <h4>Recent Security Alerts</h4>
                        <table className="trap-table" onClick={() => onItemClick('alerts-table')}>
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Event</th>
                                    <th>Severity</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.alerts.map((a, i) => (
                                    <tr key={i} onClick={() => onItemClick(`alert-${i}`)}>
                                        <td>{a.time}</td>
                                        <td>{a.msg}</td>
                                        <td><span className={`trap-badge trap-badge-${a.sev}`}>{a.sev}</span></td>
                                        <td>
                                            {clickedItem === `alert-${i}` ? (
                                                <span className="trap-spinner-sm" />
                                            ) : (
                                                <button className="trap-action-btn">View</button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    {clickedItem && !clickedItem.startsWith('alert-') && (
                        <div className="trap-loading-overlay">
                            <span className="trap-spinner" />
                            <p>Loading {clickedItem}...</p>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
}

function StageTerminated({ credentials }) {
    const incidentId = useRef(
        `CF-${Math.floor(Math.random() * 9000) + 1000}`
    );
    const traceId = useRef(
        Array.from({ length: 16 }, () =>
            Math.floor(Math.random() * 16).toString(16)
        ).join('').toUpperCase()
    );

    useEffect(() => {
        fetch('/api/honeypot/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event: 'SESSION_TERMINATED',
                data: {
                    incidentId: incidentId.current,
                    username: credentials.username,
                    duration: '~8 minutes',
                    timestamp: new Date().toISOString(),
                }
            }),
        }).catch(() => { });
    }, [credentials.username]);

    return (
        <div className="trap-terminated-page">
            <div className="trap-terminated-border" />
            <div className="trap-terminated-card">
                <div className="trap-terminated-icon">⚠</div>
                <h1 className="trap-terminated-title">SESSION TERMINATED</h1>
                <div className="trap-terminated-divider" />
                <p className="trap-terminated-reason">
                    Anomalous access pattern detected.
                    This incident has been logged and reported.
                </p>
                <div className="trap-terminated-details">
                    <div className="trap-detail-row">
                        <span>Incident ID</span>
                        <strong>{incidentId.current}</strong>
                    </div>
                    <div className="trap-detail-row">
                        <span>Status</span>
                        <strong style={{ color: '#e74c3c' }}>FILED — UNDER REVIEW</strong>
                    </div>
                    <div className="trap-detail-row">
                        <span>Timestamp</span>
                        <strong>{new Date().toLocaleString()}</strong>
                    </div>
                    <div className="trap-detail-row">
                        <span>Trace ID</span>
                        <strong style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                            {traceId.current}
                        </strong>
                    </div>
                    <div className="trap-detail-row">
                        <span>Action Taken</span>
                        <strong>Connection flagged • IP logged • Admin notified</strong>
                    </div>
                </div>
                <div className="trap-trace-animation">
                    <div className="trap-trace-line">
                        Tracing connection origin...
                    </div>
                    <div className="trap-trace-line trap-trace-done">
                        ✓ Origin identified and logged
                    </div>
                    <div className="trap-trace-line trap-trace-done">
                        ✓ Report filed with security team
                    </div>
                    <div className="trap-trace-line trap-trace-done">
                        ✓ Evidence package archived
                    </div>
                </div>
                <p className="trap-terminated-footer">
                    If you believe this is an error, contact IT Security
                    at security@securenet.internal with reference <strong>{incidentId.current}</strong>
                </p>
            </div>
        </div>
    );
}

<<<<<<< HEAD
=======
// Component for benign users - shows "User is Normal" message
function StageBenign({ credentials }) {
    return (
        <div className="trap-page">
            <header className="trap-header">
                <div className="trap-logo">🔒 <span>SecureNet</span> Enterprise Portal</div>
            </header>
            <div className="trap-card trap-card-center">
                <div className="trap-success-icon" style={{ fontSize: '64px', marginBottom: '20px' }}>✓</div>
                <h3 style={{ color: '#00e676' }}>Authentication Successful</h3>
                <div className="trap-success-box" style={{
                    backgroundColor: 'rgba(0, 230, 118, 0.1)',
                    border: '1px solid rgba(0, 230, 118, 0.3)',
                    borderRadius: '8px',
                    padding: '20px',
                    marginTop: '20px',
                    marginBottom: '20px'
                }}>
                    <strong style={{ color: '#00e676' }}>User Verified Successfully</strong><br />
                    <span style={{ color: '#7a9bbf' }}>Welcome, {credentials.username || 'User'}</span><br />
                    <span style={{ color: '#7a9bbf', fontSize: '12px' }}>Your credentials have been validated.</span>
                </div>
                <p className="trap-hint">
                    You will be redirected to the dashboard shortly.
                </p>
                <div className="trap-btn-row">
                    <a
                        href="/dashboard"
                        className="trap-btn-primary"
                        style={{ textDecoration: 'none', display: 'inline-block' }}
                    >
                        Continue to Dashboard →
                    </a>
                </div>
            </div>
            <footer className="trap-footer">
                © 2026 SecureNet Enterprise Systems v4.2.1 | IT Support: ext. 4400
                <br />
                <small>For technical issues contact helpdesk@securenet.internal</small>
            </footer>
        </div>
    );
}

>>>>>>> 5035a73d50efbedccaead6fb1e12408899a269ef

// Main Component
export default function TrapInterface() {
    const [stage, setStage] = useState(STAGES.LOGIN);
    const [progress, setProgress] = useState(0);
    const [mfaCode, setMfaCode] = useState('');
    const [mfaError, setMfaError] = useState(false);
    const [loadProgress, setLoadProgress] = useState(0);
    const [clickedItem, setClickedItem] = useState(null);
    const [credentials, setCredentials] = useState({ username: '', password: '' });
    const [currentMessage, setCurrentMessage] = useState(VERIFY_MESSAGES[0].text);
    const [loadMessage, setLoadMessage] = useState(LOAD_MESSAGES[0].text);
    const terminationTimerRef = useRef(null);

    useEffect(() => {
        const fingerprint = {
            timestamp: new Date().toISOString(),
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
        };

        fetch('/api/honeypot/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event: 'PAGE_VISIT', data: fingerprint }),
        }).catch(() => { });
    }, []);

    useEffect(() => {
        if (stage !== STAGES.VERIFYING) return;
<<<<<<< HEAD
        let current = 0;
        const interval = setInterval(() => {
            current += (100 / 45) * 0.1;
            if (current >= 99) {
                current = 99;
                clearInterval(interval);
                setTimeout(() => setStage(STAGES.ERROR), 3000);
            }
            setProgress(current);
            const msg = VERIFY_MESSAGES.filter(m => current >= m.at).pop();
            setCurrentMessage(msg?.text ?? VERIFY_MESSAGES[0].text);
        }, 100);
        return () => clearInterval(interval);
    }, [stage]);
=======

        // Call the backend API to check if user is benign or malicious
        const checkUserType = async () => {
            try {
                const response = await fetch('/api/trap/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        input_text: `LOGIN:${credentials.username}`,
                        ip_address: null,
                        user_agent: navigator.userAgent,
                    }),
                });

                const data = await response.json();

                // Check if user is benign
                if (data.status === 'benign' || data.is_malicious === false) {
                    // User is benign - show success page
                    setTimeout(() => setStage(STAGES.BENIGN), 1500);
                } else {
                    // User is malicious - continue with deception flow
                    let current = 0;
                    const interval = setInterval(() => {
                        current += (100 / 45) * 0.1;
                        if (current >= 99) {
                            current = 99;
                            clearInterval(interval);
                            setTimeout(() => setStage(STAGES.ERROR), 3000);
                        }
                        setProgress(current);
                        const msg = VERIFY_MESSAGES.filter(m => current >= m.at).pop();
                        setCurrentMessage(msg?.text ?? VERIFY_MESSAGES[0].text);
                    }, 100);
                }
            } catch (error) {
                console.error('Error checking user type:', error);
                // On error, continue with deception flow for safety
                let current = 0;
                const interval = setInterval(() => {
                    current += (100 / 45) * 0.1;
                    if (current >= 99) {
                        current = 99;
                        clearInterval(interval);
                        setTimeout(() => setStage(STAGES.ERROR), 3000);
                    }
                    setProgress(current);
                    const msg = VERIFY_MESSAGES.filter(m => current >= m.at).pop();
                    setCurrentMessage(msg?.text ?? VERIFY_MESSAGES[0].text);
                }, 100);
            }
        };

        checkUserType();
    }, [stage, credentials.username]);
>>>>>>> 5035a73d50efbedccaead6fb1e12408899a269ef

    useEffect(() => {
        if (stage !== STAGES.LOADING) return;
        let current = 0;
        const interval = setInterval(() => {
            current += (100 / 30) * 0.1;
            if (current >= 100) {
                current = 100;
                clearInterval(interval);
                setTimeout(() => setStage(STAGES.DASHBOARD), 500);
            }
            setLoadProgress(current);
            const msg = LOAD_MESSAGES.filter(m => current >= (m.at / 30 * 100)).pop();
            setLoadMessage(msg?.text ?? LOAD_MESSAGES[0].text);
        }, 100);
        return () => clearInterval(interval);
    }, [stage]);

    useEffect(() => {
        if (stage !== STAGES.DASHBOARD) return;
        terminationTimerRef.current = setTimeout(() => {
            setStage(STAGES.TERMINATED);
        }, 5 * 60 * 1000);
        return () => clearTimeout(terminationTimerRef.current);
    }, [stage]);

    useEffect(() => {
        if (stage !== STAGES.MFA) return;
        let secs = 299;
        const t = setInterval(() => {
            secs--;
            const m = Math.floor(secs / 60);
            const s = String(secs % 60).padStart(2, '0');
            const el = document.querySelector('.trap-countdown');
            if (el) el.textContent = `${m}:${s}`;
            if (secs <= 0) clearInterval(t);
        }, 1000);
        return () => clearInterval(t);
    }, [stage]);


    const handleRetry = () => {
        fetch('/api/honeypot/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event: 'RETRY_ATTEMPT', data: { timestamp: new Date().toISOString() } }),
        }).catch(() => { });
        setProgress(0);
        setStage(STAGES.MFA);
    };

    const handleItemClick = (item) => {
        setClickedItem(item);
        fetch('/api/honeypot/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event: 'DASHBOARD_INTERACTION',
                data: { item, timestamp: new Date().toISOString() }
            }),
        }).catch(() => { });
        setTimeout(() => setClickedItem(null), 3000);
    };

    const DECOY_DATA = {
        user: {
            name: credentials.username || 'j.morrison',
            role: 'Network Administrator',
            dept: 'IT Infrastructure',
            lastLogin: 'Yesterday, 3:42 PM',
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
        navItems: [
            '📊 Dashboard', '🖥 Devices', '🔒 Security',
            '📁 Documents', '👤 Users', '⚙ Settings',
            '📈 Reports', '🔔 Alerts', '🌐 Network Map',
        ],
    };

    switch (stage) {
        case STAGES.LOGIN:
            return <StageLogin onSubmit={() => setStage(STAGES.VERIFYING)} credentials={credentials} setCredentials={setCredentials} />;
        case STAGES.VERIFYING:
            return <StageVerifying progress={progress} currentMessage={currentMessage} />;
        case STAGES.ERROR:
            return <StageError onRetry={handleRetry} />;
        case STAGES.MFA:
            return <StageMFA mfaCode={mfaCode} setMfaCode={setMfaCode} mfaError={mfaError} setMfaError={setMfaError} onSubmit={() => setStage(STAGES.LOADING)} />;
        case STAGES.LOADING:
            return <StageLoading progress={loadProgress} currentMessage={loadMessage} />;
        case STAGES.DASHBOARD:
            return <StageDashboard data={DECOY_DATA} onItemClick={handleItemClick} clickedItem={clickedItem} />;
        case STAGES.TERMINATED:
            return <StageTerminated credentials={credentials} />;
<<<<<<< HEAD
=======
        case STAGES.BENIGN:
            return <StageBenign credentials={credentials} />;
>>>>>>> 5035a73d50efbedccaead6fb1e12408899a269ef
        default:
            return null;
    }
}
