import tkinter as tk
from tkinter import ttk, messagebox
import uuid
import datetime

class UUIDGeneratorTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.history_text = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        # Frame for generating and displaying UUIDs
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        result_frame = ttk.Frame(frame)
        result_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Result display area
        self.result_text = tk.Entry(result_frame, width=40)
        self.result_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        button_frame = ttk.Frame(result_frame)
        button_frame.pack(side=tk.RIGHT, padx=5, pady=5)

        # Generate button and Copy button in the same line
        generate_button = ttk.Button(button_frame, text="Generate UUID", command=self.generate_uuid)
        generate_button.pack(side=tk.LEFT, padx=5, pady=5)

        copy_button = ttk.Button(button_frame, text="Copy", command=self.copy_to_clipboard)
        copy_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Clear history button
        clear_history_button = ttk.Button(result_frame, text="Clear History", command=self.clear_history)
        clear_history_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # History display
        history_label = tk.Label(frame, text="History:", font=("Segoe UI", 12))
        history_label.pack(side=tk.TOP, padx=5, pady=5)

        self.history_display = tk.Text(frame, height=8, width=80, wrap=tk.WORD)
        self.history_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_display.config(state=tk.DISABLED)

    def generate_uuid(self):
        new_uuid = uuid.uuid4()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{current_time} - {new_uuid}\n"
        self.result_text.delete(0, tk.END)
        self.result_text.insert(tk.END, str(new_uuid))

        self.history_text.set(self.history_text.get() + entry)
        self.update_history_display()

    def copy_to_clipboard(self):
        text = self.result_text.get()
        root = self.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(text)

    def refresh_history(self):
        self.history_display.config(state=tk.NORMAL)
        self.history_display.delete(1.0, tk.END)
        self.history_display.insert(tk.END, self.history_text.get())
        self.history_display.config(state=tk.DISABLED)

    def clear_history(self):
        self.history_text.set("")
        self.update_history_display()

    def update_history_display(self):
        history = self.history_text.get()
        self.history_display.config(state=tk.NORMAL)
        self.history_display.delete(1.0, tk.END)
        self.history_display.insert(tk.END, history)
        self.history_display.config(state=tk.DISABLED)
