"""
Pytest Configuration and Shared Fixtures for Chameleon Test Suite
===================================================================

This module provides shared fixtures and configuration for all tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import asynccontextmanager


# ==============================================================================
# Mock Database Context Managers
# ==============================================================================
class MockDBContext:
    """Mock async context manager for database session_factory."""

    async def __aenter__(self):
        self.add = MagicMock()
        self.commit = AsyncMock()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockTenant:
    """Mock tenant object for get_default_tenant."""
    id = "mock_tenant_id"


# ==============================================================================
# Shared Fixtures
# ==============================================================================
@pytest.fixture
def mock_db_session():
    """Fixture providing mocked database session context manager."""
    with patch("main.db.session_factory", return_value=MockDBContext()) as mock_session:
        yield mock_session


@pytest.fixture
def mock_tenant():
    """Fixture providing mocked tenant."""
    with patch("main.get_default_tenant", new_callable=AsyncMock, return_value=MockTenant()) as mock:
        yield mock


@pytest.fixture
def mock_log_attack():
    """Fixture providing mocked log_attack function."""
    with patch("main.log_attack", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_mlx_infer():
    """Fixture providing mocked MLX infer method."""
    with patch("local_inference.mlx_model.infer", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_bilstm_predict():
    """Fixture providing mocked BiLSTM predict method."""
    with patch("pipeline.bilstm_model.predict") as mock:
        yield mock


@pytest.fixture
def mock_lifespan_override():
    """Fixture to override app lifespan for testing (skip DB connections)."""
    from main import app

    @asynccontextmanager
    async def mock_lifespan(app):
        yield

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = mock_lifespan
    yield
    app.router.lifespan_context = original_lifespan


# ==============================================================================
# Pytest Hooks
# ==============================================================================
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
