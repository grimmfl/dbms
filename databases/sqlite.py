import sqlite3
from typing import List, Any, Tuple

from databases import Database, Table, Query, QueryOp, Resolver


class SqliteResolver(Resolver):
    def resolve(self, query: "Query") -> str:
        """
        Resolves a query to a sql command.\n
        :param query: the query
        :return: the sql command as a string
        """
        if query.op.value == QueryOp.SELECT.value:
            if not isinstance(query.param, list):
                raise TypeError("Param for select query has to be of type list.")
            if query.child is not None:
                raise ValueError("Select query can not have a child.")
            return f"SELECT {','.join(query.param)} FROM {query.table.name}"
        elif query.op.value == QueryOp.WHERE.value:
            if not isinstance(query.param, str):
                raise TypeError("Param for where query has to be of type str.")
            if query.child is None:
                raise ValueError("Child for where query can not be None.")
            if not query.child.op.value == QueryOp.SELECT.value:
                raise ValueError("Child query has to have QueryOp = SELECT.")
            select_sql = query.child.resolve()
            return f"{select_sql} WHERE {query.param}"


class SqliteTable(Table):
    def get_columns(self) -> List[str]:
        sql = f"PRAGMA table_info({self.name})"
        columns = self.database.fetch(sql, ())
        return list(map(lambda c: c[1], columns))


class SqliteDatabase(Database):
    def __init__(self, path: str):
        self._path: str = path
        resolver = SqliteResolver()
        super().__init__(resolver)

    def __getitem__(self, item) -> Table:
        """
        Returns the table object for a given name\n
        :param item: The table name
        :return: The table object
        """
        if not isinstance(item, str):
            raise TypeError("Database name must be of type str")
        if item not in self.get_tables():
            raise KeyError(f"Database '{item}' does not exist")
        return SqliteTable(self, item)

    def get_tables(self) -> List[str]:
        """
        Returns all tables of the database.\n
        :return: The table names
        """
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        tables = self.fetch(sql, ())
        return list(map(lambda t: t[0], tables))

    def connect(self) -> sqlite3.Connection:
        """
        Creates a sqlite connection to the database.\n
        :return: The connection
        """
        return sqlite3.connect(self._path)

    def execute(self, sql: str, params: Tuple[Any]):
        """
        Executes a sql command\n
        :param sql: The sql command
        :param params: The params
        """
        with self.connect() as conn:
            c = conn.cursor()
            c.execute(sql, params)
            conn.commit()

    def fetch(self, sql: str, params: Tuple[Any]) -> List[Any]:
        """
        Fetches results for a sql command\n
        :param sql: The sql command
        :param params: The params
        :return: The results
        """
        with self.connect() as conn:
            c = conn.cursor()
            c.execute(sql, params)
            return c.fetchall()
