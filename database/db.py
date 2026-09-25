"""
Database Connection and Utility Module
Supports:
1. SQLite (Default local development)
2. PostgreSQL / Supabase (Cloud SQL with Web Table Editor)
3. MySQL / MariaDB (Cloud MySQL)
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
SCHEMA_POSTGRES = os.path.join(DB_DIR, "schema_postgresql.sql")

def get_database_engine():
    """Detect configured database engine: 'postgres', 'mysql', or 'sqlite'"""
    db_type = os.getenv("DB_TYPE", "").strip().lower()
    db_url = os.getenv("DATABASE_URL", "").strip().lower()

    if db_type in ["postgres", "postgresql"] or db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
        return "postgres"
    if db_type == "mysql" or db_url.startswith("mysql"):
        return "mysql"
    if os.getenv("PGHOST") or os.getenv("POSTGRES_HOST"):
        return "postgres"
    if os.getenv("MYSQL_HOST") or os.getenv("MYSQL_DATABASE"):
        return "mysql"
    return "sqlite"

def is_mysql_configured():
    return get_database_engine() == "mysql"

def is_postgres_configured():
    return get_database_engine() == "postgres"

# ------------------------------------------------------------------------------
# Unified Row Class (Supports both dict['key'] and row[0] integer index)
# ------------------------------------------------------------------------------
class UnifiedRow(dict):
    def __init__(self, data, column_names):
        super().__init__(data)
        self._columns = list(column_names)
        self._values = [data.get(c) for c in self._columns]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return super().__getitem__(key)

# ------------------------------------------------------------------------------
# Generic Remote DB Cursor & Connection Wrappers
# ------------------------------------------------------------------------------
class RemoteCursorWrapper:
    def __init__(self, raw_cursor, engine="mysql"):
        self._cur = raw_cursor
        self._engine = engine
        self._last_id = None

    def _transform_sql(self, query):
        # Convert ? to %s for PostgreSQL and MySQL
        converted = query.replace("?", "%s")

        if self._engine == "postgres":
            # Convert SQLite strftime('%Y-%m', col) to Postgres TO_CHAR(col, 'YYYY-MM')
            converted = re.sub(
                r"strftime\s*\(\s*['\"]%Y-%m['\"]\s*,\s*([^\)]+)\)",
                r"TO_CHAR(\1, 'YYYY-MM')",
                converted,
                flags=re.IGNORECASE
            )
            # Fix Postgres boolean: is_active = 1 -> is_active = TRUE
            converted = re.sub(r"\b(is_active)\s*=\s*1\b", r"\1 = TRUE", converted, flags=re.IGNORECASE)
            converted = re.sub(r"\b(is_active)\s*=\s*0\b", r"\1 = FALSE", converted, flags=re.IGNORECASE)
            converted = re.sub(r"\b(is_active)\s*=\s*%s\b", r"\1 = (%s)::boolean", converted, flags=re.IGNORECASE)
            if "INSERT INTO EBOOKS" in converted.upper() or "INSERT INTO `EBOOKS`" in converted.upper() or 'INSERT INTO "EBOOKS"' in converted.upper():
                converted = re.sub(r",\s*%s\s*\)\s*$", r", (%s)::boolean)", converted)
        elif self._engine == "mysql":
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
        self._last_id = None

        if self._engine == "postgres" and transformed.strip().upper().startswith("INSERT INTO"):
            if "RETURNING" not in transformed.upper():
                m = re.search(r"INSERT\s+INTO\s+([a-zA-Z0-9_\"`]+)", transformed, re.IGNORECASE)
                if m:
                    tbl = m.group(1).strip('"\'`').lower()
                    id_cols = {
                        "users": "user_id", "roles": "role_id", "categories": "category_id",
                        "authors": "author_id", "ebooks": "ebook_id", "carts": "cart_id",
                        "cart_items": "cart_item_id", "orders": "order_id",
                        "order_items": "order_item_id", "payments": "payment_id"
                    }
                    if tbl in id_cols:
                        transformed = f"{transformed} RETURNING {id_cols[tbl]}"
                        self._cur.execute(transformed, args)
                        res = self._cur.fetchone()
                        if res:
                            self._last_id = res[id_cols[tbl]] if isinstance(res, dict) else res[0]
                        return self

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
        if self._engine == "postgres":
            return self._last_id
        if hasattr(self._cur, "lastrowid"):
            return self._cur.lastrowid
        return None

    @property
    def rowcount(self):
        return self._cur.rowcount

    @property
    def description(self):
        return self._cur.description

    def close(self):
        self._cur.close()

class RemoteConnectionWrapper:
    def __init__(self, raw_conn, engine="mysql"):
        self._conn = raw_conn
        self._engine = engine

    def cursor(self):
        return RemoteCursorWrapper(self._conn.cursor(), engine=self._engine)

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

# ------------------------------------------------------------------------------
# PostgreSQL Connection (Supabase / Neon / Render)
# ------------------------------------------------------------------------------
def _get_postgres_connection():
    import psycopg2
    from psycopg2.extras import RealDictCursor

    db_url = os.getenv("DATABASE_URL", "").strip()
    try:
        if db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")):
            # SQLAlchemy and modern hosts use postgresql://; fix postgres:// if present
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            # Ensure sslmode=require for Supabase and modern Cloud Postgres
            if "sslmode=" not in db_url:
                separator = "&" if "?" in db_url else "?"
                db_url = f"{db_url}{separator}sslmode=require"
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor, connect_timeout=10)
        else:
            conn = psycopg2.connect(
                host=os.getenv("PGHOST", os.getenv("POSTGRES_HOST", "localhost")),
                port=int(os.getenv("PGPORT", os.getenv("POSTGRES_PORT", 5432))),
                user=os.getenv("PGUSER", os.getenv("POSTGRES_USER", "postgres")),
                password=os.getenv("PGPASSWORD", os.getenv("POSTGRES_PASSWORD", "")),
                database=os.getenv("PGDATABASE", os.getenv("POSTGRES_DB", "postgres")),
                cursor_factory=RealDictCursor,
                sslmode="require",
                connect_timeout=10
            )
        return RemoteConnectionWrapper(conn, engine="postgres")
    except Exception as e:
        print(f"[DATABASE CONNECTION ERROR - POSTGRESQL]: {e}")
        raise

# ------------------------------------------------------------------------------
# MySQL Connection
# ------------------------------------------------------------------------------
def _get_mysql_connection():
    import pymysql
    import pymysql.cursors

    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("mysql"):
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
    return RemoteConnectionWrapper(conn, engine="mysql")

# ------------------------------------------------------------------------------
# Core Connection Factory
# ------------------------------------------------------------------------------
def get_db_connection():
    """
    Establish and return a database connection:
    - 'postgres': Supabase / PostgreSQL
    - 'mysql': Cloud MySQL
    - 'sqlite': Local SQLite (Default)
    """
    engine = get_database_engine()
    if engine == "postgres":
        return _get_postgres_connection()
    if engine == "mysql":
        return _get_mysql_connection()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_recreate=False):
    """Initializes the database schema if needed."""
    engine = get_database_engine()
    if engine == "postgres":
        conn = get_db_connection()
        with open(SCHEMA_POSTGRES, "r", encoding="utf-8") as f:
            sql_script = f.read()
        for stmt in sql_script.split(";"):
            clean = stmt.strip()
            if clean:
                conn.execute(clean)
        conn.commit()
        conn.close()
        return

    if engine == "mysql":
        conn = get_db_connection()
        with open(SCHEMA_MYSQL, "r", encoding="utf-8") as f:
            sql_script = f.read()
        for stmt in sql_script.split(";"):
            clean = stmt.strip()
            if clean:
                conn.execute(clean)
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
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
    """Cross-platform schema inspector for SQLite, PostgreSQL, and MySQL"""
    engine = get_database_engine()
    schema_details = {}

    if engine == "postgres":
        tables_res = conn.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name ASC;
        """).fetchall()

        for t_row in tables_res:
            tname = t_row["table_name"]
            col_rows = conn.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = ?
                ORDER BY ordinal_position ASC;
            """, (tname,)).fetchall()

            columns = [
                {
                    "cid": idx,
                    "name": col["column_name"],
                    "type": col["data_type"],
                    "notnull": 1 if col["is_nullable"] == "NO" else 0,
                    "dflt_value": col["column_default"],
                    "pk": 1 if "id" in col["column_name"] and idx == 0 else 0
                }
                for idx, col in enumerate(col_rows)
            ]

            count_res = conn.execute(f'SELECT COUNT(*) FROM "{tname}"').fetchone()
            count = count_res[0] if count_res else 0

            schema_details[tname] = {
                "columns": columns,
                "foreign_keys": [],
                "row_count": count
            }

    elif engine == "mysql":
        tables_res = conn.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'").fetchall()
        for t_row in tables_res:
            tname = t_row[0]
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
            count_res = conn.execute(f"SELECT COUNT(*) FROM `{tname}`").fetchone()
            count = count_res[0] if count_res else 0
            schema_details[tname] = {
                "columns": columns,
                "foreign_keys": [],
                "row_count": count
            }
    else:
        # SQLite
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
