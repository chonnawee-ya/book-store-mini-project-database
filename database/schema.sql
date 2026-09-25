-- ==============================================================================
-- E-Book Store Database Schema (SQLite 3NF Specification)
-- Project: Database Mini Project ร้านขาย E-Book
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- 1. ตารางบทบาทผู้ใช้งาน (Roles)
CREATE TABLE IF NOT EXISTS roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL UNIQUE
);

-- 2. ตารางผู้ใช้งาน (Users)
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE RESTRICT
);

-- 3. ตารางหมวดหมู่หนังสือ (Categories)
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- 4. ตารางผู้แต่งหนังสือ (Authors)
CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    biography TEXT
);

-- 5. ตารางหนังสืออิเล็กทรอนิกส์ (E-Books)
CREATE TABLE IF NOT EXISTS ebooks (
    ebook_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL CHECK (price >= 0.00),
    cover_image_url TEXT,
    file_download_url TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT,
    FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE RESTRICT
);

-- 6. ตารางตะกร้าสินค้า (Carts) - 1 ตะกร้าต่อ 1 บัญชีผู้ใช้
CREATE TABLE IF NOT EXISTS carts (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 7. ตารางรายการสินค้าในตะกร้า (Cart Items)
CREATE TABLE IF NOT EXISTS cart_items (
    cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    ebook_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity = 1),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (ebook_id) REFERENCES ebooks(ebook_id) ON DELETE CASCADE,
    CONSTRAINT uq_cart_ebook UNIQUE (cart_id, ebook_id)
);

-- 8. ตารางคำสั่งซื้อ (Orders)
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_amount REAL NOT NULL CHECK (total_amount >= 0.00),
    order_status TEXT NOT NULL DEFAULT 'PENDING' CHECK (order_status IN ('PENDING', 'CONFIRMED', 'CANCELLED')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT
);

-- 9. ตารางรายการสินค้าในคำสั่งซื้อ (Order Items)
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    ebook_id INTEGER NOT NULL,
    unit_price REAL NOT NULL CHECK (unit_price >= 0.00),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (ebook_id) REFERENCES ebooks(ebook_id) ON DELETE RESTRICT,
    CONSTRAINT uq_order_ebook UNIQUE (order_id, ebook_id)
);

-- 10. ตารางการชำระเงินจำลอง (Payments)
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL UNIQUE,
    payment_method TEXT NOT NULL DEFAULT 'SIMULATED_TRANSFER',
    slip_url TEXT,
    paid_amount REAL NOT NULL CHECK (paid_amount >= 0.00),
    payment_status TEXT NOT NULL DEFAULT 'WAITING_VERIFICATION' CHECK (payment_status IN ('WAITING_VERIFICATION', 'APPROVED', 'REJECTED')),
    payment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- สร้าง Indexes เพื่อเพิ่มประสิทธิภาพการค้นหาและ JOIN
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_ebooks_category ON ebooks(category_id);
CREATE INDEX IF NOT EXISTS idx_ebooks_author ON ebooks(author_id);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_ebook ON order_items(ebook_id);
CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);
