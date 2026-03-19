"""
Test Suite: Honeytoken Canary Trap System
==========================================

Tests for all three integration points:
  Task 1 → LLM system prompt + bait file injection
  Task 2 → GET /api/beacon/{session_id} endpoint
  Task 3 → BeaconEvent SQLAlchemy model + is_exfiltration_attempt flag

Run:
    python -m unittest test_honeytoken -v
"""

import ast
import asyncio
import os
import re
import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


# ========================================================================
# Task 1: The Bait — LLM System Prompt & Static Fallback
# ========================================================================

class TestSystemPromptHoneytokens(unittest.TestCase):
    """Verify the system prompt contains honeytoken instructions."""

    def test_prompt_mentions_canary_files(self):
        """System prompt must reference aws_production_keys.csv and .env.backup."""
        from llm_controller import UBUNTU_SYSTEM_PROMPT
        self.assertIn("aws_production_keys.csv", UBUNTU_SYSTEM_PROMPT)
        self.assertIn(".env.backup", UBUNTU_SYSTEM_PROMPT)

    def test_prompt_contains_beacon_placeholder(self):
        """System prompt must contain {beacon_url} placeholder."""
        from llm_controller import UBUNTU_SYSTEM_PROMPT
        self.assertIn("{beacon_url}", UBUNTU_SYSTEM_PROMPT)

    def test_prompt_contains_fake_aws_keys(self):
        """System prompt should include fake AWS key patterns."""
        from llm_controller import UBUNTU_SYSTEM_PROMPT
        self.assertIn("AKIAIOSFODNN7EXAMPLE", UBUNTU_SYSTEM_PROMPT)
        self.assertIn("wJalrXUtnFEMI", UBUNTU_SYSTEM_PROMPT)

    def test_prompt_contains_fake_db_credentials(self):
        """System prompt should include fake database credentials."""
        from llm_controller import UBUNTU_SYSTEM_PROMPT
        self.assertIn("DB_HOST=rds-prod-01", UBUNTU_SYSTEM_PROMPT)
        self.assertIn("DB_PASSWORD=", UBUNTU_SYSTEM_PROMPT)

    def test_prompt_ls_instruction(self):
        """System prompt should instruct to INCLUDE honeytokens in ls output."""
        from llm_controller import UBUNTU_SYSTEM_PROMPT
        self.assertIn("INCLUDE aws_production_keys.csv and .env.backup", UBUNTU_SYSTEM_PROMPT)

    def test_honeypot_domain_env_var(self):
        """HONEYPOT_DOMAIN should default to localhost:8000."""
        from llm_controller import HONEYPOT_DOMAIN
        # Either env var set or default
        self.assertIsNotNone(HONEYPOT_DOMAIN)
        self.assertTrue(len(HONEYPOT_DOMAIN) > 0)


class TestStaticFallbackHoneytokens(unittest.TestCase):
    """Test _static_fallback includes honeytoken bait files."""

    def setUp(self):
        """Create a controller instance for testing."""
        # Patch settings to avoid real API calls
        with patch("llm_controller.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "deepseek"
            mock_settings.DEEPSEEK_API_KEY = "test_key"
            mock_settings.DEEPSEEK_API_URL = "https://test.api.com"
            mock_settings.DEEPSEEK_MODEL = "test-model"
            mock_settings.LLM_MAX_TOKENS = 500
            mock_settings.LLM_TEMPERATURE = 0.7
            mock_settings.LLM_TIMEOUT = 30
            from llm_controller import LLMController
            self.controller = LLMController.__new__(LLMController)
            self.controller.provider = MagicMock()
            self.controller.provider.value = "deepseek"

    def test_ls_shows_honeytokens(self):
        """ls output should include honeytoken files."""
        result = self.controller._static_fallback("ls", "test-session-id")
        self.assertIn("aws_production_keys.csv", result)
        self.assertIn(".env.backup", result)

    def test_ls_la_shows_honeytokens(self):
        """ls -la output should include honeytoken files with permissions."""
        result = self.controller._static_fallback("ls -la", "test-session-id")
        self.assertIn("aws_production_keys.csv", result)
        self.assertIn(".env.backup", result)
        # Should show file permissions
        self.assertIn("-rw-", result)

    def test_cat_aws_keys_contains_beacon_url(self):
        """Reading aws_production_keys.csv should contain beacon URL."""
        session_id = str(uuid.uuid4())
        result = self.controller._static_fallback(f"cat aws_production_keys.csv", session_id)
        self.assertIn("AKIAIOSFODNN7EXAMPLE", result)
        self.assertIn(f"/api/beacon/{session_id}", result)
        self.assertIn("SecretAccessKey", result)

    def test_cat_env_backup_contains_beacon_url(self):
        """Reading .env.backup should contain beacon URL."""
        session_id = str(uuid.uuid4())
        result = self.controller._static_fallback(f"cat .env.backup", session_id)
        self.assertIn("DB_HOST=rds-prod-01", result)
        self.assertIn("DB_PASSWORD=", result)
        self.assertIn(f"/api/beacon/{session_id}", result)
        self.assertIn("JWT_SECRET=", result)

    def test_head_aws_keys_works(self):
        """head command should also trigger honeytoken for aws_production_keys."""
        result = self.controller._static_fallback("head aws_production_keys.csv", "sid-123")
        self.assertIn("AKIAIOSFODNN7EXAMPLE", result)

    def test_cat_env_backup_has_stripe_key(self):
        """Fake .env.backup should include realistic fake Stripe key."""
        result = self.controller._static_fallback("cat .env.backup", "sid-456")
        self.assertIn("STRIPE_SK=", result)

    def test_unique_session_in_url(self):
        """Different session IDs should produce different beacon URLs."""
        result1 = self.controller._static_fallback("cat aws_production_keys.csv", "session-aaa")
        result2 = self.controller._static_fallback("cat aws_production_keys.csv", "session-bbb")
        self.assertIn("/api/beacon/session-aaa", result1)
        self.assertIn("/api/beacon/session-bbb", result2)


class TestGenerateDeceptiveResponse(unittest.TestCase):
    """Test that generate_deceptive_response returns Tuple[str, str]."""

    def test_convenience_function_returns_tuple(self):
        """generate_deceptive_response should return (response, session_id)."""
        with patch("llm_controller.settings") as mock_s:
            mock_s.USE_LLM_DECEPTION = False
            mock_s.FALLBACK_TO_STATIC_DECEPTION = True
            mock_s.LLM_PROVIDER = "deepseek"
            mock_s.DEEPSEEK_API_KEY = "fake"
            mock_s.DEEPSEEK_API_URL = "https://fake.com"
            mock_s.DEEPSEEK_MODEL = "test"
            mock_s.LLM_MAX_TOKENS = 500
            mock_s.LLM_TEMPERATURE = 0.7
            mock_s.LLM_TIMEOUT = 30

            from llm_controller import LLMController
            controller = LLMController.__new__(LLMController)
            controller.provider = MagicMock()
            controller.provider.value = "deepseek"
            controller._sessions = {}
            controller._cache = {}
            controller.stats = {
                "total_requests": 0, "successful_requests": 0,
                "failed_requests": 0, "cache_hits": 0, "provider": "deepseek"
            }

            result = asyncio.run(controller.generate_deceptive_response(
                "ls -la", session_id="test-session-123"
            ))
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            response_text, session_id = result
            self.assertIsInstance(response_text, str)
            self.assertEqual(session_id, "test-session-123")

    def test_auto_generates_session_id(self):
        """If no session_id provided, one should be auto-generated."""
        with patch("llm_controller.settings") as mock_s:
            mock_s.USE_LLM_DECEPTION = False
            mock_s.FALLBACK_TO_STATIC_DECEPTION = True
            mock_s.LLM_PROVIDER = "deepseek"
            mock_s.DEEPSEEK_API_KEY = "fake"
            mock_s.DEEPSEEK_API_URL = "https://fake.com"
            mock_s.DEEPSEEK_MODEL = "test"
            mock_s.LLM_MAX_TOKENS = 500
            mock_s.LLM_TEMPERATURE = 0.7
            mock_s.LLM_TIMEOUT = 30

            from llm_controller import LLMController
            controller = LLMController.__new__(LLMController)
            controller.provider = MagicMock()
            controller.provider.value = "deepseek"
            controller._sessions = {}
            controller._cache = {}
            controller.stats = {
                "total_requests": 0, "successful_requests": 0,
                "failed_requests": 0, "cache_hits": 0, "provider": "deepseek"
            }

            result = asyncio.run(controller.generate_deceptive_response("whoami"))
            _, session_id = result
            # Validate it's a UUID format
            uuid.UUID(session_id)  # Should not raise


# ========================================================================
# Task 2: The Tripwire — Beacon Endpoint Verification
# ========================================================================

class TestBeaconEndpoint(unittest.TestCase):
    """Verify the beacon endpoint exists in main.py with correct behavior."""

    def test_beacon_endpoint_exists(self):
        """main.py should contain the /api/beacon/{session_id} route."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("/api/beacon/{session_id}", source)

    def test_beacon_returns_pixel(self):
        """Beacon endpoint should reference TRANSPARENT_PIXEL."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("TRANSPARENT_PIXEL", source)
        self.assertIn("image/png", source)

    def test_beacon_captures_telemetry(self):
        """Beacon should capture IP, User-Agent, and X-Forwarded-For."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("request.client.host", source)
        self.assertIn("X-Forwarded-For", source)
        self.assertIn("User-Agent", source)

    def test_beacon_logs_warning(self):
        """Beacon should log a warning-level alert."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("HONEYTOKEN BEACON TRIGGERED", source)
        self.assertIn("logger.warning", source)

    def test_beacon_creates_beacon_event(self):
        """Beacon should create a BeaconEvent and add it to the session."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("BeaconEvent(", source)
        self.assertIn("session.add(beacon_event)", source)

    def test_beacon_flags_exfiltration(self):
        """Beacon should update HoneypotLog with is_exfiltration_attempt=True."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("is_exfiltration_attempt=True", source)

    def test_beacon_no_cache_headers(self):
        """Beacon response should have no-cache headers."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("no-store, no-cache", source)
        self.assertIn("Pragma", source)

    def test_trap_execute_returns_session_id(self):
        """TrapExecuteResponse should include session_id field."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("session_id=honeytoken_session_id", source)

    def test_metadata_includes_session_id(self):
        """Honeypot log metadata should include honeytoken_session_id."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn('"honeytoken_session_id": honeytoken_session_id', source)

    def test_transparent_pixel_is_valid_png(self):
        """TRANSPARENT_PIXEL should be defined as PNG bytes."""
        with open("main.py") as f:
            source = f.read()
        # Check PNG magic bytes are present
        self.assertIn("\\x89PNG", source)
        self.assertIn("IEND", source)
        self.assertIn("TRANSPARENT_PIXEL", source)


# ========================================================================
# Task 3: Threat Intel — BeaconEvent Model
# ========================================================================

class TestBeaconEventModel(unittest.TestCase):
    """Verify the BeaconEvent SQLAlchemy model."""

    def test_beacon_event_importable(self):
        """BeaconEvent should be importable from models_sqlalchemy."""
        from models_sqlalchemy import BeaconEvent
        self.assertIsNotNone(BeaconEvent)

    def test_beacon_event_tablename(self):
        """Table name should be 'beacon_events'."""
        from models_sqlalchemy import BeaconEvent
        self.assertEqual(BeaconEvent.__tablename__, "beacon_events")

    def test_beacon_event_has_required_columns(self):
        """BeaconEvent should have all required columns."""
        from models_sqlalchemy import BeaconEvent
        columns = BeaconEvent.__table__.columns
        required = [
            "id", "session_id", "source_ip", "user_agent",
            "request_headers", "original_attacker_ip", "triggered_at",
            "honeytoken_file", "forwarded_for"
        ]
        column_names = [c.name for c in columns]
        for col in required:
            self.assertIn(col, column_names, f"Missing column: {col}")

    def test_session_id_is_indexed(self):
        """session_id should have an index for fast lookup."""
        from models_sqlalchemy import BeaconEvent
        col = BeaconEvent.__table__.columns["session_id"]
        self.assertTrue(col.index, "session_id should be indexed")

    def test_source_ip_is_indexed(self):
        """source_ip should have an index for fast lookup."""
        from models_sqlalchemy import BeaconEvent
        col = BeaconEvent.__table__.columns["source_ip"]
        self.assertTrue(col.index, "source_ip should be indexed")

    def test_to_dict_method(self):
        """BeaconEvent.to_dict() should return proper dictionary."""
        from models_sqlalchemy import BeaconEvent
        event = BeaconEvent(
            session_id="test-session-uuid",
            source_ip="192.168.1.100",
            user_agent="Mozilla/5.0",
            forwarded_for="10.0.0.1, 172.16.0.1",
            honeytoken_file="aws_production_keys.csv",
            original_attacker_ip="192.168.1.50",
        )
        d = event.to_dict()
        self.assertEqual(d["session_id"], "test-session-uuid")
        self.assertEqual(d["source_ip"], "192.168.1.100")
        self.assertEqual(d["user_agent"], "Mozilla/5.0")
        self.assertEqual(d["forwarded_for"], "10.0.0.1, 172.16.0.1")
        self.assertEqual(d["honeytoken_file"], "aws_production_keys.csv")
        self.assertEqual(d["original_attacker_ip"], "192.168.1.50")

    def test_composite_indexes_exist(self):
        """Table should have composite indexes for performance."""
        from models_sqlalchemy import BeaconEvent
        indexes = [idx.name for idx in BeaconEvent.__table__.indexes]
        self.assertIn("ix_beacon_events_session_triggered", indexes)
        self.assertIn("ix_beacon_events_source_ip_triggered", indexes)


class TestHoneypotLogExfiltrationFlag(unittest.TestCase):
    """Verify is_exfiltration_attempt Boolean on HoneypotLog."""

    def test_honeypot_log_has_exfiltration_flag(self):
        """HoneypotLog should have is_exfiltration_attempt column."""
        from models_sqlalchemy import HoneypotLog
        columns = HoneypotLog.__table__.columns
        column_names = [c.name for c in columns]
        self.assertIn("is_exfiltration_attempt", column_names)

    def test_exfiltration_flag_default_false(self):
        """is_exfiltration_attempt should default to False."""
        from models_sqlalchemy import HoneypotLog
        col = HoneypotLog.__table__.columns["is_exfiltration_attempt"]
        self.assertFalse(col.default.arg)

    def test_exfiltration_flag_is_boolean(self):
        """is_exfiltration_attempt should be Boolean type."""
        from models_sqlalchemy import HoneypotLog
        from sqlalchemy import Boolean
        col = HoneypotLog.__table__.columns["is_exfiltration_attempt"]
        self.assertIsInstance(col.type, Boolean)


# ========================================================================
# Integration: Cross-component Consistency Checks
# ========================================================================

class TestCrossComponentIntegration(unittest.TestCase):
    """Verify all components are wired together correctly."""

    def test_main_imports_beacon_event(self):
        """main.py should import BeaconEvent."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("BeaconEvent", source)

    def test_main_imports_response(self):
        """main.py should import Response for pixel delivery."""
        with open("main.py") as f:
            source = f.read()
        self.assertIn("from fastapi.responses import", source)
        self.assertIn("Response", source)

    def test_main_has_valid_python_syntax(self):
        """main.py should have valid Python syntax after changes."""
        with open("main.py") as f:
            source = f.read()
        ast.parse(source)  # Raises SyntaxError if invalid

    def test_llm_controller_has_valid_python_syntax(self):
        """llm_controller.py should have valid syntax after changes."""
        with open("llm_controller.py") as f:
            source = f.read()
        ast.parse(source)

    def test_models_has_valid_python_syntax(self):
        """models_sqlalchemy.py should have valid syntax after changes."""
        with open("models_sqlalchemy.py") as f:
            source = f.read()
        ast.parse(source)

    def test_beacon_url_format_consistency(self):
        """Beacon URLs in llm_controller should match endpoint in main.py."""
        with open("llm_controller.py") as f:
            llm_source = f.read()
        with open("main.py") as f:
            main_source = f.read()

        # LLM controller uses /api/beacon/{session_id}
        self.assertIn("/api/beacon/", llm_source)
        # main.py registers /api/beacon/{session_id}
        self.assertIn("/api/beacon/{session_id}", main_source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
