"""
Export SQLite Seed Data to MySQL standard SQL script (database/seed_data_mysql.sql)
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ebook_store.db")
OUTPUT_MYSQL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_data_mysql.sql")

def export_to_mysql():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    tables = ["roles", "users", "categories", "authors", "ebooks", "carts", "cart_items", "orders", "order_items", "payments"]

    with open(OUTPUT_MYSQL_PATH, "w", encoding="utf-8") as f:
        f.write("-- ==============================================================================\n")
        f.write("-- Seed Data Script for MySQL 8.0+ / MariaDB 10.5+\n")
        f.write("-- Database: ebook_store_db\n")
        f.write("-- ==============================================================================\n\n")
        f.write("USE ebook_store_db;\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

        for table in tables:
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            if not rows:
                continue

            columns = rows[0].keys()
            col_names = ", ".join([f"`{c}`" for c in columns])

            f.write(f"-- Data for table `{table}` ({len(rows)} records)\n")
            f.write(f"INSERT INTO `{table}` ({col_names}) VALUES\n")

            value_lines = []
            for r in rows:
                vals = []
                for val in r:
                    if val is None:
                        vals.append("NULL")
                    elif isinstance(val, (int, float)):
                        vals.append(str(val))
                    else:
                        escaped = str(val).replace("'", "''").replace("\\", "\\\\")
                        vals.append(f"'{escaped}'")
                value_lines.append(f"({', '.join(vals)})")

            f.write(",\n".join(value_lines) + ";\n\n")

        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
        f.write("-- Finished seeding MySQL data.\n")

    conn.close()
    print("Generated MySQL seed script successfully.")

if __name__ == "__main__":
    export_to_mysql()
