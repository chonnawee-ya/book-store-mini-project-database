-- ==============================================================================
-- Seed Data Script for MySQL 8.0+ / MariaDB 10.5+
-- Database: ebook_store_db
-- ==============================================================================

USE ebook_store_db;
SET FOREIGN_KEY_CHECKS = 0;

-- Data for table `roles` (2 records)
INSERT INTO `roles` (`role_id`, `role_name`) VALUES
(1, 'ADMIN'),
(2, 'CUSTOMER');

-- Data for table `users` (8 records)
INSERT INTO `users` (`user_id`, `role_id`, `email`, `password_hash`, `full_name`, `phone`, `created_at`) VALUES
(1, 1, 'admin@ebookstore.com', 'scrypt:32768:8:1$JbH86jmJDIVU4RrD$5ae12e4591c191a900cd08addd0b7b2ddd8ad889f37d919747b6e89091ddbb5a44ea4077a9302980237decba574369c80ed37c1950e518a4da9dbe57ffec7022', 'ผู้ดูแลระบบ (Admin)', '0812345678', '2026-01-01 08:00:00'),
(2, 2, 'somchai@email.com', 'scrypt:32768:8:1$fH8q2iRlLJ7v9lwM$765286c6df3e19c559606eec0195e2f70e67491d38f0ec014574d9e14d51e76fe52890b48f85ca92bbe0d156a4f2897c1b56ef2e37c55b9ccaa2b6fc2aa067e0', 'สมชาย สายอ่าน', '0891112233', '2026-01-05 10:30:00'),
(3, 2, 'somsak@email.com', 'scrypt:32768:8:1$VxBed99bW32fAzCt$436ae60dfdb22ee3ca1e2e95d87d838776ea3c77d5b513ff4d1825ee4d4a213bb70ae3ef28b485f3212b3729f56017060abeb2fe66caf3f8072a941f527c7d85', 'สมศักดิ์ รักเรียนรู้', '0892223344', '2026-01-10 14:15:00'),
(4, 2, 'jane.doe@email.com', 'scrypt:32768:8:1$k6bLI4ytedFkmSXg$6120c184dab99e93f69af995e468fc941ba48f0b8647b9ff4d7974fb0e393f0b5351902e24708630458243326a941853168814ac78397a3dab4dca538b710e52', 'Jane Doe', '0893334455', '2026-01-15 09:20:00'),
(5, 2, 'john.dev@email.com', 'scrypt:32768:8:1$AaFEIjnJxffsYpIR$9377172dcdf56919829430379b66f1f26d9621bcc0faa2f812a114ccb887b002519c6ee7efb03ff315aeb723604c1f09eb137937ec60f564ea245bef1ab28800', 'John Developer', '0894445566', '2026-01-20 16:45:00'),
(6, 2, 'sarah.connor@email.com', 'scrypt:32768:8:1$w29EUHrtqrkkuWKi$d40f678b428e19f0e103c4feae0a1e60d10c971b5f0caea7a1d822e59d4125a336f171121f82634a29e87da80f07824f20525b9755feeae25139b83978ec625b', 'Sarah Connor', '0895556677', '2026-02-01 11:10:00'),
(7, 2, 'alex.tech@email.com', 'scrypt:32768:8:1$WdUe3s7mCcp8MkeW$d0cef04f6294216111df3bd84fef45f26dd5a40c9045ac75dc69764fdbdcd75f4e52c0be84dc8636de4b1e9345e26d59aca4fac48d1c1df7de24d06fb1c5569c', 'Alex Techlover', '0896667788', '2026-02-05 13:00:00'),
(8, 2, 'wichai@email.com', 'scrypt:32768:8:1$KAYLdbKnSMOlK5x3$66294adfb8058213cee2f3868b253c9d5ae32be96b933bf12205d00d2ca2f27499a2ea312b05a20b1fbaefa3b678391be53f1b361f5f4f77f573fbe513d90999', 'วิชัย มหาเศรษฐี', '0897778899', '2026-02-12 18:30:00');

-- Data for table `categories` (5 records)
INSERT INTO `categories` (`category_id`, `name`, `description`) VALUES
(1, 'วิทยาการคอมพิวเตอร์และโปรแกรมมิ่ง', 'หนังสือครอบคลุมภาษา Python, SQL, Architecture, Data Structures และ Clean Code'),
(2, 'การพัฒนาตนเองและจิตวิทยา', 'เคล็ดลับการจัดการเวลา นิสัยแห่งความสำเร็จ และจิตวิทยาพฤติกรรมมนุษย์'),
(3, 'ธุรกิจ การเงิน และการลงทุน', 'กลยุทธ์การเงินส่วนบุคคล การลงทุนในหุ้น สตาร์ทอัป และเศรษฐศาสตร์สมัยใหม่'),
(4, 'วรรณกรรมและนิยายสากล', 'นิยายไซไฟ ดิสโทเปีย และวรรณกรรมระดับมาสเตอร์พีซของโลก'),
(5, 'การออกแบบและศิลปะดิจิทัล', 'UX/UI Design, การออกแบบกราฟิก และ Design Thinking สำหรับยุคดิจิทัล');

-- Data for table `authors` (8 records)
INSERT INTO `authors` (`author_id`, `name`, `biography`) VALUES
(1, 'Robert C. Martin', 'Uncle Bob ผู้เขียน Clean Code และผู้เชี่ยวชาญด้าน Software Craftsmanship ระดับโลก'),
(2, 'James Clear', 'นักเขียนหนังสือขายดีระดับโลก Atomic Habits ผู้เชี่ยวชาญด้านจิตวิทยาการสร้างนิสัย'),
(3, 'Morgan Housel', 'นักเขียนและพาร์ทเนอร์ Collaborative Fund ผู้เขียน The Psychology of Money'),
(4, 'Dr. Donald E. Knuth', 'ปรมาจารย์ด้านวิทยาการคอมพิวเตอร์ ผู้ประพันธ์ The Art of Computer Programming'),
(5, 'Don Norman', 'บิดาแห่งวงการ User Experience (UX) ผู้เขียน The Design of Everyday Things'),
(6, 'George Orwell', 'นักประพันธ์ชาวอังกฤษผู้สร้างผลงานวรรณกรรมไซไฟการเมือง 1984 และ Animal Farm'),
(7, 'Martin Fowler', 'Chief Scientist ที่ ThoughtWorks ผู้เชี่ยวชาญด้าน Refactoring และ Microservices'),
(8, 'ภัทรพล ศิลปาจารย์', 'นักลงทุน นักคิด และนักเขียนหนังสือด้านอิสรภาพทางการเงินยอดนิยมของไทย');

-- Data for table `ebooks` (16 records)
INSERT INTO `ebooks` (`ebook_id`, `category_id`, `author_id`, `title`, `description`, `price`, `cover_image_url`, `file_download_url`, `is_active`, `created_at`) VALUES
(1, 1, 1, 'Clean Code: A Handbook of Agile Software Craftsmanship', 'แนวทางการเขียนโค้ดให้อ่านง่าย บำรุงรักษาสะดวก และมีประสิทธิภาพสูงสุด', 450.0, 'https://images.unsplash.com/photo-1532012164546-f432f2e3777a?w=400&q=80', '/download/ebook/1', 1, '2026-09-22 20:02:00'),
(2, 1, 4, 'Database Systems & SQL Mastery', 'เจาะลึกโครงสร้างฐานข้อมูลเชิงสัมพันธ์ 3NF Indexing และ Query Optimization', 520.0, 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80', '/download/ebook/2', 1, '2026-09-22 20:02:00'),
(3, 1, 7, 'Refactoring: Improving the Design of Existing Code', 'เทคนิคการปรับปรุงโค้ดเดิมให้มีสถาปัตยกรรมที่ยืดหยุ่น ปลอดภัย และทดสอบง่าย', 490.0, 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&q=80', '/download/ebook/3', 1, '2026-09-22 20:02:00'),
(4, 2, 2, 'Atomic Habits: เพราะชีวิตดีได้กว่าที่เป็น', 'เปลี่ยนชีวิตด้วยพลังแห่งการปรับนิสัยวันละ 1% ที่สร้างผลลัพธ์มหาศาล', 290.0, 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&q=80', '/download/ebook/4', 1, '2026-09-22 20:02:00'),
(5, 3, 3, 'The Psychology of Money: จิตวิทยาว่าด้วยเงิน', 'บทเรียนเหนือกาลเวลาเรื่องความมั่งคั่ง ความโลภ และความสุข', 350.0, 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400&q=80', '/download/ebook/5', 1, '2026-09-22 20:02:00'),
(6, 4, 6, '1984: นิยายดิสโทเปียระดับตำนาน', 'เรื่องราวโลกอนาคตที่ Big Brother กำลังจับตามองคุณอยู่ทุกฝีก้าว', 220.0, 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400&q=80', '/download/ebook/6', 1, '2026-09-22 20:02:00'),
(7, 5, 5, 'The Design of Everyday Things', 'ทำไมของบางอย่างใช้ง่าย บางอย่างใช้ยาก คัมภีร์ UX ที่นักออกแบบทุกคนต้องอ่าน', 380.0, 'https://images.unsplash.com/photo-1507842229458-5742130e6677?w=400&q=80', '/download/ebook/7', 1, '2026-09-22 20:02:00'),
(8, 3, 8, 'Money 101: เริ่มต้นสร้างอิสรภาพทางการเงิน', 'คู่มือวางแผนการเงินฉบับเข้าใจง่ายสำหรับคนทำงานและวัยรุ่นยุคใหม่', 250.0, 'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=400&q=80', '/download/ebook/8', 1, '2026-09-22 20:02:00'),
(9, 1, 1, 'The Clean Coder: Code of Conduct for Professional Programmers', 'จรรยาบรรณ วินัย และทัศนคติของโปรแกรมเมอร์มืออาชีพ', 390.0, 'https://images.unsplash.com/photo-1516259762381-22954d7d3ad2?w=400&q=80', '/download/ebook/9', 1, '2026-09-22 20:02:00'),
(10, 2, 2, 'Deep Work: กฎเหล็กแห่งการจดจ่อในโลกที่ถูกรบกวน', 'สร้างสมาธิขั้นสุดเพื่อผลลัพธ์การทำงานที่ทรงคุณค่าและเหนือชั้น', 310.0, 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=400&q=80', '/download/ebook/10', 1, '2026-09-22 20:02:00'),
(11, 4, 6, 'Animal Farm: การเมืองในฟาร์มสัตว์', 'วรรณกรรมเสียดสีอำนาจเผด็จการผ่านมุมมองของเหล่าสัตว์ในฟาร์ม', 180.0, 'https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=400&q=80', '/download/ebook/11', 1, '2026-09-22 20:02:00'),
(12, 5, 5, 'Don''t Make Me Think: คัมภีร์ออกแบบ Web Usability', 'หลักการออกแบบเว็บและแอปพลิเคชันให้ผู้ใช้เข้าใจได้ในทันทีโดยไม่ต้องคิด', 360.0, 'https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=400&q=80', '/download/ebook/12', 1, '2026-09-22 20:02:00'),
(13, 1, 7, 'Building Microservices: Designing Fine-Grained Systems', 'สถาปัตยกรรม Microservices การแบ่งขอบเขต Service และการประสานงาน', 590.0, 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80', '/download/ebook/13', 1, '2026-09-22 20:02:00'),
(14, 3, 3, 'Same as Ever: คู่มือทำความเข้าใจสิ่งที่ไม่เคยเปลี่ยน', 'มองทะลุอนาคตด้วยความเข้าใจพฤติกรรมมนุษย์และสิ่งที่ไม่เคยเปลี่ยนแปลงตามกาลเวลา', 320.0, 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&q=80', '/download/ebook/14', 1, '2026-09-22 20:02:00'),
(15, 1, 4, 'Algorithms Unlocked: ไขรหัสอัลกอริทึมฉบับย่อยง่าย', 'เข้าใจแนวคิดอัลกอริทึมพื้นฐานที่ขับเคลื่อนเทคโนโลยีรอบตัวคุณ', 410.0, 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400&q=80', '/download/ebook/15', 1, '2026-09-22 20:02:00'),
(16, 2, 2, 'Thinking, Fast and Slow (ฉบับ E-Book พิเศษ)', 'ระบบการคิดเร็วและการคิดช้าที่ชี้นำการตัดสินใจของมนุษย์ทุกคน', 420.0, 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=400&q=80', '/download/ebook/16', 0, '2026-09-22 20:02:00');

-- Data for table `carts` (8 records)
INSERT INTO `carts` (`cart_id`, `user_id`, `updated_at`) VALUES
(1, 1, '2026-09-22 20:02:00'),
(2, 2, '2026-09-22 20:02:00'),
(3, 3, '2026-09-22 20:02:00'),
(4, 4, '2026-09-22 20:02:00'),
(5, 5, '2026-09-22 20:02:00'),
(6, 6, '2026-09-22 20:02:00'),
(7, 7, '2026-09-22 20:02:00'),
(8, 8, '2026-09-22 20:02:00');

-- Data for table `cart_items` (1 records)
INSERT INTO `cart_items` (`cart_item_id`, `cart_id`, `ebook_id`, `quantity`, `created_at`) VALUES
(1, 2, 1, 1, '2026-09-22 20:02:00');

-- Data for table `orders` (36 records)
INSERT INTO `orders` (`order_id`, `user_id`, `total_amount`, `order_status`, `created_at`) VALUES
(1, 2, 970.0, 'CONFIRMED', '2026-01-06 11:20:00'),
(2, 3, 290.0, 'CONFIRMED', '2026-01-08 14:10:00'),
(3, 4, 600.0, 'CONFIRMED', '2026-01-12 09:45:00'),
(4, 5, 1330.0, 'CONFIRMED', '2026-01-15 17:00:00'),
(5, 6, 380.0, 'CANCELLED', '2026-01-18 10:15:00'),
(6, 7, 1110.0, 'CONFIRMED', '2026-01-22 13:30:00'),
(7, 8, 670.0, 'CONFIRMED', '2026-01-25 19:20:00'),
(8, 2, 600.0, 'CONFIRMED', '2026-01-28 08:40:00'),
(9, 3, 400.0, 'CONFIRMED', '2026-01-30 16:55:00'),
(10, 4, 740.0, 'PENDING', '2026-01-31 21:05:00'),
(11, 5, 900.0, 'CONFIRMED', '2026-02-02 10:00:00'),
(12, 6, 880.0, 'CONFIRMED', '2026-02-04 12:45:00'),
(13, 7, 290.0, 'CONFIRMED', '2026-02-07 15:30:00'),
(14, 8, 1050.0, 'CONFIRMED', '2026-02-10 18:15:00'),
(15, 2, 740.0, 'CONFIRMED', '2026-02-12 11:25:00'),
(16, 3, 410.0, 'CANCELLED', '2026-02-14 14:50:00'),
(17, 4, 810.0, 'CONFIRMED', '2026-02-16 09:10:00'),
(18, 5, 570.0, 'CONFIRMED', '2026-02-18 20:00:00'),
(19, 6, 760.0, 'CONFIRMED', '2026-02-21 16:40:00'),
(20, 7, 220.0, 'PENDING', '2026-02-24 13:15:00'),
(21, 8, 1080.0, 'CONFIRMED', '2026-02-26 17:35:00'),
(22, 2, 350.0, 'CONFIRMED', '2026-02-28 10:50:00'),
(23, 3, 1260.0, 'CONFIRMED', '2026-03-02 09:30:00'),
(24, 4, 740.0, 'CONFIRMED', '2026-03-04 14:20:00'),
(25, 5, 800.0, 'CONFIRMED', '2026-03-06 18:00:00'),
(26, 6, 640.0, 'CONFIRMED', '2026-03-08 11:15:00'),
(27, 7, 770.0, 'CANCELLED', '2026-03-10 15:45:00'),
(28, 8, 1320.0, 'CONFIRMED', '2026-03-12 19:30:00'),
(29, 2, 250.0, 'CONFIRMED', '2026-03-14 10:10:00'),
(30, 3, 670.0, 'CONFIRMED', '2026-03-16 13:40:00'),
(31, 4, 800.0, 'CONFIRMED', '2026-03-18 16:20:00'),
(32, 5, 400.0, 'PENDING', '2026-03-19 20:00:00'),
(33, 6, 930.0, 'CONFIRMED', '2026-03-20 12:30:00'),
(34, 7, 740.0, 'CONFIRMED', '2026-03-21 14:15:00'),
(35, 8, 970.0, 'CONFIRMED', '2026-03-22 17:50:00'),
(36, 2, 520.0, 'PENDING', '2026-03-22 22:10:00');

-- Data for table `order_items` (69 records)
INSERT INTO `order_items` (`order_item_id`, `order_id`, `ebook_id`, `unit_price`) VALUES
(1, 1, 1, 450.0),
(2, 1, 2, 520.0),
(3, 2, 4, 290.0),
(4, 3, 5, 350.0),
(5, 3, 8, 250.0),
(6, 4, 1, 450.0),
(7, 4, 3, 490.0),
(8, 4, 9, 390.0),
(9, 5, 7, 380.0),
(10, 6, 2, 520.0),
(11, 6, 13, 590.0),
(12, 7, 5, 350.0),
(13, 7, 14, 320.0),
(14, 8, 4, 290.0),
(15, 8, 10, 310.0),
(16, 9, 6, 220.0),
(17, 9, 11, 180.0),
(18, 10, 1, 450.0),
(19, 10, 4, 290.0),
(20, 11, 2, 520.0),
(21, 11, 7, 380.0),
(22, 12, 3, 490.0),
(23, 12, 9, 390.0),
(24, 13, 4, 290.0),
(25, 14, 1, 450.0),
(26, 14, 5, 350.0),
(27, 14, 8, 250.0),
(28, 15, 12, 360.0),
(29, 15, 7, 380.0),
(30, 16, 15, 410.0),
(31, 17, 2, 520.0),
(32, 17, 4, 290.0),
(33, 18, 8, 250.0),
(34, 18, 14, 320.0),
(35, 19, 1, 450.0),
(36, 19, 10, 310.0),
(37, 20, 6, 220.0),
(38, 21, 3, 490.0),
(39, 21, 13, 590.0),
(40, 22, 5, 350.0),
(41, 23, 1, 450.0),
(42, 23, 2, 520.0),
(43, 23, 4, 290.0),
(44, 24, 7, 380.0),
(45, 24, 12, 360.0),
(46, 25, 15, 410.0),
(47, 25, 9, 390.0),
(48, 26, 4, 290.0),
(49, 26, 5, 350.0),
(50, 27, 1, 450.0),
(51, 27, 14, 320.0),
(52, 28, 2, 520.0),
(53, 28, 3, 490.0),
(54, 28, 10, 310.0),
(55, 29, 8, 250.0),
(56, 30, 4, 290.0),
(57, 30, 7, 380.0),
(58, 31, 1, 450.0),
(59, 31, 5, 350.0),
(60, 32, 6, 220.0),
(61, 32, 11, 180.0),
(62, 33, 2, 520.0),
(63, 33, 15, 410.0),
(64, 34, 3, 490.0),
(65, 34, 8, 250.0),
(66, 35, 4, 290.0),
(67, 35, 12, 360.0),
(68, 35, 14, 320.0),
(69, 36, 2, 520.0);

-- Data for table `payments` (36 records)
INSERT INTO `payments` (`payment_id`, `order_id`, `payment_method`, `slip_url`, `paid_amount`, `payment_status`, `payment_date`) VALUES
(1, 1, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+1', 970.0, 'APPROVED', '2026-01-06 11:20:00'),
(2, 2, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+2', 290.0, 'APPROVED', '2026-01-08 14:10:00'),
(3, 3, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+3', 600.0, 'APPROVED', '2026-01-12 09:45:00'),
(4, 4, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+4', 1330.0, 'APPROVED', '2026-01-15 17:00:00'),
(5, 5, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/ef4444/ffffff?text=Mock+Slip+Rejected', 380.0, 'REJECTED', '2026-01-18 10:15:00'),
(6, 6, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+6', 1110.0, 'APPROVED', '2026-01-22 13:30:00'),
(7, 7, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+7', 670.0, 'APPROVED', '2026-01-25 19:20:00'),
(8, 8, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+8', 600.0, 'APPROVED', '2026-01-28 08:40:00'),
(9, 9, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+9', 400.0, 'APPROVED', '2026-01-30 16:55:00'),
(10, 10, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/f59e0b/ffffff?text=Mock+Slip+Pending', 740.0, 'WAITING_VERIFICATION', '2026-01-31 21:05:00'),
(11, 11, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+11', 900.0, 'APPROVED', '2026-02-02 10:00:00'),
(12, 12, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+12', 880.0, 'APPROVED', '2026-02-04 12:45:00'),
(13, 13, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+13', 290.0, 'APPROVED', '2026-02-07 15:30:00'),
(14, 14, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+14', 1050.0, 'APPROVED', '2026-02-10 18:15:00'),
(15, 15, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+15', 740.0, 'APPROVED', '2026-02-12 11:25:00'),
(16, 16, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/ef4444/ffffff?text=Mock+Slip+Rejected', 410.0, 'REJECTED', '2026-02-14 14:50:00'),
(17, 17, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+17', 810.0, 'APPROVED', '2026-02-16 09:10:00'),
(18, 18, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+18', 570.0, 'APPROVED', '2026-02-18 20:00:00'),
(19, 19, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+19', 760.0, 'APPROVED', '2026-02-21 16:40:00'),
(20, 20, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/f59e0b/ffffff?text=Mock+Slip+Pending', 220.0, 'WAITING_VERIFICATION', '2026-02-24 13:15:00'),
(21, 21, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+21', 1080.0, 'APPROVED', '2026-02-26 17:35:00'),
(22, 22, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+22', 350.0, 'APPROVED', '2026-02-28 10:50:00'),
(23, 23, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+23', 1260.0, 'APPROVED', '2026-03-02 09:30:00'),
(24, 24, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+24', 740.0, 'APPROVED', '2026-03-04 14:20:00'),
(25, 25, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+25', 800.0, 'APPROVED', '2026-03-06 18:00:00'),
(26, 26, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+26', 640.0, 'APPROVED', '2026-03-08 11:15:00'),
(27, 27, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/ef4444/ffffff?text=Mock+Slip+Rejected', 770.0, 'REJECTED', '2026-03-10 15:45:00'),
(28, 28, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+28', 1320.0, 'APPROVED', '2026-03-12 19:30:00'),
(29, 29, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+29', 250.0, 'APPROVED', '2026-03-14 10:10:00'),
(30, 30, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+30', 670.0, 'APPROVED', '2026-03-16 13:40:00'),
(31, 31, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+31', 800.0, 'APPROVED', '2026-03-18 16:20:00'),
(32, 32, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/f59e0b/ffffff?text=Mock+Slip+Pending', 400.0, 'WAITING_VERIFICATION', '2026-03-19 20:00:00'),
(33, 33, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+33', 930.0, 'APPROVED', '2026-03-20 12:30:00'),
(34, 34, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+34', 740.0, 'APPROVED', '2026-03-21 14:15:00'),
(35, 35, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/22c55e/ffffff?text=Mock+Slip+Order+35', 970.0, 'APPROVED', '2026-03-22 17:50:00'),
(36, 36, 'SIMULATED_TRANSFER', 'https://placehold.co/400x600/f59e0b/ffffff?text=Mock+Slip+Pending', 520.0, 'WAITING_VERIFICATION', '2026-03-22 22:10:00');

SET FOREIGN_KEY_CHECKS = 1;
-- Finished seeding MySQL data.
