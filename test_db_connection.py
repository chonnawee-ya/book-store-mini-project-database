"""
Test Database Connection Utility
Run: python test_db_connection.py
"""

import sys
import os

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from database.db import get_db_connection, get_database_engine

def test_connection():
    engine = get_database_engine()
    print("==================================================")
    print("TESTING DATABASE CONNECTION")
    print(f"Detected Engine: {engine.upper()}")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set (using local SQLite)')}")
    print("==================================================")

    try:
        conn = get_db_connection()
        print("[OK] Connection Established Successfully!")

        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM users;")
        res = cur.fetchone()
        count = res[0] if res else 0
        print(f"[OK] Found {count} users in 'users' table.")

        cur.execute("SELECT count(*) FROM ebooks;")
        b_res = cur.fetchone()
        b_count = b_res[0] if b_res else 0
        print(f"[OK] Found {b_count} ebooks in 'ebooks' table.")

        conn.close()
        print("==================================================")
        print("[SUCCESS] ALL TESTS PASSED! Your database is ready!")
        print("==================================================")
        return True
    except Exception as e:
        print("==================================================")
        print(f"[ERROR] Connection Failed: {e}")
        print("==================================================")
        print("Troubleshooting steps:")
        print("1. Check .env file has valid DATABASE_URL")
        print("2. Ensure [YOUR-PASSWORD] is replaced with real password")
        print("3. Ensure schema_postgresql.sql has been executed in Supabase")
        print("==================================================")
        return False

if __name__ == "__main__":
    test_connection()
