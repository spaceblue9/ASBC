import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from ASBC_Main import ASBCConverter
import configparser
import os
import shutil

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

class TextEditor(tk.Toplevel):
    def __init__(self, parent_window, file_path_var, default_name="template.txt"):
        super().__init__(parent_window)
        self.file_path_var = file_path_var
        self.file_path = file_path_var.get()
        self.default_name = default_name
        self.title(f"Template Editor")
        self.geometry("900x600")
        self.grab_set()
        self.create_widgets()
        self.load_content()
        
    def create_widgets(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        editor_frame = ttk.Frame(paned)
        paned.add(editor_frame, weight=3)
        self.text_area = tk.Text(editor_frame, wrap=tk.NONE, font=("Courier New", 11), undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(self.text_area, orient="vertical", command=self.text_area.yview)
        hsb = ttk.Scrollbar(self.text_area, orient="horizontal", command=self.text_area.xview)
        self.text_area.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        help_frame = ttk.LabelFrame(paned, text=" 💡 วิธีเขียนแบบง่ายๆ (อ่านจบทำได้เลย!) ", padding=15)
        paned.add(help_frame, weight=1)
        
        help_text = (
            "ยินดีต้อนรับครับ! มาดูวิธีเขียนกันนะ:\n\n"
            "📂 [ 1. เข้าใจส่วนประกอบ ]\n"
            "- ส่วนหัว (Header): พิมพ์ครั้งเดียวบนสุด\n"
            "- เนื้อหา (Body): พิมพ์ซ้ำตามจำนวนแถวใน Excel\n"
            "- ส่วนท้าย (Footer): พิมพ์ครั้งเดียวล่างสุด\n\n"
            "🌟 [ 2. วิธีดึงข้อมูลจาก Excel ]\n"
            "อยากเอาข้อมูลช่องไหนมาใส่ ให้พิมพ์ชื่อหัวข้อ\n"
            "ไว้ในเครื่องหมาย {{ }}\n"
            "เช่น... {{ CI Name }}, {{ OS }}\n\n"
            "✨ [ 3. คำสั่งพิเศษ (โหมดแนวตั้ง) ]\n"
            "ใช้ 3 คำนี้ดึงข้อมูลได้ทันที:\n"
            "{{ ID }} -> เลขที่บรรทัด\n"
            "{{ Key }} -> ชื่อหัวข้อใน Excel\n"
            "{{ Value }} -> ข้อมูลในช่องนั้นๆ\n\n"
            "📝 [ 4. ตัวอย่างการเขียน ]\n"
            "ชื่อเครื่อง: {{ CI Name }}\n"
            "ระบบที่ใช้: {{ OS }}\n"
            "-----------------------------\n\n"
            "🔄 [ 5. โหมดแนวตั้ง (Transpose) ]\n"
            "โหมดนี้คือการ 'จับตารางแนวนอนมาตั้งขึ้น'\n"
            "จากเดิม 1 คน มี 1 บรรทัดยาวๆ...\n"
            "จะกลายเป็น 1 คน มีหลายๆ บรรทัดแทนครับ\n\n"
            "เช่น ถ้าใน Excel มีหัวข้อ ชื่อ, อายุ, เพศ\n"
            "โปรแกรมจะพิมพ์ Body ซ้ำ 3 ครั้งต่อ 1 คน:\n"
            "- รอบที่ 1: {{ Key }} คือ 'ชื่อ'\n"
            "- รอบที่ 2: {{ Key }} คือ 'อายุ'\n"
            "- รอบที่ 3: {{ Key }} คือ 'เพศ'\n\n"
            "💡 สรุปคือ: ใช้ {{ Key }} เพื่อดึง 'ชื่อหัวข้อ'\n"
            "และใช้ {{ Value }} เพื่อดึง 'ข้อมูลในช่อง' ครับ\n\n"
            "⚠️ ข้อควรระวัง:\n"
            "- ชื่อใน {{ }} ต้องตรงกับหัวข้อใน Excel\n"
            "- ตัวพิมพ์เล็ก-ใหญ่ ใช้แบบไหนก็ได้ครับ"
        )
        tk.Label(help_frame, text=help_text, justify=tk.LEFT, anchor="nw", 
                 font=("Tahoma", 10), wraplength=250, foreground="#2c3e50").pack(fill=tk.BOTH, expand=True)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="💾 Save & Close", command=self.save_content, padding=5).pack(side=tk.RIGHT, padx=20)
        
    def load_content(self):
        if self.file_path and os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.text_area.insert(tk.END, f.read())
            except Exception as e: messagebox.showerror("Error", str(e))
                
    def save_content(self):
        if not self.file_path:
            self.file_path = filedialog.asksaveasfilename(initialfile=self.default_name, defaultextension=".txt")
            if not self.file_path: return
            self.file_path_var.set(self.file_path)
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f: f.write(self.text_area.get("1.0", tk.END))
            messagebox.showinfo("Success", "บันทึกเรียบร้อย")
            self.destroy()
        except Exception as e: messagebox.showerror("Error", str(e))

class TaskEditor(tk.Toplevel):
    def __init__(self, main_app, section=None):
        super().__init__(main_app.root)
        self.main_app = main_app
        self.config = main_app.config
        self.section = section
        self.title("Project Task Editor")
        self.geometry("850x700")
        self.grab_set()
        
        # ตั้งค่าตัวแปร
        init_name = section[5:] if section else ""
        self.vars = {
            'name': tk.StringVar(value=init_name),
            'file_path': tk.StringVar(value=self.config.get(section, 'file_path', fallback="") if section else ""),
            'header_file': tk.StringVar(value=self.config.get(section, 'header_file', fallback="") if section else ""),
            'body_file': tk.StringVar(value=self.config.get(section, 'body_file', fallback="") if section else ""),
            'footer_file': tk.StringVar(value=self.config.get(section, 'footer_file', fallback="") if section else ""),
            'output_name': tk.StringVar(value=self.config.get(section, 'output_name', fallback="") if section else ""),
            'melt_id_vars': tk.StringVar(value=self.config.get(section, 'melt_id_vars', fallback="") if section else "")
        }
        
        # ตรวจจับการเปลี่ยนชื่อ Task เพื่อแนะนำ Path อัตโนมัติ
        self.vars['name'].trace_add("write", self.update_suggested_paths)

        self.scroll_container = ScrollableFrame(self)
        self.scroll_container.pack(fill="both", expand=True)
        self.main_content = self.scroll_container.scrollable_frame
        self.create_widgets()
        
    def update_suggested_paths(self, *args):
        # แนะนำโครงสร้างโฟลเดอร์ตามชื่อ Task
        name = self.vars['name'].get().strip()
        if name and not self.section: # เฉพาะตอนสร้างใหม่
            p_root = f"projects/{name}"
            self.vars['header_file'].set(f"{p_root}/templates/header.txt")
            self.vars['body_file'].set(f"{p_root}/templates/body.txt")
            self.vars['footer_file'].set(f"{p_root}/templates/footer.txt")
            self.vars['output_name'].set(f"{p_root}/output/result.csv")

    def create_widgets(self):
        pad = {'padx': 10, 'pady': 10}
        
        # Section 1
        g1 = ttk.LabelFrame(self.main_content, text=" 1. ตั้งชื่อโปรเจกต์ (Project Name) ", padding=15)
        g1.pack(fill="x", **pad)
        ttk.Label(g1, text="ชื่อ Project:").grid(row=0, column=0, sticky="w")
        ttk.Entry(g1, textvariable=self.vars['name'], width=50).grid(row=0, column=1, padx=10)
        ttk.Label(g1, text="* ระบบจะสร้างโฟลเดอร์แยกตามชื่อนี้ให้อัตโนมัติ", font=("Arial", 8, "italic"), foreground="blue").grid(row=1, column=1, sticky="w", padx=10)

        # Section 2
        g2 = ttk.LabelFrame(self.main_content, text=" 2. ไฟล์ต้นทางและรูปแบบ (Input & Templates) ", padding=15)
        g2.pack(fill="x", **pad)
        
        ttk.Label(g2, text="ไฟล์ Excel ต้นทาง:").grid(row=0, column=0, sticky="w")
        ttk.Entry(g2, textvariable=self.vars['file_path'], width=50).grid(row=0, column=1, padx=10)
        ttk.Button(g2, text="เลือกไฟล์", command=lambda: self.browse('file_path')).grid(row=0, column=2)

        self.add_row(g2, "ส่วนหัว (Header):", 'header_file', 1, "header.txt")
        self.add_row(g2, "เนื้อหา (Body):", 'body_file', 2, "body.txt")
        self.add_row(g2, "ส่วนท้าย (Footer):", 'footer_file', 3, "footer.txt")

        # Section 3
        g3 = ttk.LabelFrame(self.main_content, text=" 3. การส่งออก (Output) ", padding=15)
        g3.pack(fill="x", **pad)
        ttk.Label(g3, text="บันทึกไฟล์ไปที่:").grid(row=0, column=0, sticky="w")
        ttk.Entry(g3, textvariable=self.vars['output_name'], width=50).grid(row=0, column=1, padx=10)
        ttk.Button(g3, text="เปลี่ยนที่เซฟ", command=self.browse_output).grid(row=0, column=2)
        
        ttk.Label(g3, text="โหมด Transpose:").grid(row=1, column=0, sticky="w", pady=(10,0))
        ttk.Entry(g3, textvariable=self.vars['melt_id_vars'], width=50).grid(row=1, column=1, padx=10, pady=(10,0))
        
        # Save Task Button
        btn_frame = ttk.Frame(self.main_content)
        btn_frame.pack(fill="x", pady=20)
        ttk.Button(btn_frame, text="🚀 บันทึก Project นี้", command=self.save, padding=10).pack(side=tk.RIGHT, padx=20)

    def add_row(self, parent, label, var_key, row, def_name):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(parent, textvariable=self.vars[var_key], width=50).grid(row=row, column=1, padx=10, pady=5)
        bs = ttk.Frame(parent)
        bs.grid(row=row, column=2)
        ttk.Button(bs, text="📁", width=3, command=lambda: self.browse(var_key)).pack(side=tk.LEFT, padx=2)
        ttk.Button(bs, text="📝", width=3, command=lambda: TextEditor(self, self.vars[var_key], def_name)).pack(side=tk.LEFT, padx=2)

    def browse(self, var_key):
        f = filedialog.askopenfilename()
        if f: self.vars[var_key].set(f)

    def browse_output(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")])
        if f: self.vars['output_name'].set(f)

    def save(self):
        name = self.vars['name'].get().strip()
        if not name: return messagebox.showerror("Error", "ระบุชื่อโปรเจกต์")
        
        # สร้างโฟลเดอร์พื้นฐาน
        p_root = f"projects/{name}"
        os.makedirs(f"{p_root}/input", exist_ok=True)
        os.makedirs(f"{p_root}/templates", exist_ok=True)
        os.makedirs(f"{p_root}/output", exist_ok=True)

        new_sec = f"Task:{name}"
        if self.section and self.section != new_sec: self.config.remove_section(self.section)
        if not self.config.has_section(new_sec): self.config.add_section(new_sec)
        for k, v in self.vars.items():
            if k != 'name': self.config.set(new_sec, k, v.get())
        
        self.main_app.save_config_to_file()
        self.main_app.refresh_task_list()
        self.destroy()

class ASBCGui:
    def __init__(self, root):
        self.root = root
        self.root.title("ASBC Project-Based ScriptBot")
        self.root.geometry("1000x750")
        self.config_path = 'ASBC-Config.ini'
        self.converter = ASBCConverter(self.config_path)
        self.config = self.converter.config
        self.create_widgets()
        
    def create_widgets(self):
        main = ttk.Frame(self.root, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        t_fr = ttk.Frame(main)
        t_fr.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(t_fr, text="ASBC Project Manager", font=("Arial", 22, "bold")).pack(side=tk.LEFT)
        
        l_fr = ttk.Frame(main)
        l_fr.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(l_fr, columns=("N", "O", "M"), show='headings', selectmode='extended')
        self.tree.heading("N", text="ชื่อ Project / Task"); self.tree.heading("O", text="ตำแหน่งไฟล์ผลลัพธ์"); self.tree.heading("M", text="โหมด")
        self.tree.column("N", width=200); self.tree.column("O", width=400); self.tree.column("M", width=100)
        vsb = ttk.Scrollbar(l_fr, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.refresh_task_list()
        
        c_fr = ttk.Frame(main)
        c_fr.pack(fill=tk.X, pady=20)
        ttk.Button(c_fr, text="➕ สร้าง Project ใหม่", command=lambda: TaskEditor(self)).pack(side=tk.LEFT, padx=5)
        ttk.Button(c_fr, text="✏️ แก้ไขโปรเจกต์", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(c_fr, text="❌ ลบโปรเจกต์", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        
        run_fr = ttk.LabelFrame(main, text=" การรันงาน ", padding=15)
        run_fr.pack(fill=tk.X)
        ttk.Button(run_fr, text="🚀 รัน Project ที่เลือกไว้ (RUN SELECTED PROJECTS)", command=self.run_selected, padding=10).pack(fill=tk.X)

    def refresh_task_list(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        self.config.read(self.config_path, encoding='utf-8')
        for s in self.config.sections():
            if s.startswith('Task:'):
                m = "Transpose" if self.config.get(s, 'melt_id_vars') else "Normal"
                self.tree.insert("", tk.END, iid=s, values=(s[5:], self.config.get(s, 'output_name', fallback='-'), m))

    def edit_task(self):
        sel = self.tree.selection()
        if sel: TaskEditor(self, sel[0])
    def delete_task(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Confirm", "ยืนยันการลบ?"):
            for s in sel: self.config.remove_section(s)
            self.save_config_to_file(); self.refresh_task_list()
    def save_config_to_file(self):
        with open(self.config_path, 'w', encoding='utf-8') as f: self.config.write(f)
    def run_selected(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("Warning", "เลือกงานก่อนรัน")
        errs = self.converter.validate_tasks()
        sel_errs = [e for e in errs if any(f"[{s[5:]}]" in e for s in sel)]
        if sel_errs: return messagebox.showerror("Error", "\n".join(sel_errs))
        try:
            for s in sel: self.converter.process_task(s[5:], dict(self.config[s]))
            messagebox.showinfo("Success", "แปลงไฟล์เรียบร้อย!")
        except Exception as e: messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ASBCGui(root)
    root.mainloop()
