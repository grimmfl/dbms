import sqlite3
from enum import Enum
from typing import List, Any, Tuple


class Resolver:
    def resolve(self, query: "Query") -> str:
        """
        Resolves a query to a sql command.\n
        Has to be implemented by concrete resolvers.\n
        :param query: the query
        :return: the sql command as a string
        """
        raise NotImplementedError()


class QueryOp(Enum):
    SELECT = 0
    WHERE = 1


class Query:
    def __init__(self, table: "Table", op: QueryOp, param: Any, child: "Query" = None):
        """
        Initializes a query.\n
        :param table: The table the query should work on
        :param op: The operand
        :param param: The parameters for the query
        :param child: The child of the query
        """
        self._table: "Table" = table
        self._op: QueryOp = op
        self._param: Any = param
        self._child: Query = child

    @property
    def op(self) -> QueryOp:
        return self._op

    @property
    def param(self) -> Any:
        return self._param

    @property
    def table(self) -> "Table":
        return self._table

    @property
    def child(self) -> "Query":
        return self._child

    #def where(self, filters: List[Dict[str, Any]]) -> "Query":
    #    """
    #    Creates a query with QueryOp = WHERE and appends itself as the child\n
    #    :param filters: The filters to filter for. Dicts are linked with or, items in dict are linked with and.
    #    :return: The where query
    #    """
    #    return Query(self._table, QueryOp.WHERE, filters, self)

    def resolve(self) -> str:
        """
        Resolves the query with the resolver on the database\n
        :return: The sql command as a string
        """
        return self._table.database.resolver.resolve(self)


class Table:
    def __init__(self, database: "Database", name: str):
        """
        Initializes a table.\n
        :param database: The database to work on
        :param name: The table name
        """
        self._database: "Database" = database
        self._name: str = name

    @property
    def database(self) -> "Database":
        return self._database

    @property
    def name(self) -> str:
        return self._name

    def select(self, columns: str or List[str]) -> Query:
        """
        Creates a query with QueryOp = SELECT and no child.\n
        :param columns: The columns to select
        :return: The select query
        """
        if columns == "*":
            columns = self.get_columns()
        return Query(self, QueryOp.SELECT, columns)

    def get_columns(self) -> List[str]:
        """
        Returns all columns of the table.\n
        Has to be implemented by concrete tables.\n
        :return: The columns
        """
        raise NotImplementedError()


Connection = sqlite3.Connection


class Database:
    def __init__(self, resolver: Resolver):
        """
        Initializes the database with a query resolver\n
        :param resolver: The resolver
        """
        self._resolver: Resolver = resolver

    @property
    def resolver(self) -> Resolver:
        return self._resolver

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
        return Table(self, item)

    def get_tables(self) -> List[str]:
        """
        Returns all tables of the database.\n
        Has to be implemented by concrete tables.\n
        :return: The table names
        """
        raise NotImplementedError()

    def connect(self) -> Connection:
        """
        Creates a connection to the database.\n
        Has to be implemented by concrete tables.\n
        :return: The connection
        """
        raise NotImplementedError()

    def fetch(self, sql: str, params: Tuple[Any]) -> List[Any]:
        """
        Fetches results for a sql command\n
        Has to be implemented by concrete tables.\n
        :param sql: The sql command
        :param params: The params
        :return: The results
        """
        raise NotImplementedError()

    def execute(self, sql: str, params: Tuple[Any]):
        """
        Executes a sql command\n
        Has to be implemented by concrete tables.\n
        :param sql: The sql command
        :param params: The params
        """
        raise NotImplementedError()
