"""SQL warehouse connection scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence


class DbApiCursor(Protocol):
    description: Sequence[Sequence[Any]] | None

    def execute(self, operation: str, parameters: object | None = None) -> Any:
        ...

    def fetchall(self) -> Sequence[Sequence[Any]]:
        ...

    def fetchone(self) -> Sequence[Any] | None:
        ...

    def close(self) -> None:
        ...


class DbApiConnection(Protocol):
    def cursor(self) -> DbApiCursor:
        ...

    def close(self) -> None:
        ...


class ConnectionPool(Protocol):
    def open(self) -> None:
        ...

    def close(self) -> None:
        ...

    def acquire(self) -> DbApiConnection:
        ...

    def release(self, connection: DbApiConnection) -> None:
        ...


class ConnectionProvider(Protocol):
    def connect(self) -> DbApiConnection:
        ...

    def release(self, connection: DbApiConnection) -> None:
        ...


@dataclass(frozen=True)
class WarehouseConfig:
    server_hostname: str | None = None
    http_path: str | None = None
    access_token: str | None = None
    catalog: str | None = None
    schema: str | None = None

    def is_configured(self) -> bool:
        return bool(self.server_hostname and self.http_path and self.access_token)


def _load_databricks_sql() -> Any:
    try:
        from databricks import sql
    except Exception as exc:  # pragma: no cover - exercised by import failure
        raise RuntimeError(
            "Databricks SQL connector is not installed. "
            "Add databricks-sql-connector to backend dependencies."
        ) from exc
    return sql


class DatabricksSqlConnector(ConnectionProvider):
    """Placeholder connector for Databricks SQL with pooling hooks."""

    def __init__(
        self, config: WarehouseConfig, pool: ConnectionPool | None = None
    ) -> None:
        self._config = config
        self._pool = pool

    def open_pool(self) -> None:
        if self._pool is not None:
            self._pool.open()

    def close_pool(self) -> None:
        if self._pool is not None:
            self._pool.close()

    def connect(self) -> DbApiConnection:
        if self._pool is not None:
            return self._pool.acquire()
        return self._connect_direct()

    def release(self, connection: DbApiConnection) -> None:
        if self._pool is not None:
            self._pool.release(connection)
        else:
            connection.close()

    def _connect_direct(self) -> DbApiConnection:
        if not self._config.is_configured():
            raise RuntimeError(
                "Databricks SQL connection is not configured. "
                "Set server hostname, http path, and access token."
            )

        config = self._config
        assert config.server_hostname is not None
        assert config.http_path is not None
        assert config.access_token is not None

        sql = _load_databricks_sql()
        kwargs: dict[str, Any] = {
            "server_hostname": config.server_hostname,
            "http_path": config.http_path,
            "access_token": config.access_token,
        }
        if config.catalog:
            kwargs["catalog"] = config.catalog
        if config.schema:
            kwargs["schema"] = config.schema
        return sql.connect(**kwargs)
