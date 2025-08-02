"""Tests for configuration management."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from unifi_protect_exporter.core.config import Settings


def test_settings_with_valid_credentials(monkeypatch):
    """Test settings with valid UniFi credentials."""
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__HOST", "192.168.1.100")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__USERNAME", "testuser")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__PASSWORD", "testpass123")

    settings = Settings()
    assert settings.unifi.host == "192.168.1.100"
    assert settings.unifi.username == "testuser"
    assert settings.unifi.password.get_secret_value() == "testpass123"
    assert settings.update_intervals.fast == 60  # default value
    assert settings.server.host == "0.0.0.0"
    assert settings.server.port == 9099


def test_settings_with_missing_credentials(monkeypatch):
    """Test settings with missing UniFi credentials."""
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__HOST", "192.168.1.100")
    # Missing username and password

    with pytest.raises(ValidationError) as exc_info:
        Settings()

    assert "Field required" in str(exc_info.value)


def test_settings_with_otel_enabled_without_endpoint(monkeypatch):
    """Test OTEL validation when enabled without endpoint."""
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__HOST", "192.168.1.100")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__USERNAME", "testuser")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__PASSWORD", "testpass123")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_OTEL__ENABLED", "true")

    with pytest.raises(ValidationError) as exc_info:
        Settings()

    assert "OTEL endpoint must be provided" in str(exc_info.value)


def test_settings_with_custom_values(monkeypatch):
    """Test settings with custom values."""
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__HOST", "192.168.1.100")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__USERNAME", "testuser")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__PASSWORD", "testpass123")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UNIFI__PORT", "8443")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UPDATE_INTERVALS__FAST", "60")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UPDATE_INTERVALS__MEDIUM", "300")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_UPDATE_INTERVALS__SLOW", "900")
    monkeypatch.setenv("UNIFI_PROTECT_EXPORTER_LOGGING__LEVEL", "DEBUG")

    settings = Settings()
    assert settings.unifi.port == 8443

    assert settings.update_intervals.fast == 60
    assert settings.update_intervals.medium == 300
    assert settings.update_intervals.slow == 900
    assert settings.logging.level == "DEBUG"
