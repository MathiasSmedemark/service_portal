"""Identity extraction tests."""

from app.auth.identity import extract_identity


def test_forwarded_identity_prefers_user() -> None:
    headers = {
        "X-Forwarded-User": "alice",
        "X-Forwarded-Email": "alice@example.com",
        "X-Forwarded-Preferred-Username": "alicep",
    }
    identity = extract_identity(headers, {})
    assert identity is not None
    assert identity.user == "alice"
    assert identity.email == "alice@example.com"
    assert identity.preferred_username == "alicep"
    assert identity.source == "forwarded"


def test_forwarded_identity_falls_back_to_email() -> None:
    headers = {"X-Forwarded-Email": "bob@example.com"}
    identity = extract_identity(headers, {})
    assert identity is not None
    assert identity.user == "bob@example.com"
    assert identity.email == "bob@example.com"
    assert identity.source == "forwarded"


def test_forwarded_headers_override_dev_identity() -> None:
    headers = {"X-Forwarded-User": "carol"}
    env = {"DEV_USER": "devuser", "DEV_EMAIL": "dev@example.com"}
    identity = extract_identity(headers, env)
    assert identity is not None
    assert identity.user == "carol"
    assert identity.source == "forwarded"


def test_dev_override_applies_when_allowed() -> None:
    env = {"DEV_USER": "devuser", "DEV_EMAIL": "dev@example.com"}
    identity = extract_identity({}, env)
    assert identity is not None
    assert identity.user == "devuser"
    assert identity.email == "dev@example.com"
    assert identity.source == "dev"


def test_dev_override_disabled_with_databricks_host() -> None:
    env = {"DEV_USER": "devuser", "DATABRICKS_HOST": "https://example"}
    identity = extract_identity({}, env)
    assert identity is None
