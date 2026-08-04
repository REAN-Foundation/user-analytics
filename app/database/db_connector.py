import re

import mysql.connector

try:
    import psycopg2
except ImportError:  # psycopg2 is only required when using PostgreSQL
    psycopg2 = None


PG_IDENTIFIER_RE = None

_STRING_LITERAL_RE = re.compile(r"('(?:[^']|'')*')")


def _pg_identifier_regex():
    """Lazily build a regex matching the mixed-case column names of every model."""
    global PG_IDENTIFIER_RE
    if PG_IDENTIFIER_RE is None:
        names = set()
        try:
            from app.database.base import Base
            import app.database.models  # noqa: F401  -- registers all tables
            for table in Base.metadata.tables.values():
                for column in table.columns:
                    # Only names that PostgreSQL would fold need quoting.
                    if column.name != column.name.lower():
                        names.add(column.name)
        except Exception as error:  # pragma: no cover - defensive
            print("Could not build PostgreSQL identifier map:", error)
        if names:
            alternation = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
            PG_IDENTIFIER_RE = re.compile(r'(?<![\w"])(' + alternation + r')(?![\w"])')
        else:
            PG_IDENTIFIER_RE = re.compile(r"(?!x)x")  # matches nothing
    return PG_IDENTIFIER_RE


def quote_pg_identifiers(query):
    """Double-quote known mixed-case column names outside of string literals."""
    regex = _pg_identifier_regex()
    parts = _STRING_LITERAL_RE.split(query)
    for i in range(0, len(parts), 2):
        parts[i] = regex.sub(r'"\1"', parts[i])
    return "".join(parts)

# endregion


class RowDict(dict):
    """
    Result row with case-insensitive key lookup.

    MySQL is case-insensitive for column names while PostgreSQL folds unquoted
    identifiers to lowercase, so a raw ``SELECT *`` returns keys like
    ``TenantName`` on MySQL but ``tenantname`` on PostgreSQL. This dict keeps the
    keys exactly as the driver returned them (serialisation is unchanged) but
    resolves lookups, ``in`` and ``get`` case-insensitively, so existing code can
    read ``row['TenantName']`` on either engine.
    """

    def _actual_key(self, key):
        if isinstance(key, str) and not super().__contains__(key):
            lowered = key.lower()
            for existing in self.keys():
                if isinstance(existing, str) and existing.lower() == lowered:
                    return existing
        return key

    def __getitem__(self, key):
        return super().__getitem__(self._actual_key(key))

    def __contains__(self, key):
        return super().__contains__(self._actual_key(key))

    def get(self, key, default=None):
        return super().get(self._actual_key(key), default)


class DatabaseConnector:
    """
    Dialect-aware raw database connector.

    Picks the underlying driver (mysql.connector or psycopg2) based on the
    `dialect` so that switching DB_DIALECT in the environment automatically
    connects to the right engine without code changes.
    """

    def __init__(self, host, user, password, database, port=None, dialect="mysql", driver=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.dialect = (dialect or "mysql").lower()
        self.driver = driver
        if port:
            self.port = int(port)
        else:
            self.port = 5432 if self.is_postgres else 3306

    @property
    def is_postgres(self):
        return self.dialect in ("postgres", "postgresql")

    # region Connection management

    def connect(self, database=None):
        target_db = database if database is not None else self.database
        try:
            if self.is_postgres:
                if psycopg2 is None:
                    raise ImportError(
                        "psycopg2 is required for PostgreSQL. Install it with "
                        "`pip install psycopg2-binary`."
                    )
                return psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    dbname=target_db,
                    user=self.user,
                    password=self.password,
                )
            return mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=target_db,
                user=self.user,
                password=self.password,
            )
        except Exception as error:
            print(
                f"Error connecting to the database "
                f"[dialect={self.dialect} driver={self.driver} host={self.host} "
                f"port={self.port} db={target_db} user={self.user}]:",
                error,
            )
            return None

    def _new_cursor(self, connection):
        if self.is_postgres:
            return connection.cursor()
        return connection.cursor(buffered=True)

    def close_connection(self, connection):
        if connection is None:
            return
        try:
            if self.is_postgres:
                if connection.closed == 0:
                    connection.close()
            else:
                if connection.is_connected():
                    connection.close()
        except Exception:
            pass

    # endregion

    def create_db(self):
        if self.is_postgres:
            self._create_postgres_db()
        else:
            self._create_mysql_db()

    def _create_mysql_db(self):
        connection = self.connect(database=None)
        if connection is None:
            return
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        cursor.execute(f"USE {self.database}")
        connection.commit()
        cursor.close()
        connection.close()

    def _create_postgres_db(self):
        connection = self.connect(database="postgres")
        if connection is None:
            return
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
        if cursor.fetchone() is None:
            cursor.execute(f'CREATE DATABASE "{self.database}"')
        cursor.close()
        connection.close()

    def is_read_only_query(self, query):
        q = query.strip().upper()
        return q.startswith("SELECT") or q.startswith("WITH") or q.find('SELECT') != -1

    def execute_query(self, query, params=None):
        read_only_query = self.is_read_only_query(query)
        if self.is_postgres:
            query = quote_pg_identifiers(query)
        connection = None
        try:
            connection = self.connect()
            with self._new_cursor(connection) as cursor:
                cursor.execute(query, params)
                if read_only_query:
                    rows = cursor.fetchall()
                    column_names = [i[0] for i in cursor.description]
                    result = [RowDict(zip(column_names, row)) for row in rows]
                    self.close_connection(connection)
                    return result
                else:
                    connection.commit()
                    rowcount = cursor.rowcount
                    self.close_connection(connection)
                    return rowcount
        except Exception as error:
            print("Error executing the query:", error)
            if not read_only_query and connection is not None:
                connection.rollback()
            self.close_connection(connection)
            return None

    def execute_read_query(self, query, params=None):
        read_only_query = self.is_read_only_query(query)
        if not read_only_query:
            print("This method is only for read-only queries.")
            return None
        if self.is_postgres:
            query = quote_pg_identifiers(query)
        connection = None
        try:
            connection = self.connect()
            with self._new_cursor(connection) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                column_names = [i[0] for i in cursor.description]
                result = [RowDict(zip(column_names, row)) for row in rows]
                self.close_connection(connection)
                return result
        except Exception as error:
            print("Error executing the read query:", error)
            self.close_connection(connection)
            return None

    def execute_write_query(self, query, params=None):
        read_only_query = self.is_read_only_query(query)
        if read_only_query:
            print("This method is only for write queries.")
            return None
        if self.is_postgres:
            query = quote_pg_identifiers(query)
        connection = None
        try:
            connection = self.connect()
            with self._new_cursor(connection) as cursor:
                cursor.execute(query, params)
                connection.commit()
                rowcount = cursor.rowcount
                self.close_connection(connection)
                return rowcount
        except Exception as error:
            print("Error executing the write query:", error)
            if connection is not None:
                connection.rollback()
            self.close_connection(connection)
            return None
