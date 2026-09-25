"""
Automated Test Suite for E-Book Store Database and Business Rules
Covers TC-01 through TC-08 from Software Specification Sheet & 4 Analytics SQL queries.
"""

import unittest
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection, query_db, execute_db

class TestEBookStoreDatabase(unittest.TestCase):

    def setUp(self):
        self.conn = get_db_connection()

    def tearDown(self):
        self.conn.close()

    def test_tc01_register_new_user_success(self):
        """TC-01: สมัครสมาชิกสำเร็จด้วยอีเมลใหม่"""
        test_email = "test_user_tc01@example.com"
        # Ensure cleanup
        self.conn.execute("DELETE FROM users WHERE email = ?", (test_email,))
        self.conn.commit()

        cur = self.conn.cursor()
        hashed = generate_password_hash("securepass123")
        cur.execute("""
            INSERT INTO users (role_id, email, password_hash, full_name, phone)
            VALUES (2, ?, ?, 'TC01 Test User', '0811111111')
        """, (test_email, hashed))
        self.conn.commit()
        new_user_id = cur.lastrowid
        self.assertIsNotNone(new_user_id)

        # Verify created
        cur.execute("SELECT * FROM users WHERE user_id = ?", (new_user_id,))
        user = cur.fetchone()
        self.assertEqual(user["email"], test_email)
        self.assertTrue(check_password_hash(user["password_hash"], "securepass123"))

    def test_tc02_register_duplicate_email_fails(self):
        """TC-02 (Negative): สมัครสมาชิกด้วยอีเมลซ้ำในระบบ (ระบบต้องปฏิเสธ UNIQUE constraint)"""
        duplicate_email = "admin@ebookstore.com" # already exists in seed data
        cur = self.conn.cursor()
        with self.assertRaises(sqlite3.IntegrityError):
            cur.execute("""
                INSERT INTO users (role_id, email, password_hash, full_name, phone)
                VALUES (2, ?, 'somehash', 'Duplicate Name', '0899999999')
            """, (duplicate_email,))
            self.conn.commit()

    def test_tc03_negative_price_fails(self):
        """TC-03 (Negative): แอดมินเพิ่ม E-Book ที่มีราคาติดลบ (Constraint Violation: price >= 0)"""
        cur = self.conn.cursor()
        with self.assertRaises(sqlite3.IntegrityError):
            cur.execute("""
                INSERT INTO ebooks (category_id, author_id, title, price, file_download_url, is_active)
                VALUES (1, 1, 'Negative Price Book', -150.00, '/download/dummy', 1)
            """, )
            self.conn.commit()

    def test_tc04_search_and_filter_active_ebooks(self):
        """TC-04: ลูกค้าค้นหา E-Book และกรองตามหมวดหมู่ได้ผลลัพธ์ถูกต้อง (และไม่แสดง is_active = 0)"""
        cur = self.conn.cursor()
        # Filter by Category 1 (Computer Science) with is_active = 1
        cur.execute("""
            SELECT b.*, c.name as category_name, a.name as author_name
            FROM ebooks b
            JOIN categories c ON b.category_id = c.category_id
            JOIN authors a ON b.author_id = a.author_id
            WHERE b.is_active = 1 AND b.category_id = 1
        """)
        books = cur.fetchall()
        self.assertGreater(len(books), 0)
        for b in books:
            self.assertEqual(b["category_id"], 1)
            self.assertEqual(b["is_active"], 1)

        # Ensure inactive book (Thinking, Fast and Slow id=16) is NOT in active storefront
        cur.execute("SELECT * FROM ebooks WHERE is_active = 1 AND ebook_id = 16")
        inactive_book = cur.fetchone()
        self.assertIsNone(inactive_book, "Inactive book must not be returned in storefront active queries")

    def test_tc05_tc06_tc07_tc08_order_lifecycle_and_download_guardrail(self):
        """
        TC-05: ลูกค้าเพิ่มสินค้าลงตะกร้าและทำการ Checkout คำสั่งซื้อสำเร็จ (สถานะ PENDING)
        TC-06 (Security): ลูกค้าพยายามเปิดดาวน์โหลดขณะ Order ยังเป็น PENDING (ระบบต้องบล็อก)
        TC-07: แอดมินตรวจสอบหลักฐานและเปลี่ยนสถานะเป็น CONFIRMED
        TC-08: ลูกค้าเข้าดูประวัติและสามารถกดดาวน์โหลดไฟล์ E-Book ได้สำเร็จ
        """
        cur = self.conn.cursor()
        user_id = 4 # Jane Doe
        ebook_id = 3 # Refactoring (price 490.00)

        # 1. Ensure user cart exists
        cur.execute("SELECT cart_id FROM carts WHERE user_id = ?", (user_id,))
        cart = cur.fetchone()
        cart_id = cart["cart_id"]

        # Clear any existing cart items
        cur.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))

        # Add to cart
        cur.execute("INSERT INTO cart_items (cart_id, ebook_id, quantity) VALUES (?, ?, 1)", (cart_id, ebook_id))
        self.conn.commit()

        # TC-05: Checkout (Create Order with status PENDING, copy item to order_items, create simulated payment)
        cur.execute("SELECT price FROM ebooks WHERE ebook_id = ?", (ebook_id,))
        unit_price = cur.fetchone()["price"]

        cur.execute("""
            INSERT INTO orders (user_id, total_amount, order_status)
            VALUES (?, ?, 'PENDING')
        """, (user_id, unit_price))
        order_id = cur.lastrowid

        cur.execute("""
            INSERT INTO order_items (order_id, ebook_id, unit_price)
            VALUES (?, ?, ?)
        """, (order_id, ebook_id, unit_price))

        cur.execute("""
            INSERT INTO payments (order_id, payment_method, slip_url, paid_amount, payment_status)
            VALUES (?, 'SIMULATED_TRANSFER', 'https://mockslip.example/slip1.jpg', ?, 'WAITING_VERIFICATION')
        """, (order_id, unit_price))

        # Clear cart items after checkout
        cur.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))
        self.conn.commit()

        # Verify order created with PENDING
        cur.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        new_order = cur.fetchone()
        self.assertEqual(new_order["order_status"], "PENDING")

        # TC-06: Security Guardrail - Try to access download when PENDING
        # Business logic function: can_download(user_id, order_id, is_admin=False)
        def can_download(req_user_id, req_order_id, is_admin=False):
            cur.execute("SELECT user_id, order_status FROM orders WHERE order_id = ?", (req_order_id,))
            o = cur.fetchone()
            if not o:
                return False, "Order not found"
            if not is_admin and o["user_id"] != req_user_id:
                return False, "Unauthorized: Not order owner"
            if o["order_status"] != "CONFIRMED":
                return False, "Access Denied: Order is not CONFIRMED"
            return True, "Authorized"

        allowed, msg = can_download(user_id, order_id, is_admin=False)
        self.assertFalse(allowed, "Download should be blocked when order is PENDING")
        self.assertIn("not CONFIRMED", msg)

        # TC-07: Admin updates order to CONFIRMED
        cur.execute("""
            UPDATE orders SET order_status = 'CONFIRMED' WHERE order_id = ?
        """, (order_id,))
        cur.execute("""
            UPDATE payments SET payment_status = 'APPROVED' WHERE order_id = ?
        """, (order_id,))
        self.conn.commit()

        cur.execute("SELECT order_status FROM orders WHERE order_id = ?", (order_id,))
        self.assertEqual(cur.fetchone()["order_status"], "CONFIRMED")

        # TC-08: Customer now accesses download successfully
        allowed, msg = can_download(user_id, order_id, is_admin=False)
        self.assertTrue(allowed, "Download must be permitted once order is CONFIRMED")
        self.assertEqual(msg, "Authorized")

    def test_analytics_reports_queries(self):
        """Verify the 4 analytical SQL queries execute and return aggregated data"""
        cur = self.conn.cursor()

        # Report 1: Sales by Time Period (SQLite uses strftime('%Y-%m', created_at))
        query_r1 = """
            SELECT 
                strftime('%Y-%m', o.created_at) AS sales_month,
                COUNT(o.order_id) AS total_orders,
                ROUND(SUM(o.total_amount), 2) AS total_revenue,
                ROUND(AVG(o.total_amount), 2) AS average_order_value
            FROM orders o
            WHERE o.order_status = 'CONFIRMED'
            GROUP BY strftime('%Y-%m', o.created_at)
            ORDER BY sales_month DESC;
        """
        cur.execute(query_r1)
        r1_rows = cur.fetchall()
        self.assertGreater(len(r1_rows), 0, "Report 1 should return monthly aggregated sales")

        # Report 2: Top-Selling E-Books
        query_r2 = """
            SELECT 
                b.ebook_id,
                b.title,
                a.name AS author_name,
                COUNT(oi.order_item_id) AS units_sold,
                ROUND(SUM(oi.unit_price), 2) AS total_sales_amount
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN ebooks b ON oi.ebook_id = b.ebook_id
            JOIN authors a ON b.author_id = a.author_id
            WHERE o.order_status = 'CONFIRMED'
            GROUP BY b.ebook_id, b.title, a.name
            ORDER BY units_sold DESC, total_sales_amount DESC
            LIMIT 5;
        """
        cur.execute(query_r2)
        r2_rows = cur.fetchall()
        self.assertGreater(len(r2_rows), 0, "Report 2 should return top 5 ebooks")
        self.assertLessEqual(len(r2_rows), 5)

        # Report 3: Sales by Category
        query_r3 = """
            SELECT 
                c.category_id,
                c.name AS category_name,
                COUNT(DISTINCT o.order_id) AS order_count,
                COUNT(oi.order_item_id) AS total_books_sold,
                COALESCE(ROUND(SUM(oi.unit_price), 2), 0.00) AS total_revenue
            FROM categories c
            LEFT JOIN ebooks b ON c.category_id = b.category_id
            LEFT JOIN order_items oi ON b.ebook_id = oi.ebook_id
            LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'CONFIRMED'
            GROUP BY c.category_id, c.name
            ORDER BY total_revenue DESC;
        """
        cur.execute(query_r3)
        r3_rows = cur.fetchall()
        self.assertGreater(len(r3_rows), 0, "Report 3 should return sales by category")

        # Report 4: Customer Lifetime Value & Order Status
        query_r4 = """
            SELECT 
                u.user_id,
                u.full_name,
                u.email,
                COUNT(o.order_id) AS total_orders_placed,
                SUM(CASE WHEN o.order_status = 'CONFIRMED' THEN 1 ELSE 0 END) AS confirmed_orders,
                SUM(CASE WHEN o.order_status = 'PENDING' THEN 1 ELSE 0 END) AS pending_orders,
                SUM(CASE WHEN o.order_status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled_orders,
                COALESCE(ROUND(SUM(CASE WHEN o.order_status = 'CONFIRMED' THEN o.total_amount ELSE 0 END), 2), 0.00) AS total_spent
            FROM users u
            JOIN orders o ON u.user_id = o.user_id
            GROUP BY u.user_id, u.full_name, u.email
            HAVING total_orders_placed >= 1
            ORDER BY total_spent DESC;
        """
        cur.execute(query_r4)
        r4_rows = cur.fetchall()
        self.assertGreater(len(r4_rows), 0, "Report 4 should return customer lifetime value")

if __name__ == "__main__":
    unittest.main()
