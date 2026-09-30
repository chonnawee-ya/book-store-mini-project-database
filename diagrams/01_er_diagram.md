# 01. แผนภาพความสัมพันธ์ฐานข้อมูลเชิงสัมพันธ์ (3NF Relational ER-Diagram)

แผนภาพนี้แสดงโครงสร้างฐานข้อมูลเชิงสัมพันธ์ทั้ง 10 ตาราง ที่ได้รับการปรับปรุงให้อยู่ในรูปแบบ **3NF (Third Normal Form)** พร้อมระบุ Primary Key (`PK`), Foreign Key (`FK`), Data Constraints และ Cardinality ความสัมพันธ์อย่างครบถ้วน

---

## 🗄️ Mermaid ER-Diagram

```mermaid
erDiagram
    ROLES {
        int role_id PK
        string role_name UK "UNIQUE ('ADMIN', 'CUSTOMER')"
    }

    USERS {
        int user_id PK
        int role_id FK "REFERENCES roles(role_id)"
        string email UK "UNIQUE"
        string password_hash
        string full_name
        string phone
        datetime created_at
    }

    CATEGORIES {
        int category_id PK
        string name UK "UNIQUE"
        string description
    }

    AUTHORS {
        int author_id PK
        string name
        string biography
    }

    EBOOKS {
        int ebook_id PK
        int category_id FK "REFERENCES categories(category_id)"
        int author_id FK "REFERENCES authors(author_id)"
        string title
        string description
        real price "CHECK (price >= 0.00)"
        string cover_image_url
        string file_download_url
        int is_active "CHECK (is_active IN (0, 1))"
        datetime created_at
    }

    CARTS {
        int cart_id PK
        int user_id FK "UNIQUE (1:1 with users)"
        datetime updated_at
    }

    CART_ITEMS {
        int cart_item_id PK
        int cart_id FK "REFERENCES carts(cart_id)"
        int ebook_id FK "REFERENCES ebooks(ebook_id)"
        int quantity "CHECK (quantity = 1)"
        datetime created_at
    }

    ORDERS {
        int order_id PK
        int user_id FK "REFERENCES users(user_id)"
        real total_amount "CHECK (total_amount >= 0.00)"
        string order_status "CHECK ('PENDING', 'CONFIRMED', 'CANCELLED')"
        datetime created_at
    }

    ORDER_ITEMS {
        int order_item_id PK
        int order_id FK "REFERENCES orders(order_id)"
        int ebook_id FK "REFERENCES ebooks(ebook_id)"
        real unit_price "CHECK (unit_price >= 0.00) Historical Snapshot"
    }

    PAYMENTS {
        int payment_id PK
        int order_id FK "UNIQUE (1:1 with orders)"
        string payment_method "DEFAULT 'SIMULATED_TRANSFER'"
        string slip_url
        real paid_amount "CHECK (paid_amount >= 0.00)"
        string payment_status "CHECK ('WAITING_VERIFICATION', 'APPROVED', 'REJECTED')"
        datetime payment_date
    }

    ROLES ||--o{ USERS : "defines (1:N)"
    USERS ||--|| CARTS : "owns (1:1)"
    USERS ||--o{ ORDERS : "places (1:N)"
    CATEGORIES ||--o{ EBOOKS : "classifies (1:N)"
    AUTHORS ||--o{ EBOOKS : "writes (1:N)"
    CARTS ||--o{ CART_ITEMS : "contains (1:N)"
    EBOOKS ||--o{ CART_ITEMS : "referenced_in (1:N)"
    ORDERS ||--o{ ORDER_ITEMS : "composed_of (1:N)"
    EBOOKS ||--o{ ORDER_ITEMS : "snapshot_in (1:N)"
    ORDERS ||--|| PAYMENTS : "settled_by (1:1)"
```

---

## 🔍 คำอธิบายจุดสำคัญตามหลัก 3NF และความปลอดภัยของข้อมูล

1. **การป้องกันราคาเปลี่ยนย้อนหลัง (`order_items.unit_price`):**
   * แม้ว่าตาราง `ebooks` จะมีฟิลด์ `price` อยู่แล้ว แต่ในตาราง `order_items` จำเป็นต้องเก็บ `unit_price` ณ ขณะสั่งซื้อ เพื่อไม่ให้ยอดสั่งซื้อในอดีตเปลี่ยนแปลงเมื่อผู้ดูแลระบบปรับขึ้น/ลงราคาหนังสือในอนาคต
2. **ความสัมพันธ์ 1:1 ระหว่าง User กับ Cart:**
   * ตาราง `carts` กำหนดคอลัมน์ `user_id` ให้เป็น `UNIQUE` เพื่อรับประกันว่าผู้ใช้ 1 คนจะมีตะกร้าได้เพียง 1 ใบเท่านั้น
3. **ความสัมพันธ์ 1:1 ระหว่าง Order กับ Payment:**
   * ตาราง `payments` กำหนดคอลัมน์ `order_id` ให้เป็น `UNIQUE` เพื่อรับประกันว่า 1 คำสั่งซื้อจะจับคู่กับรายการชำระเงินเพียง 1 รายการ
4. **Data Integrity Constraints:**
   * `price >= 0.00` และ `paid_amount >= 0.00` ป้องกันยอดเงินติดลบ
   * `quantity = 1` ใน `cart_items` เป็นกฎธุรกิจสำหรับสินค้าประเภท E-Book (ไม่มีความจำเป็นต้องซื้อซ้ำหลายก็อปปี้ในออเดอร์เดียวกัน)
