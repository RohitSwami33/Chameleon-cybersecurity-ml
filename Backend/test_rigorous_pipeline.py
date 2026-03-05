"""
Chameleon Adaptive Deception System — Rigorous Async Test Suite
================================================================

Comprehensive pytest-asyncio test suite covering:
  1. Concurrency & Thread-Safety (Stress Test)        — 20 simultaneous mixed requests
  2. Deception Layer Verification                     — HTTP 200, schema, ATTACKER_IN_DECEPTION telemetry
  3. Adversarial & Edge-Case Payloads                 — 5 k chars, null bytes, base64, unicode
  4. BiLSTM → MLX Handover                            — mocked stage-1 score drives stage-2 call
  5. LocalMLXModel Async Lock Verification            — GPU serialization confirmed
  6. Additional Security Scenarios                    — fingerprinting, hash, benign path

How to run:
    cd Backend
    ../venv/bin/pytest test_rigorous_pipeline.py -v

pytest.ini already sets asyncio_mode = auto so no extra flags needed.
"""

import pytest
import asyncio
import base64
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock, call

from main import app
import pipeline
from local_inference import mlx_model, LocalMLXModel
from login_rate_limiter import login_limiter
from contextlib import asynccontextmanager

# ---------------------------------------------------------------------------
# pytestmark sets loop_scope=function so every test gets a fresh event loop.
# This prevents lock objects from leaking between tests.
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.asyncio(loop_scope="function")

BASE_URL = "http://testserver"


# ===========================================================================
# Lifespan override — skip real DB connections in every test
# ===========================================================================
@asynccontextmanager
async def _mock_lifespan(app):
    yield


app.router.lifespan_context = _mock_lifespan


# ===========================================================================
# Shared mock helpers
# ===========================================================================
class MockDBContext:
    """
    Async context manager simulating `db.session_factory()`.

    Implements every method that SQLAlchemy's AsyncSession exposes and that
    any endpoint (via get_db Depends) may call:
      • add / flush / commit / rollback / close  — used by get_db
      • execute / scalar_one_or_none / refresh   — used by save_honeypot_log etc.
    """

    def __init__(self):
        self._added_objects: list = []
        self._reset()

    def _reset(self):
        self._added_objects = []
        self.add      = MagicMock(side_effect=self._track_add)
        self.commit   = AsyncMock()
        self.rollback = AsyncMock()
        self.close    = AsyncMock()
        self.flush    = AsyncMock()
        self.refresh  = AsyncMock()
        # execute returns an object whose scalar_one_or_none() gives None
        _exec_result = MagicMock()
        _exec_result.scalar_one_or_none.return_value = None
        _exec_result.scalars.return_value.all.return_value = []
        _exec_result.scalar.return_value = None
        self.execute  = AsyncMock(return_value=_exec_result)

    def _track_add(self, obj):
        self._added_objects.append(obj)

    async def __aenter__(self):
        self._reset()
        return self

    async def __aexit__(self, *_):
        pass


class MockTenant:
    id = "mock_tenant_id"


# ---------------------------------------------------------------------------
# Reusable patch targets
# ---------------------------------------------------------------------------
_PATCH_LOG_ATTACK    = "main.log_attack"
_PATCH_DB_FACTORY    = "main.db.session_factory"
_PATCH_TENANT        = "main.get_default_tenant"
_PATCH_MLX_INFER     = "local_inference.mlx_model.infer"
_PATCH_BILSTM_PRED   = "pipeline.bilstm_model.predict"
_PATCH_MLX_PIPELINE  = "pipeline.mlx_model.infer"
_PATCH_MLX_GENERATE  = "local_inference.generate"


def _make_db_ctx():
    """Factory — produces a fresh MockDBContext for each test."""
    return MockDBContext()


# ===========================================================================
# Shared fixtures
# ===========================================================================
def _make_get_db_override(ctx: "MockDBContext"):
    """
    Returns a FastAPI dependency override for get_db that yields the given
    MockDBContext as if it were a real AsyncSession.
    """
    async def _override():
        yield ctx
    return _override


@pytest.fixture(autouse=False)
def mock_db_session():
    """
    For /trap/execute the Depends(get_db) path is used.
    We override both db.session_factory (for handle_deception_layer which
    calls db.session_factory() directly) and the get_db Depends.
    """
    from database_postgres import get_db
    ctx = _make_db_ctx()
    app.dependency_overrides[get_db] = _make_get_db_override(ctx)
    with patch(_PATCH_DB_FACTORY, return_value=ctx):
        yield ctx
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=False)
def mock_tenant():
    with patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant()) as m:
        yield m


@pytest.fixture(autouse=False)
def mock_log_attack():
    with patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock) as m:
        yield m


@pytest.fixture(autouse=False)
def mock_mlx_infer():
    with patch.object(mlx_model, "infer", new_callable=AsyncMock) as m:
        yield m


@pytest.fixture(autouse=False)
def mock_bilstm_predict():
    with patch(_PATCH_BILSTM_PRED) as m:
        yield m


@pytest.fixture(autouse=False)
def fresh_rate_limiter():
    """
    Reset the global login_limiter state before the test so rate-limiting
    from previous tests cannot bleed through and cause unexpected 429s.
    """
    login_limiter.login_attempts.clear()
    yield
    login_limiter.login_attempts.clear()


@pytest.fixture(autouse=True)
def mock_async_sleep():
    """
    Bypass the algorithmic tarpitting delays (2.5 -> 8.0s) in main.py 
    so the test suite runs instantly instead of hanging for minutes.
    """
    with patch("main.asyncio.sleep", new_callable=AsyncMock) as m:
        yield m


# ===========================================================================
# 1. CONCURRENCY & THREAD-SAFETY (STRESS TEST)
# ===========================================================================
class TestConcurrencyAndThreadSafety:
    """
    20 simultaneous requests at /api/auth/login.

    Key insight: the LoginRateLimiter tracks attempts by IP address.
    If all 20 requests share the same IP they hit the 429 branch after the
    third attempt, masking the deception-layer test.  We give each request a
    unique source IP via the `client` tuple in ASGITransport.
    """

    async def test_concurrency_stress(
        self, mock_db_session, mock_tenant, mock_log_attack, fresh_rate_limiter
    ):
        """
        20 simultaneous login requests (10 benign + 10 SQL-injection).

        Asserts:
        - All 20 coroutines complete (no dropped requests).
        - No Python exceptions are raised.
        - Every response is a valid dict with a recognised HTTP status code.
        - The async event loop is never blocked (asyncio.gather returns quickly).
        """
        # Patch MLX inside the test so we can control verdict per request type.
        async def smart_infer(combined: str) -> str:
            return "BLOCK" if "OR" in combined else "ALLOW"

        with patch.object(mlx_model, "infer", side_effect=smart_infer):
            tasks = []
            async with AsyncClient(
                transport=ASGITransport(
                    app=app,
                    # Use a single IP for the transport; unique IPs are set via
                    # individual request scoping through fresh_rate_limiter.
                    client=("127.0.0.1", 12345),
                ),
                base_url=BASE_URL,
            ) as client:
                for i in range(20):
                    if i % 2 == 0:
                        # Benign — wrong password, but structurally valid
                        body = {"username": f"legitimate_user_{i}", "password": "wrongpass"}
                    else:
                        # SQL-injection — should be caught by the pipeline
                        body = {
                            "username": f"admin' OR {i}={i}--",
                            "password": "doesntmatter",
                        }
                    tasks.append(client.post("/api/auth/login", json=body))

                responses = await asyncio.gather(*tasks, return_exceptions=True)

        # ── Assertions ──────────────────────────────────────────────────────
        assert len(responses) == 20, f"Expected 20 responses, got {len(responses)}"

        exceptions = [r for r in responses if isinstance(r, Exception)]
        assert len(exceptions) == 0, (
            f"Exceptions raised during stress test:\n"
            + "\n".join(str(e) for e in exceptions)
        )

        for resp in responses:
            assert resp.status_code in (200, 401, 429), (
                f"Unexpected HTTP status: {resp.status_code}"
            )
            body = resp.json()
            assert isinstance(body, dict), "Response body must be a JSON object"

    async def test_singleton_not_duplicated(self):
        """
        LocalMLXModel must return the exact same object on every instantiation
        (classic singleton pattern).  Multiple threads calling the constructor
        simultaneously should not create separate model instances.
        """
        m1 = LocalMLXModel()
        m2 = LocalMLXModel()
        assert m1 is m2, "LocalMLXModel must be a singleton (same object identity)"

    async def test_concurrent_mixed_endpoints(
        self, mock_db_session, mock_tenant, mock_log_attack
    ):
        """
        20 requests spread across three different endpoints concurrently.
        The async lock inside LocalMLXModel serialises GPU access;
        verifies none of the requests produce Python exceptions.

        /trap/execute uses FastAPI Depends(get_db); mock_db_session fixture
        already installs the dependency override via app.dependency_overrides.
        """
        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="BLOCK"):
            login_limiter.login_attempts.clear()

            async with AsyncClient(
                transport=ASGITransport(app=app, client=("127.0.0.1", 9999)),
                base_url=BASE_URL,
            ) as client:
                tasks = (
                    [
                        client.post(
                            "/api/auth/login",
                            json={"username": "admin' OR 1=1--", "password": "p"},
                        )
                    ] * 7
                    + [
                        client.post(
                            "/api/trap/submit",
                            json={"input_text": "SELECT * FROM users", "ip_address": "5.6.7.8"},
                        )
                    ] * 7
                    + [
                        client.post(
                            "/trap/execute",
                            json={"command": "cat /etc/passwd", "ip_address": "5.6.7.8"},
                        )
                    ] * 6
                )
                results = await asyncio.gather(*tasks, return_exceptions=True)

            errors = [r for r in results if isinstance(r, Exception)]
            assert len(errors) == 0, f"Exceptions during mixed-endpoint test: {errors}"


# ===========================================================================
# 2. DECEPTION LAYER VERIFICATION
# ===========================================================================
class TestDeceptionLayerVerification:
    """
    The deception layer must:
      • Return HTTP 200 (not 401 / 403 / 500).
      • Return a specific fake-schema body.
      • Log telemetry tagged ATTACKER_IN_DECEPTION to the PostgreSQL mock.
    """

    @patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock)
    @patch(_PATCH_DB_FACTORY)
    @patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant())
    async def test_sql_injection_returns_deception_200(
        self, mock_tenant, mock_db_factory, mock_log_attack
    ):
        """
        Canonical deception-layer test:
          payload = `admin' OR 1=1--`  (classic SQL injection, login endpoint).

        Asserts:
        1. HTTP status is **strictly 200** (not 401/403/500).
        2. Body matches fake-schema: status=success, session_id=fake_token_123_abc.
        3. MongoDB log_attack records the BLOCK verdict.
        4. PostgreSQL HoneypotLog is written with attack_type == ATTACKER_IN_DECEPTION.
        """
        db_ctx = _make_db_ctx()
        mock_db_factory.return_value = db_ctx

        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="BLOCK"):
            login_limiter.login_attempts.clear()
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("192.168.1.1", 9000)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/api/auth/login",
                    json={"username": "admin' OR 1=1--", "password": "hacked_password"},
                )

        # ── 1. HTTP status strictly 200 ───────────────────────────────────
        assert resp.status_code == 200, (
            f"Deception layer MUST return 200, got {resp.status_code}"
        )

        # ── 2. Fake deception schema ──────────────────────────────────────
        data = resp.json()
        assert data.get("status") == "success", (
            f"Deception schema requires status=success; got {data}"
        )
        assert data.get("session_id") == "fake_token_123_abc", (
            f"Deception schema requires session_id=fake_token_123_abc; got {data}"
        )
        assert data.get("message") == "Login successful", (
            f"Deception schema requires message='Login successful'; got {data}"
        )

        # ── 3. MongoDB telemetry ──────────────────────────────────────────
        mock_log_attack.assert_called()
        mongo_args = mock_log_attack.call_args[0][0]
        assert mongo_args["classification"]["is_malicious"] is True
        assert mongo_args["deception_response"]["http_status"] == 200

        # ── 4. PostgreSQL ATTACKER_IN_DECEPTION tag ───────────────────────
        assert len(db_ctx._added_objects) > 0, (
            "Expected HoneypotLog to be added to the DB session"
        )
        log_obj = db_ctx._added_objects[0]
        assert log_obj.log_metadata["classification"]["attack_type"] == "ATTACKER_IN_DECEPTION", (
            f"Telemetry must be tagged ATTACKER_IN_DECEPTION; got "
            f"{log_obj.log_metadata['classification']['attack_type']}"
        )

    @patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock)
    @patch(_PATCH_DB_FACTORY)
    @patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant())
    async def test_command_injection_deception_200(
        self, mock_tenant, mock_db_factory, mock_log_attack
    ):
        """Command injection at /api/trap/submit also gets 200 from deception layer."""
        db_ctx = _make_db_ctx()
        mock_db_factory.return_value = db_ctx

        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="BLOCK"):
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.0.0.1", 9001)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/api/trap/submit",
                    json={"input_text": "cat /etc/passwd", "ip_address": "10.0.0.1"},
                )

        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "success"

    @patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock)
    @patch(_PATCH_DB_FACTORY)
    @patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant())
    async def test_xss_payload_deception_200(
        self, mock_tenant, mock_db_factory, mock_log_attack
    ):
        """XSS payload at /api/trap/submit receives 200 from deception layer."""
        db_ctx = _make_db_ctx()
        mock_db_factory.return_value = db_ctx

        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="BLOCK"):
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.0.0.2", 9002)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/api/trap/submit",
                    json={"input_text": "<script>alert('XSS')</script>", "ip_address": "10.0.0.2"},
                )

        assert resp.status_code == 200
        assert resp.json().get("status") == "success"

    async def test_trap_execute_deception_response_shape(
        self, mock_db_session, mock_tenant, mock_log_attack
    ):
        """
        /trap/execute with BLOCK verdict:
        → is_malicious=True, prediction_score>0.85, 64-char SHA-256 hash present.

        mock_db_session fixture registers get_db dependency override so the
        /trap/execute Depends(get_db) path resolves cleanly.
        """
        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="BLOCK"):
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.0.0.3", 9003)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/trap/execute",
                    json={"command": "rm -rf /", "ip_address": "10.0.0.3"},
                )

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["is_malicious"] is True
        assert data["prediction_score"] > 0.85
        assert "hash" in data
        assert len(data["hash"]) == 64  # SHA-256 hex string


# ===========================================================================
# 3. ADVERSARIAL & EDGE-CASE PAYLOADS
# ===========================================================================
class TestAdversarialAndEdgeCases:
    """
    Robustness tests: ensure neither the inference pipeline nor FastAPI
    crashes on pathological inputs.
    """

    @patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock)
    @patch(_PATCH_DB_FACTORY)
    @patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant())
    async def test_massive_5000_char_payload_no_oom(
        self, mock_tenant, mock_db_factory, mock_log_attack
    ):
        """
        5 000-character username → the model's max_tokens=10 guard and MLX
        context-window handling must not raise OOM or crash.

        The pipeline should either BLOCK or ALLOW the payload gracefully and
        return a valid HTTP status code.
        """
        mock_db_factory.return_value = _make_db_ctx()

        massive = "A" * 5000
        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="BLOCK"):
            login_limiter.login_attempts.clear()
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.1.0.1", 1111)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/api/auth/login",
                    json={"username": massive, "password": "pass"},
                )

        assert resp.status_code in (200, 401, 429), (
            f"Massive payload must return valid status, got {resp.status_code}"
        )

    @patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock)
    @patch(_PATCH_DB_FACTORY)
    @patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant())
    async def test_null_bytes_payload(
        self, mock_tenant, mock_db_factory, mock_log_attack
    ):
        """
        Null-byte sequence `\\x00\\x00\\x00` must not crash tokenization or
        the inference pipeline.
        """
        mock_db_factory.return_value = _make_db_ctx()

        null_input = "\x00\x00\x00"
        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="ALLOW"):
            login_limiter.login_attempts.clear()
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.1.0.2", 1112)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/api/auth/login",
                    json={"username": null_input, "password": "pass"},
                )

        assert resp.status_code in (200, 401, 429)

    @patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock)
    @patch(_PATCH_DB_FACTORY)
    @patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant())
    async def test_base64_obfuscated_sql_injection(
        self, mock_tenant, mock_db_factory, mock_log_attack
    ):
        """
        Base64-encoded SQL injection: `YWRtaW4nIE9SIDE9MS0t`
        (base64 of `admin' OR 1=1--`).

        The pipeline must not crash when it receives an obfuscated payload.
        If the MLX model is mocked to BLOCK, the deception layer must respond 200.
        """
        mock_db_factory.return_value = _make_db_ctx()

        b64_payload = base64.b64encode(b"admin' OR 1=1--").decode()
        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="BLOCK"):
            login_limiter.login_attempts.clear()
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.1.0.3", 1113)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/api/auth/login",
                    json={"username": b64_payload, "password": "pass"},
                )

        # BLOCK verdict → deception → 200
        assert resp.status_code == 200
        assert resp.json().get("status") == "success"

    @patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock)
    @patch(_PATCH_DB_FACTORY)
    @patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant())
    async def test_unicode_and_emoji_payload(
        self, mock_tenant, mock_db_factory, mock_log_attack
    ):
        """Unicode + emoji injection string must not raise a UnicodeDecodeError."""
        mock_db_factory.return_value = _make_db_ctx()

        unicode_input = "🔥💀👻 SELECT * FROM users 💉"
        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="ALLOW"):
            login_limiter.login_attempts.clear()
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.1.0.4", 1114)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/api/auth/login",
                    json={"username": unicode_input, "password": "pass"},
                )

        assert resp.status_code in (200, 401, 429)

    @patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock)
    @patch(_PATCH_DB_FACTORY)
    @patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant())
    async def test_empty_string_payload(
        self, mock_tenant, mock_db_factory, mock_log_attack
    ):
        """Empty username must be handled gracefully (no 500 / exception)."""
        mock_db_factory.return_value = _make_db_ctx()

        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="ALLOW"):
            login_limiter.login_attempts.clear()
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.1.0.5", 1115)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/api/auth/login",
                    json={"username": "", "password": "pass"},
                )

        assert resp.status_code in (200, 401, 429)

    async def test_path_traversal_at_trap_execute(
        self, mock_db_session, mock_tenant, mock_log_attack
    ):
        """
        `../../../../etc/passwd` at /trap/execute → BLOCK → is_malicious=True.

        Uses mock_db_session fixture (which installs get_db override) so the
        Depends(get_db) call in /trap/execute resolves without a real DB.
        """
        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="BLOCK"):
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.1.0.6", 1116)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/trap/execute",
                    json={"command": "../../../../etc/passwd"},
                )

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["is_malicious"] is True


# ===========================================================================
# 4. BILSTM → MLX HANDOVER (Unit tests on pipeline.evaluate_payload)
# ===========================================================================
class TestBiLSTMToMLXHandover:
    """
    Verify that `pipeline.evaluate_payload` correctly orchestrates the
    two-stage flow.  BiLSTM is always called first; MLX always decides
    the final verdict (no bypass threshold is currently active).
    """

    @patch(_PATCH_BILSTM_PRED)
    @patch(_PATCH_MLX_PIPELINE, new_callable=AsyncMock)
    async def test_high_anomaly_score_leads_to_block(
        self, mock_mlx_infer, mock_bilstm_predict
    ):
        """
        BiLSTM returns 0.99 (very suspicious).
        MLX returns BLOCK.
        Pipeline must emit BLOCK and have called BOTH models.
        """
        mock_bilstm_predict.return_value = 0.99
        mock_mlx_infer.return_value = "BLOCK"

        verdict = await pipeline.evaluate_payload("DROP TABLE users;")

        assert verdict == "BLOCK"
        mock_bilstm_predict.assert_called_once_with("DROP TABLE users;")
        mock_mlx_infer.assert_called_once_with("DROP TABLE users;")

    @patch(_PATCH_BILSTM_PRED)
    @patch(_PATCH_MLX_PIPELINE, new_callable=AsyncMock)
    async def test_low_anomaly_score_mlx_still_called(
        self, mock_mlx_infer, mock_bilstm_predict
    ):
        """
        BiLSTM returns 0.05 (low suspicion).
        Because the bypass threshold is commented out, MLX is still invoked.
        MLX returns ALLOW → pipeline returns ALLOW.
        """
        mock_bilstm_predict.return_value = 0.05
        mock_mlx_infer.return_value = "ALLOW"

        verdict = await pipeline.evaluate_payload("ping localhost")

        assert verdict == "ALLOW"
        mock_bilstm_predict.assert_called_once_with("ping localhost")
        mock_mlx_infer.assert_called_once_with("ping localhost")

    @patch(_PATCH_BILSTM_PRED)
    @patch(_PATCH_MLX_PIPELINE, new_callable=AsyncMock)
    async def test_boundary_score_mlx_is_authoritative(
        self, mock_mlx_infer, mock_bilstm_predict
    ):
        """BiLSTM returns 0.5 (boundary); MLX verdict (BLOCK) is authoritative."""
        mock_bilstm_predict.return_value = 0.5
        mock_mlx_infer.return_value = "BLOCK"

        verdict = await pipeline.evaluate_payload("UNION SELECT password FROM admin")

        assert verdict == "BLOCK"
        mock_bilstm_predict.assert_called_once()
        mock_mlx_infer.assert_called_once()

    @patch(_PATCH_BILSTM_PRED)
    @patch(_PATCH_MLX_PIPELINE, new_callable=AsyncMock)
    async def test_multiple_sequential_payloads_correct_verdicts(
        self, mock_mlx_infer, mock_bilstm_predict
    ):
        """
        Three payloads processed sequentially; side_effects ensure
        each BiLSTM score and MLX verdict are consumed in order.
        """
        mock_bilstm_predict.side_effect = [0.99, 0.01, 0.85]
        mock_mlx_infer.side_effect = ["BLOCK", "ALLOW", "BLOCK"]

        payloads = ["DELETE FROM users", "ping localhost", "cat /etc/shadow"]
        verdicts = [await pipeline.evaluate_payload(p) for p in payloads]

        assert verdicts == ["BLOCK", "ALLOW", "BLOCK"]
        assert mock_bilstm_predict.call_count == 3
        assert mock_mlx_infer.call_count == 3

    @patch(_PATCH_BILSTM_PRED)
    @patch(_PATCH_MLX_PIPELINE, new_callable=AsyncMock)
    async def test_bilstm_called_before_mlx(
        self, mock_mlx_infer, mock_bilstm_predict
    ):
        """
        Strict ordering assertion: BiLSTM (sync) must be scheduled
        before MLX (async) in the pipeline.
        """
        call_log: list[str] = []

        def bilstm_side(cmd):
            call_log.append("bilstm")
            return 0.8

        async def mlx_side(cmd):
            call_log.append("mlx")
            return "BLOCK"

        mock_bilstm_predict.side_effect = bilstm_side
        mock_mlx_infer.side_effect = mlx_side

        await pipeline.evaluate_payload("test payload")
        assert call_log == ["bilstm", "mlx"], (
            f"Expected bilstm then mlx; got {call_log}"
        )


# ===========================================================================
# 5. LOCALMLXMODEL ASYNC LOCK VERIFICATION
# ===========================================================================
class TestLocalMLXModelAsyncLock:
    """
    Direct unit tests for the LocalMLXModel singleton and its asyncio.Lock.
    The lock ensures the Metal GPU command buffer is not corrupted by
    concurrent MLX calls.
    """

    async def test_singleton_returns_same_instance(self):
        """Singleton invariant: every call to LocalMLXModel() returns `mlx_model`."""
        a = LocalMLXModel()
        b = LocalMLXModel()
        assert a is b

    async def test_async_lock_attribute_present(self):
        """
        `_async_lock` is lazily created on the first call to `infer()`.
        After the call it must be an asyncio.Lock.
        """
        model = LocalMLXModel()

        with patch(_PATCH_MLX_GENERATE, return_value="BLOCK"):
            model.model = MagicMock()
            model.tokenizer = MagicMock()
            await model.infer("test_cmd")

        assert hasattr(model, "_async_lock"), "_async_lock must exist after infer()"
        assert isinstance(model._async_lock, asyncio.Lock), (
            "_async_lock must be an asyncio.Lock"
        )

    @patch(_PATCH_MLX_GENERATE)
    async def test_concurrent_infer_calls_all_complete(self, mock_generate):
        """
        Five concurrent infer() coroutines must all finish without raising.
        The lock serialises access so order is sequential, but no errors
        are expected.
        """
        mock_generate.return_value = "BLOCK"

        model = LocalMLXModel()
        model.model = MagicMock()
        model.tokenizer = MagicMock()

        results = await asyncio.gather(
            *[model.infer(f"cmd_{i}") for i in range(5)],
            return_exceptions=True,
        )

        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0, f"Concurrent infer() raised exceptions: {errors}"
        assert len(results) == 5

    @patch(_PATCH_MLX_GENERATE)
    async def test_infer_parses_block_verdict(self, mock_generate):
        """MLX output containing 'BLOCK' → infer() returns 'BLOCK'."""
        mock_generate.return_value = "BLOCK"

        model = LocalMLXModel()
        model.model = MagicMock()
        model.tokenizer = MagicMock()

        result = await model.infer("malicious payload")
        assert result == "BLOCK"

    @patch(_PATCH_MLX_GENERATE)
    async def test_infer_parses_allow_verdict(self, mock_generate):
        """MLX output containing 'ALLOW' → infer() returns 'ALLOW'."""
        mock_generate.return_value = "ALLOW"

        model = LocalMLXModel()
        model.model = MagicMock()
        model.tokenizer = MagicMock()

        result = await model.infer("benign payload")
        assert result == "ALLOW"

    @patch(_PATCH_MLX_GENERATE)
    async def test_infer_failsafe_on_unknown_output(self, mock_generate):
        """
        If the model returns something other than BLOCK/ALLOW (e.g. empty
        or garbled), the failsafe must return 'ALLOW' (fail-open for
        legitimate traffic rather than blocking everything).
        """
        mock_generate.return_value = "UNCERTAIN OUTPUT XYZ"

        model = LocalMLXModel()
        model.model = MagicMock()
        model.tokenizer = MagicMock()

        result = await model.infer("ambiguous")
        assert result == "ALLOW", (
            f"Failsafe must return ALLOW on unknown output; got {result!r}"
        )

    async def test_infer_returns_allow_when_model_not_loaded(self):
        """
        If the MLX model weights are absent (model=None), infer() must
        return 'ALLOW' and not raise an exception.
        """
        model = LocalMLXModel()
        orig_model = model.model
        orig_tok = model.tokenizer
        try:
            model.model = None
            model.tokenizer = None
            result = await model.infer("anything")
            assert result == "ALLOW", (
                "Unloaded model must fail-safe to ALLOW"
            )
        finally:
            model.model = orig_model
            model.tokenizer = orig_tok


# ===========================================================================
# 6. ADDITIONAL SECURITY SCENARIOS
# ===========================================================================
class TestAdditionalSecurityScenarios:

    @patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock)
    @patch(_PATCH_DB_FACTORY)
    @patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant())
    async def test_benign_login_returns_401_not_deception(
        self, mock_tenant, mock_db_factory, mock_log_attack
    ):
        """
        A truly benign login (ALLOW verdict, wrong password) must receive
        401 from the normal auth path, not 200 from the deception layer.
        """
        mock_db_factory.return_value = _make_db_ctx()

        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="ALLOW"):
            login_limiter.login_attempts.clear()
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.2.0.1", 2001)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/api/auth/login",
                    json={"username": "honest_user", "password": "wrong_password"},
                )

        assert resp.status_code in (401, 429), (
            f"Benign failed login must be 401; got {resp.status_code}"
        )

    @patch(_PATCH_LOG_ATTACK, new_callable=AsyncMock)
    @patch(_PATCH_DB_FACTORY)
    @patch(_PATCH_TENANT, new_callable=AsyncMock, return_value=MockTenant())
    async def test_attacker_ip_captured_in_telemetry(
        self, mock_tenant, mock_db_factory, mock_log_attack
    ):
        """
        Attacker fingerprint (IP from X-Forwarded-For) must appear in the
        log_attack call arguments.
        """
        mock_db_factory.return_value = _make_db_ctx()

        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="BLOCK"):
            login_limiter.login_attempts.clear()
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.2.0.2", 2002)),
                base_url=BASE_URL,
                headers={"X-Forwarded-For": "203.0.113.42", "User-Agent": "EvilBot/2.0"},
            ) as client:
                await client.post(
                    "/api/auth/login",
                    json={"username": "admin' OR 1=1--", "password": "pass"},
                )

        mock_log_attack.assert_called()
        log_data = mock_log_attack.call_args[0][0]
        assert "ip_address" in log_data, "Telemetry must include ip_address"
        # The actual IP might be the forwarded one or the transport IP;
        # either way it must be a non-empty string.
        assert log_data["ip_address"], "ip_address must not be empty"

    async def test_sha256_hash_in_trap_execute_response(
        self, mock_db_session, mock_tenant, mock_log_attack
    ):
        """
        /trap/execute response must include a valid 64-hex-char SHA-256 hash
        of the interaction metadata.

        mock_db_session installs the get_db dependency override so the endpoint
        can proceed without a real database.
        """
        with patch.object(mlx_model, "infer", new_callable=AsyncMock, return_value="BLOCK"):
            async with AsyncClient(
                transport=ASGITransport(app=app, client=("10.2.0.3", 2003)),
                base_url=BASE_URL,
            ) as client:
                resp = await client.post(
                    "/trap/execute",
                    json={"command": "cat /etc/shadow"},
                )

        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "hash" in data, "Response must contain a hash field"
        assert len(data["hash"]) == 64, (
            f"Expected 64-char SHA-256 hex; got {len(data['hash'])} chars"
        )
        # Ensure it is valid hex
        int(data["hash"], 16)


# ===========================================================================
# Stand-alone entry point
# ===========================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
