"""
Test Suite: Blockchain Sync Module
====================================

Tests for blockchain_sync.py — Merkle root anchoring to Sepolia.
Uses mocked web3 to test without a real network connection.

Run:
    python test_blockchain_sync.py
    # or
    pytest test_blockchain_sync.py -v
"""

import asyncio
import json
import unittest
from unittest.mock import patch, MagicMock, PropertyMock


class TestBlockchainSyncImport(unittest.TestCase):
    """Test that the module can be imported and configured."""

    def test_import_module(self):
        """blockchain_sync should import without errors."""
        import blockchain_sync
        self.assertTrue(hasattr(blockchain_sync, "anchor_latest_root"))
        self.assertTrue(hasattr(blockchain_sync, "get_root_count"))
        self.assertTrue(hasattr(blockchain_sync, "get_latest_root"))

    def test_minimal_abi_present(self):
        """Minimal ABI should contain storeMerkleRoot function."""
        from blockchain_sync import MINIMAL_ABI
        func_names = [
            entry.get("name")
            for entry in MINIMAL_ABI
            if entry.get("type") == "function"
        ]
        self.assertIn("storeMerkleRoot", func_names)
        self.assertIn("getRootCount", func_names)
        self.assertIn("getLatestRoot", func_names)

    def test_abi_event_present(self):
        """Minimal ABI should contain RootStored event."""
        from blockchain_sync import MINIMAL_ABI
        events = [
            entry.get("name")
            for entry in MINIMAL_ABI
            if entry.get("type") == "event"
        ]
        self.assertIn("RootStored", events)


class TestAnchorFunction(unittest.TestCase):
    """Test anchor_latest_root with mocked web3."""

    @patch("blockchain_sync.PRIVATE_KEY", "0x" + "a1" * 32)
    @patch("blockchain_sync.CONTRACT_ADDRESS", "0x" + "b2" * 20)
    @patch("blockchain_sync.SEPOLIA_RPC_URL", "https://mock-rpc.example.com")
    @patch("blockchain_sync._get_web3")
    def test_anchor_builds_transaction(self, mock_get_web3):
        """anchor_latest_root should build, sign, and send a transaction."""
        # Mock web3 instance
        mock_w3 = MagicMock()
        mock_get_web3.return_value = mock_w3

        # Mock chain_id
        mock_w3.eth.chain_id = 11155111  # Sepolia

        # Mock account
        mock_account = MagicMock()
        mock_account.address = "0x" + "cc" * 20
        mock_w3.eth.account.from_key.return_value = mock_account

        # Mock nonce
        mock_w3.eth.get_transaction_count.return_value = 42

        # Mock contract
        mock_contract = MagicMock()
        mock_w3.eth.contract.return_value = mock_contract

        # Mock gas estimation
        mock_contract.functions.storeMerkleRoot.return_value.estimate_gas.return_value = 55000

        # Mock build_transaction
        mock_tx = {"gas": 66000, "nonce": 42}
        mock_contract.functions.storeMerkleRoot.return_value.build_transaction.return_value = mock_tx

        # Mock block for EIP-1559
        mock_w3.eth.get_block.return_value = {"baseFeePerGas": 1000000000}
        mock_w3.to_wei.return_value = 2000000000

        # Mock sign and send
        mock_signed = MagicMock()
        mock_signed.raw_transaction = b"\x00" * 32
        mock_w3.eth.account.sign_transaction.return_value = mock_signed
        mock_w3.eth.send_raw_transaction.return_value = b"\x01" * 32

        # Mock receipt
        mock_receipt = {
            "status": 1,
            "blockNumber": 12345,
            "gasUsed": 54000,
        }
        mock_w3.eth.wait_for_transaction_receipt.return_value = mock_receipt

        # Run
        from blockchain_sync import _anchor_sync
        result = _anchor_sync("abc123def456")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["block_number"], 12345)
        self.assertEqual(result["gas_used"], 54000)
        self.assertEqual(result["root_stored"], "abc123def456")
        self.assertIn("etherscan_url", result)

    @patch("blockchain_sync.PRIVATE_KEY", "")
    def test_anchor_raises_without_private_key(self):
        """Should raise ValueError if PRIVATE_KEY is not set."""
        from blockchain_sync import anchor_latest_root

        with self.assertRaises(ValueError) as ctx:
            asyncio.run(anchor_latest_root("test_root"))
        self.assertIn("PRIVATE_KEY", str(ctx.exception))

    @patch("blockchain_sync.SEPOLIA_RPC_URL", "")
    def test_raises_without_rpc_url(self):
        """Should raise ValueError if SEPOLIA_RPC_URL is not set."""
        from blockchain_sync import _get_web3

        with self.assertRaises(ValueError) as ctx:
            _get_web3()
        self.assertIn("SEPOLIA_RPC_URL", str(ctx.exception))

    @patch("blockchain_sync.CONTRACT_ADDRESS", "")
    @patch("blockchain_sync.SEPOLIA_RPC_URL", "https://mock.example.com")
    @patch("blockchain_sync._get_web3")
    def test_raises_without_contract_address(self, mock_w3):
        """Should raise ValueError if CONTRACT_ADDRESS is not set."""
        from blockchain_sync import _get_contract

        with self.assertRaises(ValueError) as ctx:
            _get_contract(mock_w3.return_value)
        self.assertIn("CONTRACT_ADDRESS", str(ctx.exception))


class TestGasEstimation(unittest.TestCase):
    """Test gas estimation logic."""

    @patch("blockchain_sync.PRIVATE_KEY", "0x" + "a1" * 32)
    @patch("blockchain_sync.CONTRACT_ADDRESS", "0x" + "b2" * 20)
    @patch("blockchain_sync.SEPOLIA_RPC_URL", "https://mock.example.com")
    @patch("blockchain_sync._get_web3")
    def test_gas_estimation_with_buffer(self, mock_get_web3):
        """Gas limit should be 120% of estimated gas."""
        mock_w3 = MagicMock()
        mock_get_web3.return_value = mock_w3
        mock_w3.eth.chain_id = 11155111

        mock_account = MagicMock()
        mock_account.address = "0x" + "cc" * 20
        mock_w3.eth.account.from_key.return_value = mock_account
        mock_w3.eth.get_transaction_count.return_value = 0

        mock_contract = MagicMock()
        mock_w3.eth.contract.return_value = mock_contract

        # Set estimated gas to 50000
        mock_contract.functions.storeMerkleRoot.return_value.estimate_gas.return_value = 50000

        mock_w3.eth.get_block.return_value = {"baseFeePerGas": 1_000_000_000}
        mock_w3.to_wei.return_value = 2_000_000_000

        mock_signed = MagicMock()
        mock_signed.raw_transaction = b"\x00"
        mock_w3.eth.account.sign_transaction.return_value = mock_signed
        mock_w3.eth.send_raw_transaction.return_value = b"\x01" * 32
        mock_w3.eth.wait_for_transaction_receipt.return_value = {
            "status": 1, "blockNumber": 1, "gasUsed": 48000,
        }

        from blockchain_sync import _anchor_sync
        _anchor_sync("test_root")

        # Verify build_transaction was called with gas = 60000 (50000 * 1.2)
        call_args = mock_contract.functions.storeMerkleRoot.return_value.build_transaction.call_args
        self.assertEqual(call_args[0][0]["gas"], 60000)


class TestSolidityContract(unittest.TestCase):
    """Verify the Solidity contract file exists and is well-formed."""

    def test_contract_file_exists(self):
        """ChameleonLedger.sol should exist."""
        from pathlib import Path
        sol_path = Path(__file__).parent / "contracts" / "ChameleonLedger.sol"
        self.assertTrue(sol_path.exists(), f"Contract not found: {sol_path}")

    def test_contract_contains_required_functions(self):
        """Contract should contain storeMerkleRoot and RootStored."""
        from pathlib import Path
        sol_path = Path(__file__).parent / "contracts" / "ChameleonLedger.sol"
        content = sol_path.read_text()

        self.assertIn("storeMerkleRoot", content)
        self.assertIn("RootStored", content)
        self.assertIn("getRootCount", content)
        self.assertIn("getRoot", content)
        self.assertIn("getLatestRoot", content)
        self.assertIn("onlyOwner", content)
        self.assertIn("pragma solidity", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
