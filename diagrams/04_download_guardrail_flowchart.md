# 04. แผนภาพกระบวนการตรวจสอบสิทธิ์ดาวน์โหลด (Download Guardrail Flowchart)

แผนภาพนี้แสดงขั้นตอนการทำงานของระบบความปลอดภัย **Security Guardrail** ในฟังก์ชัน `download_ebook(order_id, ebook_id)` เพื่อป้องกันไม่ให้ผู้ใช้แอบดาวน์โหลดหนังสือดิจิทัลโดยไม่ได้ชำระเงิน หรือเข้าถึงไฟล์ของผู้อื่น

---

## 🛡️ Mermaid Flowchart

```mermaid
flowchart TD
    Start([ผู้ใช้คลิกปุ่มดาวน์โหลด E-Book]) --> CheckAuth{1. ผู้ใช้ล็อกอินเข้าสู่ระบบหรือยัง?}
    
    CheckAuth -- ยังไม่ได้ล็อกอิน --> RedirectLogin[Redirect ไปที่หน้า /login\nพร้อมแจ้งเตือนให้เข้าสู่ระบบก่อน]
    
    CheckAuth -- ล็อกอินแล้ว --> CheckOrderExist{2. พบข้อมูล Order ID\nในตาราง orders หรือไม่?}
    
    CheckOrderExist -- ไม่พบข้อมูล --> Abort404[ส่งกลับ HTTP 404:\nไม่พบคำสั่งซื้อที่ระบุ]
    
    CheckOrderExist -- พบคำสั่งซื้อ --> CheckOwnership{3. ตรวจสอบสิทธิ์การเข้าถึง:\nเป็นเจ้าของออเดอร์\nหรือมีบทบาท ADMIN?}
    
    CheckOwnership -- ไม่ใช่เจ้าของและไม่ใช่แอดมิน --> Abort403[ส่งกลับ HTTP 403 Forbidden:\nปฏิเสธการเข้าถึงออเดอร์ของผู้อื่น]
    
    CheckOwnership -- ยืนยันสิทธิ์ผ่าน --> CheckStatus{4. ตรวจสอบสถานะคำสั่งซื้อ:\norder_status == 'CONFIRMED'?}
    
    CheckStatus -- สถานะยังเป็น PENDING หรือ CANCELLED --> RejectStatus[Flash Danger:\nปฏิเสธการดาวน์โหลดเนื่องจาก\nคำสั่งซื้อยังไม่ได้รับการอนุมัติ]
    RejectStatus --> RedirectOrders[Redirect กลับไปที่หน้า /orders]
    
    CheckStatus -- ได้รับการอนุมัติแล้ว (CONFIRMED) --> CheckBookInOrder{5. ตรวจสอบใน order_items:\nหนังสือเล่มนี้อยู่ในออเดอร์จริงไหม?}
    
    CheckBookInOrder -- ไม่พบหนังสือในออเดอร์นี้ --> AbortBook404[ส่งกลับ HTTP 404:\nไม่พบหนังสือเล่มนี้ในรายการ]
    
    CheckBookInOrder -- ถูกต้องสมบูรณ์ --> GenerateFile[สร้าง Personalized Digital License File\nระบุชื่อผู้ซื้อ, เลขที่ออเดอร์, และ Timestamp]
    GenerateFile --> Deliver([ส่งมอบไฟล์แนบดาวน์โหลดผ่าน Flask send_file])
```

---

## 🔍 จุดเด่นของการออกแบบความปลอดภัย (Security Highlights)

1. **Defense-in-Depth:** มีการตรวจสอบหลายชั้น ไม่เพียงแค่ตรวจสถานะล็อกอิน แต่ตรวจลึกถึงความเป็นเจ้าของ (`user_id`) และสถานะการชำระเงิน (`CONFIRMED`)
2. **Dynamic Generation:** ไม่ได้ใช้ Static File ลิงก์ตรงที่เสี่ยงต่อการถูกแชร์ URL แต่ใช้วิธีการสร้างเนื้อหาไฟล์ดิจิทัลพร้อมตราประทับลิขสิทธิ์ประจำตัวผู้ซื้อ (Licensed To) แบบ Real-time
3. **Protection against Insecure Direct Object References (IDOR):** หากผู้ใช้พยายามเปลี่ยนตัวเลข `order_id` ใน URL ระบบจะดักจับด้วยเงื่อนไขข้อ 3 ทันที
