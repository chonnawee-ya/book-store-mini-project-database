"""
Database Connection and Utility Module
Supports both SQLite (Local default) and Cloud MySQL (Railway, Render, TiDB, Aiven)
with 100% Prepared Statements, Transactions, and unified Row access.
"""

import os
import re
import sqlite3
from urllib.parse import urlparse

# Optional dotenv loading if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(DB_DIR, ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "ebook_store.db")
SCHEMA_SQLITE = os.path.join(DB_DIR, "schema.sql")
SCHEMA_MYSQL = os.path.join(DB_DIR, "schema_mysql.sql")

def is_mysql_configured():
    """Detect if MySQL configuration is provided via environment variables"""
    db_type = os.getenv("DB_TYPE", "").strip().lower()
    if db_type == "mysql":
        return True
    if os.getenv("DATABASE_URL", "").strip().startswith("mysql"):
        return True
    if os.getenv("MYSQL_HOST") or os.getenv("MYSQL_DATABASE"):
        return True
    return False

# ------------------------------------------------------------------------------
# MySQL Adapter & Unified Row Class
# ------------------------------------------------------------------------------
class UnifiedRow(dict):
    """
    A dict subclass that also supports integer indexing like sqlite3.Row
    Example: row['title'] and row[0] both work properly.
    """
    def __init__(self, data, column_names):
        super().__init__(data)
        self._columns = list(column_names)
        self._values = [data.get(c) for c in self._columns]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return super().__getitem__(key)

class MySQLCursorWrapper:
    def __init__(self, raw_cursor):
        self._cur = raw_cursor

    def _transform_sql(self, query):
        # Convert ? to %s for MySQL
        converted = query.replace("?", "%s")
        # Convert SQLite strftime('%Y-%m', col) to MySQL DATE_FORMAT(col, '%Y-%m')
        converted = re.sub(
            r"strftime\s*\(\s*['\"]%Y-%m['\"]\s*,\s*([^\)]+)\)",
            r"DATE_FORMAT(\1, '%Y-%m')",
            converted,
            flags=re.IGNORECASE
        )
        return converted

    def execute(self, query, args=()):
        transformed = self._transform_sql(query)
        self._cur.execute(transformed, args)
        return self

    def fetchone(self):
        row = self._cur.fetchone()
        if row is None:
            return None
        col_names = [d[0] for d in self._cur.description] if self._cur.description else []
        return UnifiedRow(row, col_names)

    def fetchall(self):
        rows = self._cur.fetchall()
        if not rows:
            return []
        col_names = [d[0] for d in self._cur.description] if self._cur.description else []
        return [UnifiedRow(r, col_names) for r in rows]

    @property
    def lastrowid(self):
        return self._cur.lastrowid

    @property
    def rowcount(self):
        return self._cur.rowcount

    @property
    def description(self):
        return self._cur.description

    def close(self):
        self._cur.close()

class MySQLConnectionWrapper:
    """Wrapper that makes PyMySQL connection act identically to sqlite3.Connection"""
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def cursor(self):
        return MySQLCursorWrapper(self._conn.cursor())

    def execute(self, query, args=()):
        cur = self.cursor()
        cur.execute(query, args)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

def _get_mysql_connection():
    import pymysql
    import pymysql.cursors

    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("mysql"):
        # Parse mysql://user:pass@host:port/dbname
        parsed = urlparse(database_url)
        conn = pymysql.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            user=parsed.username or "root",
            password=parsed.password or "",
            database=parsed.path.lstrip("/") if parsed.path else "ebook_store",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            charset="utf8mb4"
        )
    else:
        conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "ebook_store"),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            charset="utf8mb4"
        )
    return MySQLConnectionWrapper(conn)

# ------------------------------------------------------------------------------
# Core Connection Factory
# ------------------------------------------------------------------------------
def get_db_connection():
    """
    Establish and return a database connection:
    - If Cloud MySQL is configured, returns MySQLConnectionWrapper
    - Otherwise, returns SQLite connection with Foreign Keys enabled
    """
    if is_mysql_configured():
        return _get_mysql_connection()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_recreate=False):
    """
    Initializes the database schema if not already initialized.
    """
    if is_mysql_configured():
        conn = get_db_connection()
        with open(SCHEMA_MYSQL, "r", encoding="utf-8") as f:
            sql_statements = f.read().split(";")
        for stmt in sql_statements:
            clean_stmt = stmt.strip()
            if clean_stmt:
                conn.execute(clean_stmt)
        conn.commit()
        conn.close()
        return

    if force_recreate and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = get_db_connection()
    with open(SCHEMA_SQLITE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    """
    Executes a SELECT query with parameterized inputs (100% prepared statements)
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """
    Executes an INSERT, UPDATE, or DELETE query with parameterized inputs.
    Returns the lastrowid or affected row count.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    row_count = cur.rowcount
    cur.close()
    conn.close()
    return last_id, row_count

def get_schema_overview(conn):
    """
    Inspects database tables, columns, foreign keys, and row counts
    working seamlessly on both SQLite and MySQL.
    """
    schema_details = {}

    if is_mysql_configured():
        # MySQL Schema Inspector
        tables_res = conn.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'").fetchall()
        for t_row in tables_res:
            tname = t_row[0]
            # Columns
            col_rows = conn.execute(f"SHOW COLUMNS FROM `{tname}`").fetchall()
            columns = [
                {
                    "cid": idx,
                    "name": col["Field"],
                    "type": col["Type"],
                    "notnull": 1 if col["Null"] == "NO" else 0,
                    "dflt_value": col["Default"],
                    "pk": 1 if col["Key"] == "PRI" else 0
                }
                for idx, col in enumerate(col_rows)
            ]
            # Foreign keys
            fk_sql = """
                SELECT 
                    COLUMN_NAME, 
                    REFERENCED_TABLE_NAME, 
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = ?
                  AND REFERENCED_TABLE_NAME IS NOT NULL
            """
            fk_rows = conn.execute(fk_sql, (tname,)).fetchall()
            fks = [
                {
                    "from": fk["COLUMN_NAME"],
                    "table": fk["REFERENCED_TABLE_NAME"],
                    "to": fk["REFERENCED_COLUMN_NAME"]
                }
                for fk in fk_rows
            ]
            count_res = conn.execute(f"SELECT COUNT(*) FROM `{tname}`").fetchone()
            count = count_res[0] if count_res else 0

            schema_details[tname] = {
                "columns": columns,
                "foreign_keys": fks,
                "row_count": count
            }
    else:
        # SQLite Schema Inspector
        tables = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name ASC;
        """).fetchall()

        for t in tables:
            tname = t["name"]
            columns = conn.execute(f"PRAGMA table_info({tname});").fetchall()
            fks = conn.execute(f"PRAGMA foreign_key_list({tname});").fetchall()
            count = conn.execute(f"SELECT COUNT(*) FROM {tname};").fetchone()[0]
            schema_details[tname] = {
                "columns": [dict(c) for c in columns],
                "foreign_keys": [dict(fk) for fk in fks],
                "row_count": count
            }

    return schema_details
