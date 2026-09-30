# 04. ระบบบริหารจัดการสำหรับผู้ดูแลระบบ (Admin Management Functions)

เอกสารนี้อธิบายขั้นตอนการทำงานของกลุ่มฟังก์ชันหลังบ้านของผู้ดูแลระบบ (Admin Panel) ซึ่งสงวนสิทธิ์เฉพาะผู้ใช้ที่มีบทบาท `role_name = 'ADMIN'` เท่านั้น

---

## 1. `admin_panel()`
* **Route:** `/admin` (GET)
* **สิทธิ์การเข้าถึง:** แอดมินเท่านั้น (`@login_required(role="ADMIN")`)
* **วัตถุประสงค์:** หน้ารวมศูนย์ควบคุมข้อมูลหลักของระบบ แสดงตัวเลขสถิติภาพรวม และตารางจัดการข้อมูลสำคัญ

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. **คิวรีสรุปตัวเลขสถิติด่วน (Quick Stats):**
   * นับจำนวนหนังสือทั้งหมด: `SELECT COUNT(*) FROM ebooks`
   * นับจำนวนคำสั่งซื้อทั้งหมด: `SELECT COUNT(*) FROM orders`
   * นับคำสั่งซื้อที่รอการตรวจสอบ: `SELECT COUNT(*) FROM orders WHERE order_status = 'PENDING'`
   * นับจำนวนผู้ใช้ทั้งหมด: `SELECT COUNT(*) FROM users`
2. **คิวรีรายการหนังสือทั้งหมด:** ดึงรายการ E-Book ทั้งหมดพร้อมเชื่อมโยงชื่อหมวดหมู่และชื่อผู้แต่ง
3. **คิวรีรายการหมวดหมู่:** ดึงหมวดหมู่พร้อมใช้ `COUNT(b.ebook_id)` เพื่อคำนวณจำนวนเล่มในแต่ละหมวดหมู่
4. **คิวรีรายชื่อผู้แต่ง:** ดึงข้อมูลนักเขียนทั้งหมด
5. **คิวรีคำสั่งซื้อล่าสุด (50 รายการ):** ดึงข้อมูลออเดอร์, ข้อมูลลูกค้า, ช่องทางชำระเงิน, ลิงก์รูปสลิป, สถานะสลิป
6. **คิวรีผู้ใช้งานทั้งหมด:** ดึงรายชื่อผู้ใช้, สิทธิ์ปัจจุบัน (`role_name`), และนับจำนวนออเดอร์สะสมของผู้ใช้แต่ละคนด้วย `LEFT JOIN orders` และ `GROUP BY`
7. ปิดการเชื่อมต่อ และส่งข้อมูลทั้งหมดไปเรนเดอร์ในหน้าเทมเพลต `admin.html`

---

## 2. `admin_create_ebook()`
* **Route:** `/admin/ebook/create` (POST)
* **สิทธิ์การเข้าถึง:** แอดมินเท่านั้น (`@login_required(role="ADMIN")`)
* **วัตถุประสงค์:** เพิ่มหนังสือ E-Book เล่มใหม่เข้าสู่แคตตาล็อกร้านค้า

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. ดึงข้อมูลจากฟอร์ม: `title`, `category_id`, `author_id`, `price`, `description`, `cover_image_url`, `file_download_url`, `is_active`
2. **ตรวจสอบ Data Constraints:**
   * ตรวจสอบว่ากรอกข้อมูลจำเป็นครบหรือไม่
   * **ตรวจสอบเงื่อนไขราคาไม่ติดลบ:**
     ```python
     price = float(price_str)
     if price < 0:
         flash("ราคาหนังสือต้องไม่ติดลบ (Constraint: price >= 0)")
         return redirect(...)
     ```
3. บันทึกข้อมูลลงในตาราง `ebooks`:
   ```sql
   INSERT INTO ebooks (category_id, author_id, title, description, price, cover_image_url, file_download_url, is_active)
   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
   ```
4. Commit การเปลี่ยนแปลง แจ้งเตือนข้อความสำเร็จ และ Redirect กลับหน้ารวมแอดมิน

---

## 3. `admin_toggle_ebook(ebook_id)`
* **Route:** `/admin/ebook/toggle/<int:ebook_id>` (POST)
* **สิทธิ์การเข้าถึง:** แอดมินเท่านั้น (`@login_required(role="ADMIN")`)
* **วัตถุประสงค์:** สลับสถานะเปิดขาย/ปิดการขายของหนังสือเล่มนั้นทันที โดยไม่ต้องลบข้อมูลออกจากระบบ

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. รับ `ebook_id` จาก URL Parameter
2. ดึงสถานะปัจจุบันของหนังสือ:
   ```sql
   SELECT is_active FROM ebooks WHERE ebook_id = ?
   ```
3. ตรวจสอบสถานะเดิม:
   * ถ้าเดิมเป็นเปิดขาย (`is_active = 1`) -> เปลี่ยนเป็นปิดการขาย (`0`)
   * ถ้าเดิมเป็นปิดขาย (`is_active = 0`) -> เปลี่ยนเป็นเปิดขาย (`1`)
4. อัปเดตข้อมูลด้วย Prepared Statement:
   ```sql
   UPDATE ebooks SET is_active = ? WHERE ebook_id = ?
   ```
5. บันทึกผลด้วย `conn.commit()` และรีเฟรชกลับหน้าแอดมิน

---

## 4. `admin_create_category()`
* **Route:** `/admin/category/create` (POST)
* **สิทธิ์การเข้าถึง:** แอดมินเท่านั้น (`@login_required(role="ADMIN")`)
* **วัตถุประสงค์:** เพิ่มหมวดหมู่หนังสือเล่มใหม่

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. รับชื่อหมวดหมู่ `name` และคำอธิบาย `description` จากฟอร์ม
2. ตรวจสอบว่าชื่อหมวดหมู่ไม่เป็นค่าว่าง
3. บันทึกลงตาราง `categories`:
   ```sql
   INSERT INTO categories (name, description) VALUES (?, ?)
   ```
4. จัดการ Exception ในกรณีที่มีการตั้งชื่อหมวดหมู่ซ้ำ (หากมี Unique constraint)
5. แจ้งเตือนผลลัพธ์และ Redirect กลับหน้าเดิม

---

## 5. `admin_update_order_status(order_id)`
* **Route:** `/admin/order/update-status/<int:order_id>` (POST)
* **สิทธิ์การเข้าถึง:** แอดมินเท่านั้น (`@login_required(role="ADMIN")`)
* **วัตถุประสงค์:** ตรวจสอบสลิปและปรับปรุงสถานะคำสั่งซื้อ พร้อมอัปเดตสถานะการชำระเงินให้สอดคล้องกัน

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. รับ `order_id` และค่า `status` ใหม่จากฟอร์ม (`CONFIRMED`, `CANCELLED`, `PENDING`)
2. กำหนดสถานะการชำระเงิน (`payment_status`) ให้สอดคล้องกันตามตรรกะทางธุรกิจ:
   * ถ้า `status == 'CONFIRMED'` -> `payment_status = 'APPROVED'`
   * ถ้า `status == 'CANCELLED'` -> `payment_status = 'REJECTED'`
   * ถ้า `status == 'PENDING'` -> `payment_status = 'WAITING_VERIFICATION'`
3. ทำการอัปเดต 2 ตารางพร้อมกัน:
   ```sql
   UPDATE orders SET order_status = ? WHERE order_id = ?;
   UPDATE payments SET payment_status = ? WHERE order_id = ?;
   ```
4. Commit การเปลี่ยนแปลง และแจ้งเตือนแอดมินทางหน้าจอ

---

## 6. `admin_toggle_user_role(user_id)`
* **Route:** `/admin/user/toggle-role/<int:user_id>` (POST)
* **สิทธิ์การเข้าถึง:** แอดมินเท่านั้น (`@login_required(role="ADMIN")`)
* **วัตถุประสงค์:** เปลี่ยนสิทธิ์ผู้ใช้งานระหว่างแอดมิน (`ADMIN`: role_id=1) กับลูกค้าทั่วไป (`CUSTOMER`: role_id=2)

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. รับ `user_id` ของผู้ใช้ที่ต้องการเปลี่ยนสิทธิ์
2. **ระบบความปลอดภัยป้องกันตนเอง (Self-Demotion Guard):**
   * ตรวจสอบว่า `user_id == session["user_id"]` หรือไม่
   * หากใช่: ปฏิเสธการทำงานทันที `"ไม่สามารถเปลี่ยนสิทธิ์ของบัญชีแอดมินที่กำลังใช้งานอยู่ได้"` เพื่อป้องกันกรณีแอดมินเผลอปลดสิทธิ์ตนเองจนไม่สามารถเข้าหลังบ้านได้
3. ดึง `role_id` ปัจจุบันของผู้ใช้เป้าหมาย:
   * ถ้าปัจจุบันเป็น Customer (`2`) -> เปลี่ยนเป็น Admin (`1`)
   * ถ้าปัจจุบันเป็น Admin (`1`) -> เปลี่ยนเป็น Customer (`2`)
4. อัปเดตข้อมูลลงตาราง `users`:
   ```sql
   UPDATE users SET role_id = ? WHERE user_id = ?
   ```
5. บันทึกและรีเฟรชหน้าจอแอดมิน
