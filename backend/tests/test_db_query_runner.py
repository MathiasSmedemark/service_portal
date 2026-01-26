"""Tests for SQL query runners."""

from __future__ import annotations

from typing import Any, Sequence

from app.db.query import MockQueryRunner, QueryCall, SqlQueryRunner


class _StubCursor:
    def __init__(self, rows: Sequence[Sequence[Any]], columns: Sequence[str]) -> None:
        self._rows = list(rows)
        self.description = [(column, None, None, None, None, None, None) for column in columns]
        self.executed: list[tuple[str, object | None]] = []
        self.closed = False

    def execute(self, operation: str, parameters: object | None = None) -> None:
        self.executed.append((operation, parameters))

    def fetchall(self) -> Sequence[Sequence[Any]]:
        return list(self._rows)

    def fetchone(self) -> Sequence[Any] | None:
        return self._rows[0] if self._rows else None

    def close(self) -> None:
        self.closed = True


class _StubConnection:
    def __init__(self, cursor: _StubCursor) -> None:
        self._cursor = cursor
        self.closed = False

    def cursor(self) -> _StubCursor:
        return self._cursor

    def close(self) -> None:
        self.closed = True


class _StubProvider:
    def __init__(self, connection: _StubConnection) -> None:
        self._connection = connection
        self.released: list[_StubConnection] = []

    def connect(self) -> _StubConnection:
        return self._connection

    def release(self, connection: _StubConnection) -> None:
        self.released.append(connection)
        connection.close()


def test_query_runner_fetch_all_maps_rows() -> None:
    cursor = _StubCursor(rows=[("platform-1", "ok")], columns=["id", "state"])
    connection = _StubConnection(cursor)
    provider = _StubProvider(connection)
    runner = SqlQueryRunner(provider)

    result = runner.fetch_all("select id, state from platforms", {"state": "ok"})

    assert result == [{"id": "platform-1", "state": "ok"}]
    assert cursor.executed == [("select id, state from platforms", {"state": "ok"})]
    assert cursor.closed is True
    assert connection.closed is True
    assert provider.released == [connection]


def test_query_runner_fetch_one_handles_empty_result() -> None:
    cursor = _StubCursor(rows=[], columns=["id"])
    connection = _StubConnection(cursor)
    provider = _StubProvider(connection)
    runner = SqlQueryRunner(provider)

    result = runner.fetch_one("select id from platforms")

    assert result is None


def test_mock_query_runner_records_calls() -> None:
    runner = MockQueryRunner({"select 1": [{"value": 1}]})

    assert runner.fetch_one("select 1") == {"value": 1}
    runner.execute("update platforms set state = :state", {"state": "ok"})

    assert runner.calls == [
        QueryCall(sql="select 1", params=None),
        QueryCall(sql="update platforms set state = :state", params={"state": "ok"}),
    ]
