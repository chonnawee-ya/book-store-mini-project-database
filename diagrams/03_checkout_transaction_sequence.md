# 03. แผนภาพลำดับการทำงานคำสั่งซื้อ (Checkout & ACID Transaction Sequence)

แผนภาพนี้แสดงขั้นตอนการทำงานของกระบวนการสั่งซื้อสินค้า (Checkout) ผ่านมุมมองของ **Database Transaction (ACID Properties)** ซึ่งรับประกันว่าข้อมูลทั้ง 4 ตารางจะถูกบันทึกสำเร็จพร้อมกันทั้งหมด หากมีขั้นตอนใดเกิดข้อผิดพลาด ระบบจะทำ `ROLLBACK` ทันที

---

## 💳 Mermaid Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Customer as 👤 ลูกค้า (Customer)
    participant Route as 🖥️ /checkout Controller
    participant DB as 🗄️ Database Transaction

    Customer->>Route: กดปุ่มยืนยันสั่งซื้อ (POST: payment_method, slip_url)
    Route->>DB: เริ่มต้นธุรกรรม (BEGIN TRANSACTION)
    
    rect rgb(240, 248, 255)
    Note over Route,DB: ธุรกรรมต้องทำงานครบทุกข้อ (Atomicity & Consistency)
    Route->>DB: 1. INSERT INTO orders (user_id, total_amount, 'PENDING')
    DB-->>Route: คืนค่า new_order_id
    
    Route->>DB: 2. INSERT INTO order_items (order_id, ebook_id, unit_price)
    Note over Route,DB: วนลูปบันทึกราคา Snapshot ของทุกเล่มในตะกร้า
    
    Route->>DB: 3. INSERT INTO payments (order_id, paid_amount, 'WAITING_VERIFICATION')
    Note over Route,DB: บันทึกประวัติการชำระเงินและรูปสลิปจำลอง
    
    Route->>DB: 4. DELETE FROM cart_items WHERE cart_id = user_cart_id
    Note over Route,DB: ล้างสินค้าออกจากตะกร้าผู้ใช้
    end

    alt ทุกขั้นตอนทำงานสำเร็จสมบูรณ์ (Success)
        Route->>DB: COMMIT TRANSACTION
        Note over DB: บันทึกข้อมูลลงฐานข้อมูลอย่างถาวร
        Route-->>Customer: Flash Success & นำผู้ใช้ไปยังหน้า /orders
    else เกิดข้อผิดพลาดหรือระบบขัดข้อง (Exception Encountered)
        Route->>DB: ROLLBACK TRANSACTION
        Note over DB: ยกเลิกการเปลี่ยนแปลงทั้งหมดใน 4 ขั้นตอน ข้อมูลคงเดิม
        Route-->>Customer: Flash Danger แสดงข้อความแจ้งเตือน และคงอยู่ที่หน้าเดิม
    end
```

---

## 🔍 คุณสมบัติ ACID ที่เกิดขึ้นในกระบวนการนี้

* **Atomicity (ความเป็นหนึ่งเดียว):** หากเกิดไฟดับ หรือระบบล่มในขณะกำลัง `DELETE FROM cart_items` คำสั่งซื้อจะไม่ค้างอยู่ครึ่งๆ กลางๆ เพราะระบบจะย้อนสถานะกลับทั้งหมดเหมือนไม่เคยทำรายการ
* **Consistency (ความสอดคล้อง):** ข้อมูลทุกแถวที่บันทึกต้องเป็นไปตาม Foreign Key และ Check Constraints เช่น `paid_amount >= 0` และ `order_status IN ('PENDING', 'CONFIRMED', 'CANCELLED')`
* **Isolation (ความโดดเดี่ยว):** ในขณะที่ Transaction กำลังทำงาน ผู้ใช้อื่นจะไม่สามารถเห็นข้อมูลที่ยังบันทึกไม่เสร็จ
* **Durability (ความคงทนถาวร):** เมื่อคำสั่ง `COMMIT` สำเร็จ ข้อมูลคำสั่งซื้อและยอดชำระเงินจะถูกจัดเก็บลงดิสก์อย่างถาวร
