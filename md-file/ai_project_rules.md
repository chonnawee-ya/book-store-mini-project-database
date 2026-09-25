# AI Coding Rules & Engineering Guardrails
## โครงงาน: Database Mini Project ร้านขาย E-Book (2026)

เอกสารระเบียบข้อบังคับและ Context สำหรับ AI Assistant เพื่อให้การ Generate Code, Database Migration และคำแนะนำทางเทคนิคเป็นไปตามใบงานกำหนดอย่างเคร่งครัด

---

### 1. กฎด้านขอบเขตงาน (Strict Scope Guardrails)
* **DO NOT IMPLEMENT:**
  * ห้ามสร้างระบบตัดบัตรเครดิต หรือเชื่อมต่อ Payment Gateway จริง (เช่น Stripe, Omise, PayPal) ให้ใช้ระบบจำลอง (Simulated Payment) โดยให้อัปโหลด/กรอก Mock Slip URL เท่านั้น
  * ห้ามทำระบบ DRM (Digital Rights Management) หรือ Cloud Storage ขนาดใหญ่ที่ซับซ้อนเกินความจำเป็น ให้ใช้ URL จำลอง หรือไฟล์ตัวอย่างใน Local / Public Storage เพื่อสาธิต
  * ห้ามขยายระบบไปทำ Mobile App ให้โฟกัสที่ Web Application หรือ Responsive Web Prototype ตามโจทย์
* **MUST FOCUS:**
  * โฟกัสสูงสุดที่ความถูกต้องของฐานข้อมูล (Schema, Constraints, Foreign Keys, Normalization)
  * จัดเตรียม Mock Data สำหรับคำสั่งซื้ออย่างน้อย 30 คำสั่งซื้อ ให้พร้อมสำหรับรันรายงาน

---

### 2. กฎการออกแบบฐานข้อมูล (Database Standards)
1. **Schema Design:**
   * ต้องมีตารางอย่างน้อย 8 ตาราง (โครงสร้างหลัก: `roles`, `users`, `categories`, `authors`, `ebooks`, `carts`, `cart_items`, `orders`, `order_items`, `payments`)
   * ทุกตารางต้องมี Primary Key และกำหนด Foreign Key พร้อม Action (`ON DELETE RESTRICT` หรือ `ON DELETE CASCADE`) อย่างสมเหตุสมผล
   * ต้องออกแบบให้อยู่ในรูปแบบ **3NF (Third Normal Form)**
2. **Data Integrity & Constraints:**
   * ฟิลด์ราคาและยอดเงินต้องใช้ `DECIMAL(10,2)` และมี `CHECK (price >= 0)`
   * อีเมลต้องเป็น `UNIQUE` และ `NOT NULL`
   * ในตาราง `order_items` ต้องเก็บ `unit_price` ซ้ำเพื่อคงประวัติราคา ณ วันที่สั่งซื้อ (Historical Integrity)
3. **Seed Data:**
   * เตรียม SQL Script สำหรับใส่ข้อมูลตัวอย่าง (Mock Data) ที่สมจริง มีหมวดหมู่หลากหลาย และมี Record ในตาราง `orders` ไม่น้อยกว่า 30 รายการ กระจายสถานะ `CONFIRMED`, `PENDING`, `CANCELLED` ตลอดหลายช่วงเวลา

---

### 3. กฎความปลอดภัยและ Business Logic (Access Control & Rules)
1. **Download Verification Guardrail:**
   * โค้ดที่ดึงลิงก์ดาวน์โหลดต้องมีเงื่อนไขตรวจสอบเสมอ:
     - คำสั่งซื้อต้องมีสถานะเป็น `CONFIRMED`
     - ผู้ใช้ที่ขอดาวน์โหลดต้องเป็นเจ้าของคำสั่งซื้อ (`user_id` ตรงกัน) หรือเป็น `ADMIN`
   * ห้ามเปิด Public Direct Download Endpoint โดยไม่มีการตรวจสอบสิทธิ์
2. **Password Security:**
   * ห้ามบันทึก Plaintext Password ลงในฐานข้อมูล ต้องใช้ Hash Function (เช่น bcrypt / Argon2)
3. **Input Validation:**
   * โค้ด Backend ต้อง Validate ข้อมูลฝั่งเซิร์ฟเวอร์ร่วมกับ Constraint ของฐานข้อมูลเสมอ ป้องกัน SQL Injection โดยใช้ Prepared Statements / Parameterized Queries 100%

---

### 4. กฎการเขียน SQL สำหรับการวิเคราะห์ (Analytics & Queries)
* ห้ามคำนวณสถิติในระดับ Application Code หากสามารถเขียน Aggregation ใน SQL ได้
* Query วิเคราะห์ทั้ง 4 รายงานต้องใช้ฟังก์ชัน SQL มาตรฐาน:
  - `GROUP BY`, `HAVING`
  - `SUM()`, `AVG()`, `COUNT()`
  - การ `JOIN` หลายตารางอย่างถูกต้อง
  - กรองเฉพาะคำสั่งซื้อที่สำเร็จ (`order_status = 'CONFIRMED'`) ในรายงานยอดขาย

---

### 5. แนวทางการสร้างโค้ดสำหรับ AI Assistant
* เมื่อผู้ใช้สั่งให้พัฒนาฟังก์ชันใดๆ ให้ตรวจเช็กว่าฟังก์ชันนั้นกระทบกับตารางใดใน Data Dictionary
* อธิบายคำสั่ง SQL ควบคู่ไปกับการเขียนฟังก์ชัน Backend เสมอ เพื่อให้นักศึกษาสามารถนำไปเขียนลงในเล่มรายงานได้
* ส่งเสริมการเขียนโค้ดที่สะอาด อ่านง่าย และมี Comment อธิบายชัดเจนเพื่อความพร้อมในการนำเสนอหน้าชั้นเรียน