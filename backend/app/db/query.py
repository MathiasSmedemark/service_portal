"""Query utilities for SQL adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from app.db.connection import ConnectionProvider, DbApiCursor

QueryParams = Mapping[str, Any] | Sequence[Any] | None
RowMapping = dict[str, Any]


class QueryError(RuntimeError):
    """Raised when query results cannot be mapped safely."""


@dataclass(frozen=True)
class QueryCall:
    sql: str
    params: QueryParams | None


class QueryRunner(Protocol):
    def fetch_all(self, sql: str, params: QueryParams | None = None) -> list[RowMapping]:
        ...

    def fetch_one(self, sql: str, params: QueryParams | None = None) -> RowMapping | None:
        ...

    def execute(self, sql: str, params: QueryParams | None = None) -> None:
        ...


def _column_names(description: Sequence[Sequence[Any]] | None) -> list[str]:
    if not description:
        return []
    return [str(column[0]) for column in description]


def rows_to_dicts(
    rows: Sequence[Sequence[Any]], description: Sequence[Sequence[Any]] | None
) -> list[RowMapping]:
    columns = _column_names(description)
    if not columns:
        if rows:
            raise QueryError("Query returned rows without column metadata.")
        return []
    return [dict(zip(columns, row)) for row in rows]


class SqlQueryRunner(QueryRunner):
    """Execute SQL queries using a connection provider."""

    def __init__(self, connection_provider: ConnectionProvider) -> None:
        self._connection_provider = connection_provider

    def fetch_all(self, sql: str, params: QueryParams | None = None) -> list[RowMapping]:
        connection = self._connection_provider.connect()
        cursor: DbApiCursor | None = None
        try:
            cursor = connection.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return rows_to_dicts(rows, cursor.description)
        finally:
            if cursor is not None:
                cursor.close()
            self._connection_provider.release(connection)

    def fetch_one(self, sql: str, params: QueryParams | None = None) -> RowMapping | None:
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: QueryParams | None = None) -> None:
        connection = self._connection_provider.connect()
        cursor: DbApiCursor | None = None
        try:
            cursor = connection.cursor()
            cursor.execute(sql, params)
        finally:
            if cursor is not None:
                cursor.close()
            self._connection_provider.release(connection)


class MockQueryRunner(QueryRunner):
    """Mock query runner for local dev and tests."""

    def __init__(self, results: Mapping[str, Sequence[RowMapping]] | None = None) -> None:
        self._results = {
            sql: [dict(row) for row in rows] for sql, rows in (results or {}).items()
        }
        self.calls: list[QueryCall] = []

    def fetch_all(self, sql: str, params: QueryParams | None = None) -> list[RowMapping]:
        self.calls.append(QueryCall(sql=sql, params=params))
        return [dict(row) for row in self._results.get(sql, [])]

    def fetch_one(self, sql: str, params: QueryParams | None = None) -> RowMapping | None:
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: QueryParams | None = None) -> None:
        self.calls.append(QueryCall(sql=sql, params=params))
