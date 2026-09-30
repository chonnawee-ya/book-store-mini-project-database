# 📚 E-Book Store Database Management Platform (2026)

> 🌐 **Live Demo (ออนไลน์):** [https://book-store-mini-project-database.onrender.com](https://book-store-mini-project-database.onrender.com)  
> 🗄️ **Production Database:** PostgreSQL on Supabase Cloud  
> 💻 **GitHub Repository:** [chonnawee-ya/book-store-mini-project-database](https://github.com/chonnawee-ya/book-store-mini-project-database)  
> 📄 **เอกสารรายงานส่งงานฉบับสมบูรณ์ (ตามใบงาน):** [`PROJECT_REPORT_AND_SUBMISSION.md`](PROJECT_REPORT_AND_SUBMISSION.md)

ระบบร้านค้าและบริหารจัดการฐานข้อมูล E-Book จำลองเพื่อการศึกษา ออกแบบโครงสร้างฐานข้อมูลเชิงสัมพันธ์ในรูปแบบ **3NF (Third Normal Form)**, มีระบบความปลอดภัยของข้อมูล (Security Guardrails), ระบบตะกร้า/คำสั่งซื้อ/จำลองการชำระเงิน, และระบบรายงานเชิงวิเคราะห์ (Analytics Dashboard) ผ่าน SQL Queries ขั้นสูง รองรับทั้ง SQLite, PostgreSQL (Supabase) และ MySQL

---

## 🌟 ฟีเจอร์หลักของระบบ (Core Features)

1. **ระบบลูกค้า (Customer Workflow):**
   - สมัครสมาชิก / เข้าสู่ระบบ พร้อมระบบแฮชรหัสผ่านที่ปลอดภัย (Werkzeug Security)
   - ค้นหาหนังสือ กรองตามหมวดหมู่ ดูรายละเอียดหนังสือและผู้แต่ง
   - ตะกร้าสินค้า และระบบสั่งซื้อ (Checkout) ทำงานภายใต้ **Database Transaction (ACID)**
   - **Download Guardrail (Security Rule):** สามารถดาวน์โหลดไฟล์หนังสือได้ต่อเมื่อคำสั่งซื้อได้รับการอนุมัติ (`order_status = 'CONFIRMED'`) และเป็นเจ้าของออเดอร์เท่านั้น

2. **ระบบผู้ดูแลระบบ (Admin Workflow):**
   - จัดการหนังสือ: เพิ่มหนังสือใหม่, แก้ไขข้อมูลหนังสือ (Edit E-Book Details ผ่าน Modal ทันที), เปิด/ปิดการขาย (Toggle Active)
   - จัดการหมวดหมู่หนังสือ
   - ตรวจสอบคำสั่งซื้อและสลิปการโอนเงิน (อนุมัติ / ปฏิเสธ)
   - จัดการบทบาทผู้ใช้งาน (Admin / Customer)
   - **Demo Switcher:** แถบสลับผู้ใช้งานจำลองด้านบนเพื่อความสะดวกในการทดสอบ/นำเสนอ

3. **ระบบรายงานเชิงวิเคราะห์ (4 Analytical SQL Reports):**
   - **รายงานที่ 1:** ยอดขายตามช่วงเวลารายเดือน (Sales by Time Period)
   - **รายงานที่ 2:** 5 อันดับหนังสือขายดี (Top-Selling E-Books)
   - **รายงานที่ 3:** ยอดขายแยกตามหมวดหมู่ (Sales by Category)
   - **รายงานที่ 4:** การจัดกลุ่มพฤติกรรมลูกค้าและยอดใช้จ่ายสะสม (Customer Lifetime Value - CLV)

4. **ระบบสำรวจฐานข้อมูล (Database Explorer & SQL Runner):**
   - ตรวจสอบ Schema, Data Dictionary, คอลัมน์, Foreign Keys และจำนวนแถวแบบ Real-time
   - Interactive SQL Runner สำหรับพิมพ์คำสั่ง `SELECT` เพื่อทดสอบผลลัพธ์ผ่านหน้าเว็บ (พร้อม Read-Only Security Guard)

5. **สไตล์การออกแบบมินิมอล & สลับโหมดการแสดงผล (Minimal UI, Themes & Mobile):**
   - การออกแบบสไตล์ **Minimalist Modern** โทนสีเรียบง่ายสบายตา ขนาดตัวอักษรกะทัดรัด (14px base font)
   - สลับโหมด **Dark Mode / Light Mode** ได้ทันที พร้อมจำสถานะผ่าน `localStorage` ป้องกันจอกระพริบ
   - รองรับหน้าจอมือถือและแท็บเล็ต 100% (Mobile Navigation Drawer, Touch-friendly, Horizontal Table Scroll)

---

## 🏗️ โครงสร้างฐานข้อมูล (Database Schema - 3NF)

ประกอบด้วย 10 ตารางหลักที่มี Foreign Key และ Constraints รัดกุม:
* `roles` : กำหนดสิทธิ์ (`ADMIN`, `CUSTOMER`)
* `users` : ข้อมูลผู้ใช้งาน, อีเมล (`UNIQUE`), แฮชรหัสผ่าน
* `categories` : หมวดหมู่หนังสือ
* `authors` : ข้อมูลผู้แต่ง
* `ebooks` : หนังสือ, ราคา (`CHECK (price >= 0)`), สถานะเปิด/ปิดขาย
* `carts` : ตะกร้าสินค้าของผู้ใช้ (1:1 กับ User)
* `cart_items` : รายการสินค้าในตะกร้า (`CHECK (quantity = 1)`)
* `orders` : คำสั่งซื้อ (`PENDING`, `CONFIRMED`, `CANCELLED`)
* `order_items` : รายการในคำสั่งซื้อ (เก็บบันทึก `unit_price` ณ วันสั่งซื้อ)
* `payments` : การชำระเงินจำลอง และสถานะสลิป (`WAITING_VERIFICATION`, `APPROVED`, `REJECTED`)

---

## 📖 เอกสารขั้นตอนการทำงานของแต่ละฟังก์ชัน (Function Documentation)

อ่านคำอธิบายขั้นตอนการทำงานอย่างละเอียดของแต่ละฟังก์ชัน (Step-by-step Workflow) ได้ที่โฟลเดอร์ [`function_docs/`](function_docs/README.md):
* [00_OVERVIEW.md](function_docs/00_OVERVIEW.md) : สรุปภาพรวมและผังความสัมพันธ์ของฟังก์ชันทั้งหมดในระบบ
* [01_AUTH_AND_SESSION.md](function_docs/01_AUTH_AND_SESSION.md) : ระบบยืนยันตัวตน, เซสชัน และสิทธิ์ผู้ใช้งาน (RBAC)
* [02_STOREFRONT_AND_CART.md](function_docs/02_STOREFRONT_AND_CART.md) : ระบบหน้าร้าน, แคตตาล็อก และตะกร้าสินค้า
* [03_CHECKOUT_AND_DOWNLOAD.md](function_docs/03_CHECKOUT_AND_DOWNLOAD.md) : การสั่งซื้อ, Database Transaction และ Download Security Guardrail
* [04_ADMIN_MANAGEMENT.md](function_docs/04_ADMIN_MANAGEMENT.md) : ระบบบริหารจัดการสำหรับผู้ดูแลระบบ (Admin Functions)
* [05_ANALYTICS_AND_EXPLORER.md](function_docs/05_ANALYTICS_AND_EXPLORER.md) : ระบบรายงานเชิงวิเคราะห์ 4 SQL Reports และ Database Explorer
* [06_DATABASE_LAYER.md](function_docs/06_DATABASE_LAYER.md) : สถาปัตยกรรมชั้นฐานข้อมูล (Database Layer: SQLite, Postgres, MySQL)
* [07_SYSTEM_DIAGRAMS.md](function_docs/07_SYSTEM_DIAGRAMS.md) : แผนภาพระบบรวมทุกรูปแบบ

---

## 📊 แผนภาพระบบและโครงสร้างฐานข้อมูล (System Diagrams)

สามารถดูไดอะแกรมแบบแยกไฟล์ตามแต่ละหัวข้อได้ที่โฟลเดอร์ [`diagrams/`](diagrams/README.md):
* [01_er_diagram.md](diagrams/01_er_diagram.md) : แผนภาพความสัมพันธ์ฐานข้อมูลเชิงสัมพันธ์ 3NF (10 ตาราง)
* [02_system_architecture.md](diagrams/02_system_architecture.md) : สถาปัตยกรรมระบบ 4-Tier & Multi-Engine Data Access Layer
* [03_checkout_transaction_sequence.md](diagrams/03_checkout_transaction_sequence.md) : ลำดับการทำงานของ ACID Transaction ในการสั่งซื้อ
* [04_download_guardrail_flowchart.md](diagrams/04_download_guardrail_flowchart.md) : ผังกระบวนการตรวจสอบสิทธิ์ดาวน์โหลด E-Book (Security Guardrail)
* [05_use_case_diagram.md](diagrams/05_use_case_diagram.md) : ขอบเขตการทำงานจำแนกตาม 3 ตัวละคร (Visitor, Customer, Admin)
* [06_order_payment_state_machine.md](diagrams/06_order_payment_state_machine.md) : วงจรสถานะคำสั่งซื้อและการชำระเงิน

---

## 💻 วิธีการรันในเครื่อง Local (SQLite)

```bash
# 1. ติดตั้ง Dependencies
pip install -r requirements.txt

# 2. รันแอปพลิเคชัน
python app.py
```
เปิดเว็บเบราว์เซอร์ไปที่: `http://localhost:5000`

---

## 🚀 วิธีนำขึ้น Web & เชื่อมต่อ Database Cloud

ระบบรองรับทั้ง **Render.com + Supabase (PostgreSQL)** และ **Railway.app (MySQL)**:

### ตัวเลือกที่ 1: Deploy บน Render.com + Supabase (Production ปัจจุบัน)
1. **Cloud Database (Supabase):**
   - สร้างโปรเจกต์ใหม่บน [supabase.com](https://supabase.com) (ได้ PostgreSQL ฟรี)
   - ไปที่เมนู **SQL Editor** แล้วรันสคริปต์ `database/schema_postgres.sql` ตามด้วย `database/seed_data_postgres.sql`
   - คัดลอก Connection String (URI) จาก **Project Settings** -> **Database** (โหมด Transaction Pooler หรือ Direct)
2. **Deploy เว็บ (Render.com):**
   - เชื่อมต่อ GitHub Repo `chonnawee-ya/book-store-mini-project-database` บน [Render](https://render.com)
   - เลือกประเภท **Web Service** (Python 3)
   - กำหนด Build Command: `pip install -r requirements.txt`
   - กำหนด Start Command: `gunicorn app:app`
   - ตั้งค่า **Environment Variables**:
     - `DATABASE_URL` = `postgresql://...your_supabase_url...?sslmode=require`
     - `SECRET_KEY` = `your_secure_secret_key`
     - `PYTHON_VERSION` = `3.11.9`
   - กด **Deploy** -> เข้าใช้งานผ่านลิงก์ `https://book-store-mini-project-database.onrender.com`

---

### ตัวเลือกที่ 2: Deploy บน Railway.app (Cloud MySQL)
1. สมัคร/ล็อกอิน [Railway.app](https://railway.app) ด้วยบัญชี **GitHub**
2. กด **New Project** -> เลือก **Provision MySQL**
3. ไปที่ Service MySQL -> คลิกแท็บ **Connect** -> เปิด **Public Networking**
4. เปิดโปรแกรมจัดการฐานข้อมูล เช่น **DBeaver** หรือ **MySQL Workbench**:
   - สร้าง Connection แล้วรันสคริปต์ `database/schema_mysql.sql` และ `database/seed_data_mysql.sql`
5. ในโปรเจกต์เดิมบน Railway กดปุ่ม **+ New** -> เลือก **GitHub Repo**
6. เพิ่มตัวแปรในแท็บ **Variables**:
   - `DB_TYPE` = `mysql`
   - `DATABASE_URL` = `${{MySQL.MYSQL_URL}}`
   - `SECRET_KEY` = `your_super_secret_key`
7. ไปที่แท็บ **Settings** -> **Networking** -> กด **Generate Domain** พร้อมใช้งานทันที

---

## 🧪 การรันชุดทดสอบ (Automated Unit Tests)

```bash
python -m unittest discover tests
```
ระบบจะทดสอบความถูกต้องของ Business Rules, Constraints และสิทธิ์การดาวน์โหลด (TC-01 ถึง TC-08) ครอบคลุมทั้ง SQLite และ Multi-Engine Queries

