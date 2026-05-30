import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import base64
import io

class BinaryConvertorTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.create_widgets()

    def create_widgets(self):
        # Frame for file selection and conversion controls
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # File selection
        tk.Label(frame, text="Select Image File:", font=("Segoe UI", 12)).pack(side=tk.TOP, pady=5)
        self.file_entry = tk.Entry(frame, width=60)
        self.file_entry.pack(side=tk.TOP, padx=5)
        ttk.Button(frame, text="Browse", command=self.browse_file).pack(side=tk.TOP, padx=5)

        # Conversion type
        tk.Label(frame, text="Conversion Type:", font=("Segoe UI", 12)).pack(side=tk.TOP, pady=5)
        self.conversion_var = tk.StringVar(value='binary')
        radio_frame = ttk.Frame(frame)
        radio_frame.pack(side=tk.TOP, fill=tk.X, padx=5)

        ttk.Radiobutton(radio_frame, text="Binary Text", variable=self.conversion_var, value='binary').pack(side=tk.TOP, padx=20)
        ttk.Radiobutton(radio_frame, text="Hexadecimal", variable=self.conversion_var, value='hexadecimal').pack(side=tk.TOP, padx=20)
        ttk.Radiobutton(radio_frame, text="Base64", variable=self.conversion_var, value='base64').pack(side=tk.TOP, padx=20)

        # Convert button
        convert_button = ttk.Button(frame, text="Convert", command=self.convert_image)
        convert_button.pack(side=tk.TOP, pady=10)
        convert_button.config(style="TButton")

        # Result display with copy icon
        result_frame = ttk.Frame(frame)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(result_frame, height=10, width=80, wrap=tk.WORD)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        copy_button = ttk.Button(result_frame, text="Copy", command=self.copy_to_clipboard)
        copy_button.config(style="TButton")
        copy_button.pack(side=tk.TOP, padx=5, pady=5)

        # Style for buttons
        style = ttk.Style()
        style.configure("TButton", foreground="#faf7f2", background="#1d4ed8", font=("Segoe UI", 10, "bold"))

    def browse_file(self):
        filetypes = (("Image files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*"))
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def convert_image(self):
        file_path = self.file_entry.get()
        conversion_type = self.conversion_var.get()

        if not file_path:
            messagebox.showerror("Error", "Please select a file.")
            return

        try:
            with open(file_path, "rb") as image_file:
                binary_data = image_file.read()
        except FileNotFoundError:
            messagebox.showerror("Error", f"File {file_path} not found.")
            return

        if conversion_type == 'binary':
            result = binary_data
        elif conversion_type == 'hexadecimal':
            result = ''.join(f'{byte:02x}' for byte in binary_data)
        elif conversion_type == 'base64':
            result = base64.b64encode(binary_data).decode('utf-8')
        else:
            messagebox.showerror("Error", "Invalid conversion type.")
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

    def copy_to_clipboard(self):
        text = self.result_text.get(1.0, tk.END).strip()
        root = self.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(text)

