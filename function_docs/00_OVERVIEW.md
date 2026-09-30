# 00. สรุปภาพรวมและผังความสัมพันธ์ของฟังก์ชันทั้งหมด (System Overview)

เอกสารนี้รวบรวมฟังก์ชันทั้งหมดในระบบ E-Book Store โดยจำแนกตามกลุ่มงาน เส้นทาง URL (Routes), HTTP Methods, สิทธิ์การเข้าถึง (RBAC), และตารางฐานข้อมูลที่เกี่ยวข้อง

---

### 📋 ตารางสรุปฟังก์ชันทั้งหมดใน `app.py`

| ลำดับ | ฟังก์ชัน | Method | URL / Route | สิทธิ์เข้าถึง | หน้าที่โดยสังเขป | ตารางที่เกี่ยวข้อง |
|:---:|:---|:---:|:---|:---:|:---|:---|
| **1** | `inject_global_data()` | - | *Context Processor* | ทุกคน | ส่งข้อมูล User ปัจจุบัน, จำนวนของในตะกร้า, บัญชี Demo ไปให้ทุกหน้า Template | `users`, `roles`, `carts`, `cart_items` |
| **2** | `login_required(role)` | - | *Custom Decorator* | - | ป้องกันการเข้าถึงหน้าเว็บ ตรวจสอบการ Login และ Role ของผู้ใช้ | `users`, `roles` |
| **3** | `demo_switch(user_id)` | GET | `/demo/switch/<id>` | ทุกคน | สลับบัญชีจำลองใน Session ทันทีเพื่อความสะดวกในการสาธิต | `users`, `roles` |
| **4** | `register()` | GET, POST | `/register` | ผู้เยี่ยมชม | สมัครสมาชิกใหม่ ตรวจสอบ Email ซ้ำ แฮชรหัสผ่าน และสร้างตะกร้าเริ่มต้น | `users`, `carts` |
| **5** | `login()` | GET, POST | `/login` | ผู้เยี่ยมชม | ตรวจสอบรหัสผ่านที่แฮชไว้ และสร้าง Session เก็บข้อมูล User | `users`, `roles` |
| **6** | `logout()` | GET | `/logout` | สมาชิก | ล้างค่า Session ทั้งหมดและส่งกลับหน้าแรก | - |
| **7** | `index()` | GET | `/` | ทุกคน | หน้าแรก แสดงรายการ E-Book ค้นหาชื่อ/คำอธิบาย และกรองตามหมวดหมู่ | `ebooks`, `categories`, `authors` |
| **8** | `ebook_detail(ebook_id)` | GET | `/ebook/<id>` | ทุกคน | แสดงรายละเอียดของหนังสือเล่มที่เลือก พร้อมประวัติผู้แต่ง | `ebooks`, `categories`, `authors` |
| **9** | `view_cart()` | GET | `/cart` | สมาชิก | ดูรายการหนังสือในตะกร้าของตนเองและคำนวณยอดรวม | `carts`, `cart_items`, `ebooks`, `authors`, `categories` |
| **10** | `add_to_cart(ebook_id)` | POST | `/cart/add/<id>` | สมาชิก | เพิ่มหนังสือลงตะกร้า ป้องกันการเพิ่มซ้ำ (E-Book จำกัด 1 เล่ม/คำสั่งซื้อ) | `carts`, `cart_items` |
| **11** | `remove_from_cart(item_id)` | POST | `/cart/remove/<id>` | สมาชิก | นำหนังสือออกจากตะกร้า โดยตรวจว่าไอเทมต้องเป็นของตะกร้าตนเอง | `cart_items`, `carts` |
| **12** | `checkout()` | GET, POST | `/checkout` | สมาชิก | สั่งซื้อสินค้า ภายใต้ **ACID Transaction** (สร้าง Order, OrderItems, Payment, เคลียร์ Cart) | `orders`, `order_items`, `payments`, `cart_items`, `carts` |
| **13** | `order_history()` | GET | `/orders` | สมาชิก | ดูประวัติคำสั่งซื้อ สถานะการจ่ายเงิน และรายการหนังสือในแต่ละออเดอร์ | `orders`, `payments`, `order_items`, `ebooks`, `authors` |
| **14** | `download_ebook(order_id, ebook_id)` | GET | `/download/<order_id>/<ebook_id>` | สมาชิก/แอดมิน | **Download Guardrail:** ตรวจสอบสิทธิ์ว่าต้องเป็นเจ้าของออเดอร์ และออเดอร์ต้องมีสถานะ `CONFIRMED` | `orders`, `order_items`, `ebooks`, `users`, `roles` |
| **15** | `download_ebook_by_catalog(ebook_id)` | GET | `/download/ebook/<id>` | สมาชิก/แอดมิน | ตรวจสอบว่าผู้ใช้เคยมีคำสั่งซื้อที่ `CONFIRMED` ของหนังสือเล่มนี้หรือไม่ ก่อนดาวน์โหลด | `orders`, `order_items`, `ebooks`, `users`, `roles` |
| **16** | `admin_panel()` | GET | `/admin` | แอดมิน (ADMIN) | หน้ารวมสำหรับแอดมิน แสดงสถิติรวม และตารางจัดการหนังสือ/หมวดหมู่/ออเดอร์/ผู้ใช้ | `ebooks`, `categories`, `authors`, `orders`, `payments`, `users`, `roles` |
| **17** | `admin_create_ebook()` | POST | `/admin/ebook/create` | แอดมิน (ADMIN) | เพิ่มหนังสือเล่มใหม่ ตรวจสอบราคาห้ามติดลบ (`CHECK (price >= 0)`) | `ebooks` |
| **18** | `admin_toggle_ebook(ebook_id)` | POST | `/admin/ebook/toggle/<id>` | แอดมิน (ADMIN) | สลับสถานะเปิด/ปิดการขายของหนังสือ (`is_active` 1 <-> 0) | `ebooks` |
| **19** | `admin_create_category()` | POST | `/admin/category/create` | แอดมิน (ADMIN) | เพิ่มหมวดหมู่หนังสือใหม่ | `categories` |
| **20** | `admin_update_order_status(order_id)` | POST | `/admin/order/update-status/<id>` | แอดมิน (ADMIN) | อัปเดตสถานะออเดอร์ (`CONFIRMED`, `CANCELLED`) และสถานะการชำระเงินพร้อมกัน | `orders`, `payments` |
| **21** | `admin_toggle_user_role(user_id)` | POST | `/admin/user/toggle-role/<id>` | แอดมิน (ADMIN) | สลับสิทธิ์ผู้ใช้ระหว่าง ADMIN และ CUSTOMER (ห้ามเปลี่ยนตนเอง) | `users` |
| **22** | `analytics_dashboard()` | GET | `/analytics` | แอดมิน (ADMIN) | รายงานเชิงวิเคราะห์ 4 รูปแบบผ่าน SQL ขั้นสูง (ยอดขายตามเดือน, หนังสือขายดี, แยกตามหมวดหมู่, CLV) | `orders`, `order_items`, `ebooks`, `categories`, `users`, `authors` |
| **23** | `database_explorer()` | GET | `/database-explorer` | ทุกคน | แสดงโครงสร้างตาราง, Data Dictionary, คอลัมน์, Foreign Keys, และจำนวนเรคอร์ด | `information_schema` / `sqlite_master` / `PRAGMA` |
| **24** | `api_query_runner()` | POST | `/api/query-runner` | ทุกคน | API รันคำสั่ง SQL สดผ่านหน้าเว็บ โดยมี Guardrail อนุญาตเฉพาะ `SELECT` และ `EXPLAIN` | ทุกตาราง (Read-Only) |
| **25** | `server_error(e)` | - | *Error Handler (500)* | ทุกคน | แสดงหน้า Error พร้อมคำแนะนำการตั้งค่า Database และ Log Traceback | - |

---

### 📋 ตารางสรุปฟังก์ชันใน `database/db.py` (Database Layer)

| ฟังก์ชัน | หน้าที่โดยสังเขป |
|:---|:---|
| `get_database_engine()` | ตรวจสอบตัวแปร Environment เพื่อระบุว่าต้องเชื่อมต่อกับ `postgres`, `mysql`, หรือ `sqlite` |
| `is_postgres_configured()` | คืนค่า True หากกำลังใช้งาน PostgreSQL / Supabase |
| `is_mysql_configured()` | คืนค่า True หากกำลังใช้งาน Cloud MySQL |
| `_get_postgres_connection()` | จัดการเชื่อมต่อ PostgreSQL ผ่าน `psycopg2` รองรับ Pooler และ SSL |
| `_get_mysql_connection()` | จัดการเชื่อมต่อ MySQL ผ่าน `pymysql` รองรับ UTF8MB4 และ DictCursor |
| `get_db_connection()` | Factory Function คืนค่า Connection Object ที่พร้อมใช้งาน |
| `init_db(force_recreate)` | รันสคริปต์ SQL เพื่อสร้าง Schema ตารางเริ่มต้นตามฐานข้อมูลที่เลือก |
| `query_db(query, args, one)` | ฟังก์ชันช่วยเหลือสำหรับ Query ดึงข้อมูลพร้อมปิด Cursor อัตโนมัติ |
| `execute_db(query, args)` | ฟังก์ชันช่วยเหลือสำหรับ Insert/Update/Delete พร้อม Commit ข้อมูล |
| `get_schema_overview(conn)` | ดึง Metadata ของทุกตารางในฐานข้อมูล (Cross-Platform) เพื่อแสดงในหน้า Data Dictionary |
