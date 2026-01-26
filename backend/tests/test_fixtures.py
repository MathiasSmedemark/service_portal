"""Local fixture repository tests."""

from app.db.fixtures import LocalFixtureRepository


def test_list_platforms() -> None:
    repo = LocalFixtureRepository()
    platforms = repo.list_platforms()
    assert platforms
    assert platforms[0].id


def test_get_platform_returns_none_for_missing() -> None:
    repo = LocalFixtureRepository()
    assert repo.get_platform("missing") is None


def test_filter_status_checks_by_platform() -> None:
    repo = LocalFixtureRepository()
    platform_id = repo.list_platforms()[0].id
    checks = repo.list_status_checks(platform_id=platform_id)
    assert checks
    assert all(check.platform_id == platform_id for check in checks)


def test_filter_work_items_by_state() -> None:
    repo = LocalFixtureRepository()
    items = repo.list_work_items(state="open")
    assert items
    assert all(item.state == "open" for item in items)
