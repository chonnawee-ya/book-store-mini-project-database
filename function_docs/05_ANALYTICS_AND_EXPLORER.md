# 05. ระบบรายงานเชิงวิเคราะห์ และเครื่องมือสำรวจฐานข้อมูล (Analytics & Explorer)

เอกสารนี้อธิบายขั้นตอนการทำงานของกลุ่มฟังก์ชันรายงานสถิติขั้นสูง (Advanced Analytical SQL Reports), หน้าสำรวจ Data Dictionary และเครื่องมือทดสอบคำสั่ง SQL สดผ่านหน้าเว็บ

---

## 1. `analytics_dashboard()`
* **Route:** `/analytics` (GET)
* **สิทธิ์การเข้าถึง:** แอดมินเท่านั้น (`@login_required(role="ADMIN")`)
* **วัตถุประสงค์:** ประมวลผลและแสดงรายงานเชิงวิเคราะห์ธุรกิจ 4 มิติผ่านคำสั่ง SQL ขั้นสูง

### 📊 ขั้นตอนการประมวลผลคำสั่ง SQL ทั้ง 4 รายงาน:

#### สเต็ปที่ 1: ดึงตัวชี้วัดหลักทางธุรกิจ (Summary KPIs)
ใช้ Subquery และ Aggregate Functions ในการสรุปผลคำสั่งซื้อที่สำเร็จ (`CONFIRMED`):
* จำนวนออเดอร์ที่ยืนยันแล้ว
* รายได้รวมสุทธิ (`SUM(total_amount)`)
* ยอดใช้จ่ายเฉลี่ยต่อออเดอร์ (`AVG(total_amount)`)
* จำนวนเล่มที่ขายได้ทั้งหมด
* จำนวนลูกค้าทั้งหมดในระบบ

#### สเต็ปที่ 2: รายงานที่ 1 - แนวโน้มยอดขายตามช่วงเวลารายเดือน (Sales by Time Period)
ใช้คำสั่งจัดกลุ่มตามเดือน เพื่อวิเคราะห์แนวโน้มการเติบโตของรายได้:
```sql
SELECT 
    strftime('%Y-%m', o.created_at) AS sales_month,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS average_order_value
FROM orders o
WHERE o.order_status = 'CONFIRMED'
GROUP BY strftime('%Y-%m', o.created_at)
ORDER BY sales_month DESC;
```

#### สเต็ปที่ 3: รายงานที่ 2 - 5 อันดับหนังสือขายดี (Top-Selling E-Books)
เชื่อมโยง 4 ตาราง (`orders`, `order_items`, `ebooks`, `authors`) เพื่อจัดอันดับหนังสือยอดนิยม:
```sql
SELECT 
    b.ebook_id,
    b.title,
    a.name AS author_name,
    COUNT(oi.order_item_id) AS units_sold,
    ROUND(SUM(oi.unit_price), 2) AS total_sales_amount
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN ebooks b ON oi.ebook_id = b.ebook_id
JOIN authors a ON b.author_id = a.author_id
WHERE o.order_status = 'CONFIRMED'
GROUP BY b.ebook_id, b.title, a.name
ORDER BY units_sold DESC, total_sales_amount DESC
LIMIT 5;
```

#### สเต็ปที่ 4: รายงานที่ 3 - สรุปรายได้แยกตามหมวดหมู่ (Sales by Category)
ใช้ `LEFT JOIN` เพื่อให้แสดงผลทุกหมวดหมู่ แม้ว่าบางหมวดหมู่จะยังไม่มียอดขายก็ตาม:
```sql
SELECT 
    c.category_id,
    c.name AS category_name,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(oi.order_item_id) AS total_books_sold,
    COALESCE(ROUND(SUM(oi.unit_price), 2), 0.00) AS total_revenue
FROM categories c
LEFT JOIN ebooks b ON c.category_id = b.category_id
LEFT JOIN order_items oi ON b.ebook_id = oi.ebook_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'CONFIRMED'
GROUP BY c.category_id, c.name
ORDER BY total_revenue DESC;
```

#### สเต็ปที่ 5: รายงานที่ 4 - การวิเคราะห์พฤติกรรมและมูลค่าลูกค้าตลอดชีพ (Customer Lifetime Value - CLV)
ใช้ Conditional Aggregation (`SUM(CASE WHEN...)`) และคำสั่ง `HAVING` เพื่อจำแนกสถานะออเดอร์ของลูกค้าแต่ละคน:
```sql
SELECT 
    u.user_id,
    u.full_name,
    u.email,
    COUNT(o.order_id) AS total_orders_placed,
    SUM(CASE WHEN o.order_status = 'CONFIRMED' THEN 1 ELSE 0 END) AS confirmed_orders,
    SUM(CASE WHEN o.order_status = 'PENDING' THEN 1 ELSE 0 END) AS pending_orders,
    SUM(CASE WHEN o.order_status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled_orders,
    COALESCE(ROUND(SUM(CASE WHEN o.order_status = 'CONFIRMED' THEN o.total_amount ELSE 0 END), 2), 0.00) AS total_spent
FROM users u
JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.full_name, u.email
HAVING COUNT(o.order_id) >= 1
ORDER BY total_spent DESC;
```
ส่งผลลัพธ์ทั้งหมดไปยังเทมเพลต `analytics.html`

---

## 2. `database_explorer()`
* **Route:** `/database-explorer` (GET)
* **สิทธิ์การเข้าถึง:** ทุกคน
* **วัตถุประสงค์:** แสดง Data Dictionary ของระบบแบบสดๆ เพื่อใช้ในการตรวจสอบ Schema, โครงสร้างคอลัมน์, Data Types, Foreign Keys, และจำนวนข้อมูลในแต่ละตาราง

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. เรียกฟังก์ชัน `get_schema_overview(conn)` จากโมดูลฐานข้อมูล
2. ดึงรายชื่อตารางทั้งหมดในฐานข้อมูล พร้อมโครงสร้างของแต่ละฟิลด์
3. นับจำนวนเรคอร์ดของแต่ละตาราง (`row_count`)
4. ดึงข้อมูล Foreign Key Constraints เพื่อแสดงความสัมพันธ์ระหว่างตาราง
5. เรนเดอร์หน้า `db_explorer.html` แสดงผลเป็นแท็บตารางที่อ่านง่าย

---

## 3. `api_query_runner()`
* **Route:** `/api/query-runner` (POST)
* **สิทธิ์การเข้าถึง:** ทุกคน (ผ่านหน้า Database Explorer)
* **รูปแบบข้อมูล:** JSON `{ "sql": "..." }`
* **วัตถุประสงค์:** รันคำสั่ง SQL สดผ่านหน้าเว็บ พร้อมระบบความปลอดภัยป้องกันการแก้ไขข้อมูลโดยมิชอบ

### 🛡️ กฎความปลอดภัยและขั้นตอนการทำงาน:
1. รับคำสั่ง SQL จาก JSON Payload: `data.get("sql")`
2. **ระบบความปลอดภัยแบบ Read-Only Guard:**
   ```python
   upper_sql = sql.upper().strip()
   if not upper_sql.startswith("SELECT") and not upper_sql.startswith("EXPLAIN"):
       return jsonify({"success": False, "error": "อนุญาตเฉพาะคำสั่ง SELECT หรือ EXPLAIN เท่านั้นเพื่อความปลอดภัย"}), 403
   ```
   *(ป้องกันไม่ให้ผู้ใช้ส่งคำสั่ง `DROP`, `DELETE`, `UPDATE`, หรือ `INSERT` ผ่าน API สาธารณะ)*
3. รันคำสั่ง SQL ผ่าน Cursor
4. ดึงรายชื่อคอลัมน์จาก `cur.description`
5. ดึงผลลัพธ์ทั้งหมดและแปลงเป็น List of Dictionaries
6. คืนค่า JSON กลับไปยังหน้าเว็บ:
   ```json
   {
       "success": true,
       "columns": ["title", "price"],
       "data": [...],
       "row_count": 10
   }
   ```
7. หากคำสั่ง SQL มีข้อผิดพลาดทางไวยากรณ์ จะจับ Exception และส่ง Error Message กลับอย่างชัดเจน

---

## 4. `server_error(e)`
* **ประเภท:** Flask Custom Error Handler (HTTP 500)
* **วัตถุประสงค์:** แสดงหน้าจอแจ้งเตือนที่ชัดเจนและเป็นมิตรกับผู้พัฒนาเมื่อเกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูลบน Cloud
* **ขั้นตอน:** บันทึก Traceback ข้อผิดพลาดลง Terminal พร้อมแสดงหน้า HTML สรุปสาเหตุที่เป็นไปได้ เช่น ยังไม่ได้รันสคริปต์ใน Supabase หรือรหัสผ่านใน Connection String ไม่ถูกต้อง
