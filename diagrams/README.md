# 📊 สารบัญและภาพรวมแผนภาพระบบ (System Diagrams Directory)
## E-Book Store Database Management Platform (2026)

โฟลเดอร์ `diagrams/` นี้รวบรวม **Diagram มาตรฐานสากลทั้ง 6 รูปแบบ** ที่แยกเป็นไฟล์เฉพาะรายหัวข้อ เพื่อง่ายต่อการอ่าน นำไปใส่ในสไลด์นำเสนอ หรือใช้แนบในเล่มรายงานโครงงานวิชาฐานข้อมูล

---

### 📂 รายการไฟล์ Diagram ทั้งหมด

| ลำดับ | ไฟล์ Diagram | รูปแบบแผนภาพ | วัตถุประสงค์หลัก |
| :---: | :--- | :---: | :--- |
| **01** | [01_er_diagram.md](01_er_diagram.md) | **ER-Diagram (3NF)** | แสดงความสัมพันธ์ของทั้ง 10 ตาราง, PK/FK, Cardinality (1:1, 1:N) และ Data Constraints |
| **02** | [02_system_architecture.md](02_system_architecture.md) | **Architecture Diagram** | แสดงสถาปัตยกรรมระบบ 4-Tier และ Data Access Layer ที่รองรับ SQLite / Postgres / MySQL |
| **03** | [03_checkout_transaction_sequence.md](03_checkout_transaction_sequence.md) | **Sequence Diagram** | แสดงกระบวนการทำงาน 4 สเต็ปของ **ACID Database Transaction** ในขณะสั่งซื้อ |
| **04** | [04_download_guardrail_flowchart.md](04_download_guardrail_flowchart.md) | **Flowchart** | แสดงขั้นตอนตรวจสอบสิทธิ์ 4 ด่านของ **Download Security Guardrail** ก่อนส่งมอบไฟล์ |
| **05** | [05_use_case_diagram.md](05_use_case_diagram.md) | **Use Case Diagram** | สรุปบทบาทและขอบเขตฟังก์ชันการใช้งานของ 3 Actor (Visitor, Customer, Admin) |
| **06** | [06_order_payment_state_machine.md](06_order_payment_state_machine.md) | **State Machine** | แสดงวงจรชีวิตและการเปลี่ยนสถานะของคำสั่งซื้อและการชำระเงิน |

---

### 💡 วิธีการนำไปใช้งาน
1. **ดูพรีวิวบน GitHub / VS Code / IDE:** ไฟล์ทั้งหมดใช้รูปแบบ Mermaid syntax ซึ่งจะเรนเดอร์เป็นภาพแผนภูมิโดยอัตโนมัติ
2. **แปลงเป็นรูปภาพสำหรับใส่สไลด์หรือรายงาน:** สามารถคัดลอกโค้ด Mermaid ไปวางที่ [Mermaid Live Editor](https://mermaid.live) เพื่อส่งออก (Export) เป็นรูปภาพ PNG หรือ SVG ความละเอียดสูงได้ทันที
