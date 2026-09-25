# 📚 E-Book Store Database Management Platform (2026)

ระบบร้านค้าและบริหารจัดการฐานข้อมูล E-Book จำลองเพื่อการศึกษา ออกแบบโครงสร้างฐานข้อมูลเชิงสัมพันธ์ในรูปแบบ **3NF (Third Normal Form)**, มีระบบความปลอดภัยของข้อมูล (Security Guardrails), ระบบตะกร้า/คำสั่งซื้อ/จำลองการชำระเงิน, และระบบรายงานเชิงวิเคราะห์ (Analytics Dashboard) ผ่าน SQL Queries ขั้นสูง

---

## 🌟 ฟีเจอร์หลักของระบบ (Core Features)

1. **ระบบลูกค้า (Customer Workflow):**
   - สมัครสมาชิก / เข้าสู่ระบบ พร้อมระบบแฮชรหัสผ่านที่ปลอดภัย
   - ค้นหาหนังสือ กรองตามหมวดหมู่ ดูรายละเอียดหนังสือและผู้แต่ง
   - ตะกร้าสินค้า และระบบสั่งซื้อ (Checkout) ทำงานภายใต้ **Database Transaction**
   - **Download Guardrail (Security Rule):** สามารถดาวน์โหลดไฟล์หนังสือได้ต่อเมื่อคำสั่งซื้อได้รับการอนุมัติ (`order_status = 'CONFIRMED'`) และเป็นเจ้าของออเดอร์เท่านั้น

2. **ระบบผู้ดูแลระบบ (Admin Workflow):**
   - จัดการหนังสือ: เพิ่มหนังสือ, เปิด/ปิดการขาย (Toggle Active)
   - จัดการหมวดหมู่หนังสือ
   - ตรวจสอบคำสั่งซื้อและสลิปการโอนเงิน (อนุมัติ / ปฏิเสธ)
   - จัดการบทบาทผู้ใช้งาน (Admin / Customer)
   - **Demo Switcher:** แถบสลับผู้ใช้งานจำลองด้านบนเพื่อความสะดวกในการนำเสนอ

3. **ระบบรายงานเชิงวิเคราะห์ (4 Analytical SQL Reports):**
   - **รายงานที่ 1:** ยอดขายตามช่วงเวลารายเดือน (Sales by Time Period)
   - **รายงานที่ 2:** 5 อันดับหนังสือขายดี (Top-Selling E-Books)
   - **รายงานที่ 3:** ยอดขายแยกตามหมวดหมู่ (Sales by Category)
   - **รายงานที่ 4:** การจัดกลุ่มพฤติกรรมลูกค้าและยอดใช้จ่ายสะสม (Customer Lifetime Value)

4. **ระบบสำรวจฐานข้อมูล (Database Explorer & SQL Runner):**
   - ตรวจสอบ Schema, Data Dictionary, คอลัมน์, Foreign Keys และจำนวนแถวแบบ Real-time
   - Interactive SQL Runner สำหรับพิมพ์คำสั่ง `SELECT` เพื่อทดสอบผลลัพธ์ผ่านหน้าเว็บ

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

## 💻 วิธีการรันในเครื่อง Local (SQLite)

```bash
# 1. ติดตั้ง Dependencies
pip install -r requirements.txt

# 2. รันแอปพลิเคชัน
python app.py
```
เปิดเว็บเบราว์เซอร์ไปที่: `http://localhost:5000`

---

## 🚀 วิธีนำขึ้น Web & เชื่อมต่อ Database ภายนอก (Railway.app)

[Railway.app](https://railway.app) เป็นแพลตฟอร์มที่แนะนำที่สุดเพราะสามารถสร้างทั้ง **เว็บ Flask** และ **Cloud MySQL** ได้ในโปรเจกต์เดียวกัน:

### ขั้นตอนที่ 1: สร้าง Cloud Database บน Railway
1. สมัคร/ล็อกอิน [Railway.app](https://railway.app) ด้วยบัญชี **GitHub**
2. กด **New Project** -> เลือก **Provision MySQL**
3. ไปที่ Service MySQL -> คลิกแท็บ **Connect** -> เปิด **Public Networking**
4. คุณจะได้รับข้อมูลเชื่อมต่อ:
   - `Host`, `Port`, `Username`, `Password`, `Database`
5. เปิดโปรแกรมจัดการฐานข้อมูลภายนอก เช่น **DBeaver** หรือ **MySQL Workbench**:
   - สร้าง New Connection (MySQL) แล้วกรอก Host, Port, User, Password จาก Railway
   - รันสคริปต์ `database/schema_mysql.sql` และ `database/seed_data_mysql.sql`
   - ตอนนี้คุณสามารถแก้ไข เพิ่ม ลบ ข้อมูลในตารางได้โดยตรงจากคอมพิวเตอร์ของคุณ!

### ขั้นตอนที่ 2: นำโค้ดขึ้น GitHub
```bash
# เริ่มต้น git และบันทึก commit
git init
git add .
git commit -m "Deploy E-Book Store Mini Project"
git branch -M main

# ผูกกับ Repository ของคุณบน GitHub
git remote add origin https://github.com/YOUR_USERNAME/miniproject-database.git
git push -u origin main
```

### ขั้นตอนที่ 3: Deploy เว็บขึ้น Railway
1. ในโปรเจกต์เดิมบน Railway กดปุ่ม **+ New** -> เลือก **GitHub Repo**
2. เลือก Repository `miniproject-database`
3. ไปที่แท็บ **Variables** ใน Service ของเว็บ แล้วเพิ่มตัวแปร:
   - `DB_TYPE` = `mysql`
   - `DATABASE_URL` = `${{MySQL.MYSQL_URL}}` *(หรือก๊อปปี้ค่า Connection URL จาก Service MySQL)*
   - `SECRET_KEY` = `your_super_secret_key`
4. ไปที่แท็บ **Settings** -> หัวข้อ **Networking** -> กด **Generate Domain**
5. รอ Deploy เสร็จ เข้าใช้งานผ่านลิงก์โดเมนที่ได้ทันที!

---

## 🧪 การรันชุดทดสอบ (Automated Unit Tests)

```bash
python -m unittest discover tests
```
ระบบจะทดสอบความถูกต้องของสิทธิ์และการจัดการข้อมูล (TC-01 ถึง TC-08)
