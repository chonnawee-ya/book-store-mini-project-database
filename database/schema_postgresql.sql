-- ==============================================================================
-- E-Book Store Database Schema (PostgreSQL / Supabase Specification)
-- Project: Database Mini Project ร้านขาย E-Book
-- Normalized: 3NF (Third Normal Form)
-- ==============================================================================

DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS cart_items CASCADE;
DROP TABLE IF EXISTS carts CASCADE;
DROP TABLE IF EXISTS ebooks CASCADE;
DROP TABLE IF EXISTS authors CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- 1. ตารางบทบาทผู้ใช้งาน (Roles)
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

-- 2. ตารางผู้ใช้งาน (Users)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    role_id INT NOT NULL REFERENCES roles(role_id) ON DELETE RESTRICT,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. ตารางหมวดหมู่หนังสือ (Categories)
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL
);

-- 4. ตารางผู้แต่งหนังสือ (Authors)
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    biography TEXT NULL
);

-- 5. ตารางหนังสืออิเล็กทรอนิกส์ (E-Books)
CREATE TABLE ebooks (
    ebook_id SERIAL PRIMARY KEY,
    category_id INT NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
    author_id INT NOT NULL REFERENCES authors(author_id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0.00),
    cover_image_url VARCHAR(500) NULL,
    file_download_url VARCHAR(500) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. ตารางตะกร้าสินค้า (Carts)
CREATE TABLE carts (
    cart_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7. ตารางรายการสินค้าในตะกร้า (Cart Items)
CREATE TABLE cart_items (
    cart_item_id SERIAL PRIMARY KEY,
    cart_id INT NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
    ebook_id INT NOT NULL REFERENCES ebooks(ebook_id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity = 1),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cart_ebook UNIQUE (cart_id, ebook_id)
);

-- 8. ตารางคำสั่งซื้อ (Orders)
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    total_amount NUMERIC(10,2) NOT NULL CHECK (total_amount >= 0.00),
    order_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (order_status IN ('PENDING', 'CONFIRMED', 'CANCELLED')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 9. ตารางรายการสินค้าในคำสั่งซื้อ (Order Items)
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    ebook_id INT NOT NULL REFERENCES ebooks(ebook_id) ON DELETE RESTRICT,
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0.00),
    CONSTRAINT uq_order_ebook UNIQUE (order_id, ebook_id)
);

-- 10. ตารางการชำระเงินจำลอง (Payments)
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    payment_method VARCHAR(50) NOT NULL DEFAULT 'SIMULATED_TRANSFER',
    slip_url VARCHAR(500) NULL,
    paid_amount NUMERIC(10,2) NOT NULL CHECK (paid_amount >= 0.00),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'WAITING_VERIFICATION' CHECK (payment_status IN ('WAITING_VERIFICATION', 'APPROVED', 'REJECTED')),
    payment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes เพื่อเพิ่มประสิทธิภาพการค้นหาและ JOIN
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_ebooks_category ON ebooks(category_id);
CREATE INDEX idx_ebooks_author ON ebooks(author_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_ebook ON order_items(ebook_id);
CREATE INDEX idx_payments_order ON payments(order_id);
