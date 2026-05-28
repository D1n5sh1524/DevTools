"""
compare_tab.py — Side-by-side Text Compare tab (3-level granular diff)
"""
import tkinter as tk
from tkinter import ttk
import difflib

from theme import (
    BLANK_BG, FG_DIM,
    A_REM_FG, A_CHG_FG, B_ADD_FG, B_NEW_FG,
    STATUS_OK, STATUS_ERR, STATUS_DIM,
    hsep,
)
from widgets import make_lnt, link_scroll
from diff_utils import (
    ALL_DIFF_TAGS, setup_tags, word_diff, render_view,
    TAG_CHAR_REM, TAG_CHAR_ADD, TAG_WORD_REM, TAG_WORD_CHG,
)


class CompareTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._edit_mode = True
        self._orig_a = self._orig_b = ""
        self._build()

    def _build(self):
        # ── Side-by-side panes ────────────────────────────────────────────────
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 4))

        lf = ttk.LabelFrame(pane, text="  Original  (A)  ")
        self.text_a = make_lnt(lf, wrap=tk.WORD)
        setup_tags(self.text_a)
        pane.add(lf, weight=1)

        rf = ttk.LabelFrame(pane, text="  Modified  (B)  ")
        self.text_b = make_lnt(rf, wrap=tk.WORD)
        setup_tags(self.text_b)
        pane.add(rf, weight=1)

        link_scroll(self.text_a, self.text_b)

        # ── Legend ────────────────────────────────────────────────────────────
        leg = ttk.Frame(self)
        leg.pack(fill=tk.X, padx=16, pady=(4, 2))

        bold9 = ("Segoe UI", 9, "bold")
        for label, bg, fg in [
            ("  Line removed ",  "#fde8e8", A_REM_FG),
            ("  Line added ",    "#d4f4dd", B_ADD_FG),
            ("  Changed (A) ",   "#fff8e1", A_CHG_FG),
            ("  Changed (B) ",   "#e8f0fe", B_NEW_FG),
            ("  Word removed ",  "#fca5a5", "#7f1d1d"),
            ("  Word added ",    "#6ee7b7", "#064e3b"),
            ("  Char removed ",  "#ef4444", "#ffffff"),
            ("  Char added ",    "#16a34a", "#ffffff"),
            ("  ░ Blank ",       BLANK_BG,  FG_DIM),
        ]:
            tk.Label(leg, text=label, bg=bg, fg=fg, font=bold9,
                     relief="flat", padx=3, pady=2
                     ).pack(side=tk.LEFT, padx=(0, 3))

        # ── Status ────────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(
            value="Type or paste text in both boxes  ·  Ctrl+Enter to compare")
        self.status_lbl = ttk.Label(self, textvariable=self.status_var,
                                    style="Dim.TLabel")
        self.status_lbl.pack(anchor=tk.W, padx=16, pady=(2, 2))
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

        ttk.Button(bar, text="Swap A ↔ B",
                   command=self.swap).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(bar, text="Clear All", style="Danger.TButton",
                   command=self.clear).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Separator(bar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=14, pady=2)

        self.ignore_ws = tk.BooleanVar()
        ttk.Checkbutton(bar, text="Ignore whitespace",
                        variable=self.ignore_ws).pack(side=tk.LEFT)

        self.text_a.bind("<Control-Return>", lambda _e: self.compare())
        self.text_b.bind("<Control-Return>", lambda _e: self.compare())

    # ── helpers ───────────────────────────────────────────────────────────────
    def _set_status(self, msg, color=STATUS_DIM):
        self.status_var.set(msg)
        self.status_lbl.configure(foreground=color)

    # ── compare ───────────────────────────────────────────────────────────────
    def compare(self):
        a_raw = self.text_a.get("1.0", tk.END)
        b_raw = self.text_b.get("1.0", tk.END)
        self._orig_a, self._orig_b = a_raw, b_raw

        a_cmp = ("\n".join(" ".join(l.split()) for l in a_raw.splitlines())
                 if self.ignore_ws.get() else a_raw)
        b_cmp = ("\n".join(" ".join(l.split()) for l in b_raw.splitlines())
                 if self.ignore_ws.get() else b_raw)

        if a_cmp.strip() == b_cmp.strip():
            self._set_status("✓  Texts are identical.", STATUS_OK)
            return

        a_lines = a_cmp.splitlines()
        b_lines = b_cmp.splitlines()

        view_a, view_b = [], []
        matcher = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)

        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal":
                for ln in a_lines[i1:i2]: view_a.append(("equal", ln))
                for ln in b_lines[j1:j2]: view_b.append(("equal", ln))

            elif op == "delete":
                for ln in a_lines[i1:i2]: view_a.append(("remove", ln))
                for _  in range(i2 - i1):  view_b.append(("blank",))

            elif op == "insert":
                for _  in range(j2 - j1):  view_a.append(("blank",))
                for ln in b_lines[j1:j2]:  view_b.append(("add", ln))

            elif op == "replace":
                ab = list(a_lines[i1:i2])
                bb = list(b_lines[j1:j2])
                while len(ab) < len(bb): ab.append(None)
                while len(bb) < len(ab): bb.append(None)

                for la, lb in zip(ab, bb):
                    if la is None:
                        view_a.append(("blank",))
                        view_b.append(("add", lb))
                    elif lb is None:
                        view_a.append(("remove", la))
                        view_b.append(("blank",))
                    else:
                        toks_a, toks_b = word_diff(la, lb)
                        view_a.append(("inline", toks_a))
                        view_b.append(("inline", toks_b))

        render_view(self.text_a, view_a)
        render_view(self.text_b, view_b)

        self._edit_mode = False
        self.btn_edit.state(["!disabled"])

        adds  = sum(1 for v in view_b if v[0] == "add")
        rems  = sum(1 for v in view_a if v[0] == "remove")
        chng  = sum(1 for v in view_a if v[0] == "inline")
        chars_changed = sum(
            sum(1 for _, t in v[1]
                if t in (TAG_CHAR_REM, TAG_CHAR_ADD, TAG_WORD_REM, TAG_WORD_CHG))
            for v in view_a if v[0] == "inline"
        )
        self._set_status(
            f"  +{adds} lines added   −{rems} lines removed"
            f"   ~{chng} lines changed   ±{chars_changed} word/char spots",
            STATUS_ERR if rems else STATUS_OK)

    # ── edit mode ─────────────────────────────────────────────────────────────
    def edit_mode(self):
        for widget, orig in [(self.text_a, self._orig_a),
                              (self.text_b, self._orig_b)]:
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert("1.0", orig.rstrip("\n"))
            for t in ALL_DIFF_TAGS:
                widget.tag_remove(t, "1.0", tk.END)
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
            for t in ALL_DIFF_TAGS:
                widget.tag_remove(t, "1.0", tk.END)
        self._edit_mode = True
        self._orig_a = self._orig_b = ""
        self.btn_edit.state(["disabled"])
        self._set_status(
            "Type or paste text in both boxes  ·  Ctrl+Enter to compare")