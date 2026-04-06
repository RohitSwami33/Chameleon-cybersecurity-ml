import React, { useState, useRef, useEffect } from 'react';

export function FakeTerminal({ activeDelay, onCommand }) {
    const [history, setHistory] = useState(['NexaCorp Secure Shell v4.1', 'Type "help" for a list of commands.']);
    const [input, setInput] = useState('');
    const bottomRef = useRef(null);

    useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [history, activeDelay]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && input.trim()) {
            const cmd = input.trim();
            setHistory(p => [...p, `admin@nexa-core:~$ ${cmd}`]);
            setInput('');
            onCommand(cmd);
            
            setTimeout(() => {
                let resp = '';
                if (cmd === 'ls') resp = 'drwxr-xr-x 4 root log 4096 Apr  7 04:00 ./\ndrwxr-xr-x 8 root bin 4096 Mar 15 12:00 ../\n-rw------- 1 root root 1485 Apr  7 04:01 admin_rsa\n-rw-r--r-- 1 root root  220 Apr  7 04:01 .bash_logout';
                else if (cmd === 'whoami') resp = 'admin (uid=0, euid=0)';
                else if (cmd.startsWith('cat')) resp = `cat: ${cmd.split(' ')[1]}: Permission denied (requires hardware sign-in)`;
                else if (cmd === 'help') resp = 'Available commands: ls, cat, ping, whoami, ssh, top, tail, grep';
                else resp = `bash: ${cmd.split(' ')[0]}: command not found`;
                
                setHistory(p => [...p, resp]);
            }, activeDelay ? (activeDelay * 1000) + 500 : 1000);
        }
    };

    return (
        <div className="trap2-panel" style={{ height: '500px', display: 'flex', flexDirection: 'column', background: '#0a0a0a', border: '1px solid #333' }}>
            <div className="trap2-panel-header" style={{ background: '#1a1a1a', borderBottom: '1px solid #333' }}>
                <span className="trap2-panel-title" style={{ color: '#00e676', fontFamily: 'monospace' }}>💻 root@nexa-core:~</span>
            </div>
            <div style={{ flex: 1, padding: '16px', overflowY: 'auto', color: '#00e676', fontFamily: 'monospace', fontSize: '13px', whiteSpace: 'pre-wrap' }}>
                {history.map((line, i) => <div key={i} style={{ marginBottom: '4px' }}>{line}</div>)}
                <div style={{ display: 'flex', marginTop: '8px' }}>
                    <span style={{ marginRight: '8px' }}>admin@nexa-core:~$</span>
                    <input 
                        value={input} 
                        onChange={e => setInput(e.target.value)} 
                        onKeyDown={handleKeyDown}
                        disabled={activeDelay > 0}
                        style={{ flex: 1, background: 'transparent', border: 'none', color: '#00e676', fontFamily: 'monospace', outline: 'none' }} 
                        autoFocus
                    />
                </div>
                <div ref={bottomRef} />
            </div>
        </div>
    );
}

export function FakeDatabase({ activeDelay, onQuery }) {
    const [query, setQuery] = useState('SELECT * FROM employees LIMIT 10;');
    const [results, setResults] = useState(null);

    const executeInfo = () => {
        onQuery(query);
        setTimeout(() => {
            if (query.toLowerCase().includes('drop') || query.toLowerCase().includes('delete') || query.toLowerCase().includes('update')) {
                setResults({ error: 'SqlException: Table lock active or insufficient privileges.' });
            } else {
                setResults({
                    columns: ['id', 'username', 'role', 'salary_band'],
                    rows: [
                        [101, 'j.doe', 'IT_ADMIN', 'Tier 4'],
                        [102, 'm.smith', 'SEC_OPS', 'Tier 5'],
                        [103, 'admin', 'SYS_ADMIN', 'Tier 6'],
                    ]
                });
            }
        }, activeDelay ? (activeDelay * 1000) + 800 : 1500);
    };

    return (
        <div className="trap2-panel">
            <div className="trap2-panel-header">
                <span className="trap2-panel-title">🗄 Primary HR Database (ReadOnly Mode)</span>
            </div>
            <div style={{ padding: '16px' }}>
                <textarea 
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    style={{ width: '100%', height: '80px', background: 'rgba(0,0,0,0.4)', border: '1px solid #334', color: '#ffaa00', fontFamily: 'monospace', padding: '8px', borderRadius: '4px' }}
                />
                <button 
                    onClick={executeInfo}
                    className="trap2-btn-primary" 
                    style={{ marginTop: '12px', padding: '6px 16px' }}
                    disabled={activeDelay > 0}
                >
                    ▶ Execute Query
                </button>

                <div style={{ marginTop: '24px', borderTop: '1px solid #223', paddingTop: '16px', overflowX: 'auto' }}>
                    {results?.error && <div style={{ color: '#ff3344', fontFamily: 'monospace' }}>[ERROR] {results.error}</div>}
                    {results?.rows && (
                        <table className="trap2-table">
                            <thead><tr>{results.columns.map(c => <th key={c} style={{ padding: '8px', textAlign: 'left', borderBottom: '1px solid #334', color: '#88a' }}>{c}</th>)}</tr></thead>
                            <tbody>
                                {results.rows.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j} style={{ padding: '8px', borderBottom: '1px solid #223' }}>{c}</td>)}</tr>)}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}

export function FakeSecurityControls({ activeDelay, onToggle }) {
    const [firewall, setFW] = useState(true);
    const [ids, setIDS] = useState(true);

    const handleToggle = (name) => {
        onToggle(`${name}_DISABLE_ATTEMPT`);
        setTimeout(() => {
            alert(`[ERROR] Policy enforcement prevents modifying ${name}. Escalating privileges required.`);
        }, activeDelay ? (activeDelay * 1000) + 1000 : 2000);
    };

    return (
        <div className="trap2-panel">
            <div className="trap2-panel-header">
                <span className="trap2-panel-title">🛡 Perimeter Security Policy</span>
            </div>
            <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '8px' }}>
                    <div>
                        <div style={{ color: '#e8f4fd', fontWeight: 600 }}>Enterprise WAF & Firewall</div>
                        <div style={{ color: '#7a9bbf', fontSize: '12px' }}>Inbound/Outbound traffic filtering and deep packet inspection.</div>
                    </div>
                    <button onClick={() => handleToggle('FIREWALL')} disabled={activeDelay > 0} className={firewall ? 'trap2-btn-ghost' : 'trap2-btn-primary'} style={{ borderColor: firewall ? '#00e676' : '#ff3344', color: firewall ? '#00e676' : '#fff' }}>
                        {firewall ? 'ENABLED (Click to Disable)' : 'DISABLED'}
                    </button>
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '8px' }}>
                    <div>
                        <div style={{ color: '#e8f4fd', fontWeight: 600 }}>Intrusion Detection System (IDS)</div>
                        <div style={{ color: '#7a9bbf', fontSize: '12px' }}>Real-time anomalous pattern recognition and alert dispatching.</div>
                    </div>
                    <button onClick={() => handleToggle('IDS')} disabled={activeDelay > 0} className={ids ? 'trap2-btn-ghost' : 'trap2-btn-primary'} style={{ borderColor: ids ? '#00e676' : '#ff3344', color: ids ? '#00e676' : '#fff' }}>
                        {ids ? 'ENABLED (Click to Disable)' : 'DISABLED'}
                    </button>
                </div>
            </div>
        </div>
    );
}
