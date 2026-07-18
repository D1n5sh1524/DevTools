"""
widgets.py — LineNumberedText widget and sync-scroll helper
"""
import tkinter as tk
from theme import (
    PANEL, BORDER, LNUM_BG, LNUM_FG,
    BG, FG, ACCENT, MONO_FONT, LNUM_FONT,
)


class LineNumberedText(tk.Frame):
    """
    A frame containing:
      • a narrow Canvas gutter showing line numbers
      • a Text widget  (the actual editor)
      • a shared vertical Scrollbar

    Both the canvas and text share the same yview so scrolling stays in sync.
    """

    def __init__(self, parent, undo=True, readonly=False, wrap=tk.NONE, **kw):
        super().__init__(parent, bg=PANEL, bd=0, highlightthickness=0)
        self._readonly  = readonly
        self._sync_lock = False

        # ── Vertical scrollbar ───────────────────────────────────────────────
        self.vbar = tk.Scrollbar(
            self, orient=tk.VERTICAL, width=8,
            bg=LNUM_BG, troughcolor=BG,
            activebackground=BORDER,
            relief="flat", bd=0,
        )
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Horizontal scrollbar ─────────────────────────────────────────────
        self.hbar = tk.Scrollbar(
            self, orient=tk.HORIZONTAL, width=6,
            bg=LNUM_BG, troughcolor=BG,
            activebackground=BORDER,
            relief="flat", bd=0,
        )
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)

        # ── Gutter canvas ────────────────────────────────────────────────────
        self.gutter = tk.Canvas(
            self, width=44,
            bg=LNUM_BG, highlightthickness=0, bd=0,
        )
        self.gutter.pack(side=tk.LEFT, fill=tk.Y)

        # 1 px separator between gutter and text
        tk.Frame(self, width=1, bg=BORDER).pack(side=tk.LEFT, fill=tk.Y)

        # ── Main text widget ─────────────────────────────────────────────────
        self.text = tk.Text(
            self,
            bg=PANEL, fg=FG,
            insertbackground=FG,
            insertwidth=2,
            selectbackground=ACCENT, selectforeground="#fff",
            font=MONO_FONT,
            relief="flat", bd=0,
            wrap=wrap,
            undo=undo, maxundo=-1,
            yscrollcommand=self._on_text_scroll,
            xscrollcommand=self.hbar.set,
            state=tk.DISABLED if readonly else tk.NORMAL,
            padx=8, pady=4,
            spacing1=2, spacing3=2,   # slight line-height breathing
            **kw,
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.vbar.config(command=self._on_scroll_cmd)
        self.hbar.config(command=self.text.xview)

        self.text.bind("<<Modified>>",    self._on_modified)
        self.text.bind("<Configure>",     lambda _e: self._redraw_gutter())
        self.text.bind("<KeyRelease>",    lambda _e: self._redraw_gutter())
        self.text.bind("<ButtonRelease>", lambda _e: self._redraw_gutter())

        self._redraw_gutter()

    # ── scrollbar plumbing ───────────────────────────────────────────────────
    def _on_text_scroll(self, first, last):
        self.vbar.set(first, last)
        self._redraw_gutter()

    def _on_scroll_cmd(self, *args):
        self.text.yview(*args)
        self._redraw_gutter()

    def yview(self, *args):
        self.text.yview(*args)
        self._redraw_gutter()

    def yview_moveto(self, fraction):
        self.text.yview_moveto(fraction)
        self._redraw_gutter()

    def get_yview(self):
        return self.text.yview()

    # ── gutter drawing ───────────────────────────────────────────────────────
    def _on_modified(self, _event=None):
        self.text.edit_modified(False)
        self._redraw_gutter()

    def _redraw_gutter(self):
        self.gutter.delete("all")
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break
            y       = dline[1]
            linenum = int(str(i).split(".")[0])
            self.gutter.create_text(
                38, y + dline[3] // 2,
                anchor="e",
                text=str(linenum),
                fill=LNUM_FG,
                font=LNUM_FONT,
            )
            next_i = self.text.index(f"{i}+1line")
            if next_i == i:
                break
            i = next_i

    # ── proxy helpers ────────────────────────────────────────────────────────
    def get(self, *args, **kw):           return self.text.get(*args, **kw)
    def insert(self, *args, **kw):        self.text.insert(*args, **kw);    self._redraw_gutter()
    def delete(self, *args, **kw):        self.text.delete(*args, **kw);    self._redraw_gutter()
    def config(self, **kw):               self.text.config(**kw)
    def configure(self, **kw):            self.text.configure(**kw)
    def tag_configure(self, *a, **kw):    self.text.tag_configure(*a, **kw)
    def tag_add(self, *a, **kw):          self.text.tag_add(*a, **kw)
    def tag_remove(self, *a, **kw):       self.text.tag_remove(*a, **kw)
    def bind(self, *a, **kw):             self.text.bind(*a, **kw)
    def index(self, *a, **kw):            return self.text.index(*a, **kw)
    def see(self, *a, **kw):              self.text.see(*a, **kw)
    def edit_modified(self, *a, **kw):    return self.text.edit_modified(*a, **kw)


def make_lnt(parent, readonly=False, wrap=tk.NONE, undo=True):
    """Convenience factory — returns a LineNumberedText packed inside parent."""
    w = LineNumberedText(parent, undo=undo, readonly=readonly, wrap=wrap)
    w.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
    return w


def link_scroll(*widgets):
    """
    Given two or more LineNumberedText widgets, make them scroll together.
    Each widget's vbar drives all others.
    """
    for w in widgets:
        others = [o for o in widgets if o is not w]

        def make_combined(widget, synced):
            def combined(*args):
                widget._on_scroll_cmd(*args)
                for o in synced:
                    o.yview(*args)
            return combined

        w.vbar.config(command=make_combined(w, others))

        def make_yscroll(widget, peers):
            def ys(first, last):
                widget.vbar.set(first, last)
                widget._redraw_gutter()
                frac = widget.text.yview()[0]
                for p in peers:
                    p.yview_moveto(frac)
            return ys

        w.text.configure(yscrollcommand=make_yscroll(w, others))
