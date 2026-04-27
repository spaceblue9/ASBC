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
- [x] **Phase 8: Batch Processing Support**
    - [x] 8.1 ปรับปรุง ASBC_Main ให้รองรับการทำงานหลาย Task จาก Config เดียว
    - [x] 8.2 ปรับปรุงระบบ Template ให้แยกตามราย Task
    - [x] 8.3 ทดสอบการรันครั้งเดียวเพื่อออกไฟล์ elements.csv และ properties.csv พร้อมกัน
- [ ] **Phase 9: Advanced Project-based GUI (User-Friendly)**
    - [x] 9.1 สร้าง Git Branch `feature/advanced-gui` และโครงสร้างโปรเจกต์ใหม่
    - [x] 9.2 พัฒนา "Task Manager" สำหรับ เพิ่ม/ลบ/แก้ไข Task ผ่าน GUI ทั้งหมด
    - [x] 9.3 พัฒนา "Template Editor" ในตัว (ไม่ต้องเปิด Notepad)
    - [x] 9.4 ปรับปรุง UI/UX (เพิ่ม Scrollbar ในหน้า Task Editor และระบบ Auto-fill ชื่อไฟล์)
    - [x] 9.5 เพิ่มระบบช่วยเหลือ (Guideline/Cheat Sheet) ใน Template Editor เพื่อให้ User ใช้งานง่าย
    - [x] 9.6 ระบบตรวจสอบความถูกต้องอัตโนมัติ (Validation) ก่อนรันงาน
    - [x] 9.7 แก้ไขการบันทึกไฟล์ Excel ให้เปิดได้ปกติ (บันทึกเป็นตารางจริง)
    - [x] 9.8 เพิ่มปุ่มเลือกประเภทไฟล์ Output (.csv, .xlsx, .json, .txt) ใน GUI
    - [x] 9.9 นำ .xlsx ออกจากตัวเลือก Output และปรับให้ทุกไฟล์บันทึกตาม Template 100%
    - [x] 9.10 เพิ่มระบบเลือกงาน (Multi-select) ในหน้าจอหลัก เพื่อสั่งรันเฉพาะงานที่ต้องการ
    - [ ] **Phase 10: Project Folder Management (Organization)**
    - [ ] 10.1 ปรับปรุง GUI ให้แนะนำและสร้างโครงสร้างโฟลเดอร์แยกตาม Project (projects/Name/...)
    - [ ] 10.2 ระบบจัดระเบียบไฟล์ Template ให้อยู่ในโฟลเดอร์ย่อยของแต่ละงาน
    - [x] 10.3 อัปเดตการแสดงผลในหน้าหลักให้ดูง่ายขึ้นตามชื่อโฟลเดอร์
    - [x] 10.4 เพิ่มคำอธิบายหน้าที่ของ Header, Body, Footer ในหน้า Guideline ให้ User เข้าใจง่าย
    - [x] 10.5 เพิ่มคำอธิบาย "โหมดแนวตั้ง (Transpose)" อย่างละเอียดในหน้า Guideline
- [x] **Phase 11: UI Overhaul & Modernization**
    - [x] 11.1 เปลี่ยน UI เป็นภาษาอังกฤษทั้งหมด (ยกเว้น Guideline)
    - [x] 11.2 ปรับปรุงความสวยงามด้วย Modern Style (Flat Design & Better Spacing)
    - [x] 11.3 ทดสอบการใช้งานหน้าจอใหม่
    - [x] 11.4 แก้ไขสีตัวอักษรในปุ่มและคืนค่า Guideline ภาษาไทยแบบเดิม
    - [x] 11.5 เพิ่มชื่อผู้พัฒนา "นายศราวุฒิ สิทธารถ" ในหน้าจอหลัก






---

## กฎเหล็กในการทำงาน (Strict Rules)
1. **Plan First:** ต้องตรวจสอบและอัปเดต `plan.md` ก่อนเริ่มทำ Task เสมอ
2. **Update Status:** เมื่อ Task ใดเสร็จสิ้น ให้เปลี่ยน `[ ]` เป็น `[x]` ใน `plan.md` ทันที
3. **Atomic Changes:** ทำทีละ Task เพื่อป้องกันบั๊กสะสม
4. **Validation:** ทุกครั้งที่จบ Task ต้องมีการตรวจสอบความถูกต้องของโค้ด
