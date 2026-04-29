"""
ASBC Converter Pro — Activation Dialog
Shown at startup when no valid license is found.
"""

import tkinter as tk
from tkinter import messagebox

from license_manager import activate, get_machine_id

# ── Color palette ─────────────────────────────────────────────────────────────
BG = "#f1f5f9"
DARK = "#0f172a"
CARD = "#ffffff"
BORDER = "#e2e8f0"
PRIMARY = "#2563eb"
SUCCESS = "#059669"
DANGER = "#dc2626"
TEXT = "#0f172a"
TEXT_S = "#64748b"
TEXT_W = "#ffffff"
TEXT_M = "#94a3b8"
STATUS = "#1e293b"
CODE_BG = "#1e2030"
CODE_FG = "#cdd6f4"
FF = "Segoe UI"
FM = "Consolas"


def _flat(parent, text, cmd, bg, hov, fg=TEXT_W, px=14, py=8, bold=False):
    w = tk.Label(
        parent,
        text=text,
        bg=bg,
        fg=fg,
        font=(FF, 10, "bold" if bold else "normal"),
        padx=px,
        pady=py,
        cursor="hand2",
        relief="flat",
    )
    w.bind("<Enter>", lambda e: w.configure(bg=hov))
    w.bind("<Leave>", lambda e: w.configure(bg=bg))
    w.bind("<Button-1>", lambda e: cmd())
    return w


class ActivationDialog(tk.Tk):
    """
    Standalone activation window.
    After mainloop() exits, check `.approved` to decide whether to proceed.
    """

    def __init__(self):
        super().__init__()
        self.approved = False
        self.machine_id = get_machine_id()

        self.title("ASBC Converter Pro — Activation Required")
        self.geometry("580x500")
        self.resizable(False, False)
        self.configure(bg=BG)
        try:
            self.iconbitmap("ea.ico")
        except Exception:
            pass

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        self._hdr()
        tk.Frame(self, bg=PRIMARY, height=3).pack(fill="x")
        self._body()
        self._footer()

    def _hdr(self):
        hdr = tk.Frame(self, bg=DARK, height=68)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=DARK)
        left.pack(side="left", padx=22, pady=14)

        icon_box = tk.Frame(left, bg=DANGER, width=40, height=40)
        icon_box.pack_propagate(False)
        icon_box.pack(side="left", padx=(0, 14))
        tk.Label(
            icon_box, text="🔒", bg=DANGER, fg=TEXT_W, font=("Segoe UI Emoji", 18)
        ).pack(expand=True)

        col = tk.Frame(left, bg=DARK)
        col.pack(side="left")
        tk.Label(
            col, text="ASBC Converter Pro", bg=DARK, fg=TEXT_W, font=(FF, 14, "bold")
        ).pack(anchor="w")
        tk.Label(
            col,
            text="โปรแกรมนี้ยังไม่ได้รับอนุญาตให้ใช้งาน",
            bg=DARK,
            fg="#f87171",
            font=(FF, 9),
        ).pack(anchor="w")

        right = tk.Frame(hdr, bg=DARK)
        right.pack(side="right", padx=22)
        tk.Label(
            right,
            text="  v2.0  ",
            bg=PRIMARY,
            fg=TEXT_W,
            font=(FF, 8, "bold"),
            padx=6,
            pady=3,
        ).pack()

    def _body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=22, pady=16)

        # ── Step 1 ────────────────────────────────────────────────────────────
        s1 = tk.Frame(body, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        s1.pack(fill="x", pady=(0, 14))

        s1_hdr = tk.Frame(s1, bg="#f8fafc", height=36)
        s1_hdr.pack(fill="x")
        s1_hdr.pack_propagate(False)
        tk.Label(
            s1_hdr,
            text="  STEP 1  ",
            bg=PRIMARY,
            fg=TEXT_W,
            font=(FF, 9, "bold"),
            pady=2,
        ).pack(side="left")
        tk.Label(
            s1_hdr,
            text="  คัดลอก Machine ID แล้วส่งให้ผู้พัฒนา",
            bg="#f8fafc",
            fg=TEXT,
            font=(FF, 9),
        ).pack(side="left")

        id_row = tk.Frame(s1, bg=CARD)
        id_row.pack(fill="x", padx=16, pady=(10, 14))

        id_lbl = tk.Label(
            id_row,
            text=self.machine_id,
            bg=CODE_BG,
            fg=CODE_FG,
            font=(FM, 17, "bold"),
            padx=18,
            pady=12,
        )
        id_lbl.pack(side="left")

        self._copy_btn = tk.Label(
            id_row,
            text="📋  Copy",
            bg=PRIMARY,
            fg=TEXT_W,
            font=(FF, 10, "bold"),
            padx=14,
            pady=12,
            cursor="hand2",
        )
        self._copy_btn.pack(side="left", padx=(10, 0))
        self._copy_btn.bind("<Button-1>", lambda e: self._copy())

        # ── Step 2 ────────────────────────────────────────────────────────────
        s2 = tk.Frame(body, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        s2.pack(fill="x")

        s2_hdr = tk.Frame(s2, bg="#f8fafc", height=36)
        s2_hdr.pack(fill="x")
        s2_hdr.pack_propagate(False)
        tk.Label(
            s2_hdr,
            text="  STEP 2  ",
            bg=SUCCESS,
            fg=TEXT_W,
            font=(FF, 9, "bold"),
            pady=2,
        ).pack(side="left")
        tk.Label(
            s2_hdr, text="  ใส่ License Key ที่ได้รับมา", bg="#f8fafc", fg=TEXT, font=(FF, 9)
        ).pack(side="left")

        key_frame = tk.Frame(s2, bg=CARD)
        key_frame.pack(fill="x", padx=16, pady=(10, 14))

        self.key_var = tk.StringVar()
        key_entry = tk.Entry(
            key_frame,
            textvariable=self.key_var,
            bg="#f8fafc",
            fg=TEXT,
            font=(FM, 13),
            relief="flat",
            highlightbackground=BORDER,
            highlightthickness=1,
            insertbackground=PRIMARY,
        )
        key_entry.pack(fill="x", ipady=10)
        key_entry.bind("<Return>", lambda e: self._activate())

        tk.Label(
            s2,
            text="  รูปแบบ: XXXXX-XXXXX-XXXXX-XXXXX",
            bg=CARD,
            fg=TEXT_S,
            font=(FF, 8),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 10))

        # ── Activate button ───────────────────────────────────────────────────
        act = _flat(
            body,
            "🔓  Activate License",
            self._activate,
            SUCCESS,
            "#047857",
            bold=True,
            py=14,
        )
        act.pack(fill="x", pady=(14, 0))

    def _footer(self):
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        foot = tk.Frame(self, bg=STATUS, height=28)
        foot.pack(fill="x")
        foot.pack_propagate(False)
        tk.Label(
            foot,
            text="ต้องการความช่วยเหลือ? ติดต่อผู้พัฒนา  |  ASBC Converter Pro © 2025",
            bg=STATUS,
            fg="#475569",
            font=(FF, 8),
        ).pack(side="right", padx=16)

    # ── Actions ───────────────────────────────────────────────────────────────
    def _copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.machine_id)
        self._copy_btn.configure(text="✅  Copied!", bg=SUCCESS)
        self.after(2000, lambda: self._copy_btn.configure(text="📋  Copy", bg=PRIMARY))

    def _activate(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning(
                "กรุณาใส่ Key", "กรุณาใส่ License Key ที่ได้รับมา", parent=self
            )
            return
        if activate(key):
            self.approved = True
            messagebox.showinfo(
                "✅  ลงทะเบียนสำเร็จ",
                "ยินดีต้อนรับสู่ ASBC Converter Pro!\n\nการลงทะเบียนเสร็จสมบูรณ์",
                parent=self,
            )
            self.destroy()
        else:
            messagebox.showerror(
                "❌  License Key ไม่ถูกต้อง",
                "ไม่สามารถลงทะเบียนได้\n\n"
                "• ตรวจสอบว่าพิมพ์ Key ถูกต้อง\n"
                "• ตรวจสอบว่า Machine ID ตรงกัน\n"
                "• ติดต่อผู้พัฒนาถ้าปัญหายังไม่หาย",
                parent=self,
            )
