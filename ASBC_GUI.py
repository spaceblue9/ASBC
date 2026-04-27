import tkinter as tk
from tkinter import messagebox, ttk
from ASBC_Main import ASBCConverter
import os

class ASBCGui:
    def __init__(self, root):
        self.root = root
        self.root.title("ASBC - Advanced ScriptBot Converter (Batch Version)")
        self.root.geometry("700x500")
        
        self.config_path = 'ASBC-Config.ini'
        self.load_engine()
        self.create_widgets()
        
    def load_engine(self):
        try:
            self.converter = ASBCConverter(self.config_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load config: {e}")
            self.root.destroy()

    def create_widgets(self):
        # Main Container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="ASBC Batch Script Generator", font=("Arial", 16, "bold")).pack(pady=(0, 10))
        ttk.Label(main_frame, text=f"Config Path: {os.path.abspath(self.config_path)}", font=("Arial", 8)).pack(pady=(0, 20))

        # Task List Label
        ttk.Label(main_frame, text="รายการงานที่พบใน Config (Tasks):", font=("Arial", 10, "bold")).pack(anchor="w")

        # Treeview (Table) to show tasks
        self.tree = ttk.Treeview(main_frame, columns=("Input", "Output", "Mode"), show='headings', height=10)
        self.tree.heading("Input", text="Input File")
        self.tree.heading("Output", text="Output Name")
        self.tree.heading("Mode", text="Mode")
        self.tree.column("Input", width=250)
        self.tree.column("Output", width=200)
        self.tree.column("Mode", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        self.refresh_task_list()

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="โหลดข้อมูลใหม่ (Refresh)", command=self.refresh_task_list).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="รันทุกงานพร้อมกัน (RUN ALL TASKS)", command=self.run_all).pack(side=tk.LEFT, padx=10)

    def refresh_task_list(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Reload config
        self.converter.config.read(self.config_path, encoding='utf-8')
        
        # Add tasks to treeview
        for section in self.converter.config.sections():
            if section.startswith('Task:'):
                config = self.converter.config[section]
                mode = "Transpose" if config.get('melt_id_vars') else "Normal"
                self.tree.insert("", tk.END, values=(
                    config.get('file_path', '-'),
                    config.get('output_name', '-'),
                    mode
                ))

    def run_all(self):
        try:
            # ใช้ Engine จาก ASBC_Main รันงานทั้งหมด
            self.converter.run_all_tasks()
            messagebox.showinfo("Success", "ประมวลผลทุกงานเสร็จสมบูรณ์!\nตรวจสอบไฟล์ได้ที่โฟลเดอร์ output")
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดระหว่างรัน: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    # ปรับแต่งธีมให้ดูทันสมัยขึ้น
    style = ttk.Style()
    if 'vista' in style.theme_names():
        style.theme_use('vista')
    
    app = ASBCGui(root)
    root.mainloop()
