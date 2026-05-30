"""
main.py — DevTools entry point
Assembles JSON Formatter, Text Compare, and QR Code Generator tabs.

Run:  python main.py
Deps: Python 3.x, qrcode, Pillow  (tkinter built-in)
"""

import tkinter as tk
from tkinter import ttk

from theme   import apply_theme, BG, HDR_BG, ACCENT, FG_DIM
from json_tab    import JsonTab
from compare_tab import CompareTab
from qr_tab      import QRCodeTab
from binary_convertor_tab import BinaryConvertorTab
from uuid_generator_tab import UUIDGeneratorTab 


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
    tk.Label(hdr, text="by Dinesh, using open source AI",
             bg=HDR_BG, fg=FG_DIM, font=("Segoe UI", 10)).pack(side=tk.LEFT)
    tk.Label(hdr,
             text="Ctrl+Z = undo  ·  Ctrl+Enter = run  ·  100% local",
             bg=HDR_BG, fg=FG_DIM,
             font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=18)

    ttk.Separator(root).pack(fill=tk.X)

    # ── Notebook tabs ─────────────────────────────────────────────────────────
    nb = ttk.Notebook(root)
    nb.pack(fill=tk.BOTH, expand=True)

    nb.add(JsonTab(nb),    text="   { }  JSON Formatter   ")
    nb.add(CompareTab(nb), text="   ≠   Text Compare   ")
    nb.add(QRCodeTab(nb),  text="   ⊞  QR Code Generator   ")
    nb.add(BinaryConvertorTab(nb, root), text="   ⊞  Binary Convertor   ")
    nb.add(UUIDGeneratorTab(nb, root), text="   ⊞  UUID Generator   ")

    root.mainloop()


if __name__ == "__main__":
    main()