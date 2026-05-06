# ⚡ ASBC Converter Pro

**Advanced ScriptBot Converter** — โปรแกรมแปลงข้อมูลจาก Excel / CSV ให้เป็นไฟล์ Output ตามรูปแบบ Template ที่กำหนดเองได้ 100%

> พัฒนาโดย **นายศราวุฒิ สิทธารถ** &nbsp;|&nbsp; Version 2.0 &nbsp;|&nbsp; Python 3.x + Tkinter

---

## ✨ ความสามารถหลัก

| ความสามารถ | รายละเอียด |
|------------|-----------|
| 📥 **รับไฟล์ได้หลายรูปแบบ** | `.xlsx`, `.xls`, `.csv` พร้อมเลือก Sheet ได้ |
| 📤 **ส่งออกได้ทุกรูปแบบ** | `.csv`, `.json`, `.txt`, `.sidata` และอื่นๆ |
| 📝 **Template Engine** | กำหนด Header / Body / Footer เองได้อิสระ |
| 🔄 **Transpose Mode** | แปลงตารางแนวนอน → คู่ Key-Value แนวตั้ง |
| 🔙 **Un-Transpose (Reverse Melt)** | กู้คืนข้อมูลจาก Reverse Melt กลับเป็นตารางปกติ |
| 🎛️ **Filter Rules** | กรองข้อมูลก่อนแปลงด้วยเงื่อนไข 9 แบบ (AND Logic) |
| 📋 **Multi-Project** | จัดการหลาย Project พร้อมกัน รันทีเดียวได้หลายงาน |
| 🔒 **License Protection** | 1 License = 1 เครื่อง ป้องกันการใช้งานโดยไม่ได้รับอนุญาต |

---

## 🖥️ หน้าตาโปรแกรม

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚡ ASBC Converter Pro                              v2.0        │  ← Header
├─────────────────────────────────────────────────────────────────┤
│  📋 Active Projects              [➕ New] [✏ Edit] [🗑 Delete]  │  ← Toolbar
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📁 Project Name  │  📂 Output Path  │  ⚙ Mode         │   │  ← Project List
│  │  Archi-elements   │  .../elements.csv │  📋 Normal      │   │
│  │  Archi-properties │  .../props.csv    │  🔄 Transpose   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ⚙ Execution Panel          [🚀 RUN SELECTED PROJECTS]         │  ← Run Panel
├─────────────────────────────────────────────────────────────────┤
│  ✅ Ready — 2 project(s) loaded        ASBC Converter Pro © 2025│  ← Status Bar
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔒 การลงทะเบียน (License Activation)

โปรแกรมต้องลงทะเบียนก่อนใช้งาน **ทำเพียงครั้งเดียวต่อเครื่อง**

### ขั้นตอนสำหรับผู้ใช้

```
1. เปิดโปรแกรม → หน้า Activation จะขึ้นมาอัตโนมัติ
2. กด [📋 Copy] เพื่อคัดลอก Machine ID
3. ส่ง Machine ID ให้ผู้พัฒนา (Line / Email)
4. รับ License Key กลับมา (รูปแบบ XXXXX-XXXXX-XXXXX-XXXXX)
5. วาง License Key ในช่อง Step 2 แล้วกด [🔓 Activate License]
6. ✅ ลงทะเบียนสำเร็จ — ใช้งานได้ปกติ ไม่ต้องทำซ้ำ
```

> ⚠️ License ผูกกับเครื่องนี้เครื่องเดียว หากเปลี่ยนเครื่องต้องขอ License ใหม่

---

## 🚀 วิธีใช้งาน

### 1. สร้าง Project ใหม่

กดปุ่ม **➕ New Project** แล้วกรอกข้อมูล:

| ฟิลด์ | คำอธิบาย |
|-------|---------|
| **Project Name** | ชื่อ Project (Folder จะถูกสร้างอัตโนมัติ) |
| **Source Excel File** | เลือกไฟล์ข้อมูลต้นทาง (.xlsx / .xls / .csv) |
| **Sheet Name / Index** | เลือก Sheet (โหลดรายชื่ออัตโนมัติเมื่อเลือกไฟล์) |
| **Header Template** | Template สำหรับส่วนหัว (แสดงครั้งเดียว) |
| **Body Template** | Template สำหรับเนื้อหา (วนซ้ำทุกแถวข้อมูล) |
| **Footer Template** | Template สำหรับส่วนท้าย (แสดงครั้งเดียว) |
| **Output File Path** | Path ของไฟล์ผลลัพธ์ที่ต้องการสร้าง |
| **Transpose Column ID** | ชื่อคอลัมน์ ID สำหรับโหมด Transpose (เว้นว่างถ้าไม่ใช้) |
| **Filter Rules** | กฎกรองข้อมูล (เช่น `OS:eq:Windows;Status:eq:Active`) |

### กฎกรองข้อมูล (Filter Rules)

ใช้กรองข้อมูลเฉพาะแถวที่ต้องการก่อนนำไปแปลง Template:

```
Field:Operator:Value
```

| Operator | ความหมาย | ตัวอย่าง |
|----------|---------|---------|
| `eq` | เท่ากับ | `OS:eq:Windows` |
| `neq` | ไม่เท่ากับ | `Status:neq:Inactive` |
| `contains` | มีข้อความ | `Name:contains:Server` |
| `not_contains` | ไม่มีข้อความ | `Name:not_contains:Test` |
| `sw` | ขึ้นต้นด้วย | `ID:sw:SRV` |
| `ew` | ลงท้ายด้วย | `Name:ew:DB` |
| `gt` | มากกว่า | `CPU:gt:4` |
| `lt` | น้อยกว่า | `RAM:lt:16` |
| `in` | อยู่ในรายการ | `OS:in:Windows,Linux` |

> 🔗 กฎหลายข้อใช้ **AND Logic** — ทุกเงื่อนไขต้องเป็นจริง

### 2. เขียน Template

กดปุ่ม **✏ Edit** ที่หน้า Template Editor เพื่อแก้ไขแบบ inline

#### วิธีดึงข้อมูลจาก Excel

ใช้ `{{ ชื่อคอลัมน์ }}` ตามชื่อ Header ใน Excel:

```
D:\ASBC\projects\MyProject\templates\body.txt#L1-3
CI_NAME={{ CI Name }}
OS={{ OS Version }}
IP_ADDRESS={{ IP Address }}
```

#### Variable พิเศษ (Transpose Mode)

```
D:\ASBC\projects\MyProject\templates\body.txt#L1-1
{{ ID }},{{ Key }},{{ Value }}
```

| Variable | ความหมาย |
|----------|---------|
| `{{ ID }}` | หมายเลขแถว |
| `{{ Key }}` | ชื่อคอลัมน์จาก Excel |
| `{{ Value }}` | ข้อมูลในช่องนั้น |

#### Variable พิเศษ (Un-Transpose Mode)

ใช้เมื่อต้องการแปลงข้อมูล Reverse Melt กลับเป็นตารางปกติ:

| Variable | ความหมาย |
|----------|---------|
| `{{ Row_ID }}` | หมายเลขแถวเดิมก่อน Transpose |
| `{{ Column_Name }}` | ชื่อคอลัมน์เดิมที่กู้คืนมา |
| `{{ Row_Value }}` | ค่าข้อมูลในคอลัมน์นั้น |

### 3. รันโปรแกรม

1. เลือก Project ที่ต้องการ (คลิกเลือกได้หลาย Project พร้อมกัน)
2. กดปุ่ม **🚀 RUN SELECTED PROJECTS**
3. ไฟล์ผลลัพธ์จะถูกสร้างที่ Output Path ที่กำหนดไว้

---

## 📁 โครงสร้างโฟลเดอร์

```
ASBC/
├── ASBC_GUI.py              # โปรแกรมหลัก (GUI)
├── ASBC_Main.py             # Core Engine
├── license_manager.py       # ระบบ License
├── activate_dialog.py       # หน้าจอ Activation
├── keygen.py                # ⚠️ เครื่องมือออก Key [ผู้พัฒนาเท่านั้น]
├── build.bat                # Script สร้าง .exe
├── ASBC-Config.ini          # ไฟล์ Config (บันทึก Project ทั้งหมด)
├── ea.ico                   # ไอคอนโปรแกรม
└── projects/                # โฟลเดอร์ Project
    └── MyProject/
        ├── input/           # วางไฟล์ Excel ต้นทางที่นี่
        ├── templates/       # ไฟล์ Template
        │   ├── header.txt
        │   ├── body.txt
        │   └── footer.txt
        └── output/          # ไฟล์ผลลัพธ์จะออกมาที่นี่
```

---

## ⚙️ ไฟล์ Config (ASBC-Config.ini)

โปรแกรมบันทึกการตั้งค่าในรูปแบบ INI โดยอัตโนมัติ ไม่จำเป็นต้องแก้ไขมือ แต่สามารถดูโครงสร้างได้ดังนี้:

```ini
D:\ASBC\ASBC-Config.ini#L1-9
[Task:ชื่อ-Project]
file_path    = path/to/input.xlsx
sheet_name   = Sheet1
header_file  = path/to/header.txt
body_file    = path/to/body.txt
footer_file  =
output_name  = path/to/output.csv
melt_id_vars =
filter_rules = OS:eq:Windows;Status:eq:Active
encoding     = utf-8
```

---

## 🔧 การ Build เป็น .exe

```bat
# รัน build.bat เพื่อ compile โปรแกรมเป็น Standalone .exe
build.bat
```

ไฟล์ `.exe` จะอยู่ที่ `dist\ASBC Converter Pro.exe`

> ⚠️ **อย่าแจก `keygen.py` ให้ลูกค้า** — เก็บไว้เฉพาะผู้พัฒนาเท่านั้น

---

## 🛠️ สำหรับนักพัฒนา

### Requirements

```bash
pip install pandas openpyxl xlrd pyinstaller
```

### รันจาก Source

```bash
python ASBC_GUI.py
```

### ออก License Key (Developer Only)

```bash
python keygen.py
# ใส่ Machine ID ของลูกค้า → กด Generate → ได้ License Key
```

### Architecture

```
ASBC_GUI.py
  └── license_manager.py   # HMAC-SHA256 + Machine Fingerprint (MAC+Hostname)
  └── activate_dialog.py   # Activation UI
  └── ASBC_Main.py         # Core: load → template → save
        └── ASBC-Config.ini
```

---

## ❓ คำถามที่พบบ่อย

**Q: ภาษาไทยในไฟล์ Output อ่านไม่ออก?**
> เพิ่ม `encoding = cp874` ในหน้า Edit Project

**Q: รันแล้ว Error "ไม่พบไฟล์"?**
> ตรวจสอบ Path ของไฟล์ใน Edit Project ว่าถูกต้องและไฟล์ยังอยู่ในตำแหน่งนั้น

**Q: เปลี่ยนเครื่องใหม่ต้องทำอย่างไร?**
> แจ้ง Machine ID ของเครื่องใหม่ให้ผู้พัฒนา เพื่อออก License Key ใหม่

**Q: ตัวพิมพ์เล็ก-ใหญ่ใน `{{ }}` สำคัญไหม?**
> ไม่สำคัญ — `{{ CI Name }}`, `{{ ci name }}`, `{{ CI NAME }}` ทำงานเหมือนกัน

**Q: ไฟล์ Excel เปิดค้างอยู่แล้วรัน Error?**
> ปิดไฟล์ Excel ทั้งต้นทางและปลายทางก่อนกด RUN

**Q: Filter Rules ไม่ทำงาน?**
> ตรวจสอบชื่อ Field ให้ตรงกับ Header ใน Excel (ไม่สนใจตัวพิมพ์เล็ก-ใหญ่) และใช้ Operator ที่ถูกต้อง เช่น `eq`, `contains`, `sw`

**Q: อยากได้ข้อมูลเฉพาะบางแถวมาแปลง?**
> ใช้ Filter Rules ในหน้า Edit Project เช่น `Region:eq:BKK;Type:eq:Server` จะดึงเฉพาะแถวที่ Region=BKK **และ** Type=Server

**Q: Un-Transpose ใช้อะไรได้บ้าง?**
> ใช้เมื่อข้อมูลต้นทางถูก Reverse Melt มาแล้วต้องการกู้คืนกลับเป็นตารางปกติ กำหนด Transpose Column ID แล้วเลือกโหมด Un-Transpose

---

## 📄 License

โปรแกรมนี้เป็น **Proprietary Software** สงวนลิขสิทธิ์ทุกประการ
การใช้งานต้องได้รับ License Key จากผู้พัฒนาเท่านั้น

© 2025 **นายศราวุฒิ สิทธารถ** — All rights reserved.
