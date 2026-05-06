import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd

from ASBC_Main import ASBCConverter

# ══════════════════════════════════════════════════════════════════════════════
#  APP METADATA
# ══════════════════════════════════════════════════════════════════════════════
APP_NAME = "ASBC Converter Pro"
APP_SUB = "Advanced ScriptBot Converter"
APP_VER = "v2.0"
DEVELOPER = "นายศราวุฒิ สิทธารถ"

# ══════════════════════════════════════════════════════════════════════════════
#  COLOR PALETTE  (Modern Professional Dark/Light Hybrid)
# ══════════════════════════════════════════════════════════════════════════════
C = {
    # Backgrounds
    "bg": "#f1f5f9",  # Page background (light slate)
    "header": "#0f172a",  # Dark navy header
    "card": "#ffffff",  # White card
    "card_alt": "#f8fafc",  # Slightly off-white
    "status_bg": "#1e293b",  # Dark status bar
    "badge_bg": "#1e3a8a",  # Dark blue badge
    # Brand Colors
    "primary": "#2563eb",  # Primary blue
    "pri_h": "#1d4ed8",  # Blue hover
    "pri_lt": "#eff6ff",  # Light blue tint
    "success": "#059669",  # Emerald green
    "suc_h": "#047857",  # Green hover
    "suc_lt": "#ecfdf5",  # Light green tint
    "danger": "#dc2626",  # Red
    "dan_h": "#b91c1c",  # Red hover
    "dan_lt": "#fef2f2",  # Light red tint
    "warning": "#d97706",  # Amber
    "accent": "#7c3aed",  # Purple accent
    # Text
    "text": "#0f172a",  # Primary text
    "text_s": "#64748b",  # Secondary text
    "text_w": "#ffffff",  # White text
    "text_m": "#94a3b8",  # Muted text
    # Borders & Separators
    "border": "#e2e8f0",  # Default border
    "divider": "#cbd5e1",  # Divider line
    "sep_blue": "#2563eb",  # Blue accent separator
    # Table
    "row_a": "#f8fafc",  # Alternating row A
    "row_b": "#ffffff",  # Alternating row B
    "sel": "#dbeafe",  # Selection background
    "sel_fg": "#1e40af",  # Selection text
    # Tags
    "tag_n_bg": "#d1fae5",  # Normal mode tag bg
    "tag_n_fg": "#065f46",  # Normal mode tag text
    "tag_t_bg": "#fef3c7",  # Transpose mode tag bg
    "tag_t_fg": "#92400e",  # Transpose mode tag text
}

FF = "Segoe UI"  # Primary font family
FM = "Consolas"  # Monospace font


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER: Flat Button Factory (tk.Label-based for full style control)
# ══════════════════════════════════════════════════════════════════════════════
def flat_btn(
    parent,
    text,
    command,
    bg,
    hover_bg,
    fg="white",
    padx=14,
    pady=7,
    font_size=10,
    bold=False,
    width=None,
):
    """Create a modern flat button with hover effect."""
    weight = "bold" if bold else "normal"
    cfg = dict(
        text=text,
        bg=bg,
        fg=fg,
        font=(FF, font_size, weight),
        padx=padx,
        pady=pady,
        cursor="hand2",
        relief="flat",
    )
    if width:
        cfg["width"] = width
    btn = tk.Label(parent, **cfg)
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
    btn.bind("<Button-1>", lambda e: command())
    return btn


# ══════════════════════════════════════════════════════════════════════════════
#  SCROLLABLE FRAME
# ══════════════════════════════════════════════════════════════════════════════
class ScrollableFrame(tk.Frame):
    """A vertically scrollable container with proper width propagation."""

    def __init__(self, parent, bg=None, **kwargs):
        bg = bg or C["bg"]
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        # Update scrollregion when content changes
        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        # KEY FIX: Stretch inner frame to fill canvas width
        self.canvas.bind(
            "<Configure>", lambda e: self.canvas.itemconfig(self._win_id, width=e.width)
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.inner.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# ══════════════════════════════════════════════════════════════════════════════
#  TEXT / TEMPLATE EDITOR
# ══════════════════════════════════════════════════════════════════════════════
class TextEditor(tk.Toplevel):
    """Dark-themed template editor with syntax-friendly styling."""

    def __init__(self, parent_window, file_path_var, default_name="template.txt"):
        super().__init__(parent_window)
        self.file_path_var = file_path_var
        self.file_path = file_path_var.get()
        self.default_name = default_name
        self.title(f"Template Editor — {default_name}")
        self.geometry("1080x700")
        self.configure(bg=C["bg"])
        self.minsize(800, 500)
        self.grab_set()
        self._build_ui()
        self._load_content()

    # ── UI Construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_footer()  # ← pack to bottom FIRST (same fix as run panel)
        self._build_body()  # ← then body fills remaining middle space

    def _build_header(self):
        hdr = tk.Frame(self, bg=C["header"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=C["header"])
        left.pack(side="left", padx=20, pady=12)

        icon_box = tk.Frame(left, bg="#7c3aed", width=32, height=32)
        icon_box.pack_propagate(False)
        icon_box.pack(side="left", padx=(0, 10))
        tk.Label(icon_box, text="✏", bg="#7c3aed", fg="white", font=(FF, 13)).pack(
            expand=True
        )

        tk.Label(
            left,
            text="Template Editor",
            bg=C["header"],
            fg=C["text_w"],
            font=(FF, 13, "bold"),
        ).pack(side="left")

        right = tk.Frame(hdr, bg=C["header"])
        right.pack(side="right", padx=20, pady=12)
        tk.Label(
            right,
            text=f"  {self.default_name}  ",
            bg="#374151",
            fg="#e5e7eb",
            font=(FF, 9),
            padx=8,
            pady=3,
        ).pack(side="right")

    def _build_body(self):
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=14, pady=14)

        # ── Left: Code Editor ──
        editor_wrap = tk.Frame(
            body, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        editor_wrap.pack(side="left", fill="both", expand=True)

        editor_top = tk.Frame(editor_wrap, bg="#1e2030", height=34)
        editor_top.pack(fill="x")
        editor_top.pack_propagate(False)
        tk.Label(
            editor_top,
            text="  📄  Content",
            bg="#1e2030",
            fg="#a6adc8",
            font=(FF, 9, "bold"),
        ).pack(side="left", pady=8)
        tk.Label(
            editor_top, text="UTF-8", bg="#1e2030", fg="#585b70", font=(FF, 8)
        ).pack(side="right", padx=12)

        text_frame = tk.Frame(editor_wrap, bg="#1e1e2e")
        text_frame.pack(fill="both", expand=True)

        self.text_area = tk.Text(
            text_frame,
            wrap=tk.NONE,
            font=(FM, 12),
            bg="#1e1e2e",
            fg="#cdd6f4",
            insertbackground="#f38ba8",
            selectbackground="#45475a",
            selectforeground="#cdd6f4",
            relief="flat",
            borderwidth=0,
            padx=16,
            pady=12,
            undo=True,
            spacing1=2,
            spacing3=2,
        )
        vsb = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        hsb = ttk.Scrollbar(
            text_frame, orient="horizontal", command=self.text_area.xview
        )
        self.text_area.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.text_area.pack(fill="both", expand=True)

        # ── Right: Help Panel ──
        help_wrap = tk.Frame(
            body,
            bg=C["card"],
            highlightbackground=C["border"],
            highlightthickness=1,
            width=310,
        )
        help_wrap.pack(side="right", fill="y", padx=(12, 0))
        help_wrap.pack_propagate(False)

        help_top = tk.Frame(help_wrap, bg="#1e293b", height=34)
        help_top.pack(fill="x")
        help_top.pack_propagate(False)
        tk.Label(
            help_top,
            text="  💡  Quick Reference",
            bg="#1e293b",
            fg="#e2e8f0",
            font=(FF, 9, "bold"),
        ).pack(side="left", pady=8)
        tk.Label(
            help_top,
            text=f"  {self.default_name}  ",
            bg="#334155",
            fg="#94a3b8",
            font=(FF, 8),
        ).pack(side="right", padx=8)

        scroll = ScrollableFrame(help_wrap, bg=C["card"])
        scroll.pack(fill="both", expand=True)
        c = scroll.inner

        def _badge(parent, text, bg, fg="white"):
            f = tk.Frame(parent, bg=bg)
            f.pack(fill="x")
            tk.Label(
                f, text=f"  {text}", bg=bg, fg=fg, font=(FF, 8, "bold"), pady=5
            ).pack(anchor="w")

        def _code(parent, text):
            f = tk.Frame(parent, bg="#1e2030")
            f.pack(fill="x", padx=10, pady=(0, 8))
            tk.Label(
                f,
                text=text,
                bg="#1e2030",
                fg="#a6e3a1",
                font=(FM, 9),
                justify="left",
                anchor="w",
                padx=10,
                pady=8,
            ).pack(fill="x")

        def _txt(parent, text, color=None):
            tk.Label(
                parent,
                text=text,
                bg=C["card"],
                fg=color or C["text_s"],
                font=(FF, 9),
                justify="left",
                anchor="w",
                padx=12,
                pady=3,
            ).pack(fill="x")

        def _div(parent):
            tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", pady=4)

        # ── Section 1: โครงสร้าง Template ─────────────────────────────────
        _badge(c, "📋  โครงสร้าง Template", C["primary"])
        tk.Frame(c, bg=C["primary"], height=2).pack(fill="x")

        for clr, name, desc in [
            ("#2563eb", "HEADER", "แสดง 1 ครั้ง — ด้านบนสุดของไฟล์"),
            ("#059669", "BODY  ", "วนซ้ำ — 1 รอบต่อ 1 แถวข้อมูล"),
            ("#7c3aed", "FOOTER", "แสดง 1 ครั้ง — ด้านล่างสุดของไฟล์"),
        ]:
            row = tk.Frame(c, bg=C["card"])
            row.pack(fill="x", padx=10, pady=2)
            badge = tk.Frame(row, bg=clr, width=60, height=28)
            badge.pack_propagate(False)
            badge.pack(side="left", padx=(0, 8))
            tk.Label(
                badge, text=name, bg=clr, fg="white", font=(FM, 8, "bold")
            ).place(relx=0.5, rely=0.5, anchor="center")
            tk.Label(
                row, text=desc, bg=C["card"], fg=C["text_s"], font=(FF, 8), anchor="w"
            ).pack(side="left")

        _div(c)

        # ── Section 2: วิธีดึงข้อมูล ────────────────────────────────────────
        _badge(c, "🌟  ดึงข้อมูลจาก Excel", "#059669")
        tk.Frame(c, bg="#059669", height=2).pack(fill="x")
        _txt(c, "ใช้ {{ชื่อคอลัมน์}} ใน Body Template")
        _txt(c, "ชื่อต้องตรงกับ Header ใน Excel")
        _txt(c, "⚠️ ห้ามมี space ก่อน }} เช่น {{ CI Name }} จะ Error", "#ef4444")
        _code(c, "{{CI Name}}\n{{OS Version}}\n{{IP Address}}")

        _div(c)

        # ── Section 3: ตัวอย่าง Body ─────────────────────────────────────────
        _badge(c, "📝  ตัวอย่าง Body Template", "#374151")
        tk.Frame(c, bg="#374151", height=2).pack(fill="x")
        _txt(c, "กรณีไฟล์ Excel มี column:\nCI Name, OS, IP Address")
        _code(
            c, "CI_NAME={{CI Name}}\nOS_TYPE={{OS}}\nIP_ADDR={{IP Address}}\n---"
        )

        _div(c)

        # ── Section 4: Variable พิเศษ ─────────────────────────────────────────
        _badge(c, "✨  Variable พิเศษ (Transpose Mode)", "#7c3aed")
        tk.Frame(c, bg="#7c3aed", height=2).pack(fill="x")
        _txt(c, "ใช้เมื่อตั้งค่า Transpose Column ID")
        for var, desc in [
            ("{{ID}}   ", "→ ค่า ID ของแถวนั้น"),
            ("{{Key}}  ", "→ ชื่อคอลัมน์จาก Excel"),
            ("{{Value}}", "→ ข้อมูลในช่องนั้น"),
        ]:
            row = tk.Frame(c, bg=C["card"])
            row.pack(fill="x", padx=10, pady=1)
            tk.Label(
                row,
                text=var,
                bg="#1e2030",
                fg="#89b4fa",
                font=(FM, 8, "bold"),
                padx=6,
                pady=3,
            ).pack(side="left", padx=(0, 6))
            tk.Label(row, text=desc, bg=C["card"], fg=C["text_s"], font=(FF, 8)).pack(
                side="left"
            )
        tk.Frame(c, bg=C["card"], height=6).pack()

        _div(c)

        # ── Section 5: Un-Transpose Mode ────────────────────────────────────────
        _badge(c, "↩️  Un-Transpose Mode (แปลงกลับ)", "#2563eb")
        tk.Frame(c, bg="#2563eb", height=2).pack(fill="x")
        _txt(c, "แปลงข้อมูล Key-Value กลับเป็นตารางปกติ")
        _txt(c, "ระบุ 3 ชื่อคอลัมน์ใน 'Un-Transpose Columns'")
        _code(c, "ID,Key,Value")
        _txt(c, "Body Template ใช้ {{ชื่อคอลัมน์}} ปกติ")
        _code(c, "{{ID}},{{Hostname}},{{OS}},{{IP}}")
        _txt(c, "ผลลัพธ์จะเป็นตารางแนวนอน:")
        _code(c, "1,SERVER-01,Windows,10.0.0.1\n2,SERVER-02,Linux,10.0.0.2")

        _div(c)

        # ── Section 6: ข้อควรระวัง ─────────────────────────────────────────────
        _badge(c, "⚠️  ข้อควรระวัง", "#b45309", "white")
        tk.Frame(c, bg="#b45309", height=2).pack(fill="x")
        for note in [
            "ชื่อใน {{ }} ต้องสะกดตรงกับ Excel",
            "ตัวพิมพ์เล็ก-ใหญ่ ใช้ได้ทั้งคู่",
            "กด 💾 Save & Close หรือ Ctrl+S",
        ]:
            _txt(c, f"  • {note}")
        tk.Frame(c, bg=C["card"], height=8).pack()

    def _build_footer(self):
        tk.Frame(self, bg=C["border"], height=1).pack(side="bottom", fill="x")
        footer = tk.Frame(self, bg=C["card_alt"], height=54)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        btn_row = tk.Frame(footer, bg=C["card_alt"])
        btn_row.pack(side="right", padx=18, pady=10)

        flat_btn(
            btn_row, "  Cancel  ", self.destroy, C["card_alt"], C["border"], C["text_s"]
        ).pack(side="left", padx=(0, 8))
        flat_btn(
            btn_row,
            "💾  Save & Close",
            self._save_content,
            C["success"],
            C["suc_h"],
            "white",
            bold=True,
        ).pack(side="left")

        tk.Label(
            footer,
            text="Ctrl+S to save  •  Changes are not auto-saved",
            bg=C["card_alt"],
            fg=C["text_m"],
            font=(FF, 8),
        ).pack(side="left", padx=18)

        # Keyboard shortcut
        self.bind("<Control-s>", lambda e: self._save_content())

    # ── Logic ────────────────────────────────────────────────────────────────
    def _load_content(self):
        if self.file_path and os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.text_area.insert(tk.END, f.read())
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self)

    def _save_content(self):
        if not self.file_path:
            self.file_path = filedialog.asksaveasfilename(
                initialfile=self.default_name, defaultextension=".txt", parent=self
            )
            if not self.file_path:
                return
            self.file_path_var.set(self.file_path)
        try:
            os.makedirs(os.path.dirname(self.file_path) or ".", exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.text_area.get("1.0", tk.END))
            messagebox.showinfo("Saved", "Template saved successfully.", parent=self)
            self.destroy()
        except Exception as ex:
            messagebox.showerror("Error", str(ex), parent=self)


# ══════════════════════════════════════════════════════════════════════════════
#  TASK / PROJECT EDITOR DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class TaskEditor(tk.Toplevel):
    """Modern project configuration dialog."""

    def __init__(self, main_app, section=None):
        super().__init__(main_app.root)
        self.main_app = main_app
        self.config = main_app.config
        self.section = section
        is_edit = section is not None

        self.title("Edit Project" if is_edit else "Create New Project")
        self.geometry("920x640")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.minsize(720, 500)
        self.grab_set()

        init_name = section[5:] if section else ""

        def _get(key, fallback=""):
            return (
                self.config.get(section, key, fallback=fallback)
                if section
                else fallback
            )

        self.vars = {
            "name": tk.StringVar(value=init_name),
            "file_path": tk.StringVar(value=_get("file_path")),
            "sheet_name": tk.StringVar(value=_get("sheet_name", "0")),
            "header_file": tk.StringVar(value=_get("header_file")),
            "body_file": tk.StringVar(value=_get("body_file")),
            "footer_file": tk.StringVar(value=_get("footer_file")),
            "output_name": tk.StringVar(value=_get("output_name")),
            "melt_id_vars": tk.StringVar(value=_get("melt_id_vars")),
            "un_melt_columns": tk.StringVar(value=_get("un_melt_columns")),
            "filter_rules": tk.StringVar(value=_get("filter_rules")),
        }
        self.vars["name"].trace_add("write", self._auto_suggest_paths)
        self.vars["file_path"].trace_add("write", self._refresh_sheet_list)

        self._build_ui()
        self._refresh_sheet_list()

    # ── UI Construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()

        # Scrollable body
        sf = ScrollableFrame(self, bg=C["bg"])
        sf.pack(fill="both", expand=True)

        # Single flat grid form — fills full width automatically
        self._f = tk.Frame(sf.inner, bg=C["bg"])
        self._f.pack(fill="x", padx=26, pady=18)
        self._f.columnconfigure(1, weight=1)  # entry column stretches
        self._f.columnconfigure(2, minsize=160)  # button column fixed

        r = 0
        # ── Section 1 ──────────────────────────────────────────────
        r = self._sec(r, "1", "Project Information")
        r = self._entry(r, "Project Name  *", "name")
        r = self._hint(r, "ชื่อโปรเจกต์  •  Folder จะถูกสร้างอัตโนมัติ")
        r = self._sep(r)
        # ── Section 2 ──────────────────────────────────────────────
        r = self._sec(r, "2", "Source Data & Templates")
        r = self._browse(r, "Source Excel File  *", "file_path", "file")
        r = self._combo(r, "Sheet Name / Index", "sheet_name")
        r = self._tpl(r, "Header Template", "header_file", "header.txt")
        r = self._tpl(r, "Body Template  *", "body_file", "body.txt")
        r = self._tpl(r, "Footer Template", "footer_file", "footer.txt")
        r = self._sep(r)
        # ── Section 3 ──────────────────────────────────────────────
        r = self._sec(r, "3", "Output Configuration")
        r = self._browse(r, "Output File Path  *", "output_name", "output")
        r = self._hint(r, "เช่น  projects/MyProject/output/result.csv")
        r = self._entry(r, "Transpose Column ID", "melt_id_vars")
        r = self._hint(r, "ระบุ ID column สำหรับ Melt  •  เว้นว่างถ้าไม่ใช้")
        r = self._entry(r, "Un-Transpose Columns", "un_melt_columns")
        r = self._hint(r, "เช่น  ID,Key,Value  •  แปลง Key-Value กลับเป็นตาราง")
        r = self._sep(r)
        # ── Section 4 ──────────────────────────────────────────────
        r = self._sec(r, "4", "Filter Rules")
        r = self._filter_builder(r)
        r = self._sep(r)

        # Footer buttons
        foot = tk.Frame(self._f, bg=C["bg"])
        foot.grid(row=r, column=0, columnspan=3, sticky="e", pady=(4, 8))
        flat_btn(
            foot, "  Cancel  ", self.destroy, C["card_alt"], C["border"], C["text_s"]
        ).pack(side="right", padx=(8, 0))
        flat_btn(
            foot,
            "💾  Save Project",
            self._save,
            C["success"],
            C["suc_h"],
            "white",
            bold=True,
        ).pack(side="right")

    def _build_header(self):
        is_edit = self.section is not None
        hdr = tk.Frame(self, bg=C["header"], height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=C["header"])
        left.pack(side="left", padx=20, pady=10)
        icon_bg = C["pri_h"] if is_edit else C["success"]
        icon_ch = "✏" if is_edit else "＋"
        icon_box = tk.Frame(left, bg=icon_bg, width=28, height=28)
        icon_box.pack_propagate(False)
        icon_box.pack(side="left", padx=(0, 10))
        tk.Label(
            icon_box, text=icon_ch, bg=icon_bg, fg="white", font=(FF, 11, "bold")
        ).pack(expand=True)
        title_text = "Edit Project" if is_edit else "Create New Project"
        tk.Label(
            left, text=title_text, bg=C["header"], fg=C["text_w"], font=(FF, 12, "bold")
        ).pack(side="left")
        if self.section:
            tk.Label(
                left,
                text=f"  ·  {self.section[5:]}",
                bg=C["header"],
                fg=C["text_m"],
                font=(FF, 10),
            ).pack(side="left")

        right = tk.Frame(hdr, bg=C["header"])
        right.pack(side="right", padx=16)
        flat_btn(
            right,
            "×  Cancel",
            self.destroy,
            "#374151",
            "#4b5563",
            "#9ca3af",
            padx=10,
            pady=4,
        ).pack(side="right")
        tk.Frame(self, bg=C["sep_blue"], height=3).pack(fill="x")

    # ── Grid Row Helpers ──────────────────────────────────────────────────────
    def _sec(self, r, num, title):
        """Numbered section title row."""
        wrap = tk.Frame(self._f, bg=C["bg"])
        wrap.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(6, 4))
        badge = tk.Frame(wrap, bg=C["primary"])
        badge.pack(side="left")
        tk.Label(
            badge,
            text=f"  {num}  ",
            bg=C["primary"],
            fg="white",
            font=(FF, 9, "bold"),
            pady=2,
        ).pack()
        tk.Label(
            wrap, text=f"  {title}", bg=C["bg"], fg=C["text"], font=(FF, 11, "bold")
        ).pack(side="left")
        tk.Frame(self._f, bg=C["primary"], height=2).grid(
            row=r + 1, column=0, columnspan=3, sticky="ew", pady=(0, 5)
        )
        return r + 2

    def _entry(self, r, label, var_key):
        """Plain text entry."""
        tk.Label(
            self._f,
            text=label,
            bg=C["bg"],
            fg=C["text"],
            font=(FF, 9, "bold"),
            anchor="w",
        ).grid(row=r, column=0, sticky="w", padx=(0, 12), pady=(0, 7))
        tk.Entry(
            self._f,
            textvariable=self.vars[var_key],
            bg=C["card"],
            fg=C["text"],
            font=(FF, 10),
            relief="flat",
            highlightbackground=C["border"],
            highlightthickness=1,
            insertbackground=C["primary"],
        ).grid(row=r, column=1, columnspan=2, sticky="ew", ipady=7, pady=(0, 7))
        return r + 1

    def _browse(self, r, label, var_key, mode):
        """Entry + Browse button."""
        tk.Label(
            self._f,
            text=label,
            bg=C["bg"],
            fg=C["text"],
            font=(FF, 9, "bold"),
            anchor="w",
        ).grid(row=r, column=0, sticky="w", padx=(0, 12), pady=(0, 7))
        tk.Entry(
            self._f,
            textvariable=self.vars[var_key],
            bg=C["card"],
            fg=C["text"],
            font=(FF, 10),
            relief="flat",
            highlightbackground=C["border"],
            highlightthickness=1,
            insertbackground=C["primary"],
        ).grid(row=r, column=1, sticky="ew", ipady=7, pady=(0, 7), padx=(0, 8))
        flat_btn(
            self._f,
            "📂 Browse",
            lambda m=mode, k=var_key: self._do_browse(k, m),
            C["card"],
            C["border"],
            C["text_s"],
            padx=10,
            pady=6,
        ).grid(row=r, column=2, sticky="w", pady=(0, 7))
        return r + 1

    def _combo(self, r, label, var_key):
        """Combobox row."""
        tk.Label(
            self._f,
            text=label,
            bg=C["bg"],
            fg=C["text"],
            font=(FF, 9, "bold"),
            anchor="w",
        ).grid(row=r, column=0, sticky="w", padx=(0, 12), pady=(0, 7))
        self.sheet_combo = ttk.Combobox(
            self._f, textvariable=self.vars[var_key], font=(FF, 10)
        )
        self.sheet_combo.grid(
            row=r, column=1, columnspan=2, sticky="ew", ipady=4, pady=(0, 7)
        )
        return r + 1

    def _tpl(self, r, label, var_key, def_name):
        """Template entry + Browse + Edit buttons."""
        tk.Label(
            self._f,
            text=label,
            bg=C["bg"],
            fg=C["text"],
            font=(FF, 9, "bold"),
            anchor="w",
        ).grid(row=r, column=0, sticky="w", padx=(0, 12), pady=(0, 7))
        tk.Entry(
            self._f,
            textvariable=self.vars[var_key],
            bg=C["card"],
            fg=C["text"],
            font=(FF, 10),
            relief="flat",
            highlightbackground=C["border"],
            highlightthickness=1,
            insertbackground=C["primary"],
        ).grid(row=r, column=1, sticky="ew", ipady=7, pady=(0, 7), padx=(0, 8))
        btn_wrap = tk.Frame(self._f, bg=C["bg"])
        btn_wrap.grid(row=r, column=2, sticky="w", pady=(0, 7))
        flat_btn(
            btn_wrap,
            "📂",
            lambda k=var_key: self._do_browse(k, "template"),
            C["card"],
            C["border"],
            C["text_s"],
            padx=8,
            pady=6,
        ).pack(side="left", padx=(0, 4))
        flat_btn(
            btn_wrap,
            "✏ Edit",
            lambda k=var_key, n=def_name: TextEditor(self, self.vars[k], n),
            C["accent"],
            "#6d28d9",
            "white",
            padx=10,
            pady=6,
        ).pack(side="left")
        return r + 1

    def _hint(self, r, text):
        """Helper hint text."""
        tk.Label(
            self._f,
            text=f"💡  {text}",
            bg=C["bg"],
            fg="#3b82f6",
            font=(FF, 8),
            anchor="w",
        ).grid(row=r, column=1, columnspan=2, sticky="w", pady=(0, 7))
        return r + 1

    def _sep(self, r):
        """Horizontal divider."""
        tk.Frame(self._f, bg=C["divider"], height=1).grid(
            row=r, column=0, columnspan=3, sticky="ew", pady=(2, 12)
        )
        return r + 1

    def _filter_builder(self, r):
        """Filter Rules builder UI."""
        tk.Label(
            self._f,
            text="Filter Rules",
            bg=C["bg"],
            fg=C["text"],
            font=(FF, 9, "bold"),
            anchor="w",
        ).grid(row=r, column=0, sticky="nw", padx=(0, 12), pady=(0, 7))

        card = tk.Frame(
            self._f,
            bg=C["card"],
            highlightbackground=C["border"],
            highlightthickness=1,
        )
        card.grid(row=r, column=1, columnspan=2, sticky="ew", pady=(0, 7))

        tk.Label(
            card,
            text="💡  Select column and operator, type value, then click + Add",
            bg=C["card"],
            fg=C["text_m"],
            font=(FF, 8),
        ).pack(fill="x", padx=12, pady=(8, 4))

        self._filter_frame = card

        filter_input = tk.Frame(card, bg=C["card"])
        filter_input.pack(fill="x", padx=12, pady=4)

        self.filter_field_var = tk.StringVar()
        self.filter_op_var = tk.StringVar(value="eq")
        self.filter_value_var = tk.StringVar()

        fields = self._get_available_fields()
        self.filter_field_cb = ttk.Combobox(
            filter_input,
            textvariable=self.filter_field_var,
            values=fields,
            width=14,
            font=(FF, 9),
        )
        self.filter_field_cb.pack(side="left", padx=(0, 8))
        self.filter_field_cb.set("Column")

        ops = [
            ("eq", "equals"),
            ("neq", "not equals"),
            ("contains", "contains"),
            ("not_contains", "not contains"),
            ("sw", "starts with"),
            ("ew", "ends with"),
            ("gt", "greater than"),
            ("lt", "less than"),
            ("in", "in (comma-sep)"),
        ]
        op_frame = tk.Frame(filter_input, bg=C["card"])
        op_frame.pack(side="left", padx=(0, 8))
        tk.Label(
            op_frame,
            text="if",
            bg=C["card"],
            fg=C["text_m"],
            font=(FF, 9),
        ).pack(side="left", padx=(0, 4))
        self.filter_op_cb = ttk.Combobox(
            op_frame,
            textvariable=self.filter_op_var,
            values=[o[1] for o in ops],
            width=12,
            font=(FF, 9),
        )
        self.filter_op_cb.pack(side="left")
        self.filter_op_cb.set("equals")

        tk.Entry(
            filter_input,
            textvariable=self.filter_value_var,
            bg=C["card_alt"],
            fg=C["text"],
            font=(FF, 9),
            relief="flat",
            highlightbackground=C["border"],
            highlightthickness=1,
            insertbackground=C["primary"],
        ).pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=4)

        flat_btn(
            filter_input,
            "+ Add",
            self._add_filter_rule,
            C["success"],
            C["suc_h"],
            "white",
            padx=10,
            pady=5,
        ).pack(side="left")

        self._filter_rules = []
        self._load_existing_filters()

        self._filter_list_frame = tk.Frame(card, bg=C["card"])
        self._filter_list_frame.pack(fill="x", padx=12, pady=(4, 8))
        self._render_filter_list()

        tk.Label(
            card,
            text="All rules are combined with AND logic",
            bg=C["card"],
            fg=C["text_m"],
            font=(FF, 8),
        ).pack(fill="x", padx=12, pady=(0, 6))

        return r + 1

    def _get_available_fields(self):
        path = self.vars["file_path"].get()
        if path and os.path.exists(path) and path.lower().endswith(
            (".xlsx", ".xls", ".csv")
        ):
            try:
                if path.lower().endswith(".csv"):
                    df = pd.read_csv(path, nrows=1)
                else:
                    xl = pd.ExcelFile(path)
                    df = pd.read_excel(xl, sheet_name=0, nrows=1)
                return df.columns.tolist()
            except Exception:
                pass
        return []

    def _load_existing_filters(self):
        if self.section:
            val = self.config.get(
                self.section, "filter_rules", fallback=""
            ).strip()
        else:
            val = ""
        if val:
            for rule in val.split(";"):
                rule = rule.strip()
                if rule:
                    parts = rule.split(":", 2)
                    if len(parts) == 3:
                        self._filter_rules.append(
                            {"field": parts[0], "op": parts[1], "value": parts[2]}
                        )

    def _add_filter_rule(self):
        field = self.filter_field_var.get().strip()
        if not field or field == "Column":
            messagebox.showwarning(
                "Validation Error",
                "Please select a column to filter.",
                parent=self,
            )
            return

        op_label = self.filter_op_var.get().strip()
        op_map = {
            "equals": "eq",
            "not equals": "neq",
            "contains": "contains",
            "not contains": "not_contains",
            "starts with": "sw",
            "ends with": "ew",
            "greater than": "gt",
            "less than": "lt",
            "in (comma-sep)": "in",
        }
        op = op_map.get(op_label, op_label)

        value = self.filter_value_var.get().strip()
        if not value:
            messagebox.showwarning(
                "Validation Error",
                "Please enter a filter value.",
                parent=self,
            )
            return

        self._filter_rules.append({"field": field, "op": op, "value": value})
        self._render_filter_list()
        self.filter_value_var.set("")

    def _remove_filter_rule(self, index):
        self._filter_rules.pop(index)
        self._render_filter_list()

    def _render_filter_list(self):
        for w in self._filter_list_frame.winfo_children():
            w.destroy()

        if not self._filter_rules:
            tk.Label(
                self._filter_list_frame,
                text="  No filter rules configured",
                bg=C["card"],
                fg=C["text_m"],
                font=(FF, 9, "italic"),
            ).pack(fill="x", pady=4)
            return

        for i, rule in enumerate(self._filter_rules):
            op_display = {
                "eq": "==",
                "neq": "!=",
                "contains": "contains",
                "not_contains": "not contains",
                "sw": "starts with",
                "ew": "ends with",
                "gt": ">",
                "lt": "<",
                "in": "in",
            }.get(rule["op"], rule["op"])

            row = tk.Frame(self._filter_list_frame, bg=C["card_alt"])
            row.pack(fill="x", pady=1)

            num_badge = tk.Frame(row, bg=C["primary"], width=22, height=22)
            num_badge.pack_propagate(False)
            num_badge.pack(side="left", padx=(4, 6))
            tk.Label(
                num_badge,
                text=str(i + 1),
                bg=C["primary"],
                fg="white",
                font=(FF, 7, "bold"),
            ).place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(
                row,
                text=f"{rule['field']}  {op_display}  \"{rule['value']}\"",
                bg=C["card_alt"],
                fg=C["text"],
                font=(FF, 9),
            ).pack(side="left")

            flat_btn(
                row,
                "×",
                lambda idx=i: self._remove_filter_rule(idx),
                C["card_alt"],
                C["dan_lt"],
                C["danger"],
                padx=6,
                pady=2,
            ).pack(side="right", padx=4)

    # ── Logic ─────────────────────────────────────────────────────────────────
    def _refresh_sheet_list(self, *_):
        if not hasattr(self, "sheet_combo"):
            return
        path = self.vars["file_path"].get()
        if path and os.path.exists(path) and path.lower().endswith((".xlsx", ".xls")):
            try:
                xl = pd.ExcelFile(path)
                self.sheet_combo["values"] = xl.sheet_names
            except Exception:
                self.sheet_combo["values"] = []
        else:
            self.sheet_combo["values"] = []

        if hasattr(self, "filter_field_cb"):
            fields = self._get_available_fields()
            self.filter_field_cb["values"] = fields

    def _auto_suggest_paths(self, *_):
        name = self.vars["name"].get().strip()
        if name and not self.section:
            p = f"projects/{name}"
            self.vars["header_file"].set(f"{p}/templates/header.txt")
            self.vars["body_file"].set(f"{p}/templates/body.txt")
            self.vars["footer_file"].set(f"{p}/templates/footer.txt")
            self.vars["output_name"].set(f"{p}/output/result.csv")

    def _do_browse(self, var_key, mode):
        if mode == "file":
            path = filedialog.askopenfilename(
                parent=self,
                filetypes=[("Excel / CSV", "*.xlsx *.xls *.csv"), ("All files", "*.*")],
            )
        elif mode == "output":
            path = filedialog.asksaveasfilename(
                parent=self,
                defaultextension=".csv",
                filetypes=[
                    ("CSV", "*.csv"),
                    ("JSON", "*.json"),
                    ("Text", "*.txt"),
                    ("All files", "*.*"),
                ],
            )
        else:  # template
            path = filedialog.askopenfilename(
                parent=self, filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
        if path:
            self.vars[var_key].set(path)

    def _save(self):
        name = self.vars["name"].get().strip()
        if not name:
            messagebox.showerror(
                "Validation Error", "Project name cannot be empty.", parent=self
            )
            return

        filter_rules_str = ";".join(
            f"{r['field']}:{r['op']}:{r['value']}" for r in self._filter_rules
        )

        p_root = f"projects/{name}"
        for sub in ("input", "templates", "output"):
            os.makedirs(f"{p_root}/{sub}", exist_ok=True)
        new_sec = f"Task:{name}"
        if self.section and self.section != new_sec:
            self.config.remove_section(self.section)
        if not self.config.has_section(new_sec):
            self.config.add_section(new_sec)
        for k, v in self.vars.items():
            if k != "name":
                self.config.set(new_sec, k, v.get())
        self.config.set(new_sec, "filter_rules", filter_rules_str)
        self.main_app.save_config_to_file()
        self.main_app.refresh_task_list()
        self.main_app.set_status(f"✅  Project '{name}' saved.", "#10b981")
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  HELP DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class HelpDialog(tk.Toplevel):
    """Comprehensive help & about dialog with tab navigation."""

    _PAGES = [
        ("🏠  Overview", "overview"),
        ("🚀  Quick Start", "quickstart"),
        ("📝  Template Guide", "template"),
        ("🔄  Transpose Mode", "transpose"),
        ("🔍  Filter Rules", "filter"),
        ("❓  FAQ", "faq"),
        ("👤  About & Contact", "about"),
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Help & User Guide — ASBC Converter Pro")
        self.geometry("960x700")
        self.configure(bg=C["bg"])
        self.minsize(800, 550)
        self.grab_set()
        self._active = None
        self._build()

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["header"], height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        left = tk.Frame(hdr, bg=C["header"])
        left.pack(side="left", padx=20, pady=10)
        icon = tk.Frame(left, bg="#7c3aed", width=30, height=30)
        icon.pack_propagate(False)
        icon.pack(side="left", padx=(0, 10))
        tk.Label(icon, text="?", bg="#7c3aed", fg="white", font=(FF, 13, "bold")).pack(
            expand=True
        )
        tk.Label(
            left,
            text="Help & User Guide",
            bg=C["header"],
            fg=C["text_w"],
            font=(FF, 12, "bold"),
        ).pack(side="left")
        tk.Label(
            left,
            text=f"  —  {APP_NAME} {APP_VER}",
            bg=C["header"],
            fg=C["text_m"],
            font=(FF, 9),
        ).pack(side="left")
        right = tk.Frame(hdr, bg=C["header"])
        right.pack(side="right", padx=16)
        flat_btn(
            right,
            "×  Close",
            self.destroy,
            "#374151",
            "#4b5563",
            "#9ca3af",
            padx=10,
            pady=4,
        ).pack()
        tk.Frame(self, bg=C["primary"], height=3).pack(fill="x")

        # Body
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left navigation
        nav = tk.Frame(body, bg="#1e293b", width=185)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)
        tk.Label(
            nav,
            text="  CONTENTS",
            bg="#1e293b",
            fg="#475569",
            font=(FF, 8, "bold"),
            pady=12,
        ).pack(fill="x", anchor="w")

        # Content area
        self._content = tk.Frame(body, bg=C["bg"])
        self._content.pack(side="left", fill="both", expand=True)

        self._btns = {}
        self._frames = {}
        self._loaded = set()  # track which pages have been built
        for label, key in self._PAGES:
            btn = tk.Label(
                nav,
                text=f"   {label}",
                bg="#1e293b",
                fg="#94a3b8",
                font=(FF, 10),
                anchor="w",
                pady=10,
                cursor="hand2",
            )
            btn.pack(fill="x")
            btn.bind(
                "<Enter>",
                lambda e, b=btn, k=key: b.configure(
                    bg=C["primary"] if self._active == k else "#2d3748"
                ),
            )
            btn.bind(
                "<Leave>",
                lambda e, b=btn, k=key: b.configure(
                    bg=C["primary"] if self._active == k else "#1e293b"
                ),
            )
            btn.bind("<Button-1>", lambda e, k=key: self._show(k))
            sf = ScrollableFrame(self._content, bg=C["bg"])
            self._btns[key] = btn
            self._frames[key] = sf
            # NOTE: content is NOT added here — see _show() lazy loading

        self._show("overview")

    def _show(self, key):
        # Hide all pages
        for k, sf in self._frames.items():
            sf.pack_forget()
            self._btns[k].configure(bg="#1e293b", fg="#94a3b8")

        # Show selected page
        sf = self._frames[key]
        sf.pack(fill="both", expand=True)
        self._btns[key].configure(bg=C["primary"], fg="white")
        self._active = key

        # Lazy load: build page content AFTER frame is packed and has proper dimensions
        if key not in self._loaded:
            self.update_idletasks()  # let canvas settle its size
            getattr(self, f"_pg_{key}")(sf.inner)  # build content now
            self._loaded.add(key)
            self.update_idletasks()  # refresh after content added

    # ── Shared Helpers ───────────────────────────────────────────────────────
    def _sec(self, p, title):
        f = tk.Frame(p, bg=C["bg"])
        f.pack(fill="x", padx=22, pady=(14, 2))
        tk.Label(f, text=title, bg=C["bg"], fg=C["text"], font=(FF, 11, "bold")).pack(
            anchor="w"
        )
        tk.Frame(f, bg=C["primary"], height=2).pack(fill="x", pady=(3, 0))

    def _para(self, p, text):
        tk.Label(
            p,
            text=text,
            bg=C["bg"],
            fg=C["text_s"],
            font=(FF, 10),
            justify="left",
            anchor="w",
            padx=22,
            pady=2,
            wraplength=640,
        ).pack(fill="x")

    def _card(self, p, title, body_text, hdr_color=None):
        card = tk.Frame(
            p, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(fill="x", padx=22, pady=(0, 8))
        hdr = tk.Frame(card, bg=hdr_color or C["card_alt"], height=30)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr,
            text=f"  {title}",
            bg=hdr_color or C["card_alt"],
            fg="white" if hdr_color else C["text"],
            font=(FF, 9, "bold"),
        ).pack(side="left", pady=6)
        tk.Label(
            card,
            text=body_text,
            bg=C["card"],
            fg=C["text_s"],
            font=(FM, 9),
            justify="left",
            anchor="w",
            padx=14,
            pady=8,
        ).pack(fill="x")

    def _step(self, p, num, color, title, desc):
        card = tk.Frame(
            p, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(fill="x", padx=22, pady=(0, 7))
        row = tk.Frame(card, bg=C["card"])
        row.pack(fill="x", padx=12, pady=10)
        badge = tk.Frame(row, bg=color, width=32, height=32)
        badge.pack_propagate(False)
        badge.pack(side="left", padx=(0, 12))
        tk.Label(
            badge, text=str(num), bg=color, fg="white", font=(FF, 12, "bold")
        ).pack(expand=True)
        col = tk.Frame(row, bg=C["card"])
        col.pack(side="left", fill="x", expand=True)
        tk.Label(
            col,
            text=title,
            bg=C["card"],
            fg=C["text"],
            font=(FF, 10, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            col,
            text=desc,
            bg=C["card"],
            fg=C["text_s"],
            font=(FF, 9),
            justify="left",
            anchor="w",
        ).pack(fill="x")

    # ── Pages ────────────────────────────────────────────────────────────────
    def _pg_overview(self, p):
        banner = tk.Frame(p, bg=C["primary"])
        banner.pack(fill="x", padx=22, pady=(18, 4))
        tk.Label(
            banner,
            text=f"⚡  {APP_NAME}  {APP_VER}",
            bg=C["primary"],
            fg="white",
            font=(FF, 14, "bold"),
            padx=20,
            pady=12,
        ).pack(anchor="w")
        tk.Label(
            banner,
            text=APP_SUB + "  —  แปลงข้อมูล Excel → ไฟล์ทุกรูปแบบด้วย Template",
            bg=C["primary"],
            fg="#bfdbfe",
            font=(FF, 9),
            padx=20,
            pady=(0, 12),
        ).pack(anchor="w")

        self._sec(p, "โปรแกรมนี้ทำอะไร?")
        self._para(
            p,
            "ASBC ช่วยแปลงข้อมูลจาก Excel / CSV ให้เป็นไฟล์รูปแบบใดก็ได้\n"
            "เช่น CSV สำหรับนำเข้าระบบ, ไฟล์ Config, ไฟล์ SQL, Properties หรือรายงาน\n"
            "โดยกำหนดรูปแบบผ่าน Template เองได้ 100%",
        )

        self._sec(p, "ความสามารถหลัก")
        card = tk.Frame(
            p, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(fill="x", padx=22, pady=(0, 16))
        for icon_text, title, desc in [
            ("📥", "Input", ".xlsx, .xls, .csv — เลือก Sheet ได้"),
            ("📤", "Output", ".csv, .txt, .json, .sidata และอื่นๆ"),
            ("📝", "Template", "Header / Body / Footer กำหนดเองได้อิสระ"),
            ("🔄", "Transpose", "แปลงตาราง → คู่ Key-Value แนวตั้ง"),
            ("↩️", "Un-Transpose", "แปลง Key-Value → กลับมาเป็นตารางปกติ"),
            ("🔍", "Filter Rules", "กรองข้อมูลตามเงื่อนไขก่อนแปลง"),
            ("📋", "Multi-Project", "จัดการหลาย Project รันพร้อมกันได้"),
            ("🔒", "License", "1 License = 1 เครื่อง ป้องกันการใช้งานโดยไม่อนุญาต"),
        ]:
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", padx=14, pady=5)
            tk.Label(
                row, text=f"  {icon_text}", bg=C["card"], font=(FF, 12), width=4
            ).pack(side="left")
            tk.Label(
                row,
                text=title,
                bg=C["card"],
                fg=C["primary"],
                font=(FF, 10, "bold"),
                width=14,
                anchor="w",
            ).pack(side="left")
            tk.Label(
                row, text=desc, bg=C["card"], fg=C["text_s"], font=(FF, 10), anchor="w"
            ).pack(side="left")
            tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=14)

    def _pg_quickstart(self, p):
        self._sec(p, "เริ่มต้นใช้งานใน 5 ขั้นตอน")
        steps = [
            (
                C["primary"],
                "สร้าง Project ใหม่",
                "กดปุ่ม ➤ New Project ที่หน้าหลัก  •  ใส่ชื่อ Project",
            ),
            (
                C["success"],
                "เลือกไฟล์และ Sheet",
                "กด Browse เลือกไฟล์ Excel  •  เลือก Sheet จากรายการที่โหลดอัตโนมัติ",
            ),
            (
                "#7c3aed",
                "เขียน Body Template",
                "กดปุ่ม ✏ Edit  •  ใช้ {{ชื่อคอลัมน์}} ดึงข้อมูลจาก Excel  •  กด Ctrl+S บันทึก",
            ),
            (
                C["warning"],
                "กำหนด Output Path",
                "ระบุชื่อและ Path ไฟล์ผลลัพธ์  •  กด Save Project",
            ),
            (
                C["danger"],
                "กด RUN และรับไฟล์",
                "เลือก Project ที่ต้องการ  •  กด 🚀 RUN SELECTED PROJECTS  •  รับไฟล์ Output",
            ),
        ]
        for i, (color, title, desc) in enumerate(steps, 1):
            self._step(p, i, color, title, desc)

    def _pg_template(self, p):
        self._sec(p, "โครงสร้าง Template")
        self._para(p, "Template แบ่งเป็น 3 ส่วน โปรแกรมจะประมวลผลตามลำดับ:")
        card = tk.Frame(
            p, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(fill="x", padx=22, pady=(0, 10))
        for clr, name, detail in [
            (
                "#2563eb",
                "HEADER",
                "แสดง 1 ครั้ง • ด้านบนสุด\nตัวอย่าง: หัวตาราง, DOCTYPE, opening tag",
            ),
            (
                "#059669",
                "BODY  ",
                "วนซ้ำ 1 รอบ / 1 แถวข้อมูล\nตัวอย่าง: กำหนดรูปแบบโดยใช้ {{ }}",
            ),
            (
                "#7c3aed",
                "FOOTER",
                "แสดง 1 ครั้ง • ด้านล่างสุด\nตัวอย่าง: ปิด tag, summary, footer",
            ),
        ]:
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", padx=14, pady=8)
            badge = tk.Frame(row, bg=clr, width=62, height=36)
            badge.pack_propagate(False)
            badge.pack(side="left", padx=(0, 12))
            tk.Label(badge, text=name, bg=clr, fg="white", font=(FM, 9, "bold")).pack(
                expand=True
            )
            tk.Label(
                row,
                text=detail,
                bg=C["card"],
                fg=C["text_s"],
                font=(FF, 9),
                justify="left",
                anchor="w",
            ).pack(side="left")
            tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=14)

        self._sec(p, "วิธีดึงข้อมูลจาก Excel")
        self._para(p, "ใช้ {{ชื่อคอลัมน์}} ใน Body Template ตามชื่อ Header ใน Excel:")
        tk.Label(
            p,
            text="⚠️ ห้ามเว้นวรรคก่อน }} เช่น {{ CI Name }} จะ Error",
            bg=C["bg"],
            fg="#ef4444",
            font=(FF, 10),
            justify="left",
            anchor="w",
            padx=22,
            pady=2,
            wraplength=640,
        ).pack(fill="x")
        self._card(
            p,
            "ตัวอย่าง: Excel มีคอลัมน์  CI Name, OS, IP Address",
            "CI_NAME={{CI Name}}\nOS_TYPE={{OS}}\nIP_ADDR={{IP Address}}\n---",
            "#374151",
        )

        self._sec(p, "ข้อควรระวัง")
        card = tk.Frame(
            p, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(fill="x", padx=22, pady=(0, 20))
        for note in [
            ("ชื่อต้องตรง", "ชื่อใน {{ }} ต้องสะกดตรงกับ Header ใน Excel"),
            ("เอ็มเล็ก-ใหญ่", "ใช้ได้ทั้งคู่  —  {{CI Name}} เท่ากับ {{ci name}}"),
            ("ตัวพิมพ์", "Ctrl+S = Save  •  Alt+F4 = Cancel"),
        ]:
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", padx=14, pady=5)
            tk.Label(
                row,
                text=note[0],
                bg=C["card"],
                fg=C["primary"],
                font=(FF, 9, "bold"),
                width=14,
                anchor="w",
            ).pack(side="left")
            tk.Label(
                row,
                text=note[1],
                bg=C["card"],
                fg=C["text_s"],
                font=(FF, 9),
                anchor="w",
            ).pack(side="left")
            tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=14)

    def _pg_transpose(self, p):
        self._sec(p, "Transpose Mode คืออะไร?")
        self._para(
            p,
            "โหมดนี้แปลงตารางแนวนอน (ปกติ) ให้กลายเป็นคู่ Key-Value แนวตั้ง\n"
            "เหมาะสำหรับ: ไฟล์ Properties, Config, หรือ ต้องการ 1 Property ต่อบรรทัด",
        )
        self._sec(p, "วิธีเปิดใช้งาน")
        self._para(
            p,
            "ในหน้า Edit Project ใส่ชื่อคอลัมน์ ID ลงใน 'Transpose Column ID'  เช่น RunningNo หรือ ID",
        )
        self._sec(p, "ตัวอย่าง")
        self._card(
            p,
            "📊 ข้อมูลใน Excel (ก่อน Transpose)",
            "RunningNo  Hostname   OS       IP\n"
            "1          SERVER-01  Windows  10.0.0.1\n"
            "2          SERVER-02  Linux    10.0.0.2",
            "#374151",
        )
        self._card(p, "📝 Body Template", "{{ID}},{{Key}},{{Value}}", "#7c3aed")
        self._card(
            p,
            "📄 ผลลัพธ์",
            "1,Hostname,SERVER-01\n1,OS,Windows\n1,IP,10.0.0.1\n"
            "2,Hostname,SERVER-02\n2,OS,Linux\n2,IP,10.0.0.2",
            "#059669",
        )
        self._sec(p, "Variable พิเศษ")
        card = tk.Frame(
            p, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(fill="x", padx=22, pady=(0, 20))
        for var, desc in [
            ("{{ID}}    ", "ค่าจากคอลัมน์ที่ระบุใน Transpose Column ID"),
            ("{{Key}}   ", "ชื่อคอลัมน์ (Header) จาก Excel"),
            ("{{Value}}  ", "ข้อมูลในช่องนั้น ณ แถวนั้น"),
        ]:
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", padx=14, pady=7)
            tk.Label(
                row,
                text=var,
                bg="#1e2030",
                fg="#a6e3a1",
                font=(FM, 11, "bold"),
                padx=8,
                pady=4,
            ).pack(side="left", padx=(0, 12))
            tk.Label(
                row, text=desc, bg=C["card"], fg=C["text_s"], font=(FF, 10), anchor="w"
            ).pack(side="left")
            tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=14)

        self._sec(p, "🔄 Un-Transpose Mode (แปลงกลับ)")
        self._para(
            p,
            "โหมดนี้จะแปลงข้อมูล Key-Value แนวตั้ง กลับมาเป็นตารางแนวนอนเหมือนเดิม\n"
            "เหมาะสำหรับ: ไฟล์ Output ที่ผ่านการ Transpose แล้ว ต้องการนำไปใช้ต่อในระบบที่รับตาราง",
        )
        self._para(
            p,
            "วิธีใช้งาน: ในหน้า Edit Project ใส่ชื่อคอลัมน์ 3 ชื่อ คั่นด้วย comma ในช่อง 'Un-Transpose Columns'",
        )
        self._card(
            p,
            "📊 ข้อมูล Input (หลัง Transpose)",
            "ID,Key,Value\n"
            "1,Hostname,SERVER-01\n"
            "1,OS,Windows\n"
            "1,IP,10.0.0.1\n"
            "2,Hostname,SERVER-02\n"
            "2,OS,Linux\n"
            "2,IP,10.0.0.2",
            "#374151",
        )
        self._card(
            p, "⚙️ Un-Transpose Columns", "ID,Key,Value", C["primary"]
        )
        self._card(
            p,
            "📄 ผลลัพธ์ (ตารางปกติ)",
            "ID,Hostname,OS,IP\n"
            "1,SERVER-01,Windows,10.0.0.1\n"
            "2,SERVER-02,Linux,10.0.0.2",
            "#059669",
        )

    def _pg_filter(self, p):
        self._sec(p, "Filter Rules คืออะไร?")
        self._para(
            p,
            "Filter Rules ช่วยกรองข้อมูลจากไฟล์ต้นทาง ก่อนที่จะนำไปประมวลผลผ่าน Template\n"
            "เหมาะสำหรับ: การดึงเฉพาะแถวที่ตรงกับเงื่อนไข เช่น เฉพาะ OS = Windows, เฉพาะ Status = Active",
        )

        self._sec(p, "วิธีใช้งาน")
        self._para(
            p,
            "ในหน้า Edit Project → Section 4: Filter Rules\n"
            "1. เลือก Column ที่ต้องการกรองจากรายการ\n"
            "2. เลือก Operator (เช่น equals, contains, greater than)\n"
            "3. พิมพ์ค่าที่ต้องการ\n"
            "4. กด + Add เพื่อเพิ่ม rule\n"
            "5. สามารถเพิ่มหลาย rule ได้ (ทั้งหมดจะทำงานแบบ AND logic)",
        )

        self._sec(p, "Operators ที่รองรับ")
        card = tk.Frame(
            p, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(fill="x", padx=22, pady=(0, 10))
        for op, desc, example in [
            ("equals (eq)", "เท่ากับ (ไม่สนตัวพิมพ์)", "OS equals Windows"),
            ("not equals (neq)", "ไม่เท่ากับ", "Status neq Inactive"),
            ("contains", "มีคำนี้", "Name contains Smith"),
            ("not contains", "ไม่มีคำนี้", "Name not contains Test"),
            ("starts with (sw)", "ขึ้นต้นด้วย", "ID sw SRV"),
            ("ends with (ew)", "ลงท้ายด้วย", "File ew .csv"),
            ("greater than (gt)", "มากกว่า", "Age gt 18"),
            ("less than (lt)", "น้อยกว่า", "Price lt 100"),
            ("in", "อยู่ในกลุ่ม (คั่นด้วย comma)", "OS in Windows,Linux,Mac"),
        ]:
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", padx=14, pady=5)
            tk.Label(
                row,
                text=op,
                bg=C["card"],
                fg=C["primary"],
                font=(FF, 9, "bold"),
                width=22,
                anchor="w",
            ).pack(side="left")
            tk.Label(
                row, text=desc, bg=C["card"], fg=C["text_s"], font=(FF, 9), width=20
            ).pack(side="left")
            tk.Label(
                row,
                text=example,
                bg=C["card"],
                fg=C["text"],
                font=(FM, 8),
                anchor="w",
            ).pack(side="left")
            tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=14)

        self._sec(p, "ตัวอย่าง")
        self._card(
            p,
            "📊 ข้อมูลต้นทาง (Excel)",
            "Name      OS        Status\n"
            "Server-01  Windows   Active\n"
            "Server-02  Linux     Active\n"
            "Server-03  Windows   Inactive\n"
            "Server-04  Mac       Active",
            "#374151",
        )
        self._card(
            p,
            "🔍 Filter Rules",
            "OS equals Windows  AND  Status equals Active",
            C["primary"],
        )
        self._card(
            p,
            "📄 ผลลัพธ์ (1 แถวที่ตรงเงื่อนไข)",
            "Name      OS        Status\n"
            "Server-01  Windows   Active",
            "#059669",
        )

        self._sec(p, "ข้อควรระวัง")
        card = tk.Frame(
            p, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(fill="x", padx=22, pady=(0, 20))
        for note in [
            ("เลือก Column", "ต้องเลือก Column ที่มีอยู่ในไฟล์ต้นทาง"),
            ("AND Logic", "ทุก rule ต้องตรงพร้อมกัน (ไม่ใช่ OR)"),
            ("ตัวพิมพ์", "Filter ไม่สนตัวพิมพ์เล็ก-ใหญ่ (case-insensitive)"),
            ("Operator 'in'", "ค่าต้องคั่นด้วย comma: Windows,Linux,Mac"),
        ]:
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", padx=14, pady=5)
            tk.Label(
                row,
                text=note[0],
                bg=C["card"],
                fg=C["primary"],
                font=(FF, 9, "bold"),
                width=14,
                anchor="w",
            ).pack(side="left")
            tk.Label(
                row,
                text=note[1],
                bg=C["card"],
                fg=C["text_s"],
                font=(FF, 9),
                anchor="w",
            ).pack(side="left")
            tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=14)

    def _pg_faq(self, p):
        self._sec(p, "คำถามที่พบบ่อย")
        faqs = [
            (
                "ภาษาไทยใน Output อ่านไม่ออก?",
                "เพิ่ม encoding = cp874 ในหน้า Edit Project (ค่าเริ่มต้นคือ utf-8)",
            ),
            (
                "ไฟล์ Excel เปิดค้างอยู่แล้วรัน Error?",
                "ปิดไฟล์ Excel ทั้งต้นทางและปลายทางก่อนกด RUN",
            ),
            (
                "Template แสดงชื่อ {{ }} แทนข้อมูล?",
                "ชื่อใน {{ }} สะกดไม่ตรงกับ Header ใน Excel — ตรวจสอบการสะกดอีกครั้ง",
            ),
            (
                "เปลี่ยนเครื่องใหม่ ต้องทำอย่างไร?",
                "ส่ง Machine ID ของเครื่องใหม่ให้ผู้พัฒนา เพื่อขอ License Key ใหม่",
            ),
            (
                "รัน Error: ไม่พบไฟล์ต้นทาง?",
                "ไฟล์ถูกย้ายหรือลบ — กด Edit แล้ว Browse เลือกไฟล์ใหม่",
            ),
            ("รันแล้ว Output ว่างเปล่า?", "ตรวจสอบ Body Template ว่าเขียน {{ }} ถูกต้องหรือไม่"),
            (
                "Un-Transpose คืออะไร?",
                "โหมดแปลงข้อมูล Key-Value แนวตั้ง กลับมาเป็นตารางแนวนอน (ตรงข้ามกับ Transpose)",
            ),
            (
                "วิธีใช้ Un-Transpose?",
                "ใส่ชื่อคอลัมน์ 3 ชื่อ คั่นด้วย comma ในช่อง 'Un-Transpose Columns' เช่น ID,Key,Value",
            ),
            (
                "Un-Transpose แล้ว Error?",
                "ตรวจสอบว่าชื่อคอลัมน์ทั้ง 3 (ID, Key, Value) มีอยู่ในไฟล์ Input จริง",
            ),
            (
                "Filter Rules คืออะไร?",
                "ระบบกรองข้อมูลตามเงื่อนไข เช่น เฉพาะ OS = Windows, เฉพาะ Status = Active",
            ),
            (
                "เพิ่ม Filter Rule อย่างไร?",
                "เลือก Column → เลือก Operator → พิมพ์ค่า → กด + Add",
            ),
            (
                "ใช้หลาย Filter พร้อมกันได้ไหม?",
                "ได้ — ทุก rule จะทำงานแบบ AND (ต้องตรงทุกเงื่อนไข)",
            ),
            (
                "Filter แล้วไม่มีข้อมูล?",
                "ตรวจสอบว่าค่าที่กรองตรงกับข้อมูลในไฟล์จริง และเลือก Column ถูกต้อง",
            ),
        ]
        for i, (q, a) in enumerate(faqs, 1):
            card = tk.Frame(
                p, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
            )
            card.pack(fill="x", padx=22, pady=(0, 7))
            qf = tk.Frame(card, bg="#eff6ff")
            qf.pack(fill="x")
            tk.Label(
                qf,
                text=f"  Q{i}:  {q}",
                bg="#eff6ff",
                fg=C["primary"],
                font=(FF, 9, "bold"),
                padx=8,
                pady=7,
                anchor="w",
                justify="left",
            ).pack(fill="x")
            tk.Label(
                card,
                text=f"     ▶  {a}",
                bg=C["card"],
                fg=C["text_s"],
                font=(FF, 9),
                padx=14,
                pady=7,
                anchor="w",
                justify="left",
            ).pack(fill="x")

    def _pg_about(self, p):
        # Developer card
        dev = tk.Frame(p, bg=C["header"])
        dev.pack(fill="x", padx=22, pady=(18, 4))
        inner = tk.Frame(dev, bg=C["header"])
        inner.pack(fill="x", padx=22, pady=20)
        icon_box = tk.Frame(inner, bg=C["primary"], width=60, height=60)
        icon_box.pack_propagate(False)
        icon_box.pack(side="left", padx=(0, 18))
        tk.Label(
            icon_box,
            text="👤",
            bg=C["primary"],
            fg="white",
            font=("Segoe UI Emoji", 26),
        ).pack(expand=True)
        col = tk.Frame(inner, bg=C["header"])
        col.pack(side="left")
        tk.Label(
            col, text=DEVELOPER, bg=C["header"], fg="white", font=(FF, 15, "bold")
        ).pack(anchor="w")
        tk.Label(
            col,
            text="Developer & Owner — ASBC Converter Pro",
            bg=C["header"],
            fg=C["text_m"],
            font=(FF, 10),
        ).pack(anchor="w")

        self._sec(p, "ข้อมูลติดต่อ")
        card = tk.Frame(
            p, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(fill="x", padx=22, pady=(0, 12))
        for icon, label, value, color in [
            ("📧", "Email", "sarawut.shi@mahidol.ac.th", C["primary"]),
            ("🏢", "สังกัด", "Mahidol University", C["text_s"]),
            ("🌐", "Version", f"{APP_NAME} {APP_VER}", C["text_s"]),
            ("📅", "ปีที่พัฒนา", "2025", C["text_s"]),
        ]:
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", padx=14, pady=8)
            tk.Label(
                row,
                text=f"  {icon}  {label}",
                bg=C["card"],
                fg=C["text"],
                font=(FF, 10, "bold"),
                width=14,
                anchor="w",
            ).pack(side="left")
            tk.Label(
                row, text=value, bg=C["card"], fg=color, font=(FF, 10), anchor="w"
            ).pack(side="left")
            tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=14)

        self._sec(p, "License")
        lic = tk.Frame(
            p, bg="#fef3c7", highlightbackground="#fbbf24", highlightthickness=1
        )
        lic.pack(fill="x", padx=22, pady=(0, 20))
        tk.Label(
            lic,
            text="  ⚠️  Proprietary Software — สงวนลิขสิทธิ์ทุกประการ\n"
            "  การใช้งานต้องได้รับ License Key จากผู้พัฒนาเท่านั้น\n"
            f"  © 2025  {DEVELOPER}  —  All rights reserved.",
            bg="#fef3c7",
            fg="#92400e",
            font=(FF, 10),
            padx=14,
            pady=14,
            anchor="w",
            justify="left",
        ).pack(fill="x")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class ASBCGui:
    """Main ASBC Converter Pro application."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_NAME}  —  {APP_VER}")
        self.root.geometry("1180x800")
        self.root.minsize(950, 620)
        self.root.configure(bg=C["header"])  # Header color shows during resize

        self.config_path = "ASBC-Config.ini"
        self.converter = ASBCConverter(self.config_path)
        self.config = self.converter.config

        self._setup_ttk_styles()
        self._build_header()
        self._build_body()
        self._build_status_bar()
        self.refresh_task_list()

    # ── TTK Style Setup ───────────────────────────────────────────────────────
    def _setup_ttk_styles(self):
        s = ttk.Style()
        s.theme_use("clam")

        # Treeview
        s.configure(
            "Pro.Treeview",
            background=C["card"],
            foreground=C["text"],
            font=(FF, 10),
            rowheight=40,
            borderwidth=0,
            fieldbackground=C["card"],
            relief="flat",
        )
        s.configure(
            "Pro.Treeview.Heading",
            background=C["card_alt"],
            foreground=C["text"],
            font=(FF, 10, "bold"),
            borderwidth=0,
            relief="flat",
            padding=(10, 8),
        )
        s.map(
            "Pro.Treeview",
            background=[("selected", C["sel"])],
            foreground=[("selected", C["sel_fg"])],
        )
        s.map("Pro.Treeview.Heading", background=[("active", C["border"])])

        # Scrollbar (minimal)
        s.configure(
            "TScrollbar",
            background=C["border"],
            troughcolor=C["bg"],
            borderwidth=0,
            arrowsize=12,
            relief="flat",
        )

        # Combobox
        s.configure(
            "TCombobox",
            fieldbackground=C["card_alt"],
            background=C["card_alt"],
            foreground=C["text"],
            borderwidth=1,
            relief="flat",
        )

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self.root, bg=C["header"], height=80)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # ── Left: Logo + Titles ──
        left = tk.Frame(hdr, bg=C["header"])
        left.pack(side="left", padx=28, pady=18)

        icon_outer = tk.Frame(left, bg=C["primary"], width=44, height=44)
        icon_outer.pack_propagate(False)
        icon_outer.pack(side="left", padx=(0, 14))
        tk.Label(
            icon_outer,
            text="⚡",
            bg=C["primary"],
            fg="white",
            font=("Segoe UI Emoji", 20),
        ).pack(expand=True)

        name_col = tk.Frame(left, bg=C["header"])
        name_col.pack(side="left")
        tk.Label(
            name_col,
            text=APP_NAME,
            bg=C["header"],
            fg=C["text_w"],
            font=(FF, 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            name_col, text=APP_SUB, bg=C["header"], fg=C["text_m"], font=(FF, 9)
        ).pack(anchor="w")

        # ── Right: Version badge + Developer ──
        right = tk.Frame(hdr, bg=C["header"])
        right.pack(side="right", padx=28, pady=18)

        ver = tk.Frame(right, bg=C["pri_h"])
        ver.pack(side="right", padx=(12, 0))
        tk.Label(
            ver,
            text=f"  {APP_VER}  ",
            bg=C["pri_h"],
            fg="white",
            font=(FF, 9, "bold"),
            pady=4,
        ).pack()

        dev_col = tk.Frame(right, bg=C["header"])
        dev_col.pack(side="right")
        tk.Label(
            dev_col, text="Developer", bg=C["header"], fg=C["text_m"], font=(FF, 8)
        ).pack(anchor="e")
        tk.Label(
            dev_col, text=DEVELOPER, bg=C["header"], fg="#e2e8f0", font=(FF, 9, "bold")
        ).pack(anchor="e")

        # Accent line
        tk.Frame(self.root, bg=C["primary"], height=3).pack(fill="x")

    # ── Body ─────────────────────────────────────────────────────────────────
    def _build_body(self):
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=26, pady=20)

        self._build_toolbar(body)
        self._build_run_panel(body)  # ← pack to bottom FIRST
        self._build_project_list(body)  # ← then fill remaining middle space

    def _build_toolbar(self, parent):
        toolbar = tk.Frame(parent, bg=C["bg"])
        toolbar.pack(fill="x", pady=(0, 12))

        # Left: Title + count badge
        left = tk.Frame(toolbar, bg=C["bg"])
        left.pack(side="left", fill="y")
        tk.Label(
            left,
            text="📋  Active Projects",
            bg=C["bg"],
            fg=C["text"],
            font=(FF, 14, "bold"),
        ).pack(side="left", pady=2)
        self._count_badge = tk.Label(
            left,
            text=" 0 ",
            bg=C["primary"],
            fg="white",
            font=(FF, 9, "bold"),
            padx=6,
            pady=2,
        )
        self._count_badge.pack(side="left", padx=(10, 0))

        # Right: Action buttons
        right = tk.Frame(toolbar, bg=C["bg"])
        right.pack(side="right")

        flat_btn(
            right,
            "➕  New Project",
            lambda: TaskEditor(self),
            C["primary"],
            C["pri_h"],
            "white",
            padx=16,
            pady=8,
            bold=True,
        ).pack(side="left", padx=(0, 6))

        flat_btn(
            right,
            "✏  Edit",
            self.edit_task,
            C["card"],
            C["card_alt"],
            C["text"],
            padx=14,
            pady=8,
        ).pack(side="left", padx=(0, 6))

        flat_btn(
            right,
            "🗑  Delete",
            self.delete_task,
            C["dan_lt"],
            C["danger"],
            C["danger"],
            padx=14,
            pady=8,
        ).pack(side="left", padx=(0, 14))

        # Divider
        tk.Frame(right, bg=C["border"], width=1).pack(side="left", fill="y", pady=4)

        flat_btn(
            right,
            "❓  Help",
            lambda: HelpDialog(self.root),
            C["card"],
            "#ede9fe",
            "#7c3aed",
            padx=14,
            pady=8,
        ).pack(side="left", padx=(14, 0))

    def _build_project_list(self, parent):
        # Card wrapper
        card = tk.Frame(
            parent, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(fill="both", expand=True)

        # Column header bar
        col_hdr = tk.Frame(card, bg=C["card_alt"], height=40)
        col_hdr.pack(fill="x")
        col_hdr.pack_propagate(False)
        tk.Label(
            col_hdr,
            text="  Double-click a project to edit",
            bg=C["card_alt"],
            fg=C["text_m"],
            font=(FF, 8),
        ).pack(side="right", padx=14)
        tk.Label(
            col_hdr,
            text="  Projects",
            bg=C["card_alt"],
            fg=C["text"],
            font=(FF, 9, "bold"),
        ).pack(side="left", padx=14, pady=10)

        # Treeview frame
        tv_frame = tk.Frame(card, bg=C["card"])
        tv_frame.pack(fill="both", expand=True, padx=2, pady=(0, 2))

        self.tree = ttk.Treeview(
            tv_frame,
            columns=("Name", "Output", "Mode"),
            show="headings",
            selectmode="extended",
            style="Pro.Treeview",
        )
        self.tree.heading("Name", text="  📁  Project Name", anchor="w")
        self.tree.heading("Output", text="  📂  Output Path", anchor="w")
        self.tree.heading("Mode", text="  ⚙  Mode", anchor="center")

        self.tree.column("Name", width=260, minwidth=120, anchor="w")
        self.tree.column("Output", width=560, minwidth=200, anchor="w")
        self.tree.column("Mode", width=120, minwidth=80, anchor="center")

        vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Row color tags
        self.tree.tag_configure(
            "normal", background=C["tag_n_bg"], foreground=C["tag_n_fg"]
        )
        self.tree.tag_configure(
            "transpose", background=C["tag_t_bg"], foreground=C["tag_t_fg"]
        )

        self.tree.bind("<Double-1>", lambda e: self.edit_task())
        self.tree.bind("<Delete>", lambda e: self.delete_task())

    def _build_run_panel(self, parent):
        # Separator line above panel
        tk.Frame(parent, bg=C["border"], height=1).pack(side="bottom", fill="x")
        card = tk.Frame(
            parent, bg=C["card"], highlightbackground=C["border"], highlightthickness=1
        )
        card.pack(side="bottom", fill="x", pady=(0, 0))

        inner = tk.Frame(card, bg=C["card"])
        inner.pack(fill="x", padx=20, pady=18)

        # Left: Info text
        info = tk.Frame(inner, bg=C["card"])
        info.pack(side="left")
        tk.Label(
            info,
            text="⚙  Execution Panel",
            bg=C["card"],
            fg=C["text"],
            font=(FF, 11, "bold"),
        ).pack(anchor="w")
        tk.Label(
            info,
            text="Select one or more projects, then click RUN to process them.",
            bg=C["card"],
            fg=C["text_s"],
            font=(FF, 9),
        ).pack(anchor="w")

        # Right: Big RUN button
        self._run_btn = tk.Frame(inner, bg=C["success"], cursor="hand2")
        self._run_btn.pack(side="right")
        self._run_lbl = tk.Label(
            self._run_btn,
            text="🚀  RUN SELECTED PROJECTS",
            bg=C["success"],
            fg="white",
            font=(FF, 13, "bold"),
            padx=34,
            pady=16,
            cursor="hand2",
        )
        self._run_lbl.pack()
        for w in (self._run_btn, self._run_lbl):
            w.bind("<Enter>", lambda e: self._run_hover(True))
            w.bind("<Leave>", lambda e: self._run_hover(False))
            w.bind("<Button-1>", lambda e: self.run_selected())

    def _run_hover(self, entering: bool):
        c = C["suc_h"] if entering else C["success"]
        self._run_btn.configure(bg=c)
        self._run_lbl.configure(bg=c)

    # ── Status Bar ───────────────────────────────────────────────────────────
    def _build_status_bar(self):
        tk.Frame(self.root, bg=C["divider"], height=1).pack(fill="x")
        bar = tk.Frame(self.root, bg=C["status_bg"], height=28)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        self._status_var = tk.StringVar(value="✅  Ready")
        self._status_lbl = tk.Label(
            bar,
            textvariable=self._status_var,
            bg=C["status_bg"],
            fg=C["text_m"],
            font=(FF, 9),
            padx=16,
        )
        self._status_lbl.pack(side="left", pady=4)

        tk.Label(
            bar,
            text=f"{APP_NAME}  ©  2025   |   {DEVELOPER}",
            bg=C["status_bg"],
            fg="#475569",
            font=(FF, 9),
            padx=16,
        ).pack(side="right", pady=4)

    def set_status(self, msg: str, color: str = "#94a3b8"):
        self._status_var.set(msg)
        self._status_lbl.configure(fg=color)
        self.root.update_idletasks()

    # ── Task List ─────────────────────────────────────────────────────────────
    def refresh_task_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.config.read(self.config_path, encoding="utf-8")

        count = 0
        for sec in self.config.sections():
            if not sec.startswith("Task:"):
                continue
            has_melt = bool(self.config.get(sec, "melt_id_vars", fallback="").strip())
            has_un_melt = bool(self.config.get(sec, "un_melt_columns", fallback="").strip())
            if has_un_melt:
                mode = "↩️  Un-Transpose"
                tag = "transpose"
            elif has_melt:
                mode = "🔄  Transpose"
                tag = "transpose"
            else:
                mode = "📋  Normal"
                tag = "normal"
            out = self.config.get(sec, "output_name", fallback="-")
            self.tree.insert(
                "",
                tk.END,
                iid=sec,
                values=(f"  {sec[5:]}", f"  {out}", mode),
                tags=(tag,),
            )
            count += 1

        self._count_badge.configure(text=f"  {count}  ")
        self.set_status(f"✅  Ready  —  {count} project(s) loaded")

    # ── Actions ───────────────────────────────────────────────────────────────
    def edit_task(self):
        sel = self.tree.selection()
        if sel:
            TaskEditor(self, sel[0])
        else:
            messagebox.showwarning(
                "No Selection", "Please select a project to edit.", parent=self.root
            )

    def delete_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(
                "No Selection",
                "Please select one or more projects to delete.",
                parent=self.root,
            )
            return
        names = ", ".join(s[5:] for s in sel)
        if messagebox.askyesno(
            "Confirm Deletion",
            f"Delete {len(sel)} project(s)?\n\n{names}\n\nThis action cannot be undone.",
            parent=self.root,
        ):
            for s in sel:
                self.config.remove_section(s)
            self.save_config_to_file()
            self.refresh_task_list()
            self.set_status(f"🗑  Deleted {len(sel)} project(s).", C["warning"])

    def save_config_to_file(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            self.config.write(f)

    def run_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(
                "No Selection",
                "Please select at least one project to run.",
                parent=self.root,
            )
            return

        # Validate
        errors = self.converter.validate_tasks()
        sel_errors = [e for e in errors if any(f"[{s[5:]}]" in e for s in sel)]
        if sel_errors:
            messagebox.showerror(
                "Validation Errors", "\n".join(sel_errors), parent=self.root
            )
            return

        # Processing state
        self._run_lbl.configure(text="⏳  Processing...", bg=C["warning"])
        self._run_btn.configure(bg=C["warning"])
        self.set_status(f"⏳  Processing {len(sel)} project(s)…", C["warning"])
        self.root.update()

        try:
            for s in sel:
                self.converter.process_task(s[5:], dict(self.config[s]))

            self._run_lbl.configure(text="🚀  RUN SELECTED PROJECTS", bg=C["success"])
            self._run_btn.configure(bg=C["success"])
            self.set_status(
                f"✅  Successfully processed {len(sel)} project(s)!", "#10b981"
            )
            messagebox.showinfo(
                "✅  Done!",
                f"Successfully processed {len(sel)} project(s)!\n\n"
                "Check the configured output paths for results.",
                parent=self.root,
            )
        except Exception as ex:
            self._run_lbl.configure(text="🚀  RUN SELECTED PROJECTS", bg=C["success"])
            self._run_btn.configure(bg=C["success"])
            
            # Build user-friendly error message
            err_msg = str(ex)
            suggestion = ""
            
            # Check for common errors and provide suggestions
            if "bad escape" in err_msg.lower():
                suggestion = "\n\n💡 Possible causes:\n" \
                           "• Data contains backslash (\\) which conflicts with regex\n" \
                           "• Fix: Check your Excel data for backslashes\n" \
                           "• Or simplify the data (replace \\ with / or other characters)"
            elif "template error" in err_msg.lower():
                suggestion = "\n\n💡 How to fix:\n" \
                           "• Open the template file mentioned in the error\n" \
                           "• Remove spaces before }} in {{ }}\n" \
                           "• Example: change '{{ CI Name }}' to '{{CI Name}}'"
            elif "not found" in err_msg.lower() and "header" in err_msg.lower():
                suggestion = "\n\n💡 How to fix:\n" \
                           "• Check if the Excel file has the correct column headers\n" \
                           "• Make sure {{ column name }} in template matches exactly"
            elif "no such file" in err_msg.lower() or "cannot find" in err_msg.lower():
                suggestion = "\n\n💡 How to fix:\n" \
                           "• The input file may have been moved or deleted\n" \
                           "• Click 'Edit' and browse to select the correct file again"
            
            self.set_status(f"❌  Error: {err_msg[:70]}", C["danger"])
            messagebox.showerror(
                "Process Error", 
                f"{err_msg}{suggestion}\n\n" 
                f"Task: {sel[0][5:] if sel else 'Unknown'}\n"
                f"If problem persists, check Help → FAQ for common solutions.",
                parent=self.root,
            )


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys

    from license_manager import is_activated

    # ── License Gate ────────────────────────────────────────────────────────
    if not is_activated():
        from activate_dialog import ActivationDialog

        dlg = ActivationDialog()
        dlg.mainloop()
        if not dlg.approved:
            sys.exit(0)  # ปิดโปรแกรมถ้ายังไม่ลงทะเบียน

    # ── Launch Main App ─────────────────────────────────────────────────────
    root = tk.Tk()
    try:
        root.iconbitmap("ea.ico")
    except Exception:
        pass
    app = ASBCGui(root)
    root.mainloop()
