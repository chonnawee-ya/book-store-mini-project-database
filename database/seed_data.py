"""
Seed Data Generator for E-Book Store Database
Generates realistic seed data conforming strictly to:
- 3NF constraints & Foreign Keys
- >= 30 Orders distributed across multiple months and statuses (CONFIRMED, PENDING, CANCELLED)
- Realistic books, authors, categories, users, carts, order items, and simulated payment slips
"""

import os
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from database.db import get_db_connection, init_db

def seed_database():
    print("Initializing Database...")
    init_db(force_recreate=True)
    conn = get_db_connection()
    cur = conn.cursor()

    print("Inserting Roles...")
    cur.execute("INSERT INTO roles (role_name) VALUES ('ADMIN');")
    cur.execute("INSERT INTO roles (role_name) VALUES ('CUSTOMER');")
    role_admin_id = 1
    role_customer_id = 2

    print("Inserting Users...")
    users_data = [
        (role_admin_id, "admin@ebookstore.com", generate_password_hash("admin123"), "ผู้ดูแลระบบ (Admin)", "0812345678", "2026-01-01 08:00:00"),
        (role_customer_id, "somchai@email.com", generate_password_hash("pass1234"), "สมชาย สายอ่าน", "0891112233", "2026-01-05 10:30:00"),
        (role_customer_id, "somsak@email.com", generate_password_hash("pass1234"), "สมศักดิ์ รักเรียนรู้", "0892223344", "2026-01-10 14:15:00"),
        (role_customer_id, "jane.doe@email.com", generate_password_hash("pass1234"), "Jane Doe", "0893334455", "2026-01-15 09:20:00"),
        (role_customer_id, "john.dev@email.com", generate_password_hash("pass1234"), "John Developer", "0894445566", "2026-01-20 16:45:00"),
        (role_customer_id, "sarah.connor@email.com", generate_password_hash("pass1234"), "Sarah Connor", "0895556677", "2026-02-01 11:10:00"),
        (role_customer_id, "alex.tech@email.com", generate_password_hash("pass1234"), "Alex Techlover", "0896667788", "2026-02-05 13:00:00"),
        (role_customer_id, "wichai@email.com", generate_password_hash("pass1234"), "วิชัย มหาเศรษฐี", "0897778899", "2026-02-12 18:30:00")
    ]
    cur.executemany("""
        INSERT INTO users (role_id, email, password_hash, full_name, phone, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, users_data)

    print("Inserting Categories...")
    categories_data = [
        ("วิทยาการคอมพิวเตอร์และโปรแกรมมิ่ง", "หนังสือครอบคลุมภาษา Python, SQL, Architecture, Data Structures และ Clean Code"),
        ("การพัฒนาตนเองและจิตวิทยา", "เคล็ดลับการจัดการเวลา นิสัยแห่งความสำเร็จ และจิตวิทยาพฤติกรรมมนุษย์"),
        ("ธุรกิจ การเงิน และการลงทุน", "กลยุทธ์การเงินส่วนบุคคล การลงทุนในหุ้น สตาร์ทอัป และเศรษฐศาสตร์สมัยใหม่"),
        ("วรรณกรรมและนิยายสากล", "นิยายไซไฟ ดิสโทเปีย และวรรณกรรมระดับมาสเตอร์พีซของโลก"),
        ("การออกแบบและศิลปะดิจิทัล", "UX/UI Design, การออกแบบกราฟิก และ Design Thinking สำหรับยุคดิจิทัล")
    ]
    cur.executemany("INSERT INTO categories (name, description) VALUES (?, ?)", categories_data)

    print("Inserting Authors...")
    authors_data = [
        ("Robert C. Martin", "Uncle Bob ผู้เขียน Clean Code และผู้เชี่ยวชาญด้าน Software Craftsmanship ระดับโลก"),
        ("James Clear", "นักเขียนหนังสือขายดีระดับโลก Atomic Habits ผู้เชี่ยวชาญด้านจิตวิทยาการสร้างนิสัย"),
        ("Morgan Housel", "นักเขียนและพาร์ทเนอร์ Collaborative Fund ผู้เขียน The Psychology of Money"),
        ("Dr. Donald E. Knuth", "ปรมาจารย์ด้านวิทยาการคอมพิวเตอร์ ผู้ประพันธ์ The Art of Computer Programming"),
        ("Don Norman", "บิดาแห่งวงการ User Experience (UX) ผู้เขียน The Design of Everyday Things"),
        ("George Orwell", "นักประพันธ์ชาวอังกฤษผู้สร้างผลงานวรรณกรรมไซไฟการเมือง 1984 และ Animal Farm"),
        ("Martin Fowler", "Chief Scientist ที่ ThoughtWorks ผู้เชี่ยวชาญด้าน Refactoring และ Microservices"),
        ("ภัทรพล ศิลปาจารย์", "นักลงทุน นักคิด และนักเขียนหนังสือด้านอิสรภาพทางการเงินยอดนิยมของไทย")
    ]
    cur.executemany("INSERT INTO authors (name, biography) VALUES (?, ?)", authors_data)

    print("Inserting E-Books...")
    ebooks_data = [
        # category_id, author_id, title, description, price, cover_image_url, file_download_url, is_active
        (1, 1, "Clean Code: A Handbook of Agile Software Craftsmanship", "แนวทางการเขียนโค้ดให้อ่านง่าย บำรุงรักษาสะดวก และมีประสิทธิภาพสูงสุด", 450.00, "https://images.unsplash.com/photo-1532012164546-f432f2e3777a?w=400&q=80", "/download/ebook/1", 1),
        (1, 4, "Database Systems & SQL Mastery", "เจาะลึกโครงสร้างฐานข้อมูลเชิงสัมพันธ์ 3NF Indexing และ Query Optimization", 520.00, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80", "/download/ebook/2", 1),
        (1, 7, "Refactoring: Improving the Design of Existing Code", "เทคนิคการปรับปรุงโค้ดเดิมให้มีสถาปัตยกรรมที่ยืดหยุ่น ปลอดภัย และทดสอบง่าย", 490.00, "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&q=80", "/download/ebook/3", 1),
        (2, 2, "Atomic Habits: เพราะชีวิตดีได้กว่าที่เป็น", "เปลี่ยนชีวิตด้วยพลังแห่งการปรับนิสัยวันละ 1% ที่สร้างผลลัพธ์มหาศาล", 290.00, "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&q=80", "/download/ebook/4", 1),
        (3, 3, "The Psychology of Money: จิตวิทยาว่าด้วยเงิน", "บทเรียนเหนือกาลเวลาเรื่องความมั่งคั่ง ความโลภ และความสุข", 350.00, "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400&q=80", "/download/ebook/5", 1),
        (4, 6, "1984: นิยายดิสโทเปียระดับตำนาน", "เรื่องราวโลกอนาคตที่ Big Brother กำลังจับตามองคุณอยู่ทุกฝีก้าว", 220.00, "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400&q=80", "/download/ebook/6", 1),
        (5, 5, "The Design of Everyday Things", "ทำไมของบางอย่างใช้ง่าย บางอย่างใช้ยาก คัมภีร์ UX ที่นักออกแบบทุกคนต้องอ่าน", 380.00, "https://images.unsplash.com/photo-1507842229458-5742130e6677?w=400&q=80", "/download/ebook/7", 1),
        (3, 8, "Money 101: เริ่มต้นสร้างอิสรภาพทางการเงิน", "คู่มือวางแผนการเงินฉบับเข้าใจง่ายสำหรับคนทำงานและวัยรุ่นยุคใหม่", 250.00, "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=400&q=80", "/download/ebook/8", 1),
        (1, 1, "The Clean Coder: Code of Conduct for Professional Programmers", "จรรยาบรรณ วินัย และทัศนคติของโปรแกรมเมอร์มืออาชีพ", 390.00, "https://images.unsplash.com/photo-1516259762381-22954d7d3ad2?w=400&q=80", "/download/ebook/9", 1),
        (2, 2, "Deep Work: กฎเหล็กแห่งการจดจ่อในโลกที่ถูกรบกวน", "สร้างสมาธิขั้นสุดเพื่อผลลัพธ์การทำงานที่ทรงคุณค่าและเหนือชั้น", 310.00, "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=400&q=80", "/download/ebook/10", 1),
        (4, 6, "Animal Farm: การเมืองในฟาร์มสัตว์", "วรรณกรรมเสียดสีอำนาจเผด็จการผ่านมุมมองของเหล่าสัตว์ในฟาร์ม", 180.00, "https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=400&q=80", "/download/ebook/11", 1),
        (5, 5, "Don't Make Me Think: คัมภีร์ออกแบบ Web Usability", "หลักการออกแบบเว็บและแอปพลิเคชันให้ผู้ใช้เข้าใจได้ในทันทีโดยไม่ต้องคิด", 360.00, "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=400&q=80", "/download/ebook/12", 1),
        (1, 7, "Building Microservices: Designing Fine-Grained Systems", "สถาปัตยกรรม Microservices การแบ่งขอบเขต Service และการประสานงาน", 590.00, "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80", "/download/ebook/13", 1),
        (3, 3, "Same as Ever: คู่มือทำความเข้าใจสิ่งที่ไม่เคยเปลี่ยน", "มองทะลุอนาคตด้วยความเข้าใจพฤติกรรมมนุษย์และสิ่งที่ไม่เคยเปลี่ยนแปลงตามกาลเวลา", 320.00, "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&q=80", "/download/ebook/14", 1),
        (1, 4, "Algorithms Unlocked: ไขรหัสอัลกอริทึมฉบับย่อยง่าย", "เข้าใจแนวคิดอัลกอริทึมพื้นฐานที่ขับเคลื่อนเทคโนโลยีรอบตัวคุณ", 410.00, "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400&q=80", "/download/ebook/15", 1),
        (2, 2, "Thinking, Fast and Slow (ฉบับ E-Book พิเศษ)", "ระบบการคิดเร็วและการคิดช้าที่ชี้นำการตัดสินใจของมนุษย์ทุกคน", 420.00, "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=400&q=80", "/download/ebook/16", 0) # เล่มนี้ inactive สำหรับเทสต์ TC-04
    ]
    cur.executemany("""
        INSERT INTO ebooks (category_id, author_id, title, description, price, cover_image_url, file_download_url, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ebooks_data)

    print("Inserting Initial Carts for Customers...")
    for uid in range(1, 9):
        cur.execute("INSERT INTO carts (user_id) VALUES (?)", (uid,))

    # Add sample item into Somchai's cart for demonstration
    cur.execute("INSERT INTO cart_items (cart_id, ebook_id, quantity) VALUES (2, 1, 1)")

    print("Generating >= 35 Realistic Orders & Payments across multiple months...")
    # Book prices lookup (ebook_id: price)
    cur.execute("SELECT ebook_id, price FROM ebooks")
    book_prices = {row["ebook_id"]: row["price"] for row in cur.fetchall()}

    # Customer user IDs (exclude admin id 1)
    customer_ids = [2, 3, 4, 5, 6, 7, 8]

    # Pre-defined deterministic orders to guarantee rich reporting (months: 2026-01, 2026-02, 2026-03)
    orders_blueprint = [
        # (user_id, [ebook_ids], status, created_at, payment_status, slip_url)
        (2, [1, 2], 'CONFIRMED', '2026-01-06 11:20:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+1'),
        (3, [4], 'CONFIRMED', '2026-01-08 14:10:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+2'),
        (4, [5, 8], 'CONFIRMED', '2026-01-12 09:45:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+3'),
        (5, [1, 3, 9], 'CONFIRMED', '2026-01-15 17:00:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+4'),
        (6, [7], 'CANCELLED', '2026-01-18 10:15:00', 'REJECTED', 'https://placehold.co/400x600/ef4444/ffffff?text=Mock+Slip+Rejected'),
        (7, [2, 13], 'CONFIRMED', '2026-01-22 13:30:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+6'),
        (8, [5, 14], 'CONFIRMED', '2026-01-25 19:20:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+7'),
        (2, [4, 10], 'CONFIRMED', '2026-01-28 08:40:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+8'),
        (3, [6, 11], 'CONFIRMED', '2026-01-30 16:55:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+9'),
        (4, [1, 4], 'PENDING', '2026-01-31 21:05:00', 'WAITING_VERIFICATION', 'https://placehold.co/400x600/f59e0b/ffffff?text=Mock+Slip+Pending'),

        # Month 2: February 2026
        (5, [2, 7], 'CONFIRMED', '2026-02-02 10:00:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+11'),
        (6, [3, 9], 'CONFIRMED', '2026-02-04 12:45:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+12'),
        (7, [4], 'CONFIRMED', '2026-02-07 15:30:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+13'),
        (8, [1, 5, 8], 'CONFIRMED', '2026-02-10 18:15:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+14'),
        (2, [12, 7], 'CONFIRMED', '2026-02-12 11:25:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+15'),
        (3, [15], 'CANCELLED', '2026-02-14 14:50:00', 'REJECTED', 'https://placehold.co/400x600/ef4444/ffffff?text=Mock+Slip+Rejected'),
        (4, [2, 4], 'CONFIRMED', '2026-02-16 09:10:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+17'),
        (5, [8, 14], 'CONFIRMED', '2026-02-18 20:00:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+18'),
        (6, [1, 10], 'CONFIRMED', '2026-02-21 16:40:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+19'),
        (7, [6], 'PENDING', '2026-02-24 13:15:00', 'WAITING_VERIFICATION', 'https://placehold.co/400x600/f59e0b/ffffff?text=Mock+Slip+Pending'),
        (8, [3, 13], 'CONFIRMED', '2026-02-26 17:35:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+21'),
        (2, [5], 'CONFIRMED', '2026-02-28 10:50:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+22'),

        # Month 3: March 2026
        (3, [1, 2, 4], 'CONFIRMED', '2026-03-02 09:30:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+23'),
        (4, [7, 12], 'CONFIRMED', '2026-03-04 14:20:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+24'),
        (5, [15, 9], 'CONFIRMED', '2026-03-06 18:00:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+25'),
        (6, [4, 5], 'CONFIRMED', '2026-03-08 11:15:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+26'),
        (7, [1, 14], 'CANCELLED', '2026-03-10 15:45:00', 'REJECTED', 'https://placehold.co/400x600/ef4444/ffffff?text=Mock+Slip+Rejected'),
        (8, [2, 3, 10], 'CONFIRMED', '2026-03-12 19:30:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+28'),
        (2, [8], 'CONFIRMED', '2026-03-14 10:10:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+29'),
        (3, [4, 7], 'CONFIRMED', '2026-03-16 13:40:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+30'),
        (4, [1, 5], 'CONFIRMED', '2026-03-18 16:20:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+31'),
        (5, [6, 11], 'PENDING', '2026-03-19 20:00:00', 'WAITING_VERIFICATION', 'https://placehold.co/400x600/f59e0b/ffffff?text=Mock+Slip+Pending'),
        (6, [2, 15], 'CONFIRMED', '2026-03-20 12:30:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+33'),
        (7, [3, 8], 'CONFIRMED', '2026-03-21 14:15:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+34'),
        (8, [4, 12, 14], 'CONFIRMED', '2026-03-22 17:50:00', 'APPROVED', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+35'),
        (2, [2], 'PENDING', '2026-03-22 22:10:00', 'WAITING_VERIFICATION', 'https://placehold.co/400x600/f59e0b/ffffff?text=Mock+Slip+Pending')
    ]

    for order_info in orders_blueprint:
        user_id, ebook_ids, order_status, created_at, payment_status, slip_url = order_info
        
        # Calculate total
        total_amount = sum(book_prices[bid] for bid in ebook_ids)

        # 1. Insert Order
        cur.execute("""
            INSERT INTO orders (user_id, total_amount, order_status, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, total_amount, order_status, created_at))
        order_id = cur.lastrowid

        # 2. Insert Order Items (storing historical unit_price)
        for bid in ebook_ids:
            cur.execute("""
                INSERT INTO order_items (order_id, ebook_id, unit_price)
                VALUES (?, ?, ?)
            """, (order_id, bid, book_prices[bid]))

        # 3. Insert Payment
        cur.execute("""
            INSERT INTO payments (order_id, payment_method, slip_url, paid_amount, payment_status, payment_date)
            VALUES (?, 'SIMULATED_TRANSFER', ?, ?, ?, ?)
        """, (order_id, slip_url, total_amount, payment_status, created_at))

    conn.commit()
    conn.close()
    print(f"Successfully seeded database! Total orders created: {len(orders_blueprint)}")

if __name__ == "__main__":
    seed_database()
