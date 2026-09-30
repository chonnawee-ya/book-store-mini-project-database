# 📚 สารบัญและภาพรวมเอกสารอธิบายการทำงานของแต่ละฟังก์ชัน
## E-Book Store Database Management Platform (2026)

โฟลเดอร์ `function_docs/` นี้จัดทำขึ้นเพื่ออธิบาย **ขั้นตอนการทำงานอย่างละเอียด (Step-by-step Workflow)** ของทุกฟังก์ชันในระบบ ทั้งฝั่ง Web Application Controller ([app.py](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/app.py)) และ Database Access Layer ([database/db.py](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/database/db.py)) เพื่อใช้เป็นเอกสารอ้างอิงและเตรียมนำเสนอโครงงานวิชาฐานข้อมูล

---

### 📂 โครงสร้างเอกสารในโฟลเดอร์นี้

| ลำดับ | ไฟล์เอกสาร | รายละเอียดเนื้อหา |
| :---: | :--- | :--- |
| **00** | [00_OVERVIEW.md](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/function_docs/00_OVERVIEW.md) | แผนผังภาพรวมระบบ (Architecture & Call Flow), สรุปตาราง Route, Method, Role |
| **01** | [01_AUTH_AND_SESSION.md](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/function_docs/01_AUTH_AND_SESSION.md) | ระบบสมาชิก, ตรวจสอบสิทธิ์ (RBAC), Demo Switcher, และ Context Processor |
| **02** | [02_STOREFRONT_AND_CART.md](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/function_docs/02_STOREFRONT_AND_CART.md) | หน้าร้าน, ค้นหา/กรอง E-Book, ตะกร้าสินค้า, กฎการซื้อ 1 เล่มต่อคน |
| **03** | [03_CHECKOUT_AND_DOWNLOAD.md](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/function_docs/03_CHECKOUT_AND_DOWNLOAD.md) | ระบบสั่งซื้อ Checkout (ACID Transaction), ชำระเงินจำลอง, และ Security Guardrail ดาวน์โหลดไฟล์ |
| **04** | [04_ADMIN_MANAGEMENT.md](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/function_docs/04_ADMIN_MANAGEMENT.md) | แอดมินแดชบอร์ด, จัดการหนังสือ, หมวดหมู่, อนุมัติสลิป/ออเดอร์, สลับสิทธิ์ User |
| **05** | [05_ANALYTICS_AND_EXPLORER.md](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/function_docs/05_ANALYTICS_AND_EXPLORER.md) | ระบบรายงานสถิติ 4 รูปแบบ (Advanced SQL), Data Dictionary Explorer, Safe SQL Runner |
| **06** | [06_DATABASE_LAYER.md](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/function_docs/06_DATABASE_LAYER.md) | สถาปัตยกรรมชั้นฐานข้อมูล, Cross-Engine Adapter (SQLite / Supabase Postgres / MySQL) |
| **07** | [07_SYSTEM_DIAGRAMS.md](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/function_docs/07_SYSTEM_DIAGRAMS.md) | **แผนภาพระบบทั้ง 6 แบบ (Mermaid):** 3NF ER-Diagram, System Architecture, ACID Transaction, Guardrail, Use Case, State Machine |

---

### 🗺️ แผนผังลำดับการทำงานภาพรวม (High-Level Architecture)

```
[ Web Browser / Client ]
           │
           ▼
[ Flask Application (app.py) ]
    ├── Context Processor (inject_global_data)
    ├── Route Guards (login_required Decorator)
    ├── Business Logic & Validation
    └── Jinja2 Templates (HTML Rendering)
           │
           ▼
[ Database Layer (database/db.py) ]
    ├── Engine Detection (SQLite / PostgreSQL / MySQL)
    ├── SQL Translation (strftime <-> TO_CHAR / DATE_FORMAT)
    ├── Parameterized Execution (100% Prepared Statements)
    └── UnifiedRow Wrapper (สนับสนุน dict & tuple index)
           │
           ▼
[ Physical Database ]
    (ebook_store.db / Supabase PostgreSQL / Cloud MySQL)
```
