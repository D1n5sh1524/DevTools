"""
main.py — DevTools entry point
Modern dark UI with sidebar navigation and toggle tool visibility.

Run:  python main.py
Deps: Python 3.x, qrcode, Pillow  (tkinter built-in)
"""

import tkinter as tk
from tkinter import ttk

from theme import (
    apply_theme,
    BG, PANEL, SIDEBAR_BG, BORDER, HDR_BG,
    FG, FG_DIM, FG_MID,
    ACCENT, ACCENT_DARK, ACCENT_GLOW,
    NAV_ACTIVE_BG, NAV_ACTIVE_FG, NAV_HOVER_BG, NAV_INACTIVE_FG,
    SIDEBAR_W, NAV_ITEM_H,
    TOGGLE_ON_BG, TOGGLE_OFF_BG, TOGGLE_THUMB,
    SIDEBAR_FONT, SIDEBAR_FONT_ACT,
    STATUS_DIM,
)

from json_tab              import JsonTab
from compare_tab           import CompareTab
from qr_tab                import QRCodeTab
from binary_convertor_tab  import BinaryConvertorTab
from uuid_generator_tab    import UUIDGeneratorTab
from toon_tab              import ToonTab
from image_resizer_tab     import ImageResizerTab
from jwt_tab               import JWTTab


# ─── Toggle switch widget ──────────────────────────────────────────────────────
class ToggleSwitch(tk.Canvas):
    """
    Pill-shaped on/off toggle.
    Usage: t = ToggleSwitch(parent, on_change=callback)
           t.set(True)   # programmatic
    """
    W, H = 38, 20

    def __init__(self, parent, on_change=None, initial=True, **kw):
        super().__init__(
            parent,
            width=self.W, height=self.H,
            bg=SIDEBAR_BG,
            highlightthickness=0, bd=0,
            cursor="hand2",
            **kw,
        )
        self._state     = initial
        self._on_change = on_change
        self._thumb_x   = None
        self._draw()
        self.bind("<ButtonRelease-1>", self._toggle)

    def _draw(self):
        self.delete("all")
        r   = self.H // 2
        bg  = TOGGLE_ON_BG if self._state else TOGGLE_OFF_BG

        # track (rounded rectangle)
        self.create_oval(0, 0, self.H, self.H,             fill=bg, outline="")
        self.create_oval(self.W - self.H, 0, self.W, self.H, fill=bg, outline="")
        self.create_rectangle(r, 0, self.W - r, self.H,   fill=bg, outline="")

        # thumb
        pad = 3
        if self._state:
            cx = self.W - r
        else:
            cx = r
        self.create_oval(
            cx - r + pad, pad,
            cx + r - pad, self.H - pad,
            fill=TOGGLE_THUMB, outline="",
        )

    def _toggle(self, _event=None):
        self._state = not self._state
        self._draw()
        if self._on_change:
            self._on_change(self._state)

    def set(self, value: bool):
        if self._state != value:
            self._state = value
            self._draw()

    def get(self) -> bool:
        return self._state


# ─── Sidebar nav button ────────────────────────────────────────────────────────
class NavButton(tk.Frame):
    """
    Single item in the sidebar.  Shows icon + label, highlights on active.
    """
    def __init__(self, parent, icon: str, label: str, on_click, **kw):
        super().__init__(parent, bg=SIDEBAR_BG, cursor="hand2", **kw)
        self._active   = False
        self._on_click = on_click

        self._icon_lbl = tk.Label(self, text=icon,  bg=SIDEBAR_BG,
                                  fg=NAV_INACTIVE_FG, font=("Segoe UI", 14),
                                  width=2, anchor="center")
        self._icon_lbl.pack(side=tk.LEFT, padx=(10, 4), pady=0)

        self._text_lbl = tk.Label(self, text=label, bg=SIDEBAR_BG,
                                  fg=NAV_INACTIVE_FG, font=SIDEBAR_FONT,
                                  anchor="w")
        self._text_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.configure(height=NAV_ITEM_H)
        self.pack_propagate(False)

        for w in (self, self._icon_lbl, self._text_lbl):
            w.bind("<ButtonRelease-1>", self._click)
            w.bind("<Enter>",           self._hover_on)
            w.bind("<Leave>",           self._hover_off)

    def _click(self, _e=None):
        self._on_click()

    def _hover_on(self, _e=None):
        if not self._active:
            self._set_colors(NAV_HOVER_BG, NAV_INACTIVE_FG)

    def _hover_off(self, _e=None):
        if not self._active:
            self._set_colors(SIDEBAR_BG, NAV_INACTIVE_FG)

    def _set_colors(self, bg, fg):
        self.configure(bg=bg)
        self._icon_lbl.configure(bg=bg, fg=fg)
        self._text_lbl.configure(bg=bg, fg=fg)

    def set_active(self, active: bool):
        self._active = active
        if active:
            self._set_colors(NAV_ACTIVE_BG, NAV_ACTIVE_FG)
            self._text_lbl.configure(font=SIDEBAR_FONT_ACT)
        else:
            self._set_colors(SIDEBAR_BG, NAV_INACTIVE_FG)
            self._text_lbl.configure(font=SIDEBAR_FONT)


# ─── Tool registry ─────────────────────────────────────────────────────────────
TOOLS = [
    # (icon, short_label, widget_class, extra_args)
    ("{ }",  "JSON Formatter",    JsonTab,             []),
    ("≠",    "Text Compare",      CompareTab,          []),
    ("⊞",   "QR Code",           QRCodeTab,           []),
    ("01",   "Binary Converter",  BinaryConvertorTab,  ["root"]),
    ("◎",   "UUID Generator",    UUIDGeneratorTab,    ["root"]),
    ("{[]}", "TOON Formatter",    ToonTab,             []),
    ("🖼",   "Image Resizer",     ImageResizerTab,     []),
    ("🔑",   "JWT Tool",          JWTTab,              []),
]


# ─── Main application ──────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.title("DevTools")
    root.geometry("1280x800")
    root.minsize(960, 620)
    root.configure(bg=BG)
    apply_theme(root)

    # ── Outer shell: sidebar | content ───────────────────────────────────────
    shell = tk.Frame(root, bg=BG)
    shell.pack(fill=tk.BOTH, expand=True)

    # ─── SIDEBAR ─────────────────────────────────────────────────────────────
    sidebar = tk.Frame(shell, bg=SIDEBAR_BG, width=SIDEBAR_W)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    sidebar.pack_propagate(False)

    # Logo / title
    logo_frame = tk.Frame(sidebar, bg=SIDEBAR_BG, height=56)
    logo_frame.pack(fill=tk.X)
    logo_frame.pack_propagate(False)
    tk.Label(logo_frame, text="⬡  DevTools", bg=SIDEBAR_BG, fg=ACCENT,
             font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=14, pady=14)

    # Thin separator under logo
    tk.Frame(sidebar, bg=BORDER, height=1).pack(fill=tk.X)

    # Nav area (scrollable if many tools)
    nav_canvas = tk.Canvas(sidebar, bg=SIDEBAR_BG, highlightthickness=0, bd=0)
    nav_canvas.pack(fill=tk.BOTH, expand=True)
    nav_frame = tk.Frame(nav_canvas, bg=SIDEBAR_BG)
    nav_canvas.create_window((0, 0), window=nav_frame, anchor="nw",
                              width=SIDEBAR_W)
    nav_frame.bind("<Configure>",
                   lambda e: nav_canvas.configure(
                       scrollregion=nav_canvas.bbox("all")))

    # Separator + "Tools" label
    tk.Frame(nav_frame, bg=BORDER, height=1).pack(fill=tk.X, pady=(8, 0))
    tk.Label(nav_frame, text="TOOLS", bg=SIDEBAR_BG, fg=FG_DIM,
             font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=14, pady=(8, 4))

    # Bottom section: "Manage Tools" toggle area
    tk.Frame(sidebar, bg=BORDER, height=1).pack(fill=tk.X, side=tk.BOTTOM)
    bottom_bar = tk.Frame(sidebar, bg=SIDEBAR_BG, height=44)
    bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)
    bottom_bar.pack_propagate(False)
    tk.Label(bottom_bar, text="100% local · no telemetry",
             bg=SIDEBAR_BG, fg=FG_DIM, font=("Segoe UI", 8)
             ).pack(side=tk.LEFT, padx=12, pady=12)

    # Thin vertical separator between sidebar and content
    tk.Frame(shell, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

    # ─── CONTENT AREA ────────────────────────────────────────────────────────
    content = tk.Frame(shell, bg=BG)
    content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Top bar inside content
    topbar = tk.Frame(content, bg=HDR_BG, height=48)
    topbar.pack(fill=tk.X)
    topbar.pack_propagate(False)

    title_var = tk.StringVar(value="")
    tk.Label(topbar, textvariable=title_var,
             bg=HDR_BG, fg=FG, font=("Segoe UI", 12, "bold")
             ).pack(side=tk.LEFT, padx=18, pady=12)

    shortcuts_lbl = tk.Label(
        topbar,
        text="Ctrl+Z = undo  ·  Ctrl+Enter = run",
        bg=HDR_BG, fg=FG_DIM, font=("Segoe UI", 9),
    )
    shortcuts_lbl.pack(side=tk.RIGHT, padx=18)

    tk.Frame(content, bg=BORDER, height=1).pack(fill=tk.X)

    # Frame that holds all tool pages stacked
    pages_host = tk.Frame(content, bg=BG)
    pages_host.pack(fill=tk.BOTH, expand=True)

    # ─── BUILD ALL TOOL WIDGETS ───────────────────────────────────────────────
    pages      = {}   # icon_label -> Frame wrapping the tool
    nav_btns   = {}   # icon_label -> NavButton
    toggles    = {}   # icon_label -> ToggleSwitch
    visible    = {}   # icon_label -> bool (whether visible in sidebar)

    key_list   = []   # ordered list of icon_label keys

    # We need root before widgets, so pass it where needed
    def _make_widget(cls, extra, host):
        if "root" in extra:
            return cls(host, root)
        return cls(host)

    current_key = tk.StringVar(value="")

    def show_tool(key):
        """Raise the page for the given key, update nav highlights."""
        if key not in pages:
            return
        # hide all
        for k, pg in pages.items():
            pg.pack_forget()
        # show selected
        pages[key].pack(fill=tk.BOTH, expand=True)
        current_key.set(key)
        # update nav button states
        for k, btn in nav_btns.items():
            btn.set_active(k == key)
        # update topbar title
        for icon, label, *_ in TOOLS:
            if icon == key:
                title_var.set(label)
                break

    def rebuild_nav():
        """Re-render nav buttons for visible tools."""
        for w in nav_frame.winfo_children():
            # keep the separator + "TOOLS" label (first 2 children)
            pass

        # destroy only NavButton rows (not the separator/label)
        for w in list(nav_frame.winfo_children())[2:]:
            w.destroy()
        nav_btns.clear()

        for icon, label, _cls, _extra in TOOLS:
            if not visible.get(icon, True):
                continue

            def make_click(k=icon):
                return lambda: show_tool(k)

            btn = NavButton(nav_frame, icon=icon, label=label, on_click=make_click())
            btn.pack(fill=tk.X, pady=1)
            nav_btns[icon] = btn

        # If current tool became hidden, switch to first visible
        if current_key.get() not in nav_btns and nav_btns:
            show_tool(next(iter(nav_btns)))
        elif current_key.get() in nav_btns:
            nav_btns[current_key.get()].set_active(True)

    # ── Manage-tools popup ────────────────────────────────────────────────────
    def open_manage():
        popup = tk.Toplevel(root)
        popup.title("Manage Tools")
        popup.configure(bg=PANEL)
        popup.resizable(False, False)
        popup.grab_set()

        # Header
        hdr = tk.Frame(popup, bg=PANEL)
        hdr.pack(fill=tk.X, padx=20, pady=(18, 0))
        tk.Label(hdr, text="Manage Tools", bg=PANEL, fg=FG,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT)
        tk.Label(hdr, text="toggle to show / hide", bg=PANEL, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(8, 0), pady=(3, 0))

        tk.Frame(popup, bg=BORDER, height=1).pack(fill=tk.X, padx=0, pady=(12, 0))

        rows_frame = tk.Frame(popup, bg=PANEL)
        rows_frame.pack(fill=tk.X, padx=20, pady=12)

        popup_toggles = {}

        for icon, label, _cls, _extra in TOOLS:
            row = tk.Frame(rows_frame, bg=PANEL, height=40)
            row.pack(fill=tk.X, pady=2)
            row.pack_propagate(False)

            tk.Label(row, text=icon, bg=PANEL, fg=FG_MID,
                     font=("Segoe UI", 13), width=2).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(row, text=label, bg=PANEL, fg=FG,
                     font=("Segoe UI", 11)).pack(side=tk.LEFT, fill=tk.X, expand=True)

            t = ToggleSwitch(row, initial=visible.get(icon, True))
            t.pack(side=tk.RIGHT, padx=4, pady=10)
            popup_toggles[icon] = t

        tk.Frame(popup, bg=BORDER, height=1).pack(fill=tk.X, padx=0)

        btn_row = tk.Frame(popup, bg=PANEL)
        btn_row.pack(fill=tk.X, padx=20, pady=14)

        def apply_changes():
            for icon, t in popup_toggles.items():
                visible[icon] = t.get()
            rebuild_nav()
            popup.destroy()

        ttk.Button(btn_row, text="Apply", style="Accent.TButton",
                   command=apply_changes).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(btn_row, text="Cancel", style="Ghost.TButton",
                   command=popup.destroy).pack(side=tk.RIGHT)

        popup.update_idletasks()
        px = root.winfo_rootx() + (root.winfo_width()  - popup.winfo_width())  // 2
        py = root.winfo_rooty() + (root.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{px}+{py}")

    # "⚙ Manage" button in bottom bar
    manage_btn = tk.Button(
        bottom_bar, text="⚙  Manage",
        bg=SIDEBAR_BG, fg=FG_DIM,
        font=("Segoe UI", 9), relief="flat",
        activebackground=NAV_HOVER_BG, activeforeground=FG,
        cursor="hand2", bd=0, padx=8,
        command=open_manage,
    )
    manage_btn.pack(side=tk.RIGHT, padx=8, pady=8)

    # ── Create all tool pages ─────────────────────────────────────────────────
    for icon, label, cls, extra in TOOLS:
        key_list.append(icon)
        visible[icon] = True

        pg = tk.Frame(pages_host, bg=BG)
        widget = _make_widget(cls, extra, pg)
        widget.pack(fill=tk.BOTH, expand=True)
        pages[icon] = pg

    # ── Initial nav build + show first tool ───────────────────────────────────
    rebuild_nav()
    if key_list:
        show_tool(key_list[0])

    root.mainloop()


if __name__ == "__main__":
    main()
