# 05. แผนภาพการใช้งานระบบตามบทบาทผู้ใช้ (Use Case Diagram)

แผนภาพนี้แสดงขอบเขตสิทธิ์และความสามารถในการใช้งานระบบ โดยจำแนกตาม 3 ตัวละครหลัก (Actors): **ผู้เยี่ยมชมทั่วไป (Visitor)**, **ลูกค้าสมาชิก (Customer)**, และ **ผู้ดูแลระบบ (Admin)**

---

## 👥 Mermaid Use Case Diagram

```mermaid
flowchart LR
    Visitor((👤 ผู้เยี่ยมชม\nVisitor))
    Customer((🛒 ลูกค้าสมาชิก\nCustomer))
    Admin((🛡️ ผู้ดูแลระบบ\nAdmin))

    subgraph SystemBoundary ["ขอบเขตระบบ E-Book Store Database Platform"]
        subgraph GuestModule ["โมดูลข้อมูลสาธารณะ & ยืนยันตัวตน"]
            UC1([1. ดูรายการหนังสือหน้าร้าน])
            UC2([2. ค้นหา & กรองหนังสือตามหมวดหมู่])
            UC3([3. ดูรายละเอียดหนังสือและผู้แต่ง])
            UC4([4. สมัครสมาชิก / เข้าสู่ระบบ])
            UC5([5. สลับ Demo User สำหรับทดสอบ])
        end

        subgraph ShoppingModule ["โมดูลการสั่งซื้อ & ดาวน์โหลด"]
            UC6([6. จัดการตะกร้าสินค้า เพิ่ม/ลบ])
            UC7([7. สั่งซื้อสินค้า Checkout])
            UC8([8. แนบสลิปชำระเงินจำลอง])
            UC9([9. ดูประวัติคำสั่งซื้อ & สถานะ])
            UC10([10. ดาวน์โหลด E-Book ผ่าน Guardrail])
        end

        subgraph AdminModule ["โมดูลบริหารจัดการ & ฐานข้อมูล"]
            UC11([11. จัดการหนังสือ เพิ่ม/เปิด-ปิดขาย])
            UC12([12. จัดการหมวดหมู่หนังสือ])
            UC13([13. ตรวจสอบสลิป อนุมัติ/ปฏิเสธออเดอร์])
            UC14([14. เปลี่ยนบทบาทผู้ใช้งาน User Role])
            UC15([15. ดูรายงานเชิงวิเคราะห์ 4 SQL Reports])
            UC16([16. ใช้งาน Database Explorer & SQL Runner])
        end
    end

    Visitor --> UC1
    Visitor --> UC2
    Visitor --> UC3
    Visitor --> UC4
    Visitor --> UC5

    Customer --> UC1
    Customer --> UC2
    Customer --> UC3
    Customer --> UC5
    Customer --> UC6
    Customer --> UC7
    Customer --> UC8
    Customer --> UC9
    Customer --> UC10

    Admin --> UC1
    Admin --> UC5
    Admin --> UC10
    Admin --> UC11
    Admin --> UC12
    Admin --> UC13
    Admin --> UC14
    Admin --> UC15
    Admin --> UC16
```

---

## 🔍 สรุปการแบ่งบทบาท (Role Matrix)

| ฟังก์ชันการทำงาน | Visitor (บุคคลทั่วไป) | Customer (ลูกค้า) | Admin (ผู้ดูแลระบบ) |
| :--- | :---: | :---: | :---: |
| ดูแคตตาล็อกหนังสือ / ค้นหา | ✅ | ✅ | ✅ |
| สมัครสมาชิก / ล็อกอิน | ✅ | ✅ | ✅ |
| เพิ่มหนังสือลงตะกร้า / แก้ไขตะกร้า | ❌ | ✅ | ❌ |
| สั่งซื้อ Checkout และแนบสลิป | ❌ | ✅ | ❌ |
| ดาวน์โหลดไฟล์ E-Book ของออเดอร์ตนเอง | ❌ | ✅ | ✅ (ดูตัวอย่างได้) |
| เพิ่มหนังสือใหม่ / ปิดการขาย | ❌ | ❌ | ✅ |
| อนุมัติสลิป / ปรับสถานะคำสั่งซื้อ | ❌ | ❌ | ✅ |
| ดูรายงาน 4 SQL Analytics Dashboard | ❌ | ❌ | ✅ |
| สำรวจ Data Dictionary & รันคำสั่ง SQL สด | ✅ (Read-Only) | ✅ (Read-Only) | ✅ (Read-Only) |
