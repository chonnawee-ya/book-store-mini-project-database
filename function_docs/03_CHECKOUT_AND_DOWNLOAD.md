# 03. การสั่งซื้อ, ธุรกรรมฐานข้อมูล และการดาวน์โหลด (Checkout, Transaction & Security Guardrail)

เอกสารนี้อธิบายหัวใจสำคัญของระบบการค้า นั่นคือกระบวนการ **Database Transaction (ACID)** ในขณะสั่งซื้อสินค้า และ **Security Guardrail** ในการตรวจสอบสิทธิ์ก่อนอนุญาตให้ดาวน์โหลดไฟล์ E-Book

---

## 1. `checkout()`
* **Route:** `/checkout` (GET, POST)
* **สิทธิ์การเข้าถึง:** สมาชิกที่ล็อกอินแล้ว (`@login_required()`)
* **วัตถุประสงค์:** ทำการสั่งซื้อสินค้าจากตะกร้า โดยทำงานภายใต้ **Database Transaction** เดียวกัน หากขั้นตอนใดล้มเหลว จะถูกยกเลิกทั้งหมด (`ROLLBACK`) เพื่อรักษาความถูกต้องของข้อมูล

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):

#### กรณีคำขอ GET (เปิดดูหน้าสรุปคำสั่งซื้อ):
1. ดึงรายการสินค้าทั้งหมดในตะกร้าของผู้ใช้ปัจจุบัน
2. หากไม่มีสินค้าในตะกร้า จะส่งกลับหน้าแรกพร้อมแจ้งเตือน
3. คำนวณยอดเงินรวม และเรนเดอร์หน้า `checkout.html` เพื่อให้เลือกช่องทางชำระเงินและใส่ลิงก์สลิป

#### กรณีคำขอ POST (กดยืนยันการสั่งซื้อ):
1. รับข้อมูลจากฟอร์ม: `payment_method` และ `slip_url` (หากไม่ได้ระบุจะใช้รูปจำลองอัตโนมัติ)
2. **เริ่มต้น Database Transaction (Atomic Unit of Work):**
   * **สเต็ป 1: สร้างคำสั่งซื้อหลัก (INSERT INTO `orders`)**
     บันทึก `user_id`, `total_amount`, และกำหนด `order_status = 'PENDING'`
     ```sql
     INSERT INTO orders (user_id, total_amount, order_status)
     VALUES (?, ?, 'PENDING')
     ```
     ดึงรหัส `new_order_id` ที่เพิ่งถูกสร้าง
   * **สเต็ป 2: บันทึกรายการสินค้าในคำสั่งซื้อ (INSERT INTO `order_items`)**
     วนลูปรายการสินค้าในตะกร้า เพื่อบันทึกราคา ณ วันที่สั่งซื้อจริง (`unit_price` Snapshot):
     ```sql
     INSERT INTO order_items (order_id, ebook_id, unit_price)
     VALUES (?, ?, ?)
     ```
     *(เหตุผลทาง 3NF: ต้องบันทึกราคาจริง ณ เวลาสั่งซื้อ เพื่อไม่ให้ยอดในอดีตเปลี่ยนหากแอดมินปรับราคาหนังสือในอนาคต)*
   * **สเต็ป 3: สร้างบันทึกการชำระเงิน (INSERT INTO `payments`)**
     บันทึกข้อมูลการชำระเงิน โดยกำหนดสถานะเริ่มต้นเป็น `'WAITING_VERIFICATION'`
     ```sql
     INSERT INTO payments (order_id, payment_method, slip_url, paid_amount, payment_status)
     VALUES (?, ?, ?, ?, 'WAITING_VERIFICATION')
     ```
   * **สเต็ป 4: ล้างสินค้าออกจากตะกร้า (DELETE FROM `cart_items`)**
     ล้างเฉพาะสินค้าในตะกร้าของผู้ใช้งานคนนี้:
     ```sql
     DELETE FROM cart_items
     WHERE cart_id IN (SELECT cart_id FROM carts WHERE user_id = ?)
     ```
3. **Commit Transaction:** เรียก `conn.commit()` เพื่อบันทึกข้อมูลทั้ง 4 สเต็ปอย่างสมบูรณ์
4. **Rollback on Error:** หากเกิด Exception ใดๆ ในระหว่างกระบวนการ ระบบจะเรียก `conn.rollback()` ทันที ทำให้ข้อมูลย้อนกลับเหมือนไม่เคยมีอะไรเกิดขึ้น
5. ปิดการเชื่อมต่อ และ Redirect ผู้ใช้ไปยังหน้าประวัติการสั่งซื้อ (`order_history`)

---

## 2. `order_history()`
* **Route:** `/orders` (GET)
* **สิทธิ์การเข้าถึง:** สมาชิกที่ล็อกอินแล้ว (`@login_required()`)
* **วัตถุประสงค์:** แสดงรายการคำสั่งซื้อทั้งหมดของผู้ใช้ พร้อมสถานะการชำระเงิน และรายการหนังสือแต่ละเล่ม

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. ดึงคำสั่งซื้อทั้งหมดที่เป็นของ `session["user_id"]` พร้อมเชื่อมตารางการชำระเงิน (`payments`):
   ```sql
   SELECT o.*, p.payment_method, p.slip_url, p.payment_status
   FROM orders o
   LEFT JOIN payments p ON o.order_id = p.order_id
   WHERE o.user_id = ?
   ORDER BY o.created_at DESC
   ```
2. สำหรับแต่ละคำสั่งซื้อ ให้คิวรีดึงรายการหนังสือในออเดอร์นั้น (`order_items` JOIN `ebooks` JOIN `authors`):
   ```sql
   SELECT oi.*, b.title, b.cover_image_url, a.name AS author_name
   FROM order_items oi
   JOIN ebooks b ON oi.ebook_id = b.ebook_id
   JOIN authors a ON b.author_id = a.author_id
   WHERE oi.order_id = ?
   ```
3. จัดโครงสร้างข้อมูลให้ออเดอร์มีอาเรย์ของ `items` อยู่ภายใน
4. เรนเดอร์หน้า `orders.html` โดยมีปุ่มดาวน์โหลดที่จะแสดงผลตามสถานะของออเดอร์

---

## 3. `download_ebook(order_id, ebook_id)`
* **Route:** `/download/<int:order_id>/<int:ebook_id>` (GET)
* **สิทธิ์การเข้าถึง:** เจ้าของออเดอร์ หรือ แอดมิน
* **วัตถุประสงค์:** ดาวน์โหลดไฟล์ E-Book ภายใต้ **กฎความปลอดภัยสูงสุด (Security Guardrail)**

### 🛡️ กฎความปลอดภัย 4 ขั้นตอน (Security Guardrail Steps):
ฟังก์ชันนี้ทำหน้าที่ป้องกันการละเมิดลิขสิทธิ์และการดาวน์โหลดโดยมิชอบ:

1. **ตรวจสอบความมีอยู่ของคำสั่งซื้อ:**
   คิวรีหาออเดอร์จาก `orders WHERE order_id = ?` หากไม่พบจะส่ง HTTP `404 Not Found`
2. **ตรวจสอบสิทธิ์การเป็นเจ้าของ (Authorization Check):**
   ตรวจสอบว่าผู้ใช้ที่กำลังล็อกอินอยู่ เป็นเจ้าของออเดอร์นั้นหรือไม่ (`order["user_id"] == session["user_id"]`) ยกเว้นในกรณีที่เป็นผู้ใช้บทบาท `ADMIN`
   * หากไม่ใช่: ปฏิเสธทันทีด้วย HTTP `403 Forbidden`
3. **ตรวจสอบสถานะการอนุมัติคำสั่งซื้อ (Order Status Check):**
   ตรวจสอบว่าคำสั่งซื้อได้รับการอนุมัติแล้วหรือยัง:
   ```python
   if order["order_status"] != "CONFIRMED":
       flash("ปฏิเสธการดาวน์โหลด: คำสั่งซื้อยังไม่ได้รับการอนุมัติ")
       return redirect(url_for("order_history"))
   ```
   *(หากสถานะเป็น `PENDING` หรือ `CANCELLED` จะไม่สามารถดาวน์โหลดไฟล์ได้)*
4. **ตรวจสอบว่าหนังสือนั้นอยู่ในคำสั่งซื้อจริง:**
   คิวรีตรวจในตาราง `order_items` ว่ามี `ebook_id` นั้นจริงใน `order_id` นี้
5. **การส่งมอบไฟล์ดิจิทัล (Digital Delivery):**
   ระบบจะสร้างไฟล์เอกสารยืนยันสิทธิ์ดิจิทัลเฉพาะบุคคล (Personalized Digital E-Book License) แบบ Real-time ที่ระบุชื่อผู้ซื้อ, รหัสคำสั่งซื้อ, วันเวลา และส่งกลับผ่าน `send_file()` ในรูปแบบไฟล์แนบดาวน์โหลด

---

## 4. `download_ebook_by_catalog(ebook_id)`
* **Route:** `/download/ebook/<int:ebook_id>` (GET)
* **สิทธิ์การเข้าถึง:** สมาชิกที่ล็อกอินแล้ว
* **วัตถุประสงค์:** ป้องกันกรณีผู้ใช้นำ URL ลิงก์ตรงจากหน้าร้านไปกดดาวน์โหลดโดยไม่ผ่านหน้าประวัติการสั่งซื้อ

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. ตรวจสอบว่าผู้ใช้มีบทบาท `ADMIN` หรือไม่ หากเป็นแอดมินจะอนุญาตให้ดาวน์โหลดไฟล์ตัวอย่างพรีวิวได้
2. สำหรับลูกค้าทั่วไป: ระบบจะค้นหาในฐานข้อมูลว่า ผู้ใช้คนนี้เคยมีคำสั่งซื้อหนังสือเล่มนี้ที่ได้รับการอนุมัติ (`CONFIRMED`) หรือไม่:
   ```sql
   SELECT o.order_id, b.title
   FROM orders o
   JOIN order_items oi ON o.order_id = oi.order_id
   JOIN ebooks b ON oi.ebook_id = b.ebook_id
   WHERE o.user_id = ? AND oi.ebook_id = ? AND o.order_status = 'CONFIRMED'
   LIMIT 1
   ```
3. หากพบคำสั่งซื้อที่อนุมัติแล้ว จะส่งต่อไปทำงานที่ฟังก์ชัน `download_ebook(order_id, ebook_id)`
4. หากไม่พบคำสั่งซื้อที่อนุมัติ จะแจ้งเตือนและปฏิเสธการดาวน์โหลดทันที
