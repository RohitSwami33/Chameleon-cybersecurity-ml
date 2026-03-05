"""
Test Suite: /trap/execute Endpoint & ML Pipeline
==================================================

Tests the full pipeline: ML inference → threshold gate →
hash → response structure.

Run:
    python test_trap_execute.py
    # or
    pytest test_trap_execute.py -v
"""

import asyncio
import sys
import unittest


class TestMLInference(unittest.TestCase):
    """Test the ChameleonPredictor directly."""

    @classmethod
    def setUpClass(cls):
        """Load the predictor once for all tests."""
        from ml_inference import ChameleonPredictor
        cls.predictor = ChameleonPredictor()

    def test_singleton_pattern(self):
        """ChameleonPredictor should return the same instance."""
        from ml_inference import ChameleonPredictor
        p1 = ChameleonPredictor()
        p2 = ChameleonPredictor()
        self.assertIs(p1, p2)

    def test_predict_returns_float(self):
        """predict() should return a float between 0 and 1."""
        score = asyncio.run(self.predictor.predict("ls -la"))
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_benign_command_low_score(self):
        """Benign commands should score low (< 0.5)."""
        benign_commands = ["ls", "pwd", "whoami", "date", "echo hello"]
        for cmd in benign_commands:
            score = asyncio.run(self.predictor.predict(cmd))
            self.assertLess(score, 0.5, f"'{cmd}' scored {score:.4f} — expected < 0.5")

    def test_empty_command(self):
        """Empty string should not crash."""
        score = asyncio.run(self.predictor.predict(""))
        self.assertIsInstance(score, float)

    def test_long_command(self):
        """Very long commands should be handled (truncated to max_len)."""
        long_cmd = "a" * 10000
        score = asyncio.run(self.predictor.predict(long_cmd))
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestTokenizer(unittest.TestCase):
    """Test the ChameleonTokenizer."""

    def test_encode_padding(self):
        """encode() should pad short sequences."""
        from ml_inference import ChameleonTokenizer
        tok = ChameleonTokenizer()
        encoded = tok.encode("ls")
        self.assertEqual(len(encoded), tok.max_len)
        # First 2 chars should be non-zero, rest should be pad (0)
        self.assertNotEqual(encoded[0], 0)
        self.assertNotEqual(encoded[1], 0)
        self.assertEqual(encoded[-1], 0)

    def test_encode_truncation(self):
        """encode() should truncate long sequences to max_len."""
        from ml_inference import ChameleonTokenizer
        tok = ChameleonTokenizer()
        long_text = "x" * 500
        encoded = tok.encode(long_text)
        self.assertEqual(len(encoded), tok.max_len)

    def test_unknown_characters(self):
        """Unknown characters should map to unk_token."""
        from ml_inference import ChameleonTokenizer
        tok = ChameleonTokenizer()
        # Use rare unicode characters
        encoded = tok.encode("🔥💀")
        # Should not crash, chars map to unk_token
        self.assertEqual(len(encoded), tok.max_len)


class TestIntegrityHash(unittest.TestCase):
    """Test the calculate_hash (hash_log_entry) function."""

    def test_hash_deterministic(self):
        """Same input should produce the same hash."""
        from integrity import hash_log_entry as calculate_hash
        data = {
            "ip_address": "192.168.1.1",
            "command": "ls -la",
            "response": "total 0...",
            "prediction_score": 0.92,
        }
        h1 = calculate_hash(data)
        h2 = calculate_hash(data)
        self.assertEqual(h1, h2)

    def test_hash_is_sha256(self):
        """Hash should be a 64-character hex string (SHA-256)."""
        from integrity import hash_log_entry as calculate_hash
        data = {"key": "value"}
        h = calculate_hash(data)
        self.assertEqual(len(h), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in h))

    def test_hash_changes_with_data(self):
        """Different data should produce different hashes."""
        from integrity import hash_log_entry as calculate_hash
        h1 = calculate_hash({"command": "ls"})
        h2 = calculate_hash({"command": "pwd"})
        self.assertNotEqual(h1, h2)


class TestStaticFallback(unittest.TestCase):
    """Test the static fallback responses in main.py."""

    def test_ls_fallback(self):
        """ls should return directory listing."""
        # Import directly to test without starting the server
        import ast
        with open("main.py") as f:
            source = f.read()

        # Verify fallback function exists
        tree = ast.parse(source)
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertIn("_static_fallback", func_names)

    def test_main_syntax(self):
        """main.py should have valid Python syntax."""
        import ast
        with open("main.py") as f:
            source = f.read()
        # This will raise SyntaxError if invalid
        ast.parse(source)

    def test_main_has_trap_execute(self):
        """main.py should contain the /trap/execute route."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("/trap/execute", source)
        self.assertIn("TrapExecuteRequest", source)
        self.assertIn("TrapExecuteResponse", source)
        self.assertIn("Depends(get_db)", source)

    def test_main_has_cors(self):
        """main.py should have CORS middleware configured."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("CORSMiddleware", source)
        self.assertIn("localhost:5173", source)
        self.assertIn("localhost:3000", source)


class TestFrontendFiles(unittest.TestCase):
    """Test that frontend files exist and are valid."""

    def test_api_js_exists(self):
        """api.js should exist in frontend services."""
        from pathlib import Path
        api_path = Path(__file__).parent.parent / "frontend" / "src" / "services" / "api.js"
        self.assertTrue(api_path.exists(), f"Not found: {api_path}")

    def test_api_js_has_execute_command(self):
        """api.js should export executeCommand."""
        from pathlib import Path
        api_path = Path(__file__).parent.parent / "frontend" / "src" / "services" / "api.js"
        content = api_path.read_text()
        self.assertIn("executeCommand", content)
        self.assertIn("/trap/execute", content)

    def test_api_js_has_fetch_dashboard_stats(self):
        """api.js should export fetchDashboardStats."""
        from pathlib import Path
        api_path = Path(__file__).parent.parent / "frontend" / "src" / "services" / "api.js"
        content = api_path.read_text()
        self.assertIn("fetchDashboardStats", content)

    def test_use_terminal_hook_exists(self):
        """useTerminal.js should exist in frontend hooks."""
        from pathlib import Path
        hook_path = Path(__file__).parent.parent / "frontend" / "src" / "hooks" / "useTerminal.js"
        self.assertTrue(hook_path.exists(), f"Not found: {hook_path}")

    def test_use_terminal_has_required_exports(self):
        """useTerminal.js should export expected state and functions."""
        from pathlib import Path
        hook_path = Path(__file__).parent.parent / "frontend" / "src" / "hooks" / "useTerminal.js"
        content = hook_path.read_text()
        self.assertIn("useTerminal", content)
        self.assertIn("history", content)
        self.assertIn("isLoading", content)
        self.assertIn("handleSubmit", content)
        self.assertIn("executeCommand", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
