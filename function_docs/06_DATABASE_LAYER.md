# 06. สถาปัตยกรรมชั้นฐานข้อมูล (Database Connection & Abstraction Layer)

เอกสารนี้อธิบายการทำงานของไฟล์ [database/db.py](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/database/db.py) ซึ่งทำหน้าที่เป็น **Data Access Layer (DAL)** ทำหน้าที่เชื่อมต่อและปรับเปลี่ยนไวยากรณ์ SQL ให้รองรับฐานข้อมูล 3 ระบบ (SQLite, PostgreSQL / Supabase, MySQL) ได้อย่างไร้รอยต่อ

---

## 1. การตรวจจับฐานข้อมูลอัตโนมัติ (Engine Detection)

### `get_database_engine()`
* **วัตถุประสงค์:** อ่านค่าจาก Environment Variable ใน [.env](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/.env) เพื่อตัดสินใจว่าจะเชื่อมต่อกับ Engine ใด
* **ลำดับการตรวจสอบ:**
  1. ตรวจสอบค่า `DB_TYPE` หรือ URL ใน `DATABASE_URL`:
     * หากขึ้นต้นด้วย `postgres://` หรือ `postgresql://` -> คืนค่า `"postgres"`
     * หากขึ้นต้นด้วย `mysql://` -> คืนค่า `"mysql"`
  2. ตรวจสอบค่า Host เฉพาะ เช่น `PGHOST` (PostgreSQL) หรือ `MYSQL_HOST` (MySQL)
  3. หากไม่พบค่าใดๆ ข้างต้น -> คืนค่าดีฟอลต์เป็น `"sqlite"`

---

## 2. คลาสตัวกลางสำหรับความเข้ากันได้ข้ามระบบ (Cross-Platform Adapters)

### 2.1 `UnifiedRow`
* **เหตุผลที่มี:** ใน SQLite ปกติจะคืนผลลัพธ์ที่เข้าถึงได้ทั้งชื่อฟิลด์ `row['title']` และดัชนีตัวเลข `row[0]` แต่ใน PostgreSQL (`RealDictCursor`) และ MySQL (`DictCursor`) จะไม่รองรับดัชนีตัวเลข
* **การทำงาน:** สืบทอดจาก `dict` และโอเวอร์ไรด์เมธอด `__getitem__` ให้สามารถรองรับทั้ง `row["title"]` และ `row[0]` ได้เหมือนกัน 100% ในทุก Engine

### 2.2 `RemoteCursorWrapper`
* **วัตถุประสงค์:** ห่อหุ้ม Cursor ของฐานข้อมูลระยะไกล (Remote DB) และทำ **SQL Translation (การแปลภาษา SQL อัตโนมัติ)** ก่อนส่งไปประมวลผล:
  * **แปลง Parameter Placeholder:** แปลงเครื่องหมาย `?` ของ SQLite ให้เป็น `%s` สำหรับ PostgreSQL และ MySQL
  * **แปลงฟังก์ชันวันที่:**
    * SQLite: `strftime('%Y-%m', date_col)`
    * PostgreSQL: `TO_CHAR(date_col, 'YYYY-MM')`
    * MySQL: `DATE_FORMAT(date_col, '%Y-%m')`
  * **แปลงชนิดข้อมูล Boolean (PostgreSQL):** แปลง `is_active = 1` ให้เป็น `is_active = TRUE`
  * **จำลอง `lastrowid` ใน PostgreSQL:** เนื่องจาก PostgreSQL ไม่มีแอตทริบิวต์ `lastrowid` เหมือน SQLite/MySQL ตัว Wrapper จะดักจับคำสั่ง `INSERT INTO` แล้วเติมต่อท้ายด้วย `RETURNING <primary_key_col>` ให้อัตโนมัติ เพื่อดึง Primary Key ที่เพิ่งสร้างกลับมา

---

## 3. ฟังก์ชันการเชื่อมต่อหลัก (Connection Factory)

### `get_db_connection()`
* **การทำงาน:**
  * หากเป็น `"postgres"` -> เรียก `_get_postgres_connection()` โดยใช้ไลบรารี `psycopg2` เปิดโหมด `sslmode=require` (เหมาะสำหรับ Supabase)
  * หากเป็น `"mysql"` -> เรียก `_get_mysql_connection()` โดยใช้ไลบรารี `pymysql`
  * หากเป็น `"sqlite"` -> เรียก `sqlite3.connect(DB_PATH)` พร้อมเปิดใช้ `PRAGMA foreign_keys = ON;` เพื่อบังคับใช้ Foreign Key Constraints

---

## 4. ฟังก์ชันช่วยเหลือและคำสั่งจัดการฐานข้อมูล

### `query_db(query, args=(), one=False)`
* **วัตถุประสงค์:** ช่วยลดขั้นตอนการเขียนโค้ดซ้ำซ้อนสำหรับคำสั่ง `SELECT`
* **การทำงาน:** เปิด Connection, สร้าง Cursor, รันคำสั่งพร้อมพารามิเตอร์, ดึงผลลัพธ์ (`fetchone()` หรือ `fetchall()`), และปิด Connection ให้อัตโนมัติ

### `execute_db(query, args=())`
* **วัตถุประสงค์:** ใช้สำหรับคำสั่ง `INSERT`, `UPDATE`, `DELETE`
* **การทำงาน:** รันคำสั่ง, ทำการ `conn.commit()`, และคืนค่า `(last_id, row_count)`

### `init_db(force_recreate=False)`
* **วัตถุประสงค์:** สร้างโครงสร้างตารางเริ่มต้นจากไฟล์ SQL Schema ที่กำหนด:
  * PostgreSQL: อ่านจาก [database/schema_postgresql.sql](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/database/schema_postgresql.sql)
  * MySQL: อ่านจาก [database/schema_mysql.sql](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/database/schema_mysql.sql)
  * SQLite: อ่านจาก [database/schema.sql](file:///c:/Users/titan/OneDrive/เดสก์ท็อป/miniproject-database/database/schema.sql)

### `get_schema_overview(conn)`
* **วัตถุประสงค์:** ดึงโครงสร้าง Data Dictionary ทั้งหมดมาแสดงบนหน้าเว็บ โดยรองรับความแตกต่างของแต่ละฐานข้อมูล:
  * ใน PostgreSQL: คิวรีจาก `information_schema.tables` และ `information_schema.columns`
  * ใน SQLite: ดึงจาก `sqlite_master` และคำสั่ง `PRAGMA table_info()`
  * ใน MySQL: ดึงจาก `information_schema.COLUMNS`
* **ผลลัพธ์:** คืนค่าเป็นโครงสร้าง Dictionary ระบุชื่อตาราง, รายชื่อคอลัมน์, ชนิดข้อมูล, ค่าดีฟอลต์, และจำนวนแถวทั้งหมด
