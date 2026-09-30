# 07. แผนภาพแสดงการทำงานของระบบ (System Diagrams & Workflows)

เอกสารนี้รวบรวม **Diagram สำคัญทั้ง 6 รูปแบบ** ที่จำเป็นต่อการอธิบายและนำเสนอโครงงานวิชาฐานข้อมูล (Database Mini Project) โดยใช้สัญลักษณ์มาตรฐานและรูปแบบ **Mermaid Diagram** ที่สามารถแสดงผลบน GitHub, IDE หรือนำไปแปลงเป็นรูปภาพใส่ในเล่มรายงานและสไลด์ได้ทันที

---

## 1. 🗄️ แผนภาพความสัมพันธ์ฐานข้อมูลเชิงสัมพันธ์ (3NF ER-Diagram)
* **จุดประสงค์:** แสดงโครงสร้างฐานข้อมูลทั้ง 10 ตาราง ความสัมพันธ์ (Cardinality), Primary Key (`PK`), Foreign Key (`FK`) และ Constraints ที่เป็นไปตามรูปแบบ **3NF (Third Normal Form)**

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

    ROLES ||--o{ USERS : "defines"
    USERS ||--|| CARTS : "owns (1:1)"
    USERS ||--o{ ORDERS : "places (1:N)"
    CATEGORIES ||--o{ EBOOKS : "classifies (1:N)"
    AUTHORS ||--o{ EBOOKS : "writes (1:N)"
    CARTS ||--o{ CART_ITEMS : "contains (1:N)"
    EBOOKS ||--o{ CART_ITEMS : "referenced_in"
    ORDERS ||--o{ ORDER_ITEMS : "composed_of (1:N)"
    EBOOKS ||--o{ ORDER_ITEMS : "snapshot_in"
    ORDERS ||--|| PAYMENTS : "settled_by (1:1)"
```

---

## 2. 🏗️ แผนภาพสถาปัตยกรรมระบบ (System Architecture Diagram)
* **จุดประสงค์:** แสดงการแยก Layer การทำงาน และความสามารถของ Data Access Layer ที่รองรับทั้ง **SQLite (Local)**, **Supabase PostgreSQL (Cloud)**, และ **Cloud MySQL**

```mermaid
flowchart TB
    subgraph PresentationTier ["1. Presentation Tier (Frontend)"]
        Browser["🌐 Web Browser / Client Devices"]
        Templates["🎨 HTML5 + Jinja2 Templates + Vanilla CSS"]
        Browser <--> Templates
    end

    subgraph ApplicationTier ["2. Application Tier (Flask Server)"]
        AppPy["⚡ Flask Controller (app.py)"]
        Context["🔄 Global Context Processor (inject_global_data)"]
        RBAC["🛡️ RBAC Guard (@login_required)"]
        BizLogic["📦 Business Logic (Cart, Checkout, Guardrails)"]
        
        AppPy --> Context
        AppPy --> RBAC
        AppPy --> BizLogic
    end

    subgraph DataAccessTier ["3. Data Access Layer (database/db.py)"]
        EngineDetect["⚙️ Database Engine Switcher (SQLite / Postgres / MySQL)"]
        SQLTranslate["🔄 SQL Syntax Translator (? -> %s, strftime -> TO_CHAR)"]
        UnifiedWrapper["📦 UnifiedRow & RemoteCursorWrapper"]
        
        EngineDetect --> SQLTranslate --> UnifiedWrapper
    end

    subgraph DatabaseTier ["4. Database Tier (RDBMS 3NF)"]
        direction LR
        SQLite[("📁 SQLite 3\n(Local File:\nebook_store.db)")]
        Postgres[("🐘 PostgreSQL / Supabase\n(Cloud Connection Pooler:\nport 5432 / 6543)")]
        MySQL[("🐬 MySQL / MariaDB\n(Cloud Production)")]
    end

    Templates <--> AppPy
    BizLogic <--> EngineDetect
    UnifiedWrapper <--> SQLite
    UnifiedWrapper <--> Postgres
    UnifiedWrapper <--> MySQL
```

---

## 3. 💳 แผนภาพลำดับการทำงานคำสั่งซื้อ (Checkout & ACID Transaction Sequence)
* **จุดประสงค์:** อธิบายการทำงานของฟังก์ชัน `checkout()` ภายใต้ Database Transaction หากขั้นตอนใดล้มเหลว จะถูก `ROLLBACK` ทั้งหมด

```mermaid
sequenceDiagram
    autonumber
    actor Customer as 👤 ลูกค้า (Customer)
    participant Route as 🖥️ /checkout Controller
    participant DB as 🗄️ Database (ACID Transaction)

    Customer->>Route: ส่งฟอร์มชำระเงิน (POST: payment_method, slip_url)
    Route->>DB: เริ่มต้น Transaction (BEGIN TRANSACTION)
    
    critical ขั้นตอนธุรกรรมฐานข้อมูล (All-or-Nothing)
        Route->>DB: 1. INSERT INTO orders (user_id, total_amount, 'PENDING')
        DB-->>Route: คืนค่า new_order_id
        
        Route->>DB: 2. INSERT INTO order_items (order_id, ebook_id, unit_price)
        Note over Route,DB: บันทึกราคา Snapshot ของหนังสือทุกเล่มในตะกร้า
        
        Route->>DB: 3. INSERT INTO payments (order_id, paid_amount, 'WAITING_VERIFICATION')
        Note over Route,DB: บันทึกข้อมูลการชำระเงินและสลิปจำลอง
        
        Route->>DB: 4. DELETE FROM cart_items WHERE cart_id = user_cart_id
        Note over Route,DB: เคลียร์สินค้าออกจากตะกร้าผู้ใช้
    end

    alt ทุกขั้นตอนสำเร็จสมบูรณ์ (Success)
        Route->>DB: COMMIT TRANSACTION
        Route-->>Customer: แสดงแจ้งเตือนสำเร็จ และ Redirect ไปยัง /orders
    else เกิดข้อผิดพลาดหรือขัดข้อง (Error Exception)
        Route->>DB: ROLLBACK TRANSACTION
        Note over DB: ยกเลิกการเปลี่ยนแปลงทั้งหมด ข้อมูลคงเดิม
        Route-->>Customer: แจ้งเตือนข้อผิดพลาด และให้อยู่ที่หน้าเดิม
    end
```

---

## 4. 🛡️ แผนภาพกระบวนการตรวจสอบสิทธิ์ดาวน์โหลด (Download Guardrail Flowchart)
* **จุดประสงค์:** แสดงขั้นตอนการตรวจสอบสิทธิ์ 4 ด่านของฟังก์ชัน `download_ebook()` เพื่อรักษาความปลอดภัยของไฟล์ E-Book

```mermaid
flowchart TD
    A([ลูกค้าคลิกปุ่มดาวน์โหลด E-Book]) --> B{ผู้ใช้ล็อกอินอยู่หรือไม่?}
    B -- ไม่ได้ล็อกอิน --> C[Redirect ไปหน้า /login พร้อมแจ้งเตือน]
    
    B -- ล็อกอินแล้ว --> D{พบ Order ID ในระบบหรือไม่?}
    D -- ไม่พบ --> E[ส่ง HTTP 404: ไม่พบคำสั่งซื้อ]
    
    D -- พบข้อมูล --> F{เป็นแอดมิน หรือเป็นเจ้าของออเดอร์นี้?}
    F -- ไม่ใช่เจ้าของและไม่ใช่แอดมิน --> G[ปฏิเสธ HTTP 403: Forbidden Access]
    
    F -- ผ่านการยืนยันตัวตน --> H{สถานะคำสั่งซื้อเป็น 'CONFIRMED' หรือไม่?}
    H -- ยังเป็น PENDING หรือ CANCELLED --> I[ปฏิเสธการดาวน์โหลด: ออเดอร์ยังไม่ได้รับการอนุมัติ]
    
    H -- ได้รับการอนุมัติแล้ว (CONFIRMED) --> J{หนังสือเล่มนี้อยู่ในออเดอร์จริงไหม?}
    J -- ไม่อยู่ในออเดอร์นี้ --> K[ส่ง HTTP 404: ไม่พบหนังสือในออเดอร์]
    
    J -- ข้อมูลถูกต้องครบถ้วน --> L[สร้าง Personalized License Header แบบ Real-time]
    L --> M([ส่งมอบไฟล์ E-Book ให้ดาวน์โหลดสำเร็จ])
```

---

## 5. 👥 แผนภาพการใช้งานระบบตามบทบาท (Use Case Diagram)
* **จุดประสงค์:** แสดงขอบเขตการทำงานของแต่ละ Actor ภายในระบบ

```mermaid
flowchart LR
    Visitor((👤 ผู้เยี่ยมชม\nVisitor))
    Customer((🛒 ลูกค้า\nCustomer))
    Admin((🛡️ ผู้ดูแลระบบ\nAdmin))

    subgraph GuestSystem ["ระบบทั่วไป"]
        UC1([ดูรายการหนังสือหน้าร้าน])
        UC2([ค้นหา & กรองตามหมวดหมู่])
        UC3([ดูรายละเอียดหนังสือ & ผู้แต่ง])
        UC4([สมัครสมาชิก / เข้าสู่ระบบ])
        UC5([สลับ Demo User])
    end

    subgraph ShoppingSystem ["ระบบสั่งซื้อ & บริการลูกค้า"]
        UC6([เพิ่มสินค้าลงตะกร้า])
        UC7([ลบสินค้าออกจากตะกร้า])
        UC8([สั่งซื้อ Checkout & แนบสลิป])
        UC9([ดูประวัติคำสั่งซื้อ])
        UC10([ดาวน์โหลด E-Book ผ่าน Guardrail])
    end

    subgraph AdminSystem ["ระบบบริหารจัดการ & วิเคราะห์"]
        UC11([เพิ่ม/แก้ไข/เปิด-ปิดการขาย E-Book])
        UC12([จัดการหมวดหมู่หนังสือ])
        UC13([ตรวจสอบสลิป & อนุมัติออเดอร์])
        UC14([จัดการสิทธิ์ผู้ใช้งาน])
        UC15([ดูรายงาน 4 SQL Analytics])
        UC16([ใช้งาน Database Explorer & SQL Runner])
    end

    Visitor --> UC1
    Visitor --> UC2
    Visitor --> UC3
    Visitor --> UC4
    Visitor --> UC5

    Customer --> UC1
    Customer --> UC2
    Customer --> UC3
    Customer --> UC5
    Customer --> UC6
    Customer --> UC7
    Customer --> UC8
    Customer --> UC9
    Customer --> UC10

    Admin --> UC1
    Admin --> UC5
    Admin --> UC10
    Admin --> UC11
    Admin --> UC12
    Admin --> UC13
    Admin --> UC14
    Admin --> UC15
    Admin --> UC16
```

---

## 6. 🔄 แผนภาพวงจรสถานะคำสั่งซื้อและการชำระเงิน (Order & Payment State Machine)
* **จุดประสงค์:** แสดงการเปลี่ยนแปลงสถานะของ `orders.order_status` และ `payments.payment_status`

```mermaid
stateDiagram-v2
    [*] --> OrderCreated: ลูกค้ากดยืนยันสั่งซื้อที่หน้า /checkout

    state OrderCreated {
        [*] --> PendingVerification
        PendingVerification: orders.order_status = 'PENDING'
        PendingVerification: payments.payment_status = 'WAITING_VERIFICATION'
        PendingVerification: (หนังสือในตะกร้าถูกเคลียร์)
        PendingVerification: (ยังไม่สามารถดาวน์โหลด E-Book ได้)
    }

    OrderCreated --> ConfirmedApproved: แอดมินตรวจสอบสลิปถูกต้อง และกด 'อนุมัติ'
    OrderCreated --> CancelledRejected: แอดมินตรวจสอบสลิปไม่ถูกต้อง หรือลูกค้ายกเลิก

    state ConfirmedApproved {
        [*] --> Confirmed
        Confirmed: orders.order_status = 'CONFIRMED'
        Confirmed: payments.payment_status = 'APPROVED'
        Confirmed: (ปลดล็อกสิทธิ์ดาวน์โหลดไฟล์ E-Book)
        Confirmed: (นำยอดไปคำนวณในรายงาน Analytics)
    }

    state CancelledRejected {
        [*] --> Cancelled
        Cancelled: orders.order_status = 'CANCELLED'
        Cancelled: payments.payment_status = 'REJECTED'
        Cancelled: (ปฏิเสธสิทธิ์ดาวน์โหลดไฟล์)
    }

    ConfirmedApproved --> [*]
    CancelledRejected --> [*]
```
