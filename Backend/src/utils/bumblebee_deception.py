"""
Bumblebee Deception Layer — Chameleon Integration
Dual purpose:
  1. Real scans: protect the dev machine before pushing code
  2. Fake scans: generate bait JSON served to attackers
"""

import subprocess
import json
import os
import uuid
import tempfile
from datetime import datetime, timezone


BUMBLEBEE_BINARY = "bumblebee"


# ─────────────────────────────────────────────
# REAL SCAN — protects your actual machine
# ─────────────────────────────────────────────

def run_bumblebee_scan(profile: str = "baseline", path: str = None) -> list:
    """
    Runs a real Bumblebee scan on the host machine.
    Call this before git push to check for compromised packages.
    profile: 'baseline' | 'project' | 'deep'
    """
    cmd = [BUMBLEBEE_BINARY, "scan", "--profile", profile, "--output", "file"]
    if path:
        cmd += ["--root", path]

    with tempfile.NamedTemporaryFile(suffix=".ndjson", delete=False, mode="w") as f:
        out_path = f.name

    cmd += ["--output-file", out_path]

    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        findings = []
        with open(out_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    findings.append(json.loads(line))
        return findings
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return []
    finally:
        if os.path.exists(out_path):
            os.unlink(out_path)


# ─────────────────────────────────────────────
# FAKE SCAN — bait for attackers
# ─────────────────────────────────────────────

def generate_fake_scan_bait(attacker_ip: str, threat_level: float) -> dict:
    """
    Generates a FAKE Bumblebee scan result to deceive attackers.
    threat_level comes from BiLSTM anomaly score A(t) in [0,1].
    Higher score = more juicy fake findings to keep attacker engaged longer.
    """

    bait_pool = {
        "low": [
            {
                "ecosystem": "npm",
                "package_name": "lodash",
                "version": "4.17.15",
                "severity": "low",
                "evidence": "outdated release, no active exploit",
            },
        ],
        "medium": [
            {
                "ecosystem": "pypi",
                "package_name": "requests",
                "version": "2.28.0",
                "severity": "medium",
                "evidence": "urllib3 dependency CVE-2023-43804",
            },
            {
                "ecosystem": "npm",
                "package_name": "axios",
                "version": "0.21.1",
                "severity": "medium",
                "evidence": "ReDoS via crafted URL input",
            },
        ],
        "high": [
            {
                "ecosystem": "pypi",
                "package_name": "cryptography",
                "version": "3.4.7",
                "severity": "critical",
                "evidence": "OpenSSL backend heap overflow CVE-2023-0286",
            },
            {
                "ecosystem": "npm",
                "package_name": "node-fetch",
                "version": "2.6.1",
                "severity": "high",
                "evidence": "prototype pollution via unsanitized headers CVE-2023-25653",
            },
            {
                "ecosystem": "npm",
                "package_name": "@anthropic-ai/sdk",
                "version": "0.9.0",
                "severity": "medium",
                "evidence": "API key leakage via verbose error logging",
            },
        ],
    }

    # Scale bait richness with threat level
    if threat_level < 0.3:
        selected = bait_pool["low"]
    elif threat_level < 0.7:
        selected = bait_pool["low"] + bait_pool["medium"]
    else:
        selected = bait_pool["low"] + bait_pool["medium"] + bait_pool["high"]

    run_id = uuid.uuid4().hex
    scan_time = datetime.now(timezone.utc).isoformat()

    findings = []
    for pkg in selected:
        findings.append({
            "record_type": "finding",
            "record_id": f"finding:{uuid.uuid4().hex}",
            "schema_version": "0.1.0",
            "scanner_name": "bumblebee",
            "scanner_version": "v0.1.1",
            "run_id": run_id,
            "scan_time": scan_time,
            "endpoint": {
                "hostname": "dev-workstation-01",
                "os": "linux",
                "arch": "x86_64",
                "username": "developer",
            },
            "profile": "deep",
            "finding_type": "package_exposure",
            "severity": pkg["severity"],
            "ecosystem": pkg["ecosystem"],
            "package_name": pkg["package_name"],
            "version": pkg["version"],
            "confidence": "high",
            "evidence": pkg["evidence"],
            "_chameleon_meta": {
                "is_bait": True,
                "attacker_ip": attacker_ip,
                "threat_level": round(threat_level, 4),
            },
        })

    summary = {
        "total": len(findings),
        "critical": sum(1 for f in findings if f["severity"] == "critical"),
        "high": sum(1 for f in findings if f["severity"] == "high"),
        "medium": sum(1 for f in findings if f["severity"] == "medium"),
        "low": sum(1 for f in findings if f["severity"] == "low"),
    }

    return {"scan_summary": summary, "findings": findings}


# ─────────────────────────────────────────────
# FAKE MCP CONFIG — extra bait layer
# ─────────────────────────────────────────────

def get_fake_mcp_config_bait() -> dict:
    """
    Returns a fake claude_desktop_config.json / mcp.json style object.
    Bumblebee scans these in real dev environments — attackers know to look for them.
    The fake tokens look real enough to waste attacker time.
    """
    return {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem",
                         "/home/developer/projects"],
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_BAIT_TOKEN_xK9mP2nQ7rL4vF8wZ"
                },
            },
            "postgres": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres",
                         "postgresql://developer:bait_password@localhost/proddb"],
            },
        }
    }


# ─────────────────────────────────────────────
# QUICK LOCAL TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Testing fake scan bait (threat_level=0.85) ===")
    result = generate_fake_scan_bait("10.0.0.1", 0.85)
    print(json.dumps(result, indent=2))

    print("\n=== Testing fake MCP config bait ===")
    mcp = get_fake_mcp_config_bait()
    print(json.dumps(mcp, indent=2))
