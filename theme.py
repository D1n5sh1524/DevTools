"""
theme.py — Palette constants and ttk theme application
"""
import tkinter as tk
from tkinter import ttk

# ─── Palette ──────────────────────────────────────────────────────────────────
BG          = "#faf7f2"
PANEL       = "#ffffff"
BORDER      = "#d8d0c4"
HDR_BG      = "#f0ece4"
LNUM_BG     = "#f0ece4"
LNUM_FG     = "#a09880"
FG          = "#1a1a1a"
FG_DIM      = "#7a7060"
ACCENT      = "#2563eb"
ACCENT_DARK = "#1d4ed8"
STATUS_OK   = "#16a34a"
STATUS_ERR  = "#dc2626"
STATUS_DIM  = "#7a7060"

# diff colours
A_REM_BG = "#fde8e8";  A_REM_FG = "#991b1b"
A_CHG_BG = "#fff3cd";  A_CHG_FG = "#854d0e"
B_ADD_BG = "#d4f4dd";  B_ADD_FG = "#166534"
B_NEW_BG = "#dbeafe";  B_NEW_FG = "#1e40af"
BLANK_BG = "#f5f3f0"

MONO_FONT = ("Consolas", 13)
UI_FONT   = ("Segoe UI", 11, "bold")
BTN_FONT  = ("Segoe UI", 11, "bold")
LNUM_FONT = ("Consolas", 13)


def apply_theme(root):
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=BG, foreground=FG, fieldbackground=PANEL,
                bordercolor=BORDER, troughcolor=BORDER, font=UI_FONT,
                selectbackground=ACCENT, selectforeground="#fff")
    s.configure("TNotebook", background=HDR_BG, borderwidth=0)
    s.configure("TNotebook.Tab", background=HDR_BG, foreground=FG_DIM,
                padding=[16, 8], font=BTN_FONT)
    s.map("TNotebook.Tab", background=[("selected", BG)],
          foreground=[("selected", ACCENT)])
    s.configure("TFrame",            background=BG)
    s.configure("TLabelframe",       background=BG, bordercolor=BORDER, relief="groove")
    s.configure("TLabelframe.Label", background=BG, foreground=FG_DIM,
                font=("Segoe UI", 10, "bold"))
    s.configure("TLabel",     background=BG, foreground=FG,     font=UI_FONT)
    s.configure("Dim.TLabel", background=BG, foreground=FG_DIM, font=("Segoe UI", 10))
    s.configure("TButton", background=PANEL, foreground=FG, bordercolor=BORDER,
                relief="flat", padding=[12, 6], font=BTN_FONT)
    s.map("TButton", background=[("active", HDR_BG)])
    s.configure("Accent.TButton", background=ACCENT, foreground="#fff",
                bordercolor=ACCENT, relief="flat", padding=[14, 7], font=BTN_FONT)
    s.map("Accent.TButton", background=[("active", ACCENT_DARK)])
    s.configure("Danger.TButton", background="#fee2e2", foreground=STATUS_ERR,
                bordercolor="#fca5a5", relief="flat", padding=[12, 6], font=BTN_FONT)
    s.map("Danger.TButton", background=[("active", "#fca5a5")])
    s.configure("TCheckbutton", background=BG, foreground=FG, font=UI_FONT)
    s.map("TCheckbutton", background=[("active", BG)])
    s.configure("TSpinbox", background=PANEL, foreground=FG,
                fieldbackground=PANEL, bordercolor=BORDER,
                arrowcolor=FG_DIM, insertcolor=FG, font=UI_FONT)
    s.configure("TSeparator",    background=BORDER)
    s.configure("TPanedwindow",  background=BORDER)


def hsep(parent, pady=4):
    ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=pady)