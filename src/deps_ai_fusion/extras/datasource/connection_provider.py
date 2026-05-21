from sqlalchemy.engine import Connection

from .datasource import Database

__all__ = ["ConnectionProvider"]


class ConnectionProvider:
    def __init__(self, database: Database) -> None:
        self._db = database

    def __call__(self) -> Connection:
        return self._db.get_connection()
