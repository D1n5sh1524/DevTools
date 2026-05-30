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
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        # Create a frame for the QR code display and controls
        qr_frame = ttk.Frame(self)
        qr_frame.pack(fill=tk.BOTH, expand=True)

        # Label to display the QR code image
        self.qr_label = tk.Label(qr_frame)
        self.qr_label.pack(fill=tk.BOTH, expand=True)

        # Entry widget for input text
        self.text_entry = ttk.Entry(qr_frame)
        self.text_entry.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Button to generate QR code
        self.generate_button = ttk.Button(qr_frame, text="Generate QR Code", command=self.generate_qr_code)
        self.generate_button.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Button to download QR code
        self.download_button = ttk.Button(qr_frame, text="Download QR Code", command=self.download_qr_code)
        self.download_button.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

    def generate_qr_code(self):
        text = self.text_entry.get()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        self.photo = ImageTk.PhotoImage(img)
        self.qr_label.config(image=self.photo)

    def download_qr_code(self):
        text = self.text_entry.get()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        img.save("qr_code.png")
        tk.messagebox.showinfo("Download", "QR code downloaded as 'qr_code.png'")
