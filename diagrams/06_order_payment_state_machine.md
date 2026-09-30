# 06. แผนภาพวงจรสถานะคำสั่งซื้อและการชำระเงิน (Order & Payment State Machine)

แผนภาพนี้แสดงวงจรชีวิต (Lifecycle) และการเปลี่ยนสถานะของคำสั่งซื้อในตาราง `orders` และการชำระเงินในตาราง `payments` ตั้งแต่การสั่งซื้อจนถึงการอนุมัติหรือปฏิเสธ

---

## 🔄 Mermaid State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> OrderCreated: ลูกค้ากดยืนยันคำสั่งซื้อที่หน้า /checkout

    state OrderCreated {
        [*] --> PendingVerification
        PendingVerification: orders.order_status = 'PENDING'
        PendingVerification: payments.payment_status = 'WAITING_VERIFICATION'
        PendingVerification: 🛒 สินค้าในตะกร้าถูกเคลียร์
        PendingVerification: 🔒 ยังไม่สามารถดาวน์โหลดไฟล์ E-Book ได้
    }

    OrderCreated --> ConfirmedApproved: แอดมินตรวจสอบสลิปแล้วกด 'อนุมัติ' (CONFIRMED)
    OrderCreated --> CancelledRejected: แอดมินตรวจพบสลิปผิด/ปลอม หรือกดยกเลิก (CANCELLED)

    state ConfirmedApproved {
        [*] --> Confirmed
        Confirmed: orders.order_status = 'CONFIRMED'
        Confirmed: payments.payment_status = 'APPROVED'
        Confirmed: 🔓 ปลดล็อกสิทธิ์ให้ดาวน์โหลดไฟล์ E-Book ได้ทันที
        Confirmed: 📈 นำยอดขายไปคำนวณใน 4 รายงาน Analytics Dashboard
    }

    state CancelledRejected {
        [*] --> Cancelled
        Cancelled: orders.order_status = 'CANCELLED'
        Cancelled: payments.payment_status = 'REJECTED'
        Cancelled: ⛔ ปฏิเสธสิทธิ์ดาวน์โหลดไฟล์โดยเด็ดขาด
        Cancelled: 📉 ไม่นำยอดเงินนี้ไปคำนวณเป็นรายได้ของร้าน
    }

    ConfirmedApproved --> [*]: สิ้นสุดกระบวนการ (Completed)
    CancelledRejected --> [*]: สิ้นสุดกระบวนการ (Terminated)
```

---

## 🔍 ตารางเปรียบเทียบผลลัพธ์ของสถานะในระบบ

| สถานะคำสั่งซื้อ (`order_status`) | สถานะการชำระเงิน (`payment_status`) | สิทธิ์การดาวน์โหลดหนังสือ | ผลต่อรายงานยอดขาย (Analytics) |
| :---: | :---: | :---: | :---: |
| **`PENDING`** | `WAITING_VERIFICATION` | ❌ ปฏิเสธ (รอตรวจสอบ) | ไม่ถูกนับเป็นรายได้ (นับเป็น Pending Order) |
| **`CONFIRMED`** | **`APPROVED`** | ✅ **อนุญาตให้ดาวน์โหลดได้** | **ถูกคำนวณเป็นยอดขายจริง (Revenue & Units Sold)** |
| **`CANCELLED`** | `REJECTED` | ❌ ปฏิเสธโดยเด็ดขาด | ไม่ถูกนับเป็นรายได้ (นับเป็น Cancelled Order) |
