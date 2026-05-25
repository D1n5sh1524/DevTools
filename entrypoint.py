"""
DevTools — JSON Formatter & Text Compare
Run: python devtools.py
Requires: Python 3.x  (tkinter is built-in, no pip install needed)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import difflib
import re

# ─── Light / cream palette ────────────────────────────────────────────────────
BG          = "#faf7f2"   # warm cream page
PANEL       = "#ffffff"   # pure white card
BORDER      = "#d8d0c4"
HDR_BG      = "#f0ece4"
FG          = "#1a1a1a"
FG_DIM      = "#7a7060"
ACCENT      = "#2563eb"   # blue
ACCENT_DARK = "#1d4ed8"
GREEN_BG    = "#d4f4dd"
GREEN_FG    = "#166534"
RED_BG      = "#fde8e8"
RED_FG      = "#991b1b"
AMBER_BG    = "#fff3cd"
AMBER_FG    = "#854d0e"
BLUE_BG     = "#dbeafe"
BLUE_FG     = "#1e40af"
BLANK_BG    = "#f0ede8"   # placeholder empty-line colour
STATUS_OK   = "#16a34a"
STATUS_ERR  = "#dc2626"
STATUS_DIM  = "#7a7060"

MONO_FONT = ("Consolas", 13)          # bigger + cleaner mono
UI_FONT   = ("Segoe UI", 11, "bold")  # bold UI labels
BTN_FONT  = ("Segoe UI", 11, "bold")


# ─── Theme setup ─────────────────────────────────────────────────────────────
def apply_theme(root):
    s = ttk.Style(root)
    s.theme_use("clam")

    s.configure(".", background=BG, foreground=FG,
                fieldbackground=PANEL, bordercolor=BORDER,
                troughcolor=BORDER, font=UI_FONT,
                selectbackground=ACCENT, selectforeground="#fff")

    s.configure("TNotebook", background=HDR_BG, borderwidth=0)
    s.configure("TNotebook.Tab", background=HDR_BG, foreground=FG_DIM,
                padding=[16, 8], font=BTN_FONT)
    s.map("TNotebook.Tab",
          background=[("selected", BG)],
          foreground=[("selected", ACCENT)])

    s.configure("TFrame",      background=BG)
    s.configure("Card.TFrame", background=PANEL, relief="flat")

    s.configure("TLabelframe",       background=BG, bordercolor=BORDER, relief="groove")
    s.configure("TLabelframe.Label", background=BG, foreground=FG_DIM,
                font=("Segoe UI", 10, "bold"))

    s.configure("TLabel",     background=BG, foreground=FG, font=UI_FONT)
    s.configure("Dim.TLabel", background=BG, foreground=FG_DIM, font=("Segoe UI", 10))
    s.configure("Hdr.TLabel", background=HDR_BG, foreground=FG, font=BTN_FONT)

    # Plain button
    s.configure("TButton", background=PANEL, foreground=FG,
                bordercolor=BORDER, relief="flat", padding=[12, 6], font=BTN_FONT)
    s.map("TButton",
          background=[("active", HDR_BG)],
          relief=[("active", "flat")])

    # Accent (primary) button
    s.configure("Accent.TButton", background=ACCENT, foreground="#ffffff",
                bordercolor=ACCENT, relief="flat", padding=[14, 7], font=BTN_FONT)
    s.map("Accent.TButton",
          background=[("active", ACCENT_DARK)])

    # Danger button
    s.configure("Danger.TButton", background="#fee2e2", foreground=STATUS_ERR,
                bordercolor="#fca5a5", relief="flat", padding=[12, 6], font=BTN_FONT)
    s.map("Danger.TButton",
          background=[("active", "#fca5a5")])

    s.configure("TCheckbutton", background=BG, foreground=FG, font=UI_FONT)
    s.map("TCheckbutton", background=[("active", BG)])

    s.configure("TSpinbox", background=PANEL, foreground=FG,
                fieldbackground=PANEL, bordercolor=BORDER,
                arrowcolor=FG_DIM, insertcolor=FG, font=UI_FONT)

    s.configure("TSeparator", background=BORDER)
    s.configure("TPanedwindow", background=BORDER)


def make_text(parent, undo=True, **kw):
    """Create a styled ScrolledText with undo enabled by default."""
    t = scrolledtext.ScrolledText(
        parent,
        bg=PANEL, fg=FG,
        insertbackground=FG,
        selectbackground=ACCENT, selectforeground="#fff",
        font=MONO_FONT,
        relief="flat", bd=0,
        wrap=kw.pop("wrap", tk.NONE),
        undo=undo,
        maxundo=-1,          # unlimited undo history
        **kw,
    )
    t.vbar.configure(bg=HDR_BG, troughcolor=BG, relief="flat", width=10)
    return t


# ─── Separator helper ─────────────────────────────────────────────────────────
def hsep(parent, pady=4):
    ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=pady)


# ══════════════════════════════════════════════════════════════════════════════
#  JSON FORMATTER TAB
# ══════════════════════════════════════════════════════════════════════════════
class JsonTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        # ── Text panes ────────────────────────────────────────────────────────
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 4))

        lf = ttk.LabelFrame(pane, text="  Input JSON  ")
        self.inp = make_text(lf)
        self.inp.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.inp.bind("<Control-Return>", lambda _e: self.fmt())
        pane.add(lf, weight=1)

        rf = ttk.LabelFrame(pane, text="  Formatted Output  ")
        self.out = make_text(rf, state=tk.DISABLED, undo=False)
        self.out.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        # syntax-highlight colour tags
        self.out.tag_configure("key",  foreground="#1d4ed8", font=(MONO_FONT[0], MONO_FONT[1], "bold"))
        self.out.tag_configure("str",  foreground="#166534")
        self.out.tag_configure("num",  foreground="#b45309")
        self.out.tag_configure("bool", foreground="#7c3aed")
        self.out.tag_configure("null", foreground="#dc2626")
        pane.add(rf, weight=1)

        # ── Status bar ────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Paste JSON on the left  ·  Ctrl+Enter to format")
        sl = ttk.Label(self, textvariable=self.status_var, style="Dim.TLabel")
        sl.pack(anchor=tk.W, padx=16, pady=(0, 2))
        self.status_lbl = sl

        hsep(self)

        # ── Bottom toolbar ────────────────────────────────────────────────────
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=12, pady=(4, 12))

        ttk.Button(bar, text="▶  Format / Validate", style="Accent.TButton",
                   command=self.fmt).pack(side=tk.LEFT)
        ttk.Button(bar, text="Minify",      command=self.minify).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(bar, text="Copy Output", command=self.copy_output).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(bar, text="Clear All",   command=self.clear,
                   style="Danger.TButton").pack(side=tk.LEFT, padx=(8, 0))

        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=14, pady=2)

        ttk.Label(bar, text="Indent:").pack(side=tk.LEFT)
        self.indent_var = tk.IntVar(value=2)
        ttk.Spinbox(bar, from_=1, to=8, textvariable=self.indent_var, width=4
                    ).pack(side=tk.LEFT, padx=(5, 12))

        self.sort_var = tk.BooleanVar()
        ttk.Checkbutton(bar, text="Sort Keys", variable=self.sort_var).pack(side=tk.LEFT)

    # ── helpers ───────────────────────────────────────────────────────────────
    def _set_status(self, msg, color=STATUS_DIM):
        self.status_var.set(msg)
        self.status_lbl.configure(foreground=color)

    def _write_output(self, text, highlight=True):
        self.out.config(state=tk.NORMAL)
        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, text)
        if highlight:
            self._highlight()
        self.out.config(state=tk.DISABLED)

    def _highlight(self):
        txt = self.out.get("1.0", tk.END)
        def tag_region(pattern, tag, group=0):
            for m in re.finditer(pattern, txt):
                g = m.group(group) if group else m.group(0)
                gs = m.start(group) if group else m.start()
                ge = gs + len(g)
                self.out.tag_add(tag, f"1.0+{gs}c", f"1.0+{ge}c")
        # keys
        for m in re.finditer(r'"(?:[^"\\]|\\.)*"\s*:', txt):
            end_of_key = m.end() - len(m.group(0)) + len(m.group(0).rstrip(": \t"))
            self.out.tag_add("key", f"1.0+{m.start()}c", f"1.0+{end_of_key}c")
        # string values
        for m in re.finditer(r':\s*("(?:[^"\\]|\\.)*")', txt):
            self.out.tag_add("str", f"1.0+{m.start(1)}c", f"1.0+{m.end(1)}c")
        # numbers
        for m in re.finditer(r':\s*(-?\d+\.?\d*(?:[eE][+-]?\d+)?)', txt):
            self.out.tag_add("num", f"1.0+{m.start(1)}c", f"1.0+{m.end(1)}c")
        # booleans
        for m in re.finditer(r'\b(true|false)\b', txt):
            self.out.tag_add("bool", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        # null
        for m in re.finditer(r'\bnull\b', txt):
            self.out.tag_add("null", f"1.0+{m.start()}c", f"1.0+{m.end()}c")

    # ── actions ───────────────────────────────────────────────────────────────
    def fmt(self):
        raw = self.inp.get("1.0", tk.END).strip()
        if not raw:
            return
        try:
            data = json.loads(raw)
            out = json.dumps(data, indent=self.indent_var.get(),
                             sort_keys=self.sort_var.get(), ensure_ascii=False)
            self._write_output(out)
            lines = out.count("\n") + 1
            keys  = len(re.findall(r'"[^"]*"\s*:', out))
            self._set_status(f"✓  Valid JSON  ·  {lines} lines  ·  {keys} keys", STATUS_OK)
        except json.JSONDecodeError as e:
            self._write_output(str(e), highlight=False)
            self._set_status(f"✗  {e}", STATUS_ERR)

    def minify(self):
        raw = self.inp.get("1.0", tk.END).strip()
        if not raw:
            return
        try:
            data = json.loads(raw)
            mini = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
            self._write_output(mini, highlight=False)
            self._set_status(f"✓  Minified  ·  {len(mini)} chars", STATUS_OK)
        except json.JSONDecodeError as e:
            self._set_status(f"✗  {e}", STATUS_ERR)

    def copy_output(self):
        self.out.config(state=tk.NORMAL)
        txt = self.out.get("1.0", tk.END).strip()
        self.out.config(state=tk.DISABLED)
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            self._set_status("Copied to clipboard!", ACCENT)

    def clear(self):
        self.inp.delete("1.0", tk.END)
        self._write_output("", highlight=False)
        self._set_status("Paste JSON on the left  ·  Ctrl+Enter to format")


# ══════════════════════════════════════════════════════════════════════════════
#  TEXT COMPARE TAB
# ══════════════════════════════════════════════════════════════════════════════

# Per-box colour tags
A_REMOVED_BG  = "#fde8e8"   # soft red   — line only in A
A_REMOVED_FG  = "#991b1b"
A_CHANGED_BG  = "#fff3cd"   # amber      — line changed (A side)
A_CHANGED_FG  = "#854d0e"
B_ADDED_BG    = "#d4f4dd"   # soft green — line only in B
B_ADDED_FG    = "#166534"
B_CHANGED_BG  = "#dbeafe"   # soft blue  — line changed (B side)
B_CHANGED_FG  = "#1e40af"
BLANK_LINE_BG = "#f5f3f0"   # placeholder blank row


def _configure_compare_tags(widget):
    widget.tag_configure("removed", background=A_REMOVED_BG, foreground=A_REMOVED_FG,
                         font=(MONO_FONT[0], MONO_FONT[1], "bold"))
    widget.tag_configure("changed", background=A_CHANGED_BG, foreground=A_CHANGED_FG,
                         font=(MONO_FONT[0], MONO_FONT[1], "bold"))
    widget.tag_configure("added",   background=B_ADDED_BG,   foreground=B_ADDED_FG,
                         font=(MONO_FONT[0], MONO_FONT[1], "bold"))
    widget.tag_configure("new",     background=B_CHANGED_BG, foreground=B_CHANGED_FG,
                         font=(MONO_FONT[0], MONO_FONT[1], "bold"))
    widget.tag_configure("blank",   background=BLANK_LINE_BG, foreground=BLANK_LINE_BG)


class CompareTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._edit_mode = True      # True = editable, False = showing diff
        self._orig_a = ""
        self._orig_b = ""
        self._build()

    def _build(self):
        # ── Side-by-side text boxes ───────────────────────────────────────────
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 4))

        lf = ttk.LabelFrame(pane, text="  Original  (A)  ")
        self.text_a = make_text(lf, wrap=tk.WORD)
        self.text_a.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        _configure_compare_tags(self.text_a)
        pane.add(lf, weight=1)

        rf = ttk.LabelFrame(pane, text="  Modified  (B)  ")
        self.text_b = make_text(rf, wrap=tk.WORD)
        self.text_b.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        _configure_compare_tags(self.text_b)
        pane.add(rf, weight=1)

        # ── Legend ────────────────────────────────────────────────────────────
        leg = ttk.Frame(self)
        leg.pack(fill=tk.X, padx=16, pady=(2, 0))
        for lbl, bg, fg in [
            ("  Removed (only in A) ",  A_REMOVED_BG, A_REMOVED_FG),
            ("  Changed (A side) ",     A_CHANGED_BG, A_CHANGED_FG),
            ("  Added (only in B) ",    B_ADDED_BG,   B_ADDED_FG),
            ("  Changed (B side) ",     B_CHANGED_BG, B_CHANGED_FG),
            ("  ░ Blank placeholder ",  BLANK_LINE_BG, FG_DIM),
        ]:
            tk.Label(leg, text=lbl, bg=bg, fg=fg,
                     font=("Segoe UI", 9, "bold"),
                     relief="flat", padx=4, pady=2).pack(side=tk.LEFT, padx=(0, 4))

        # ── Status ────────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(
            value="Type or paste text in both boxes  ·  Ctrl+Enter to compare")
        sl = ttk.Label(self, textvariable=self.status_var, style="Dim.TLabel")
        sl.pack(anchor=tk.W, padx=16, pady=(4, 2))
        self.status_lbl = sl

        hsep(self)

        # ── Bottom toolbar ────────────────────────────────────────────────────
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=12, pady=(4, 12))

        self.btn_compare = ttk.Button(bar, text="▶  Compare",
                                      style="Accent.TButton", command=self.compare)
        self.btn_compare.pack(side=tk.LEFT)

        self.btn_edit = ttk.Button(bar, text="✎  Edit", command=self.edit_mode)
        self.btn_edit.pack(side=tk.LEFT, padx=(8, 0))
        self.btn_edit.state(["disabled"])

        ttk.Button(bar, text="Swap A ↔ B", command=self.swap
                   ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(bar, text="Clear All", command=self.clear,
                   style="Danger.TButton").pack(side=tk.LEFT, padx=(8, 0))

        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=14, pady=2)

        self.ignore_ws = tk.BooleanVar()
        ttk.Checkbutton(bar, text="Ignore whitespace",
                        variable=self.ignore_ws).pack(side=tk.LEFT)

        # Keyboard shortcut
        self.text_a.bind("<Control-Return>", lambda _e: self.compare())
        self.text_b.bind("<Control-Return>", lambda _e: self.compare())

    # ── status helper ─────────────────────────────────────────────────────────
    def _set_status(self, msg, color=STATUS_DIM):
        self.status_var.set(msg)
        self.status_lbl.configure(foreground=color)

    # ── clear tags + make editable ────────────────────────────────────────────
    def _set_editable(self, widget, editable: bool):
        widget.config(state=tk.NORMAL)
        if not editable:
            for tag in ("removed", "changed", "added", "new", "blank"):
                widget.tag_remove(tag, "1.0", tk.END)
            widget.config(state=tk.DISABLED)

    # ── Compare logic ─────────────────────────────────────────────────────────
    def compare(self):
        a_raw = self.text_a.get("1.0", tk.END)
        b_raw = self.text_b.get("1.0", tk.END)

        # Save originals so Edit can restore
        self._orig_a = a_raw
        self._orig_b = b_raw

        if self.ignore_ws.get():
            a_cmp = "\n".join(" ".join(ln.split()) for ln in a_raw.splitlines())
            b_cmp = "\n".join(" ".join(ln.split()) for ln in b_raw.splitlines())
        else:
            a_cmp, b_cmp = a_raw, b_raw

        a_lines = a_cmp.splitlines()
        b_lines = b_cmp.splitlines()

        if a_cmp.strip() == b_cmp.strip():
            self._set_status("✓  Texts are identical — no differences found.", STATUS_OK)
            return

        # Build aligned lists for both boxes
        # a_view: list of (text, tag)  b_view: list of (text, tag)
        a_view, b_view = [], []
        matcher = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)

        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal":
                for ln in a_lines[i1:i2]:
                    a_view.append((ln, None))
                for ln in b_lines[j1:j2]:
                    b_view.append((ln, None))

            elif op == "insert":   # only in B
                count = j2 - j1
                for _ in range(count):
                    a_view.append(("", "blank"))
                for ln in b_lines[j1:j2]:
                    b_view.append((ln, "added"))

            elif op == "delete":   # only in A
                for ln in a_lines[i1:i2]:
                    a_view.append((ln, "removed"))
                count = i2 - i1
                for _ in range(count):
                    b_view.append(("", "blank"))

            elif op == "replace":  # changed
                # Pad shorter side with blanks so rows align
                a_blk = a_lines[i1:i2]
                b_blk = b_lines[j1:j2]
                while len(a_blk) < len(b_blk):
                    a_blk.append("")
                while len(b_blk) < len(a_blk):
                    b_blk.append("")
                for ln in a_blk:
                    a_view.append((ln, "changed" if ln else "blank"))
                for ln in b_blk:
                    b_view.append((ln, "new" if ln else "blank"))

        # Write aligned content into both boxes
        for widget, view in [(self.text_a, a_view), (self.text_b, b_view)]:
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            for i, (txt, tag) in enumerate(view):
                nl = "\n" if i < len(view) - 1 else ""
                if tag:
                    widget.insert(tk.END, txt + nl, tag)
                else:
                    widget.insert(tk.END, txt + nl)
            widget.config(state=tk.DISABLED)

        self._edit_mode = False
        self.btn_edit.state(["!disabled"])
        self.btn_compare.state(["!disabled"])

        adds  = sum(1 for _, t in b_view if t == "added")
        rems  = sum(1 for _, t in a_view if t == "removed")
        chng  = sum(1 for _, t in a_view if t == "changed")
        self._set_status(
            f"  +{adds} added   −{rems} removed   ~{chng} changed",
            STATUS_ERR if rems else STATUS_OK)

    # ── Edit mode: restore original text ─────────────────────────────────────
    def edit_mode(self):
        for widget, orig in [(self.text_a, self._orig_a),
                              (self.text_b, self._orig_b)]:
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert("1.0", orig.rstrip("\n"))
            for tag in ("removed", "changed", "added", "new", "blank"):
                widget.tag_remove(tag, "1.0", tk.END)
        self._edit_mode = True
        self.btn_edit.state(["disabled"])
        self._set_status("Edit mode — make changes then Compare again")

    # ── swap / clear ──────────────────────────────────────────────────────────
    def swap(self):
        if not self._edit_mode:
            self.edit_mode()
        ta = self.text_a.get("1.0", tk.END)
        tb = self.text_b.get("1.0", tk.END)
        self.text_a.delete("1.0", tk.END)
        self.text_a.insert("1.0", tb.rstrip("\n"))
        self.text_b.delete("1.0", tk.END)
        self.text_b.insert("1.0", ta.rstrip("\n"))

    def clear(self):
        for widget in (self.text_a, self.text_b):
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            for tag in ("removed", "changed", "added", "new", "blank"):
                widget.tag_remove(tag, "1.0", tk.END)
        self._edit_mode = True
        self._orig_a = self._orig_b = ""
        self.btn_edit.state(["disabled"])
        self._set_status("Type or paste text in both boxes  ·  Ctrl+Enter to compare")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    root.title("DevTools  —  JSON Formatter & Text Compare")
    root.geometry("1160x760")
    root.minsize(860, 580)
    root.configure(bg=HDR_BG)

    apply_theme(root)

    # ── Header ────────────────────────────────────────────────────────────────
    hdr = tk.Frame(root, bg=HDR_BG, height=48)
    hdr.pack(fill=tk.X)
    hdr.pack_propagate(False)
    tk.Label(hdr, text="⬡  DevTools", bg=HDR_BG, fg=ACCENT,
             font=("Segoe UI", 15, "bold")).pack(side=tk.LEFT, padx=18)
    tk.Label(hdr, text="JSON Formatter  ·  Text Compare",
             bg=HDR_BG, fg=FG_DIM,
             font=("Segoe UI", 10)).pack(side=tk.LEFT)
    tk.Label(hdr, text="Ctrl+Z = undo  ·  Ctrl+Enter = run  ·  100% local",
             bg=HDR_BG, fg=FG_DIM,
             font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=18)

    ttk.Separator(root, orient=tk.HORIZONTAL).pack(fill=tk.X)

    # ── Notebook tabs ─────────────────────────────────────────────────────────
    nb = ttk.Notebook(root)
    nb.pack(fill=tk.BOTH, expand=True)
    nb.add(JsonTab(nb),    text="   { }  JSON Formatter   ")
    nb.add(CompareTab(nb), text="   ≠   Text Compare   ")

    root.mainloop()


if __name__ == "__main__":
    main()
