"""
diff_utils.py — Diff helpers: tokeniser, word-level diff, char-level diff, renderer
"""
import re
import difflib
import tkinter as tk

from theme import (
    PANEL, BLANK_BG, FG,
    A_REM_FG, A_CHG_FG, B_ADD_FG, B_NEW_FG,
    MONO_FONT,
)

# ─── Tag names ────────────────────────────────────────────────────────────────
TAG_LINE_REM = "line_rem"
TAG_LINE_ADD = "line_add"
TAG_LINE_CHG = "line_chg"
TAG_LINE_NEW = "line_new"
TAG_LINE_EQL = "line_eql"
TAG_BLANK    = "blank"

TAG_WORD_REM = "word_rem"
TAG_WORD_ADD = "word_add"
TAG_WORD_CHG = "word_chg"
TAG_WORD_NEW = "word_new"

TAG_CHAR_REM = "char_rem"
TAG_CHAR_ADD = "char_add"

ALL_DIFF_TAGS = [
    TAG_LINE_REM, TAG_LINE_ADD, TAG_LINE_CHG, TAG_LINE_NEW, TAG_LINE_EQL, TAG_BLANK,
    TAG_WORD_REM, TAG_WORD_ADD, TAG_WORD_CHG, TAG_WORD_NEW,
    TAG_CHAR_REM, TAG_CHAR_ADD,
]


def setup_tags(widget):
    """Register every diff tag on a LineNumberedText widget."""
    bold = (MONO_FONT[0], MONO_FONT[1], "bold")

    widget.tag_configure(TAG_LINE_REM, background="#fde8e8", foreground=A_REM_FG)
    widget.tag_configure(TAG_LINE_ADD, background="#d4f4dd", foreground=B_ADD_FG)
    widget.tag_configure(TAG_LINE_CHG, background="#fff8e1", foreground=A_CHG_FG)
    widget.tag_configure(TAG_LINE_NEW, background="#e8f0fe", foreground=B_NEW_FG)
    widget.tag_configure(TAG_LINE_EQL, background=PANEL,     foreground=FG)
    widget.tag_configure(TAG_BLANK,    background=BLANK_BG,  foreground=BLANK_BG)

    widget.tag_configure(TAG_WORD_REM, background="#fca5a5", foreground="#7f1d1d", font=bold)
    widget.tag_configure(TAG_WORD_ADD, background="#6ee7b7", foreground="#064e3b", font=bold)
    widget.tag_configure(TAG_WORD_CHG, background="#fcd34d", foreground="#78350f", font=bold)
    widget.tag_configure(TAG_WORD_NEW, background="#93c5fd", foreground="#1e3a8a", font=bold)

    widget.tag_configure(TAG_CHAR_REM, background="#ef4444", foreground="#ffffff", font=bold)
    widget.tag_configure(TAG_CHAR_ADD, background="#16a34a", foreground="#ffffff", font=bold)

    for t in [TAG_BLANK, TAG_LINE_REM, TAG_LINE_ADD,
              TAG_LINE_CHG, TAG_LINE_NEW, TAG_LINE_EQL,
              TAG_WORD_REM, TAG_WORD_ADD, TAG_WORD_CHG, TAG_WORD_NEW,
              TAG_CHAR_REM, TAG_CHAR_ADD]:
        widget.text.tag_raise(t)


# ─── Inline diff helpers ──────────────────────────────────────────────────────

def _tokenise(text):
    """Split a line into word + whitespace tokens."""
    return re.findall(r'\S+|\s+', text)


def _similarity(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def _char_diff_pair(tok_a, tok_b):
    """
    Return (list_of_(substr,tag)_for_A, list_of_(substr,tag)_for_B)
    using character-level SequenceMatcher.
    Unchanged chars keep word-level tint; changed chars get solid red/green.
    """
    res_a, res_b = [], []
    sm = difflib.SequenceMatcher(None, tok_a, tok_b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            res_a.append((tok_a[i1:i2], TAG_WORD_CHG))
            res_b.append((tok_b[j1:j2], TAG_WORD_NEW))
        elif op == "delete":
            res_a.append((tok_a[i1:i2], TAG_CHAR_REM))
        elif op == "insert":
            res_b.append((tok_b[j1:j2], TAG_CHAR_ADD))
        elif op == "replace":
            res_a.append((tok_a[i1:i2], TAG_CHAR_REM))
            res_b.append((tok_b[j1:j2], TAG_CHAR_ADD))
    return res_a, res_b


def word_diff(line_a, line_b):
    """
    Return (tokens_a, tokens_b) — each a list of (text, tag_or_None) —
    covering the full content of their respective lines with word- and
    char-level diff highlights embedded.
    """
    toks_a = _tokenise(line_a)
    toks_b = _tokenise(line_b)
    result_a, result_b = [], []

    sm = difflib.SequenceMatcher(None, toks_a, toks_b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for t in toks_a[i1:i2]: result_a.append((t, None))
            for t in toks_b[j1:j2]: result_b.append((t, None))

        elif op == "delete":
            for t in toks_a[i1:i2]: result_a.append((t, TAG_WORD_REM))

        elif op == "insert":
            for t in toks_b[j1:j2]: result_b.append((t, TAG_WORD_ADD))

        elif op == "replace":
            a_blk = toks_a[i1:i2]
            b_blk = toks_b[j1:j2]
            pairs  = list(zip(a_blk, b_blk))
            for ta, tb in pairs:
                if _similarity(ta, tb) > 0.3:
                    ca, cb = _char_diff_pair(ta, tb)
                    result_a.extend(ca)
                    result_b.extend(cb)
                else:
                    result_a.append((ta, TAG_WORD_CHG))
                    result_b.append((tb, TAG_WORD_NEW))
            for ta in a_blk[len(pairs):]: result_a.append((ta, TAG_WORD_REM))
            for tb in b_blk[len(pairs):]: result_b.append((tb, TAG_WORD_ADD))

    return result_a, result_b


# ─── Renderer ─────────────────────────────────────────────────────────────────

def render_view(widget, view):
    """
    Render a view list into a LineNumberedText widget.

    Each item is one of:
      ("blank",)
      ("equal",  text)
      ("remove", text)
      ("add",    text)
      ("inline", [(tok, tag_or_None), ...])
    """
    widget.config(state=tk.NORMAL)
    widget.delete("1.0", tk.END)

    for i, item in enumerate(view):
        nl   = "\n" if i < len(view) - 1 else ""
        kind = item[0]

        if kind == "blank":
            widget.insert(tk.END, " " + nl, TAG_BLANK)

        elif kind == "equal":
            widget.insert(tk.END, item[1] + nl, TAG_LINE_EQL)

        elif kind == "remove":
            widget.insert(tk.END, item[1] + nl, TAG_LINE_REM)

        elif kind == "add":
            widget.insert(tk.END, item[1] + nl, TAG_LINE_ADD)

        elif kind == "inline":
            tokens   = item[1]
            line_tag = TAG_LINE_CHG if any(
                t in (TAG_WORD_CHG, TAG_CHAR_REM, TAG_CHAR_ADD, TAG_WORD_REM)
                for _, t in tokens
            ) else TAG_LINE_NEW

            full_line  = "".join(tok for tok, _ in tokens)
            line_start = widget.index(tk.INSERT)
            widget.insert(tk.END, full_line + nl, line_tag)

            pos = 0
            for tok, tag in tokens:
                if tag is not None:
                    s = f"{line_start}+{pos}c"
                    e = f"{line_start}+{pos + len(tok)}c"
                    widget.tag_add(tag, s, e)
                pos += len(tok)

    widget.config(state=tk.DISABLED)