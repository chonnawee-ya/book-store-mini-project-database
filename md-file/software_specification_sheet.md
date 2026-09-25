# Software Specification Sheet: E-Book Store Database Mini Project

---

## 1. System Overview
ระบบร้านค้า E-Book จำลองเพื่อการศึกษา เน้นการออกแบบโครงสร้างฐานข้อมูลที่มีความสัมพันธ์ถูกต้องตามกฎเกณฑ์ Normalization (3NF) มีระบบความปลอดภัยของข้อมูล และสามารถดึงข้อมูลมาออกรายงานวิเคราะห์ (Analytics) ได้อย่างมีประสิทธิภาพ

---

## 2. Database Architecture & Schema Design (3NF)

ฐานข้อมูลประกอบด้วยตารางหลักอย่างน้อย 9 ตาราง รองรับข้อกำหนด $\ge 8$ ตาราง:

```
[roles] 1 --- <N [users] 1 --- <N [orders] 1 --- <N [order_items] N> --- 1 [ebooks]
                                      1                 ^                     ^
                                      |                 |                     |
                                      +--- 1 [payments] |                     +--- N> 1 [categories]
                                                        |                     +--- N> 1 [authors]
[users] 1 --- 1 [carts] 1 --- <N [cart_items] ----------+
[ebooks] 1 --- <N [download_links] (สำหรับคุม secure access token/key)
```

### Table Definitions & Constraints

#### 1. `roles`
* `role_id` (INT, PK, AUTO_INCREMENT)
* `role_name` (VARCHAR(50), NOT NULL, UNIQUE) - e.g., 'CUSTOMER', 'ADMIN'

#### 2. `users`
* `user_id` (INT, PK, AUTO_INCREMENT)
* `role_id` (INT, NOT NULL, FK -> `roles.role_id`)
* `email` (VARCHAR(191), NOT NULL, UNIQUE)
* `password_hash` (VARCHAR(255), NOT NULL)
* `full_name` (VARCHAR(100), NOT NULL)
* `phone` (VARCHAR(20), NULL)
* `created_at` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)

#### 3. `categories`
* `category_id` (INT, PK, AUTO_INCREMENT)
* `name` (VARCHAR(100), NOT NULL, UNIQUE)
* `description` (TEXT, NULL)

#### 4. `authors`
* `author_id` (INT, PK, AUTO_INCREMENT)
* `name` (VARCHAR(150), NOT NULL)
* `biography` (TEXT, NULL)

#### 5. `ebooks`
* `ebook_id` (INT, PK, AUTO_INCREMENT)
* `category_id` (INT, NOT NULL, FK -> `categories.category_id`)
* `author_id` (INT, NOT NULL, FK -> `authors.author_id`)
* `title` (VARCHAR(255), NOT NULL)
* `description` (TEXT, NULL)
* `price` (DECIMAL(10,2), NOT NULL, CHECK (price >= 0.00))
* `cover_image_url` (VARCHAR(500), NULL)
* `file_download_url` (VARCHAR(500), NOT NULL) -- ลิงก์ไฟล์ปลายทางจำลอง
* `is_active` (BOOLEAN, NOT NULL, DEFAULT TRUE)
* `created_at` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)

#### 6. `carts` & `cart_items`
* **`carts`**:
  * `cart_id` (INT, PK, AUTO_INCREMENT)
  * `user_id` (INT, NOT NULL, UNIQUE, FK -> `users.user_id`)
  * `updated_at` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
* **`cart_items`**:
  * `cart_item_id` (INT, PK, AUTO_INCREMENT)
  * `cart_id` (INT, NOT NULL, FK -> `carts.cart_id` ON DELETE CASCADE)
  * `ebook_id` (INT, NOT NULL, FK -> `ebooks.ebook_id`)
  * `quantity` (INT, NOT NULL, DEFAULT 1, CHECK (quantity = 1)) -- E-Book มี 1 เล่มต่อตะกร้า
  * CONSTRAINT `uq_cart_ebook` UNIQUE (`cart_id`, `ebook_id`)

#### 7. `orders` & `order_items`
* **`orders`**:
  * `order_id` (INT, PK, AUTO_INCREMENT)
  * `user_id` (INT, NOT NULL, FK -> `users.user_id`)
  * `total_amount` (DECIMAL(10,2), NOT NULL, CHECK (total_amount >= 0.00))
  * `order_status` (VARCHAR(20), NOT NULL, DEFAULT 'PENDING', CHECK (order_status IN ('PENDING', 'CONFIRMED', 'CANCELLED')))
  * `created_at` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
* **`order_items`**:
  * `order_item_id` (INT, PK, AUTO_INCREMENT)
  * `order_id` (INT, NOT NULL, FK -> `orders.order_id` ON DELETE CASCADE)
  * `ebook_id` (INT, NOT NULL, FK -> `ebooks.ebook_id`)
  * `unit_price` (DECIMAL(10,2), NOT NULL, CHECK (unit_price >= 0.00)) -- เก็บล็อคราคาตอนที่ซื้อ
  * CONSTRAINT `uq_order_ebook` UNIQUE (`order_id`, `ebook_id`)

#### 8. `payments`
* `payment_id` (INT, PK, AUTO_INCREMENT)
* `order_id` (INT, NOT NULL, UNIQUE, FK -> `orders.order_id`)
* `payment_method` (VARCHAR(50), NOT NULL, DEFAULT 'SIMULATED_TRANSFER')
* `slip_url` (VARCHAR(500), NULL)
* `paid_amount` (DECIMAL(10,2), NOT NULL, CHECK (paid_amount >= 0.00))
* `payment_status` (VARCHAR(20), NOT NULL, DEFAULT 'WAITING_VERIFICATION', CHECK (payment_status IN ('WAITING_VERIFICATION', 'APPROVED', 'REJECTED')))
* `payment_date` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)

---

## 3. Core Business Logic & Security Rules

1. **สิทธิ์การเข้าถึงไฟล์ดาวน์โหลด (Download Authorization Rule):**
   * ลูกค้าจะได้รับสิทธิ์เข้าถึง `file_download_url` หรือ Download Token ก็ต่อเมื่อ:
     $$\text{orders.order\_status} = \text{'CONFIRMED'}$$
     และ
     $$\text{orders.user\_id} = \text{Current Authenticated User ID}$$
   * ปฏิเสธการเข้าถึงและซ่อนปุ่มหากสถานะเป็น `PENDING` หรือ `CANCELLED`
2. **การป้องกันข้อมูลทางการเงิน:**
   * ไม่อนุญาตให้จัดเก็บข้อมูลบัตรเดบิต/เครดิต หรือเลขบัญชีธนาคารจริงของลูกค้าเด็ดขาด
   * ใช้ข้อมูลจำลอง (Mock Data) สำหรับการแจ้งชำระเงินและรูปสลิป
3. **การรักษาความถูกต้องของข้อมูล (Data Integrity):**
   * ใช้ Transactions ในขั้นตอน Checkout (สร้าง Order, Insert Order Items, สร้าง Payment จำลอง, เคลียร์ Cart) เพื่อป้องกันข้อมูลค้าง

---

## 4. Analytical Reports & SQL Queries (4 รายงานหลัก)

### รายงานที่ 1: ยอดขายตามช่วงเวลา (Sales by Time Period)
* **โจทย์:** วิเคราะห์ยอดขายรวม จำนวนคำสั่งซื้อ และยอดเฉลี่ยต่อคำสั่งซื้อ (AOV) รายเดือน
```sql
SELECT 
    DATE_FORMAT(o.created_at, '%Y-%m') AS sales_month,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS average_order_value
FROM orders o
WHERE o.order_status = 'CONFIRMED'
GROUP BY DATE_FORMAT(o.created_at, '%Y-%m')
ORDER BY sales_month DESC;
```

### รายงานที่ 2: E-Book ขายดี (Top-Selling E-Books)
* **โจทย์:** ค้นหาหนังสือที่ขายดีที่สุด 5 อันดับแรก ทั้งในแง่จำนวนเล่มและมูลค่ายอดขาย
```sql
SELECT 
    b.ebook_id,
    b.title,
    a.name AS author_name,
    COUNT(oi.order_item_id) AS units_sold,
    SUM(oi.unit_price) AS total_sales_amount
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN ebooks b ON oi.ebook_id = b.ebook_id
JOIN authors a ON b.author_id = a.author_id
WHERE o.order_status = 'CONFIRMED'
GROUP BY b.ebook_id, b.title, a.name
ORDER BY units_sold DESC, total_sales_amount DESC
LIMIT 5;
```

### รายงานที่ 3: ยอดขายตามหมวดหมู่ (Sales by Category)
* **โจทย์:** เปรียบเทียบผลประกอบการของแต่ละหมวดหมู่ เพื่อดูหมวดหมู่ที่ทำรายได้สูงสุด
```sql
SELECT 
    c.category_id,
    c.name AS category_name,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(oi.order_item_id) AS total_books_sold,
    COALESCE(SUM(oi.unit_price), 0.00) AS total_revenue
FROM categories c
LEFT JOIN ebooks b ON c.category_id = b.category_id
LEFT JOIN order_items oi ON b.ebook_id = oi.ebook_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'CONFIRMED'
GROUP BY c.category_id, c.name
ORDER BY total_revenue DESC;
```

### รายงานที่ 4: พฤติกรรมลูกค้าและสถานะคำสั่งซื้อ (Customer Lifetime Value & Status)
* **โจทย์:** วิเคราะห์ลูกค้าที่มียอดสั่งซื้อสะสมสูง พร้อมสรุปสัดส่วนสถานะคำสั่งซื้อ
```sql
SELECT 
    u.user_id,
    u.full_name,
    u.email,
    COUNT(o.order_id) AS total_orders_placed,
    SUM(CASE WHEN o.order_status = 'CONFIRMED' THEN 1 ELSE 0 END) AS confirmed_orders,
    SUM(CASE WHEN o.order_status = 'PENDING' THEN 1 ELSE 0 END) AS pending_orders,
    SUM(CASE WHEN o.order_status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled_orders,
    COALESCE(SUM(CASE WHEN o.order_status = 'CONFIRMED' THEN o.total_amount ELSE 0 END), 0.00) AS total_spent
FROM users u
JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.full_name, u.email
HAVING total_orders_placed >= 1
ORDER BY total_spent DESC;
```

---

## 5. Test Case Scenarios (เกณฑ์อย่างน้อย 8 กรณีทดสอบ)
1. **TC-01:** สมัครสมาชิกสำเร็จด้วยอีเมลใหม่
2. **TC-02 (Negative):** สมัครสมาชิกด้วยอีเมลซ้ำในระบบ (ระบบต้องปฏิเสธ)
3. **TC-03 (Negative):** แอดมินเพิ่ม E-Book ที่มีราคาติดลบ (Constraint Violation)
4. **TC-04:** ลูกค้าค้นหา E-Book และกรองตามหมวดหมู่ได้ผลลัพธ์ถูกต้อง
5. **TC-05:** ลูกค้าเพิ่มสินค้าลงตะกร้าและทำการ Checkout คำสั่งซื้อสำเร็จ (สถานะ PENDING)
6. **TC-06 (Security/Logic):** ลูกค้าพยายามเปิดดาวน์โหลดขณะ Order ยังเป็น PENDING (ระบบต้องบล็อก)
7. **TC-07:** แอดมินตรวจสอบหลักฐานและเปลี่ยนสถานะเป็น CONFIRMED
8. **TC-08:** ลูกค้าเข้าดูประวัติและสามารถกดดาวน์โหลดไฟล์ E-Book ได้สำเร็จ