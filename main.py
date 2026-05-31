"""
main.py — DevTools entry point
Assembles JSON Formatter, Text Compare, and QR Code Generator tabs.

Run:  python main.py
Deps: Python 3.x, qrcode, Pillow  (tkinter built-in)
"""

import tkinter as tk
from tkinter import ttk

from theme            import apply_theme, BG, HDR_BG, ACCENT, FG_DIM
from json_tab         import JsonTab
from compare_tab      import CompareTab
from qr_tab           import QRCodeTab
from binary_convertor_tab import BinaryConvertorTab
from uuid_generator_tab   import UUIDGeneratorTab
from toon_tab         import ToonTab

# ── Tool registry — add new tools here only ───────────────────────────────────
def _build_tool_registry(nb, root):
    """Return ordered list of (label, widget_instance) for every available tool."""
    return [
        ("{ }  JSON Formatter",    JsonTab(nb)),
        ("≠   Text Compare",       CompareTab(nb)),
        ("⊞  QR Code Generator",   QRCodeTab(nb)),
        ("01  Binary Convertor",    BinaryConvertorTab(nb, root)),
        ("UUID Generator",      UUIDGeneratorTab(nb, root)),
        ("{[]}  TOON Formatter",    ToonTab(nb)),
    ]


# ── Dropdown / checklist popup ────────────────────────────────────────────────
class ToolPickerPopup(tk.Toplevel):
    """Small popup with checkboxes for each tool; calls back on Apply."""

    def __init__(self, parent, tool_labels, visible_set, on_apply):
        super().__init__(parent)
        self.title("Select Tools")
        self.resizable(False, False)
        self.configure(bg=HDR_BG)
        self.grab_set()                       # modal
        self.on_apply = on_apply

        tk.Label(self, text="Visible tabs", bg=HDR_BG, fg=ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(padx=16, pady=(12, 6))

        ttk.Separator(self).pack(fill=tk.X, padx=8)

        frame = tk.Frame(self, bg=HDR_BG)
        frame.pack(padx=16, pady=8)

        self.vars = {}
        for label in tool_labels:
            var = tk.BooleanVar(value=(label in visible_set))
            cb  = tk.Checkbutton(frame, text=f"  {label}", variable=var,
                                 bg=HDR_BG, fg="white", selectcolor=HDR_BG,
                                 activebackground=HDR_BG, activeforeground=ACCENT,
                                 font=("Segoe UI", 10), anchor="w")
            cb.pack(fill=tk.X, pady=2)
            self.vars[label] = var

        ttk.Separator(self).pack(fill=tk.X, padx=8)

        btn_row = tk.Frame(self, bg=HDR_BG)
        btn_row.pack(pady=10)

        tk.Button(btn_row, text="Apply", bg=ACCENT, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  padx=18, pady=4,
                  command=self._apply).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_row, text="Cancel", bg=HDR_BG, fg="white",
                  font=("Segoe UI", 10), relief="flat",
                  padx=18, pady=4,
                  command=self.destroy).pack(side=tk.LEFT, padx=6)

        # Centre the popup over parent
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")

    def _apply(self):
        selected = {label for label, var in self.vars.items() if var.get()}
        if not selected:
            tk.messagebox.showwarning("DevTools", "Select at least one tool.",
                                      parent=self)
            return
        self.on_apply(selected)
        self.destroy()


# ── Main app ──────────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.title("DevTools - Ding! Your Swiss Army Knife for Developers")
    root.geometry("1200x780")
    root.minsize(900, 600)
    root.configure(bg=HDR_BG)
    apply_theme(root)

    # ── Header bar ────────────────────────────────────────────────────────────
    hdr = tk.Frame(root, bg=HDR_BG, height=48)
    hdr.pack(fill=tk.X)
    hdr.pack_propagate(False)

    tk.Label(hdr, text="⬡  DevTools", bg=HDR_BG, fg=ACCENT,
             font=("Segoe UI", 15, "bold")).pack(side=tk.LEFT, padx=18)
    tk.Label(hdr, text="building with AI",
             bg=HDR_BG, fg=FG_DIM, font=("Segoe UI", 10)).pack(side=tk.LEFT)
    tk.Label(hdr,
             text="Ctrl+Z = undo  ·  Ctrl+Enter = run  ·  100% local",
             bg=HDR_BG, fg=FG_DIM,
             font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=18)

    # "Tools ▾" picker button — sits on the right of the header
    def open_picker():
        ToolPickerPopup(
            parent      = root,
            tool_labels = [label for label, _ in tools],
            visible_set = visible_labels,
            on_apply    = apply_visibility,
        )

    tk.Button(hdr, text="Tools ▾", bg=HDR_BG, fg=ACCENT,
              font=("Segoe UI", 10, "bold"), relief="flat",
              activebackground=HDR_BG, activeforeground="white",
              cursor="hand2", command=open_picker
              ).pack(side=tk.RIGHT, padx=(0, 8))

    ttk.Separator(root).pack(fill=tk.X)

    # ── Notebook ──────────────────────────────────────────────────────────────
    nb = ttk.Notebook(root)
    nb.pack(fill=tk.BOTH, expand=True)

    # Build all tool widgets once (so state survives hide/show)
    tools = _build_tool_registry(nb, root)        # [(label, widget), ...]

    # All tools visible by default
    visible_labels: set[str] = {label for label, _ in tools}

    def apply_visibility(new_visible: set[str]):
        """Show only the tabs whose labels are in new_visible."""
        nonlocal visible_labels
        visible_labels = new_visible

        # Remove every tab currently in the notebook
        for tab_id in nb.tabs():
            nb.forget(tab_id)

        # Re-add in original order, only if selected
        for label, widget in tools:
            if label in visible_labels:
                nb.add(widget, text=f"   {label}   ")

    # Initial population
    apply_visibility(visible_labels)

    root.mainloop()


if __name__ == "__main__":
    main()