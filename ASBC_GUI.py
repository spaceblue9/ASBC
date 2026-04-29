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
        self._build_body()
        self._build_footer()

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
            width=290,
        )
        help_wrap.pack(side="right", fill="y", padx=(12, 0))
        help_wrap.pack_propagate(False)

        help_top = tk.Frame(help_wrap, bg=C["card_alt"], height=34)
        help_top.pack(fill="x")
        help_top.pack_propagate(False)
        tk.Label(
            help_top,
            text="  💡  Quick Reference",
            bg=C["card_alt"],
            fg=C["text"],
            font=(FF, 9, "bold"),
        ).pack(side="left", pady=8)

        scroll = ScrollableFrame(help_wrap, bg=C["card"])
        scroll.pack(fill="both", expand=True)
        content = scroll.inner

        sections = [
            (
                "📂  Template Structure",
                "Header  → แสดงครั้งเดียวด้านบน\n"
                "Body    → ซ้ำตามจำนวนแถวข้อมูล\n"
                "Footer  → แสดงครั้งเดียวด้านล่าง",
            ),
            (
                "🌟  ดึงข้อมูลจาก Excel",
                "ใส่ชื่อหัวคอลัมน์ใน {{ }}\n"
                "ตัวอย่าง:\n"
                "  {{ CI Name }}\n"
                "  {{ OS Version }}\n"
                "  {{ IP Address }}",
            ),
            (
                "✨  Variable พิเศษ",
                "{{ ID }}     → หมายเลขแถว\n"
                "{{ Key }}    → ชื่อคอลัมน์\n"
                "{{ Value }}  → ข้อมูลในช่อง",
            ),
            (
                "🔄  โหมด Transpose",
                "จับตารางแนวนอนมาเป็น\nคู่ Key-Value แนวตั้ง\nเหมาะกับไฟล์ Properties",
            ),
            (
                "📝  ตัวอย่าง Body",
                "CI_NAME={{ CI Name }}\nOS={{ OS }}\nIP={{ IP Address }}\n---",
            ),
            (
                "⚠️  ข้อควรระวัง",
                "• ชื่อใน {{ }} ต้องตรงกับ\n"
                "  หัวข้อใน Excel\n"
                "• ตัวพิมพ์เล็ก-ใหญ่ ใช้ได้ทั้งคู่\n"
                "• กด Save ก่อนปิดเสมอ",
            ),
        ]

        for title, text in sections:
            tk.Label(
                content,
                text=title,
                bg=C["card"],
                fg=C["text"],
                font=(FF, 9, "bold"),
                anchor="w",
                padx=14,
                pady=(8, 2),
            ).pack(fill="x")
            bar = tk.Frame(content, bg=C["primary"], height=2)
            bar.pack(fill="x", padx=14, pady=(0, 4))
            tk.Label(
                content,
                text=text,
                bg=C["card"],
                fg=C["text_s"],
                font=(FM, 9),
                justify="left",
                anchor="w",
                padx=14,
                pady=(0, 8),
            ).pack(fill="x")

    def _build_footer(self):
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")
        footer = tk.Frame(self, bg=C["card_alt"], height=54)
        footer.pack(fill="x")
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
        self.main_app.save_config_to_file()
        self.main_app.refresh_task_list()
        self.main_app.set_status(f"✅  Project '{name}' saved.", "#10b981")
        self.destroy()


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
        ).pack(side="left")

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
            mode = "🔄  Transpose" if has_melt else "📋  Normal"
            tag = "transpose" if has_melt else "normal"
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
            self.set_status(f"❌  Error: {str(ex)[:70]}", C["danger"])
            messagebox.showerror("Process Error", str(ex), parent=self.root)


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
