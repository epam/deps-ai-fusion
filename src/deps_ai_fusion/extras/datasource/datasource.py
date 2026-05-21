import logging
import threading
from contextlib import contextmanager
from typing import Any, Dict, Generator

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.engine.url import URL

from .backoff import backoff
from .constants import DBDialect, DBDriver

__all__ = ["Database", "metadata"]


metadata = MetaData()


class Database:  # noqa: WPS230
    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        dialect: DBDialect = DBDialect.POSTGRES,
        driver: DBDriver = DBDriver.PSYCOPG2,
        metaflags: dict = None,
        require_secure_transport: bool = False,
        sslkey: str = "",
        sslcert: str = "",
        sslrootcert: str = "",
        sslmode: str = "verify-full",
    ) -> None:
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.dialect = dialect
        self.driver = driver
        self.drivename = f"{dialect.value}+{driver.value}"
        self.metaflags = metaflags if metaflags is not None else {}
        self.require_secure_transport = require_secure_transport
        self._sslkey = sslkey
        self._sslcert = sslcert
        self._sslmode = sslmode
        self._sslrootcert = sslrootcert

        self.engine: Engine = None
        self.engine_url: URL = None

        self._registry = threading.local()
        self._logger = logging.getLogger(self.__class__.__name__)

    @backoff(times=3)
    def get_connection(self) -> Connection:
        if not self.engine:
            raise ValueError("Database isn't configured")

        try:
            connection = self._registry.connection
            if connection is None:
                raise AttributeError()
        except AttributeError:
            self._logger.debug("Start new database connection")
            connection = self.configure_connection(self.engine.connect())
        self.check_connection(connection)
        self._registry.connection = connection
        return connection

    @contextmanager
    def connection(self) -> Generator[Connection, None, None]:
        connection = self.get_connection()

        transaction = connection.begin_nested() if connection.in_transaction() else connection.begin()
        try:
            yield connection
            transaction.commit()
        except Exception:  # noqa: E722
            transaction.rollback()
            raise

    def configure_connection(self, connection) -> Connection:
        return connection.execution_options(autocommit=False)

    def connect(self) -> None:
        self._logger.debug("Initialize database engine")
        self.engine_url = URL(
            drivername=self.drivename,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            query=self.metaflags,
        )
        connect_args: Dict[str, Any] = {}
        if self.require_secure_transport:
            if self.driver == DBDriver.PSYCOPG2:
                connect_args = {
                    "sslcert": self._sslcert,
                    "sslkey": self._sslkey,
                    "sslmode": self._sslmode,
                    "sslrootcert": self._sslrootcert,
                }

        self.engine = create_engine(
            self.engine_url,
            pool_size=5,
            connect_args=connect_args,
        )

    def close(self) -> None:
        self._logger.debug("Close database connection")
        try:
            if self._registry.connection:
                self._registry.connection.close()
                self._registry.connection = None
        except AttributeError:
            pass

    def healthcheck(self):
        with self.connection() as conn:
            conn.execute(text("select 1;"))

    def check_connection(self, connection: Connection) -> None:
        try:
            if connection.in_transaction():
                with connection.begin_nested():
                    connection.execute(text("select 1;"))
            else:
                with connection.begin():
                    connection.execute(text("select 1;"))
        except Exception as err:
            self._logger.error(f"Checking connection failed with error: {err}.")
            self.close()
            raise
