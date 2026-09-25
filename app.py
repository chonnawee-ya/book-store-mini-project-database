"""
E-Book Store Web Application & Database Management Platform
Mini Project Database 2026
Clean Architecture with Parameterized SQL queries (100% Prepared Statements)
"""

import os
import io
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, send_file, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection, query_db, execute_db, get_schema_overview

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ebook_store_super_secure_secret_key_2026")

# ------------------------------------------------------------------------------
# Context Processors & Helpers
# ------------------------------------------------------------------------------
@app.context_processor
def inject_global_data():
    """Inject current logged-in user and cart count into all Jinja templates"""
    current_user = None
    cart_count = 0
    if "user_id" in session:
        conn = get_db_connection()
        user_row = conn.execute("""
            SELECT u.*, r.role_name
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.user_id = ?
        """, (session["user_id"],)).fetchone()

        if user_row:
            current_user = dict(user_row)
            cart_row = conn.execute("""
                SELECT COUNT(ci.cart_item_id) as total_items
                FROM carts c
                JOIN cart_items ci ON c.cart_id = ci.cart_id
                WHERE c.user_id = ?
            """, (session["user_id"],)).fetchone()
            if cart_row:
                cart_count = cart_row["total_items"]
        conn.close()

    # Get sample demo accounts for quick switcher
    conn = get_db_connection()
    demo_users = conn.execute("""
        SELECT u.user_id, u.full_name, u.email, r.role_name
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        ORDER BY u.role_id ASC, u.user_id ASC
        LIMIT 6
    """).fetchall()
    conn.close()

    return {
        "current_user": current_user,
        "cart_count": cart_count,
        "demo_users": [dict(u) for u in demo_users]
    }

def login_required(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("กรุณาเข้าสู่ระบบก่อนดำเนินการ", "warning")
                return redirect(url_for("login"))
            if role:
                conn = get_db_connection()
                user = conn.execute("""
                    SELECT r.role_name FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = ?
                """, (session["user_id"],)).fetchone()
                conn.close()
                if not user or user["role_name"] != role:
                    flash("คุณไม่มีสิทธิ์เข้าถึงหน้านี้ (Admin Only)", "danger")
                    return redirect(url_for("index"))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# ------------------------------------------------------------------------------
# Authentication & Demo Quick Switch Routes
# ------------------------------------------------------------------------------
@app.route("/demo/switch/<int:user_id>")
def demo_switch(user_id):
    """Quickly switch active session user for demonstration & grading"""
    conn = get_db_connection()
    user = conn.execute("""
        SELECT u.*, r.role_name FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE u.user_id = ?
    """, (user_id,)).fetchone()
    conn.close()

    if user:
        session["user_id"] = user["user_id"]
        session["user_name"] = user["full_name"]
        session["role_name"] = user["role_name"]
        flash(f"สลับผู้ใช้งานเป็น: {user['full_name']} ({user['role_name']})", "info")
    return redirect(request.referrer or url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()

        if not full_name or not email or not password:
            flash("กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน", "danger")
            return render_template("register.html")

        conn = get_db_connection()
        existing = conn.execute("SELECT user_id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            flash("อีเมลนี้ถูกใช้งานแล้วในระบบ (Email must be UNIQUE)", "danger")
            return render_template("register.html")

        hashed_pw = generate_password_hash(password)
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (role_id, email, password_hash, full_name, phone)
                VALUES (2, ?, ?, ?, ?)
            """, (email, hashed_pw, full_name, phone))
            new_uid = cur.lastrowid
            # Create user's cart
            cur.execute("INSERT INTO carts (user_id) VALUES (?)", (new_uid,))
            conn.commit()
            conn.close()

            session["user_id"] = new_uid
            session["user_name"] = full_name
            session["role_name"] = "CUSTOMER"
            flash("สมัครสมาชิกและเข้าสู่ระบบสำเร็จ!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            conn.close()
            flash(f"เกิดข้อผิดพลาดในการลงทะเบียน: {str(e)}", "danger")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        user = conn.execute("""
            SELECT u.*, r.role_name
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.email = ?
        """, (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["user_name"] = user["full_name"]
            session["role_name"] = user["role_name"]
            flash(f"ยินดีต้อนรับคุณ {user['full_name']} เข้าสู่ระบบ", "success")
            return redirect(url_for("index"))
        else:
            flash("อีเมลหรือรหัสผ่านไม่ถูกต้อง", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("ออกจากระบบเรียบร้อยแล้ว", "info")
    return redirect(url_for("index"))

# ------------------------------------------------------------------------------
# Storefront Routes (US-01, US-02)
# ------------------------------------------------------------------------------
@app.route("/")
def index():
    search_q = request.args.get("q", "").strip()
    category_id = request.args.get("category", "").strip()

    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()

    # Build SQL query with parameterized conditions
    base_sql = """
        SELECT b.*, c.name AS category_name, a.name AS author_name
        FROM ebooks b
        JOIN categories c ON b.category_id = c.category_id
        JOIN authors a ON b.author_id = a.author_id
        WHERE b.is_active = 1
    """
    params = []

    if search_q:
        base_sql += " AND (b.title LIKE ? OR b.description LIKE ? OR a.name LIKE ?)"
        term = f"%{search_q}%"
        params.extend([term, term, term])

    if category_id and category_id.isdigit():
        base_sql += " AND b.category_id = ?"
        params.append(int(category_id))

    base_sql += " ORDER BY b.ebook_id DESC"
    ebooks = conn.execute(base_sql, params).fetchall()
    conn.close()

    return render_template("index.html",
                           ebooks=[dict(b) for b in ebooks],
                           categories=[dict(c) for c in categories],
                           search_q=search_q,
                           selected_cat=int(category_id) if category_id.isdigit() else None)

@app.route("/ebook/<int:ebook_id>")
def ebook_detail(ebook_id):
    conn = get_db_connection()
    ebook = conn.execute("""
        SELECT b.*, c.name AS category_name, a.name AS author_name, a.biography AS author_bio
        FROM ebooks b
        JOIN categories c ON b.category_id = c.category_id
        JOIN authors a ON b.author_id = a.author_id
        WHERE b.ebook_id = ?
    """, (ebook_id,)).fetchone()
    conn.close()

    if not ebook:
        flash("ไม่พบข้อมูลหนังสือที่ระบุ", "warning")
        return redirect(url_for("index"))

    return render_template("ebook_detail.html", ebook=dict(ebook))

# ------------------------------------------------------------------------------
# Shopping Cart Routes (US-03)
# ------------------------------------------------------------------------------
@app.route("/cart")
@login_required()
def view_cart():
    conn = get_db_connection()
    cart_items = conn.execute("""
        SELECT ci.cart_item_id, ci.quantity, b.ebook_id, b.title, b.price, b.cover_image_url,
               a.name AS author_name, c.name AS category_name
        FROM carts ca
        JOIN cart_items ci ON ca.cart_id = ci.cart_id
        JOIN ebooks b ON ci.ebook_id = b.ebook_id
        JOIN authors a ON b.author_id = a.author_id
        JOIN categories c ON b.category_id = c.category_id
        WHERE ca.user_id = ?
        ORDER BY ci.created_at DESC
    """, (session["user_id"],)).fetchall()
    conn.close()

    total_amount = sum(item["price"] for item in cart_items)
    return render_template("cart.html", items=[dict(i) for i in cart_items], total_amount=total_amount)

@app.route("/cart/add/<int:ebook_id>", methods=["POST"])
@login_required()
def add_to_cart(ebook_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Ensure user has a cart
    cart = cur.execute("SELECT cart_id FROM carts WHERE user_id = ?", (session["user_id"],)).fetchone()
    if not cart:
        cur.execute("INSERT INTO carts (user_id) VALUES (?)", (session["user_id"],))
        cart_id = cur.lastrowid
    else:
        cart_id = cart["cart_id"]

    # 2. Check if already in cart (E-Book rule: max 1 per user/order)
    existing = cur.execute("SELECT cart_item_id FROM cart_items WHERE cart_id = ? AND ebook_id = ?",
                           (cart_id, ebook_id)).fetchone()
    if existing:
        conn.close()
        flash("หนังสือเล่มนี้อยู่ในตะกร้าสินค้าของคุณแล้ว (E-Book มีสิทธิ์ซื้อได้ 1 เล่มต่อคำสั่งซื้อ)", "info")
        return redirect(request.referrer or url_for("view_cart"))

    # 3. Insert cart item
    try:
        cur.execute("""
            INSERT INTO cart_items (cart_id, ebook_id, quantity)
            VALUES (?, ?, 1)
        """, (cart_id, ebook_id))
        conn.commit()
        flash("เพิ่มหนังสือลงในตะกร้าสินค้าเรียบร้อยแล้ว", "success")
    except Exception as e:
        flash(f"เกิดข้อผิดพลาดในการเพิ่มสินค้า: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(request.referrer or url_for("view_cart"))

@app.route("/cart/remove/<int:cart_item_id>", methods=["POST"])
@login_required()
def remove_from_cart(cart_item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Ensure item belongs to current user's cart
    cur.execute("""
        DELETE FROM cart_items
        WHERE cart_item_id = ? AND cart_id IN (SELECT cart_id FROM carts WHERE user_id = ?)
    """, (cart_item_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("นำหนังสือออกจากตะกร้าสินค้าเรียบร้อยแล้ว", "info")
    return redirect(url_for("view_cart"))

# ------------------------------------------------------------------------------
# Checkout & Simulated Payment Routes (US-04)
# ------------------------------------------------------------------------------
@app.route("/checkout", methods=["GET", "POST"])
@login_required()
def checkout():
    conn = get_db_connection()
    cur = conn.cursor()

    cart_items = cur.execute("""
        SELECT ci.cart_item_id, b.ebook_id, b.title, b.price, a.name AS author_name
        FROM carts ca
        JOIN cart_items ci ON ca.cart_id = ci.cart_id
        JOIN ebooks b ON ci.ebook_id = b.ebook_id
        JOIN authors a ON b.author_id = a.author_id
        WHERE ca.user_id = ?
    """, (session["user_id"],)).fetchall()

    if not cart_items:
        conn.close()
        flash("ไม่มีสินค้าในตะกร้าสำหรับการสั่งซื้อ", "warning")
        return redirect(url_for("index"))

    total_amount = sum(item["price"] for item in cart_items)

    if request.method == "POST":
        payment_method = request.form.get("payment_method", "SIMULATED_TRANSFER")
        slip_url = request.form.get("slip_url", "").strip()

        if not slip_url:
            slip_url = f"https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+User+{session['user_id']}"

        try:
            # Transaction starts automatically in sqlite3 connection
            # 1. Create Order (Status PENDING)
            cur.execute("""
                INSERT INTO orders (user_id, total_amount, order_status)
                VALUES (?, ?, 'PENDING')
            """, (session["user_id"], total_amount))
            new_order_id = cur.lastrowid

            # 2. Insert Order Items (Preserving historical price)
            for item in cart_items:
                cur.execute("""
                    INSERT INTO order_items (order_id, ebook_id, unit_price)
                    VALUES (?, ?, ?)
                """, (new_order_id, item["ebook_id"], item["price"]))

            # 3. Create Payment record
            cur.execute("""
                INSERT INTO payments (order_id, payment_method, slip_url, paid_amount, payment_status)
                VALUES (?, ?, ?, ?, 'WAITING_VERIFICATION')
            """, (new_order_id, payment_method, slip_url, total_amount))

            # 4. Clear Cart Items for this user
            cur.execute("""
                DELETE FROM cart_items
                WHERE cart_id IN (SELECT cart_id FROM carts WHERE user_id = ?)
            """, (session["user_id"],))

            conn.commit()
            flash(f"สร้างคำสั่งซื้อ #{new_order_id} สำเร็จ! สถานะปัจจุบัน: รอการตรวจสอบชำระเงิน (PENDING)", "success")
            return redirect(url_for("order_history"))
        except Exception as e:
            conn.rollback()
            flash(f"เกิดข้อผิดพลาดในการทำรายการสั่งซื้อ: {str(e)}", "danger")
        finally:
            conn.close()

    conn.close()
    return render_template("checkout.html", items=[dict(i) for i in cart_items], total_amount=total_amount)

# ------------------------------------------------------------------------------
# Order History & Download Guardrail (US-05, TC-06, TC-08)
# ------------------------------------------------------------------------------
@app.route("/orders")
@login_required()
def order_history():
    conn = get_db_connection()
    orders = conn.execute("""
        SELECT o.*, p.payment_method, p.slip_url, p.payment_status
        FROM orders o
        LEFT JOIN payments p ON o.order_id = p.order_id
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
    """, (session["user_id"],)).fetchall()

    orders_with_items = []
    for ord_row in orders:
        ord_dict = dict(ord_row)
        items = conn.execute("""
            SELECT oi.*, b.title, b.cover_image_url, a.name AS author_name
            FROM order_items oi
            JOIN ebooks b ON oi.ebook_id = b.ebook_id
            JOIN authors a ON b.author_id = a.author_id
            WHERE oi.order_id = ?
        """, (ord_dict["order_id"],)).fetchall()
        ord_dict["items"] = [dict(i) for i in items]
        orders_with_items.append(ord_dict)

    conn.close()
    return render_template("orders.html", orders=orders_with_items)

@app.route("/download/<int:order_id>/<int:ebook_id>")
@login_required()
def download_ebook(order_id, ebook_id):
    """
    CRITICAL SECURITY GUARDRAIL:
    1. Order must exist
    2. Order status MUST be 'CONFIRMED'
    3. User MUST be the order owner OR role == 'ADMIN'
    4. E-book must belong to that order
    """
    conn = get_db_connection()
    user_row = conn.execute("""
        SELECT r.role_name FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE u.user_id = ?
    """, (session["user_id"],)).fetchone()
    is_admin = (user_row and user_row["role_name"] == "ADMIN")

    order = conn.execute("""
        SELECT * FROM orders WHERE order_id = ?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        abort(404, description="ไม่พบคำสั่งซื้อที่ระบุ")

    # Authorization verification
    if not is_admin and order["user_id"] != session["user_id"]:
        conn.close()
        abort(403, description="ปฏิเสธการเข้าถึง: คุณไม่ใช่เจ้าของคำสั่งซื้อนี้")

    # Order Status check
    if order["order_status"] != "CONFIRMED":
        conn.close()
        flash(f"ปฏิเสธการดาวน์โหลด: คำสั่งซื้อ #{order_id} ยังไม่ได้รับการอนุมัติ (สถานะปัจจุบัน: {order['order_status']})", "danger")
        return redirect(url_for("order_history"))

    # Verify item exists in order
    item = conn.execute("""
        SELECT oi.*, b.title FROM order_items oi
        JOIN ebooks b ON oi.ebook_id = b.ebook_id
        WHERE oi.order_id = ? AND oi.ebook_id = ?
    """, (order_id, ebook_id)).fetchone()
    conn.close()

    if not item:
        abort(404, description="ไม่พบหนังสือเล่มนี้ในคำสั่งซื้อของคุณ")

    # Generate a demo personalized ebook file
    content = f"""========================================================================
E-BOOK STORE OFFICIAL DIGITAL DOWNLOAD (VERIFIED & CONFIRMED)
========================================================================
Title: {item['title']}
E-Book ID: {ebook_id}
Order ID: #{order_id}
Licensed To: {session.get('user_name', 'Customer')}
Verification Status: CONFIRMED
Timestamp: 2026

Dear Reader,
Thank you for supporting authors through the E-Book Store Mini Project!
This file confirms that your order was verified and processed under 3NF
relational integrity and strict access control rules.

Happy reading!
========================================================================
"""
    return send_file(
        io.BytesIO(content.encode("utf-8")),
        mimetype="text/plain",
        as_attachment=True,
        download_name=f"EBook_{ebook_id}_{item['title'].replace(' ', '_')[:30]}.txt"
    )

@app.route("/download/ebook/<int:ebook_id>")
@login_required()
def download_ebook_by_catalog(ebook_id):
    """
    Direct catalog URL download protection:
    Verifies that the user owns a CONFIRMED order for this ebook.
    """
    conn = get_db_connection()
    user_row = conn.execute("""
        SELECT r.role_name FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE u.user_id = ?
    """, (session["user_id"],)).fetchone()
    is_admin = (user_row and user_row["role_name"] == "ADMIN")

    if is_admin:
        # Admin can access sample download
        book = conn.execute("SELECT title FROM ebooks WHERE ebook_id = ?", (ebook_id,)).fetchone()
        conn.close()
        if not book:
            abort(404)
        content = f"ADMIN DOWNLOAD PREVIEW: {book['title']} (Book ID: {ebook_id})\nRole: ADMIN"
        return send_file(
            io.BytesIO(content.encode("utf-8")),
            mimetype="text/plain",
            as_attachment=True,
            download_name=f"Admin_Preview_{ebook_id}.txt"
        )

    # Check for confirmed order for this user and ebook
    confirmed_order = conn.execute("""
        SELECT o.order_id, b.title
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN ebooks b ON oi.ebook_id = b.ebook_id
        WHERE o.user_id = ? AND oi.ebook_id = ? AND o.order_status = 'CONFIRMED'
        LIMIT 1
    """, (session["user_id"], ebook_id)).fetchone()

    conn.close()

    if not confirmed_order:
        flash("ปฏิเสธการดาวน์โหลด: คุณยังไม่ได้สั่งซื้อหนังสือเล่มนี้ หรือคำสั่งซื้อยังไม่ได้รับการอนุมัติ (Security Guardrail)", "danger")
        return redirect(url_for("order_history"))

    return download_ebook(confirmed_order["order_id"], ebook_id)


# ------------------------------------------------------------------------------
# Admin Management Routes (US-06, US-07, US-08, US-09)
# ------------------------------------------------------------------------------
@app.route("/admin")
@login_required(role="ADMIN")
def admin_panel():
    conn = get_db_connection()
    # Stats
    total_ebooks = conn.execute("SELECT COUNT(*) FROM ebooks").fetchone()[0]
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    pending_orders_count = conn.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'PENDING'").fetchone()[0]
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    # E-books
    ebooks = conn.execute("""
        SELECT b.*, c.name AS category_name, a.name AS author_name
        FROM ebooks b
        JOIN categories c ON b.category_id = c.category_id
        JOIN authors a ON b.author_id = a.author_id
        ORDER BY b.ebook_id DESC
    """).fetchall()

    # Categories
    categories = conn.execute("""
        SELECT c.*, COUNT(b.ebook_id) AS book_count
        FROM categories c
        LEFT JOIN ebooks b ON c.category_id = b.category_id
        GROUP BY c.category_id, c.name
        ORDER BY c.category_id ASC
    """).fetchall()

    # Authors
    authors = conn.execute("SELECT * FROM authors ORDER BY name ASC").fetchall()

    # Orders & Payments
    orders = conn.execute("""
        SELECT o.*, u.full_name, u.email, p.payment_method, p.slip_url, p.payment_status, p.paid_amount
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        LEFT JOIN payments p ON o.order_id = p.order_id
        ORDER BY o.created_at DESC
        LIMIT 50
    """).fetchall()

    # Users
    users = conn.execute("""
        SELECT u.*, r.role_name, COUNT(o.order_id) AS order_count
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        LEFT JOIN orders o ON u.user_id = o.user_id
        GROUP BY u.user_id, u.email
        ORDER BY u.user_id ASC
    """).fetchall()

    conn.close()

    return render_template("admin.html",
                           stats={
                               "total_ebooks": total_ebooks,
                               "total_orders": total_orders,
                               "pending_orders": pending_orders_count,
                               "total_users": total_users
                           },
                           ebooks=[dict(b) for b in ebooks],
                           categories=[dict(c) for c in categories],
                           authors=[dict(a) for a in authors],
                           orders=[dict(o) for o in orders],
                           users=[dict(u) for u in users])

@app.route("/admin/ebook/create", methods=["POST"])
@login_required(role="ADMIN")
def admin_create_ebook():
    title = request.form.get("title", "").strip()
    category_id = request.form.get("category_id")
    author_id = request.form.get("author_id")
    price_str = request.form.get("price", "0")
    description = request.form.get("description", "").strip()
    cover_image_url = request.form.get("cover_image_url", "").strip()
    file_download_url = request.form.get("file_download_url", "").strip() or "/download/sample"
    is_active = 1 if request.form.get("is_active") == "1" else 0

    try:
        price = float(price_str)
        if price < 0:
            flash("ราคาหนังสือต้องไม่ติดลบ (Constraint: price >= 0)", "danger")
            return redirect(url_for("admin_panel"))
    except ValueError:
        flash("กรุณากรอกตัวเลขราคาที่ถูกต้อง", "danger")
        return redirect(url_for("admin_panel"))

    if not title or not category_id or not author_id:
        flash("กรุณากรอกข้อมูลหนังสือที่จำเป็นให้ครบถ้วน", "danger")
        return redirect(url_for("admin_panel"))

    try:
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO ebooks (category_id, author_id, title, description, price, cover_image_url, file_download_url, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (category_id, author_id, title, description, price, cover_image_url, file_download_url, is_active))
        conn.commit()
        conn.close()
        flash(f"เพิ่มหนังสือ '{title}' สำเร็จแล้ว", "success")
    except Exception as e:
        flash(f"เกิดข้อผิดพลาดในการบันทึก: {str(e)}", "danger")

    return redirect(url_for("admin_panel"))

@app.route("/admin/ebook/toggle/<int:ebook_id>", methods=["POST"])
@login_required(role="ADMIN")
def admin_toggle_ebook(ebook_id):
    conn = get_db_connection()
    book = conn.execute("SELECT is_active FROM ebooks WHERE ebook_id = ?", (ebook_id,)).fetchone()
    if book:
        new_status = 0 if book["is_active"] == 1 else 1
        conn.execute("UPDATE ebooks SET is_active = ? WHERE ebook_id = ?", (new_status, ebook_id))
        conn.commit()
        flash(f"เปลี่ยนสถานะหนังสือเป็น {'เปิดขาย' if new_status == 1 else 'ปิดการขาย'} เรียบร้อยแล้ว", "info")
    conn.close()
    return redirect(url_for("admin_panel"))

@app.route("/admin/category/create", methods=["POST"])
@login_required(role="ADMIN")
def admin_create_category():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if not name:
        flash("กรุณาระบุชื่อหมวดหมู่", "warning")
        return redirect(url_for("admin_panel"))

    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        flash(f"เพิ่มหมวดหมู่ '{name}' สำเร็จ", "success")
    except Exception as e:
        flash(f"ไม่สามารถเพิ่มหมวดหมู่ได้ (อาจมีชื่อนี้แล้ว): {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for("admin_panel"))

@app.route("/admin/order/update-status/<int:order_id>", methods=["POST"])
@login_required(role="ADMIN")
def admin_update_order_status(order_id):
    new_status = request.form.get("status")
    if new_status not in ["CONFIRMED", "CANCELLED", "PENDING"]:
        flash("สถานะคำสั่งซื้อไม่ถูกต้อง", "danger")
        return redirect(url_for("admin_panel"))

    payment_status = "APPROVED" if new_status == "CONFIRMED" else ("REJECTED" if new_status == "CANCELLED" else "WAITING_VERIFICATION")

    conn = get_db_connection()
    conn.execute("UPDATE orders SET order_status = ? WHERE order_id = ?", (new_status, order_id))
    conn.execute("UPDATE payments SET payment_status = ? WHERE order_id = ?", (payment_status, order_id))
    conn.commit()
    conn.close()

    flash(f"อัปเดตคำสั่งซื้อ #{order_id} เป็นสถานะ '{new_status}' (Payment: {payment_status}) เรียบร้อยแล้ว", "success")
    return redirect(url_for("admin_panel"))

@app.route("/admin/user/toggle-role/<int:user_id>", methods=["POST"])
@login_required(role="ADMIN")
def admin_toggle_user_role(user_id):
    if user_id == session["user_id"]:
        flash("ไม่สามารถเปลี่ยนสิทธิ์ของบัญชีแอดมินที่กำลังใช้งานอยู่ได้", "warning")
        return redirect(url_for("admin_panel"))

    conn = get_db_connection()
    user = conn.execute("SELECT role_id FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if user:
        new_role = 1 if user["role_id"] == 2 else 2
        conn.execute("UPDATE users SET role_id = ? WHERE user_id = ?", (new_role, user_id))
        conn.commit()
        flash("เปลี่ยนบทบาทผู้ใช้งานเรียบร้อยแล้ว", "info")
    conn.close()
    return redirect(url_for("admin_panel"))

# ------------------------------------------------------------------------------
# Analytics & Reports Dashboard (US-10 & 4 SQL Reports)
# ------------------------------------------------------------------------------
@app.route("/analytics")
@login_required(role="ADMIN")
def analytics_dashboard():
    conn = get_db_connection()

    # Summary KPIs
    kpis = conn.execute("""
        SELECT 
            (SELECT COUNT(*) FROM orders WHERE order_status = 'CONFIRMED') AS confirmed_orders,
            (SELECT COALESCE(ROUND(SUM(total_amount), 2), 0.00) FROM orders WHERE order_status = 'CONFIRMED') AS total_revenue,
            (SELECT COALESCE(ROUND(AVG(total_amount), 2), 0.00) FROM orders WHERE order_status = 'CONFIRMED') AS avg_order_value,
            (SELECT COUNT(*) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'CONFIRMED') AS total_books_sold,
            (SELECT COUNT(*) FROM users WHERE role_id = 2) AS customer_count
    """).fetchone()

    # Report 1: Sales by Time Period (Monthly Trend)
    r1_sql = """
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
    report1 = conn.execute(r1_sql).fetchall()

    # Report 2: Top-Selling E-Books
    r2_sql = """
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
    report2 = conn.execute(r2_sql).fetchall()

    # Report 3: Sales by Category
    r3_sql = """
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
    report3 = conn.execute(r3_sql).fetchall()

    # Report 4: Customer Lifetime Value & Order Status Distribution
    r4_sql = """
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
    report4 = conn.execute(r4_sql).fetchall()

    conn.close()

    return render_template("analytics.html",
                           kpis=dict(kpis),
                           report1=[dict(r) for r in report1],
                           report2=[dict(r) for r in report2],
                           report3=[dict(r) for r in report3],
                           report4=[dict(r) for r in report4])

# ------------------------------------------------------------------------------
# Database Explorer & Data Dictionary Inspector
# ------------------------------------------------------------------------------
@app.route("/database-explorer")
def database_explorer():
    conn = get_db_connection()
    schema_details = get_schema_overview(conn)
    conn.close()
    return render_template("db_explorer.html", schema_details=schema_details)

@app.route("/api/query-runner", methods=["POST"])
def api_query_runner():
    """Allows running read-only SELECT queries from the database explorer UI"""
    data = request.get_json() or {}
    sql = data.get("sql", "").strip()

    if not sql:
        return jsonify({"success": False, "error": "กรุณาระบุคำสั่ง SQL"}), 400

    # Read-only guard
    upper_sql = sql.upper().strip()
    if not upper_sql.startswith("SELECT") and not upper_sql.startswith("EXPLAIN"):
        return jsonify({"success": False, "error": "อนุญาตเฉพาะคำสั่ง SELECT หรือ EXPLAIN เท่านั้นเพื่อความปลอดภัย"}), 403

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []
        results = [dict(row) for row in rows]
        conn.close()
        return jsonify({
            "success": True,
            "columns": columns,
            "data": results,
            "row_count": len(results)
        })
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
