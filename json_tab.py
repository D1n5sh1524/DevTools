"""
json_tab.py — JSON Formatter & Validator tab
"""
import tkinter as tk
from tkinter import ttk
import json
import re

from theme import (
    ACCENT, STATUS_OK, STATUS_ERR, STATUS_DIM,
    MONO_FONT, hsep,
)
from widgets import make_lnt, link_scroll


class JsonTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        # ── Text panes ────────────────────────────────────────────────────────
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 4))

        lf = ttk.LabelFrame(pane, text="  Input JSON  ")
        self.inp = make_lnt(lf)
        self.inp.bind("<Control-Return>", lambda _e: self.fmt())
        pane.add(lf, weight=1)

        rf = ttk.LabelFrame(pane, text="  Formatted Output  ")
        self.out = make_lnt(rf, readonly=True, undo=False)
        # syntax-highlight tags
        self.out.tag_configure("key",  foreground="#1d4ed8",
                               font=(MONO_FONT[0], MONO_FONT[1], "bold"))
        self.out.tag_configure("str",  foreground="#166534")
        self.out.tag_configure("num",  foreground="#b45309")
        self.out.tag_configure("bool", foreground="#7c3aed")
        self.out.tag_configure("null", foreground="#dc2626")
        pane.add(rf, weight=1)

        link_scroll(self.inp, self.out)

        # ── Status ────────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(
            value="Paste JSON on the left  ·  Ctrl+Enter to format")
        self.status_lbl = ttk.Label(self, textvariable=self.status_var,
                                    style="Dim.TLabel")
        self.status_lbl.pack(anchor=tk.W, padx=16, pady=(0, 2))
        hsep(self)

        # ── Bottom toolbar ────────────────────────────────────────────────────
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=12, pady=(4, 12))

        ttk.Button(bar, text="▶  Format / Validate",
                   style="Accent.TButton", command=self.fmt).pack(side=tk.LEFT)
        ttk.Button(bar, text="Minify",
                   command=self.minify).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(bar, text="Copy Output",
                   command=self.copy_output).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(bar, text="Clear All", style="Danger.TButton",
                   command=self.clear).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Separator(bar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=14, pady=2)

        ttk.Label(bar, text="Indent:").pack(side=tk.LEFT)
        self.indent_var = tk.IntVar(value=2)
        ttk.Spinbox(bar, from_=1, to=8, textvariable=self.indent_var,
                    width=4).pack(side=tk.LEFT, padx=(5, 12))

        self.sort_var = tk.BooleanVar()
        ttk.Checkbutton(bar, text="Sort Keys",
                        variable=self.sort_var).pack(side=tk.LEFT)

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
        # keys
        for m in re.finditer(r'"(?:[^"\\]|\\.)*"\s*:', txt):
            end_key = m.end() - len(m.group(0)) + len(m.group(0).rstrip(": \t"))
            self.out.tag_add("key", f"1.0+{m.start()}c", f"1.0+{end_key}c")
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
            out  = json.dumps(data, indent=self.indent_var.get(),
                              sort_keys=self.sort_var.get(), ensure_ascii=False)
            self._write_output(out)
            lines = out.count("\n") + 1
            keys  = len(re.findall(r'"[^"]*"\s*:', out))
            self._set_status(
                f"✓  Valid JSON  ·  {lines} lines  ·  {keys} keys", STATUS_OK)
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