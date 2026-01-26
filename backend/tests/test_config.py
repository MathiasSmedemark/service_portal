"""Settings tests."""

from app.core.config import get_settings


def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)
    monkeypatch.delenv("DATABRICKS_APP_PORT", raising=False)
    monkeypatch.delenv("DEV_USER", raising=False)
    monkeypatch.delenv("DEV_EMAIL", raising=False)

    get_settings.cache_clear()
    settings = get_settings()
    assert settings.databricks_host is None
    assert settings.databricks_app_port == 8000
    assert settings.dev_override_enabled is True
    get_settings.cache_clear()


def test_dev_override_disabled_with_host(monkeypatch) -> None:
    monkeypatch.setenv("DATABRICKS_HOST", "https://example")

    get_settings.cache_clear()
    settings = get_settings()
    assert settings.dev_override_enabled is False
    get_settings.cache_clear()
