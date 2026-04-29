"""
╔══════════════════════════════════════════════════════════╗
║  ASBC License Key Generator  —  DEVELOPER TOOL ONLY     ║
║  ⚠️  DO NOT DISTRIBUTE THIS FILE TO CUSTOMERS           ║
╚══════════════════════════════════════════════════════════╝
"""

import hashlib
import hmac
import tkinter as tk
from tkinter import messagebox

# ──────────────────────────────────────────────────────────────────────────────
# ⚠️  MUST match _P in license_manager.py EXACTLY
# ──────────────────────────────────────────────────────────────────────────────
_P = ["ASBC", "P40x", "2025", "rK9n", "Wq7v", "mJ3z"]
_SK = "-".join(_P)

FF = "Segoe UI"
FM = "Consolas"


def _generate(machine_id: str) -> str:
    mid = machine_id.replace("-", "").upper().encode("utf-8")
    h = hmac.new(_SK.encode("utf-8"), mid, hashlib.sha256).hexdigest()[:20].upper()
    return "-".join(h[i : i + 5] for i in range(0, 20, 5))


# ── GUI ───────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("🔑  ASBC License Key Generator  [DEVELOPER ONLY]")
root.geometry("520x340")
root.resizable(False, False)
root.configure(bg="#0f172a")

# Warning banner
tk.Label(
    root,
    text="  ⚠️  DEVELOPER TOOL — DO NOT DISTRIBUTE TO CUSTOMERS  ⚠️  ",
    bg="#dc2626",
    fg="white",
    font=(FF, 9, "bold"),
    pady=5,
).pack(fill="x")

body = tk.Frame(root, bg="#0f172a")
body.pack(fill="both", expand=True, padx=24, pady=20)

# Machine ID input
tk.Label(
    body, text="Machine ID  (รับมาจากลูกค้า):", bg="#0f172a", fg="#94a3b8", font=(FF, 9)
).pack(anchor="w")
mid_var = tk.StringVar()
mid_entry = tk.Entry(
    body,
    textvariable=mid_var,
    bg="#1e293b",
    fg="#e2e8f0",
    font=(FM, 13),
    relief="flat",
    insertbackground="white",
    highlightbackground="#334155",
    highlightthickness=1,
)
mid_entry.pack(fill="x", ipady=9, pady=(4, 18))

# Generated key output
tk.Label(
    body, text="License Key  (ส่งให้ลูกค้า):", bg="#0f172a", fg="#94a3b8", font=(FF, 9)
).pack(anchor="w")
key_var = tk.StringVar()
key_out = tk.Entry(
    body,
    textvariable=key_var,
    bg="#1e2030",
    fg="#a6e3a1",
    font=(FM, 15, "bold"),
    relief="flat",
    state="readonly",
    highlightbackground="#334155",
    highlightthickness=1,
    readonlybackground="#1e2030",
)
key_out.pack(fill="x", ipady=10, pady=(4, 20))


def do_generate():
    mid = mid_var.get().strip()
    if not mid:
        messagebox.showwarning("Error", "กรุณาใส่ Machine ID ก่อน", parent=root)
        return
    key_var.set(_generate(mid))


def do_copy():
    key = key_var.get().strip()
    if not key:
        messagebox.showwarning("Error", "กด Generate ก่อน", parent=root)
        return
    root.clipboard_clear()
    root.clipboard_append(key)
    messagebox.showinfo("Copied", f"คัดลอก License Key แล้ว:\n\n{key}", parent=root)


# Buttons
btn_row = tk.Frame(body, bg="#0f172a")
btn_row.pack(fill="x")

for text, cmd, bg, hov in [
    ("⚡  Generate Key", do_generate, "#2563eb", "#1d4ed8"),
    ("📋  Copy Key", do_copy, "#059669", "#047857"),
]:
    lbl = tk.Label(
        btn_row,
        text=text,
        bg=bg,
        fg="white",
        font=(FF, 11, "bold"),
        padx=18,
        pady=10,
        cursor="hand2",
    )
    lbl.pack(side="left", padx=(0, 10))
    lbl.bind("<Enter>", lambda e, h=hov: e.widget.configure(bg=h))
    lbl.bind("<Leave>", lambda e, b=bg: e.widget.configure(bg=b))
    lbl.bind("<Button-1>", lambda e, c=cmd: c())

root.mainloop()
