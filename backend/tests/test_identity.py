"""Identity extraction tests."""

from app.auth.identity import extract_identity
from app.core.config import Settings


def _settings(
    databricks_host: str | None = None,
    databricks_app_port: int = 8000,
    dev_user: str | None = None,
    dev_email: str | None = None,
) -> Settings:
    return Settings(
        databricks_host=databricks_host,
        databricks_app_port=databricks_app_port,
        dev_user=dev_user,
        dev_email=dev_email,
    )


def test_forwarded_identity_prefers_user() -> None:
    headers = {
        "X-Forwarded-User": "alice",
        "X-Forwarded-Email": "alice@example.com",
        "X-Forwarded-Preferred-Username": "alicep",
    }
    identity = extract_identity(headers, _settings())
    assert identity is not None
    assert identity.user == "alice"
    assert identity.email == "alice@example.com"
    assert identity.preferred_username == "alicep"
    assert identity.source == "forwarded"


def test_forwarded_identity_falls_back_to_email() -> None:
    headers = {"X-Forwarded-Email": "bob@example.com"}
    identity = extract_identity(headers, _settings())
    assert identity is not None
    assert identity.user == "bob@example.com"
    assert identity.email == "bob@example.com"
    assert identity.source == "forwarded"


def test_forwarded_headers_override_dev_identity() -> None:
    headers = {"X-Forwarded-User": "carol"}
    settings = _settings(dev_user="devuser", dev_email="dev@example.com")
    identity = extract_identity(headers, settings)
    assert identity is not None
    assert identity.user == "carol"
    assert identity.source == "forwarded"


def test_dev_override_applies_when_allowed() -> None:
    settings = _settings(dev_user="devuser", dev_email="dev@example.com")
    identity = extract_identity({}, settings)
    assert identity is not None
    assert identity.user == "devuser"
    assert identity.email == "dev@example.com"
    assert identity.source == "dev"


def test_dev_override_disabled_with_databricks_host() -> None:
    settings = _settings(dev_user="devuser", databricks_host="https://example")
    identity = extract_identity({}, settings)
    assert identity is None
