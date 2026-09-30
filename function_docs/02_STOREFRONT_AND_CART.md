# 02. ระบบหน้าร้าน, แคตตาล็อก และตะกร้าสินค้า (Storefront & Cart)

เอกสารนี้อธิบายขั้นตอนการทำงานของกลุ่มฟังก์ชันฝั่งลูกค้า ได้แก่ การค้นหาหนังสือ การกรองตามหมวดหมู่ การดูรายละเอียด และการจัดการตะกร้าสินค้า

---

## 1. `index()`
* **Route:** `/` (GET)
* **สิทธิ์การเข้าถึง:** ทุกคน (Public Access)
* **พารามิเตอร์ Query String:** `q` (คำค้นหา), `category` (รหัสหมวดหมู่)
* **วัตถุประสงค์:** แสดงหน้าแรกของร้านค้า พร้อมระบบค้นหาและกรองหนังสือที่เปิดขายอยู่

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. ดึงพารามิเตอร์ `q` (Search keyword) และ `category` จาก `request.args`
2. ดึงหมวดหมู่ทั้งหมดจากตาราง `categories` เพื่อนำไปแสดงเป็นปุ่มหรือตัวเลือกกรอง:
   ```sql
   SELECT * FROM categories ORDER BY name ASC
   ```
3. กำหนดโครงสร้างคำสั่ง SQL เริ่มต้น (เฉพาะหนังสือที่เปิดขาย `is_active = 1`):
   ```sql
   SELECT b.*, c.name AS category_name, a.name AS author_name
   FROM ebooks b
   JOIN categories c ON b.category_id = c.category_id
   JOIN authors a ON b.author_id = a.author_id
   WHERE b.is_active = 1
   ```
4. ตรวจสอบเงื่อนไขการค้นหา:
   * **หากมีคำค้นหา `search_q`:** ต่อเงื่อนไข `AND (b.title LIKE ? OR b.description LIKE ? OR a.name LIKE ?)` และเพิ่มพารามิเตอร์ค้นหาเข้าไป
   * **หากมีการเลือกหมวดหมู่ `category_id`:** ต่อเงื่อนไข `AND b.category_id = ?`
5. จัดเรียงลำดับจากหนังสือใหม่ไปเก่า (`ORDER BY b.ebook_id DESC`)
6. รันคำสั่ง SQL ผ่าน Prepared Statement
7. ปิดการเชื่อมต่อ และส่งข้อมูลไปยังเทมเพลต `index.html`

---

## 2. `ebook_detail(ebook_id)`
* **Route:** `/ebook/<int:ebook_id>` (GET)
* **สิทธิ์การเข้าถึง:** ทุกคน (Public Access)
* **วัตถุประสงค์:** แสดงรายละเอียดของหนังสืออย่างครบถ้วน รวมถึงข้อมูลและประวัติผู้แต่ง

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. รับรหัส `ebook_id` จาก URL
2. คิวรีข้อมูลหนังสือเล่มนั้น ร่วมกับตารางหมวดหมู่และตารางผู้แต่ง:
   ```sql
   SELECT b.*, c.name AS category_name, a.name AS author_name, a.biography AS author_bio
   FROM ebooks b
   JOIN categories c ON b.category_id = c.category_id
   JOIN authors a ON b.author_id = a.author_id
   WHERE b.ebook_id = ?
   ```
3. หากไม่พบหนังสือในฐานข้อมูล: ส่ง Flash message เตือนและ Redirect กลับหน้าแรก
4. หากพบหนังสือ: ส่งข้อมูลหนังสือและผู้แต่งไปยังเทมเพลต `ebook_detail.html`

---

## 3. `view_cart()`
* **Route:** `/cart` (GET)
* **สิทธิ์การเข้าถึง:** สมาชิกที่ล็อกอินแล้ว (`@login_required()`)
* **วัตถุประสงค์:** แสดงรายการหนังสือที่อยู่ในตะกร้าปัจจุบันของผู้ใช้งาน พร้อมคำนวณยอดเงินรวม

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. ตรวจสอบ `user_id` จาก Session
2. คิวรีดึงรายการสินค้าในตะกร้าของผู้ใช้คนนั้น:
   ```sql
   SELECT ci.cart_item_id, ci.quantity, b.ebook_id, b.title, b.price, b.cover_image_url,
          a.name AS author_name, c.name AS category_name
   FROM carts ca
   JOIN cart_items ci ON ca.cart_id = ci.cart_id
   JOIN ebooks b ON ci.ebook_id = b.ebook_id
   JOIN authors a ON b.author_id = a.author_id
   JOIN categories c ON b.category_id = c.category_id
   WHERE ca.user_id = ?
   ORDER BY ci.created_at DESC
   ```
3. คำนวณผลรวมราคาสินค้าทั้งหมด: `total_amount = sum(item["price"] for item in cart_items)`
4. เรนเดอร์หน้า `cart.html` พร้อมส่งรายการสินค้าและยอดเงินรวมไปแสดงผล

---

## 4. `add_to_cart(ebook_id)`
* **Route:** `/cart/add/<int:ebook_id>` (POST)
* **สิทธิ์การเข้าถึง:** สมาชิกที่ล็อกอินแล้ว (`@login_required()`)
* **วัตถุประสงค์:** เพิ่มหนังสือเล่มที่เลือกลงในตะกร้า โดยมีเงื่อนไขตรวจสอบความถูกต้อง

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. รับ `ebook_id` จาก URL Parameter
2. **ขั้นตอนที่ 1 - ตรวจสอบตะกร้าผู้ใช้:**
   * ตรวจสอบว่าผู้ใช้มีแถวในตาราง `carts` หรือไม่
   * หากยังไม่มี ให้สร้างตะกร้าใหม่ขึ้นมาโดยอัตโนมัติ: `INSERT INTO carts (user_id) VALUES (?)`
3. **ขั้นตอนที่ 2 - ตรวจสอบเงื่อนไข E-Book Rule (จำกัด 1 เล่มต่อคน/ออเดอร์):**
   * ตรวจสอบว่าในตะกร้ามีสินค้ารายการนี้อยู่แล้วหรือไม่:
     ```sql
     SELECT cart_item_id FROM cart_items WHERE cart_id = ? AND ebook_id = ?
     ```
   * หากมีอยู่แล้ว จะปฏิเสธการเพิ่มซ้ำ และแจ้งเตือนผู้ใช้ว่าหนังสืออยู่ในตะกร้าแล้ว
4. **ขั้นตอนที่ 3 - บันทึกสินค้าลงตะกร้า:**
   * ดำเนินการเพิ่มรายการด้วยคำสั่ง INSERT (กำหนด `quantity = 1` ตาม Check Constraint):
     ```sql
     INSERT INTO cart_items (cart_id, ebook_id, quantity) VALUES (?, ?, 1)
     ```
5. ทำการ `conn.commit()` และส่งผู้ใช้กลับไปยังหน้าเดิมที่กด หรือเปิดไปที่หน้าตะกร้าสินค้า

---

## 5. `remove_from_cart(cart_item_id)`
* **Route:** `/cart/remove/<int:cart_item_id>` (POST)
* **สิทธิ์การเข้าถึง:** สมาชิกที่ล็อกอินแล้ว (`@login_required()`)
* **วัตถุประสงค์:** ลบรายการหนังสือออกจากตะกร้า โดยมีระบบป้องกันการลบข้ามบัญชี

### 🔄 ขั้นตอนการทำงาน (Step-by-Step):
1. รับรหัส `cart_item_id` ที่ต้องการลบ
2. ดำเนินการลบข้อมูลด้วยเงื่อนไข Subquery ที่รัดกุม เพื่อป้องกันไม่ให้ผู้ใช้ลบรายการของคนอื่น:
   ```sql
   DELETE FROM cart_items
   WHERE cart_item_id = ? 
     AND cart_id IN (SELECT cart_id FROM carts WHERE user_id = ?)
   ```
3. บันทึกการเปลี่ยนแปลงด้วย `conn.commit()`
4. แจ้งเตือน `"นำหนังสือออกจากตะกร้าสินค้าเรียบร้อยแล้ว"` และ Redirect กลับหน้าตะกร้าสินค้า (`view_cart`)
