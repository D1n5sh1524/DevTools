"""
qr_tab.py — QR Code Generator tab
"""
import tkinter as tk
from tkinter import ttk, messagebox

import qrcode
from io import BytesIO
from PIL import ImageTk


class QRCodeTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.url_var = tk.StringVar()

        ttk.Label(self, text="Enter a URL:").grid(
            row=0, column=0, padx=10, pady=5)
        ttk.Entry(self, textvariable=self.url_var, width=50).grid(
            row=0, column=1, padx=10, pady=5)

        ttk.Button(self, text="Generate QR Code",
                   command=self.generate).grid(
            row=1, column=0, columnspan=2, padx=10, pady=5)

        self.qr_label = ttk.Label(self, background="white")
        self.qr_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    # ── action ───────────────────────────────────────────────────────────────
    def generate(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")

        buf   = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        photo = ImageTk.PhotoImage(data=buf.read())

        self.qr_label.config(image=photo)
        self.qr_label.image = photo   # keep reference alive