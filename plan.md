# Project: Advanced ScriptBot Converter (ASBC)

## Objective
โปรแกรมแปลงข้อมูลจาก Input หลากหลายรูปแบบ (Excel, CSV, JSON, TXT) ให้ออกมาเป็นไฟล์ Output ตามโครงสร้าง Template (Header, Body, Footer) ที่กำหนดเองได้ พร้อมระบบ Mapping Parameter ที่ยืดหยุ่น

## Technical Specs
- **Language:** Python 3.x
- **Core Library:** `pandas` (จัดการข้อมูล), `openpyxl` (xlsx), `xlrd` (xls), `jinja2` (ทางเลือกสำหรับ Template ขั้นสูง)
- **Input Formats:** `.txt`, `.csv`, `.xlsx`, `.xls`, `.json`
- **Output Formats:** ตามที่ระบุใน Config (.txt, .csv, .xlsx, .json, .sidata, ฯลฯ)
- **Mapping Logic:** รองรับการเรียกใช้ชื่อ Header แทนการนับเลขคอลัมน์ (เช่น `{{CustomerName}}`)

---

## Tasklist
- [ ] **Phase 1: Environment & Architecture Setup**
    - [x] 1.1 ตรวจสอบและติดตั้ง Dependencies (pandas, openpyxl, etc.)
    - [x] 1.2 ออกแบบโครงสร้างไฟล์ Config ใหม่ (ASBC-Config.ini หรือ .json)
- [x] **Phase 2: Universal Input Loader**
    - [x] 2.1 พัฒนา Module สำหรับอ่านไฟล์ Input แต่ละประเภท
    - [x] 2.2 ระบบตรวจจับ Header อัตโนมัติ
- [x] **Phase 3: Core Engine & Template Processor**
    - [x] 3.1 พัฒนาระบบ Mapping `{{Parameter}}` จากชื่อ Header
    - [x] 3.2 ระบบประมวลผล Header.txt, Body.txt (Loop), Footer.txt
- [x] **Phase 4: Multi-Format Output Exporter**
    - [x] 4.1 พัฒนาระบบบันทึกไฟล์ตาม Extension ที่กำหนด
    - [x] 4.2 ระบบจัดการ Encoding และ Line Break
- [x] **Phase 5: User Interface & Error Handling**
    - [x] 5.1 เพิ่มระบบ Log และ Error Handling (กรณีไฟล์เปิดอยู่หรือ Data ผิดพลาด)
    - [x] 5.2 (Optional) ระบบเลือกไฟล์ผ่าน File Dialog
- [x] **Phase 6: Testing & Validation**
    - [x] 6.1 ทดสอบกับเคส Excel เดิม และรูปแบบใหม่ๆ
- [x] **Phase 7: Graphical User Interface (GUI)**
    - [x] 7.1 ออกแบบหน้าจอ Interface ด้วย Tkinter
    - [x] 7.2 เชื่อมต่อปุ่มเลือกไฟล์ (File Dialog) เข้ากับระบบ Config
    - [x] 7.3 รวมระบบรันโปรแกรมเข้ากับหน้าจอ GUI พร้อมการแจ้งเตือน Error
- [ ] **Phase 8: Batch Processing Support**
    - [ ] 8.1 ปรับปรุง ASBC_Main ให้รองรับการทำงานหลาย Task จาก Config เดียว
    - [ ] 8.2 ปรับปรุงระบบ Template ให้แยกตามราย Task
    - [ ] 8.3 ทดสอบการรันครั้งเดียวเพื่อออกไฟล์ elements.csv และ properties.csv พร้อมกัน

---

## กฎเหล็กในการทำงาน (Strict Rules)
1. **Plan First:** ต้องตรวจสอบและอัปเดต `plan.md` ก่อนเริ่มทำ Task เสมอ
2. **Update Status:** เมื่อ Task ใดเสร็จสิ้น ให้เปลี่ยน `[ ]` เป็น `[x]` ใน `plan.md` ทันที
3. **Atomic Changes:** ทำทีละ Task เพื่อป้องกันบั๊กสะสม
4. **Validation:** ทุกครั้งที่จบ Task ต้องมีการตรวจสอบความถูกต้องของโค้ด
