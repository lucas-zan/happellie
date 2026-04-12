import sqlite3
from contextlib import contextmanager
from typing import Iterator


class SqliteConnectionFactory:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
