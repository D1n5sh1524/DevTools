"""
theme.py — Modern dark palette + ttk theme application
"""
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk


# ── Font probe (must be before MONO_FONT constant) ────────────────────────────
def _font_exists(name: str) -> bool:
    """Return True if a font family is available on this system."""
    try:
        # tkinter.font.families() needs a root window; if none exists yet
        # we skip gracefully and fall back to the safe default.
        root = tk._default_root
        if root is None:
            return False
        return name in tkfont.families(root)
    except Exception:
        return False


# ─── Dark Palette ─────────────────────────────────────────────────────────────
BG          = "#0f1117"        # main content background
PANEL       = "#1a1d27"        # card / text-area background
SIDEBAR_BG  = "#13151f"        # sidebar background
BORDER      = "#2a2d3e"        # subtle dividers
HDR_BG      = "#13151f"        # header strip
LNUM_BG     = "#161926"        # gutter background
LNUM_FG     = "#3d4166"        # line-number digits

FG          = "#e2e4f0"        # primary text
FG_DIM      = "#565a7a"        # secondary / hint text
FG_MID      = "#9295b0"        # mid-contrast labels

ACCENT      = "#6c8ef5"        # blue accent
ACCENT_DARK = "#4f72e8"        # accent pressed
ACCENT_GLOW = "#1e2a5e"        # accent subtle tint

STATUS_OK   = "#4ade80"        # green
STATUS_ERR  = "#f87171"        # red
STATUS_DIM  = "#565a7a"        # grey

# ── Sidebar nav constants ─────────────────────────────────────────────────────
SIDEBAR_W         = 200        # px
NAV_ITEM_H        = 44         # px per nav button
NAV_ACTIVE_BG     = "#1e2a5e"  # selected tool highlight
NAV_ACTIVE_FG     = "#6c8ef5"
NAV_HOVER_BG      = "#1c1f2e"
NAV_INACTIVE_FG   = "#9295b0"

# ── Toggle constants ──────────────────────────────────────────────────────────
TOGGLE_ON_BG      = "#6c8ef5"
TOGGLE_OFF_BG     = "#2a2d3e"
TOGGLE_THUMB      = "#ffffff"

# ── Diff colours ──────────────────────────────────────────────────────────────
A_REM_BG = "#3b1219";  A_REM_FG = "#f87171"
A_CHG_BG = "#2d2000";  A_CHG_FG = "#fbbf24"
B_ADD_BG = "#0f2d1a";  B_ADD_FG = "#4ade80"
B_NEW_BG = "#0d1e3b";  B_NEW_FG = "#93c5fd"
BLANK_BG = "#161926"

# ── Fonts ─────────────────────────────────────────────────────────────────────
# MONO_FONT resolved at apply_theme() time when a root window exists;
# here we provide a safe startup default.
MONO_FONT        = ("Consolas", 13)
UI_FONT          = ("Segoe UI", 11)
BTN_FONT         = ("Segoe UI", 11, "bold")
LNUM_FONT        = ("Consolas", 13)
SIDEBAR_FONT     = ("Segoe UI", 11)
SIDEBAR_FONT_ACT = ("Segoe UI", 11, "bold")


def apply_theme(root):
    """Apply the modern dark theme to the application."""
    global MONO_FONT, LNUM_FONT

    # Resolve best monospace font now that a root window exists
    for candidate in ("JetBrains Mono", "Cascadia Code", "Fira Code",
                      "SF Mono", "Menlo", "Consolas"):
        if _font_exists(candidate):
            MONO_FONT = (candidate, 13)
            LNUM_FONT = (candidate, 13)
            break

    s = ttk.Style(root)
    s.theme_use("clam")

    # ── Base defaults ─────────────────────────────────────────────────────────
    s.configure(".",
        background=BG, foreground=FG,
        fieldbackground=PANEL,
        bordercolor=BORDER, troughcolor=BORDER,
        selectbackground=ACCENT, selectforeground="#fff",
        font=UI_FONT,
        relief="flat",
    )

    # ── Frames ────────────────────────────────────────────────────────────────
    s.configure("TFrame",         background=BG)
    s.configure("Card.TFrame",    background=PANEL, relief="flat")
    s.configure("Sidebar.TFrame", background=SIDEBAR_BG)

    # ── LabelFrames ───────────────────────────────────────────────────────────
    s.configure("TLabelframe",
        background=PANEL, bordercolor=BORDER, relief="flat")
    s.configure("TLabelframe.Label",
        background=PANEL, foreground=FG_MID,
        font=("Segoe UI", 10, "bold"))

    # ── Labels ────────────────────────────────────────────────────────────────
    s.configure("TLabel",
        background=BG, foreground=FG, font=UI_FONT)
    s.configure("Dim.TLabel",
        background=BG, foreground=FG_DIM, font=("Segoe UI", 10))
    s.configure("Mid.TLabel",
        background=BG, foreground=FG_MID, font=("Segoe UI", 10))
    s.configure("Panel.TLabel",
        background=PANEL, foreground=FG, font=UI_FONT)

    # ── Buttons ───────────────────────────────────────────────────────────────
    s.configure("TButton",
        background=PANEL, foreground=FG_MID,
        bordercolor=BORDER, relief="flat",
        padding=[12, 7], font=BTN_FONT)
    s.map("TButton",
        background=[("active", BORDER)],
        foreground=[("active", FG)])

    s.configure("Accent.TButton",
        background=ACCENT, foreground="#fff",
        bordercolor=ACCENT, relief="flat",
        padding=[14, 7], font=BTN_FONT)
    s.map("Accent.TButton",
        background=[("active", ACCENT_DARK)])

    s.configure("Danger.TButton",
        background="#2d1515", foreground=STATUS_ERR,
        bordercolor="#5a2222", relief="flat",
        padding=[12, 7], font=BTN_FONT)
    s.map("Danger.TButton",
        background=[("active", "#3d1a1a")])

    s.configure("Ghost.TButton",
        background=BG, foreground=FG_DIM,
        bordercolor=BORDER, relief="flat",
        padding=[10, 6], font=UI_FONT)
    s.map("Ghost.TButton",
        background=[("active", PANEL)],
        foreground=[("active", FG)])

    # ── Notebook (kept for compat; sidebar is primary nav) ────────────────────
    s.configure("TNotebook",     background=BG, borderwidth=0)
    s.configure("TNotebook.Tab", background=BG, foreground=FG_DIM,
                padding=[16, 8], font=BTN_FONT)
    s.map("TNotebook.Tab",
        background=[("selected", PANEL)],
        foreground=[("selected", ACCENT)])

    # ── Checkbutton ───────────────────────────────────────────────────────────
    s.configure("TCheckbutton",  background=BG, foreground=FG_MID, font=UI_FONT)
    s.map("TCheckbutton",
        background=[("active", BG)],
        foreground=[("active", FG)])

    # ── Spinbox ───────────────────────────────────────────────────────────────
    s.configure("TSpinbox",
        background=PANEL, foreground=FG,
        fieldbackground=PANEL, bordercolor=BORDER,
        arrowcolor=FG_DIM, insertcolor=FG, font=UI_FONT)

    # ── Separators / Panes ────────────────────────────────────────────────────
    s.configure("TSeparator",   background=BORDER)
    s.configure("TPanedwindow", background=BORDER)

    # ── Scrollbars ────────────────────────────────────────────────────────────
    s.configure("Vertical.TScrollbar",
        background=LNUM_BG, troughcolor=BG,
        arrowcolor=FG_DIM, bordercolor=BG, relief="flat", width=8)
    s.map("Vertical.TScrollbar",
        background=[("active", BORDER)])
    s.configure("Horizontal.TScrollbar",
        background=LNUM_BG, troughcolor=BG,
        arrowcolor=FG_DIM, bordercolor=BG, relief="flat", width=6)
    s.map("Horizontal.TScrollbar",
        background=[("active", BORDER)])


def hsep(parent, pady=4):
    """Thin horizontal separator."""
    ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=pady)
