"""
Chameleon Blockchain Sync — Ethereum Sepolia Anchor
=====================================================

Scheduled background task that anchors Merkle root hashes from the
honeypot's integrity module onto the Ethereum Sepolia testnet.

Prerequisites:
    pip install web3 python-dotenv

Environment Variables (in Backend/.env):
    SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
    PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
    CONTRACT_ADDRESS=0xDEPLOYED_CONTRACT_ADDRESS

Usage:
    # As a standalone script
    python blockchain_sync.py

    # Programmatic
    from blockchain_sync import anchor_latest_root
    tx_hash = await anchor_latest_root("a1b2c3d4e5f6...")

ABI Compilation Guide:
    1. Open Remix IDE (https://remix.ethereum.org)
    2. Paste ChameleonLedger.sol into a new file
    3. Compile with Solidity 0.8.19+
    4. Go to "Compilation Details" → copy the ABI JSON
    5. Save it as Backend/contracts/ChameleonLedger.json
    OR use solcx:
        pip install py-solc-x
        python -c "
        from solcx import compile_standard, install_solc
        install_solc('0.8.19')
        # ... compile and extract ABI
        "
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.exceptions import (
    ContractLogicError,
    TransactionNotFound,
)

logger = logging.getLogger(__name__)

# ── Load .env ────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parent / ".env")

SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL", "")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")

# ── ABI ──────────────────────────────────────────────────────────────────
# Path to the compiled ABI JSON (from Remix or solcx)
ABI_PATH = Path(__file__).parent / "contracts" / "ChameleonLedger.json"

# Minimal ABI — sufficient to call storeMerkleRoot and getRootCount
# Use this if the full ABI file is not yet available.
MINIMAL_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "_rootHash", "type": "string"}],
        "name": "storeMerkleRoot",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getRootCount",
        "outputs": [{"internalType": "uint256", "name": "count", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getLatestRoot",
        "outputs": [{"internalType": "string", "name": "rootHash", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "index", "type": "uint256"}],
        "name": "getRoot",
        "outputs": [{"internalType": "string", "name": "rootHash", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "string", "name": "rootHash", "type": "string"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "index", "type": "uint256"},
        ],
        "name": "RootStored",
        "type": "event",
    },
]


def _load_abi() -> list:
    """Load ABI from JSON file, falling back to minimal inline ABI."""
    if ABI_PATH.exists():
        with open(ABI_PATH, "r") as f:
            data = json.load(f)
            # Handle both raw ABI array and Remix-style { "abi": [...] }
            return data if isinstance(data, list) else data.get("abi", MINIMAL_ABI)
    logger.info("ABI file not found at %s, using minimal inline ABI", ABI_PATH)
    return MINIMAL_ABI


def _get_web3() -> Web3:
    """
    Create a Web3 instance connected to Sepolia.

    Supports HTTP (Infura/Alchemy) and WebSocket providers.
    """
    if not SEPOLIA_RPC_URL:
        raise ValueError(
            "SEPOLIA_RPC_URL not set. Add it to Backend/.env:\n"
            "  SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID"
        )

    if SEPOLIA_RPC_URL.startswith("wss://"):
        provider = Web3.WebsocketProvider(SEPOLIA_RPC_URL)
    else:
        provider = Web3.HTTPProvider(SEPOLIA_RPC_URL, request_kwargs={"timeout": 30})

    w3 = Web3(provider)

    # PoA middleware for Sepolia (Proof of Authority testnet)
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to Sepolia at {SEPOLIA_RPC_URL}")

    logger.info("Connected to Sepolia (chain ID: %s)", w3.eth.chain_id)
    return w3


def _get_contract(w3: Web3):
    """Get the ChameleonLedger contract instance."""
    if not CONTRACT_ADDRESS:
        raise ValueError(
            "CONTRACT_ADDRESS not set. Deploy ChameleonLedger.sol first, "
            "then add CONTRACT_ADDRESS=0x... to Backend/.env"
        )
    abi = _load_abi()
    return w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=abi,
    )


# ========================================================================
# Core: anchor_latest_root
# ========================================================================

async def anchor_latest_root(merkle_root: str) -> Dict[str, Any]:
    """
    Sign and send a transaction to store a Merkle root on Sepolia.

    Args:
        merkle_root: SHA-256 Merkle root hash string (64 hex chars).

    Returns:
        Dict with transaction details:
        {
            "tx_hash": "0x...",
            "block_number": 12345,
            "gas_used": 54321,
            "root_stored": "a1b2c3...",
            "status": "success"
        }

    Raises:
        ValueError: If env vars are missing.
        ConnectionError: If Sepolia RPC is unreachable.
        Exception: On transaction failure.
    """
    if not PRIVATE_KEY:
        raise ValueError(
            "PRIVATE_KEY not set. Add to Backend/.env:\n"
            "  PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE\n"
            "  ⚠️  Never commit this file to git!"
        )

    # Run blocking web3 calls in executor to keep async non-blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _anchor_sync, merkle_root)


def _anchor_sync(merkle_root: str) -> Dict[str, Any]:
    """Synchronous web3 transaction logic (runs in thread pool)."""
    w3 = _get_web3()
    contract = _get_contract(w3)
    account = w3.eth.account.from_key(PRIVATE_KEY)

    logger.info(
        "Anchoring Merkle root: %s... (from %s)",
        merkle_root[:16], account.address,
    )

    # ── Build transaction ────────────────────────────────────────────
    nonce = w3.eth.get_transaction_count(account.address, "pending")

    # Gas estimation with safety margin
    try:
        estimated_gas = contract.functions.storeMerkleRoot(
            merkle_root
        ).estimate_gas({"from": account.address})
        gas_limit = int(estimated_gas * 1.2)  # 20% safety buffer
    except ContractLogicError as e:
        logger.error("Contract logic error during gas estimation: %s", e)
        raise
    except Exception as e:
        logger.warning("Gas estimation failed, using default: %s", e)
        gas_limit = 100_000  # Safe default for storeMerkleRoot

    # EIP-1559 gas pricing (Sepolia supports it)
    try:
        latest_block = w3.eth.get_block("latest")
        base_fee = latest_block.get("baseFeePerGas", w3.to_wei(1, "gwei"))
        max_priority_fee = w3.to_wei(2, "gwei")
        max_fee = base_fee * 2 + max_priority_fee
    except Exception:
        # Fallback to legacy gas pricing
        max_fee = w3.to_wei(20, "gwei")
        max_priority_fee = w3.to_wei(2, "gwei")

    tx = contract.functions.storeMerkleRoot(merkle_root).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": gas_limit,
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": max_priority_fee,
        "chainId": w3.eth.chain_id,
    })

    # ── Sign & Send ──────────────────────────────────────────────────
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    logger.info("Transaction sent: %s  (waiting for receipt...)", tx_hash.hex())

    # ── Wait for confirmation (max 120s) ─────────────────────────────
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    except Exception as e:
        logger.error("Transaction timed out or failed: %s", e)
        return {
            "tx_hash": tx_hash.hex(),
            "status": "pending",
            "error": str(e),
        }

    status = "success" if receipt["status"] == 1 else "failed"

    result = {
        "tx_hash": tx_hash.hex(),
        "block_number": receipt["blockNumber"],
        "gas_used": receipt["gasUsed"],
        "root_stored": merkle_root,
        "status": status,
        "etherscan_url": f"https://sepolia.etherscan.io/tx/{tx_hash.hex()}",
    }

    if status == "success":
        logger.info(
            "✅ Merkle root anchored on Sepolia! Block #%d | Gas: %d | TX: %s",
            receipt["blockNumber"], receipt["gasUsed"], tx_hash.hex(),
        )
    else:
        logger.error("❌ Transaction failed! Receipt: %s", receipt)

    return result


# ========================================================================
# Read Functions
# ========================================================================

async def get_root_count() -> int:
    """Get total number of anchored Merkle roots."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_root_count_sync)


def _get_root_count_sync() -> int:
    w3 = _get_web3()
    contract = _get_contract(w3)
    return contract.functions.getRootCount().call()


async def get_latest_root() -> str:
    """Get the most recently anchored Merkle root."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_latest_root_sync)


def _get_latest_root_sync() -> str:
    w3 = _get_web3()
    contract = _get_contract(w3)
    return contract.functions.getLatestRoot().call()


# ========================================================================
# Standalone Entry Point
# ========================================================================

async def _main():
    """
    Standalone usage: anchor the current Merkle root from integrity.py.
    """
    from integrity import MerkleLogger

    # Build Merkle root from recent in-memory logs
    merkle_logger = MerkleLogger()

    # In production you'd load recent logs from PostgreSQL here
    # For demo, we create a sample root
    sample_logs = [
        {"attacker_ip": "192.168.1.100", "command": "ls -la", "response": "total 0..."},
        {"attacker_ip": "10.0.0.5", "command": "cat /etc/passwd", "response": "Permission denied"},
    ]
    merkle_logger.add_logs(sample_logs)
    root = merkle_logger.build_tree()

    if root:
        print(f"Merkle Root: {root}")
        result = await anchor_latest_root(root)
        print(f"Result: {json.dumps(result, indent=2)}")
    else:
        print("No logs to anchor.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(_main())
