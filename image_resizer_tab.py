"""
image_resizer_tab.py — Image Resizer utility tab
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

from theme import (
    ACCENT, STATUS_OK, STATUS_ERR, STATUS_DIM,
    hsep,
)

class ImageResizerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.original_image = None
        self.resized_image = None
        self.preview_image = None
        self.aspect_ratio = 1.0
        self._updating = False

        self._build()

    def _build(self):
        # Main layout: Split into Left controls and Right preview using a PanedWindow
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 4))

        # Left Panel (Controls)
        left_frame = ttk.Frame(pane)
        pane.add(left_frame, weight=1)

        # Right Panel (Preview)
        right_frame = ttk.LabelFrame(pane, text="  Image Preview  ")
        pane.add(right_frame, weight=1)

        # --- PREVIEW AREA ---
        self.preview_label = ttk.Label(right_frame, text="No image loaded", anchor="center")
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- CONTROLS AREA (left_frame) ---
        # File Selection Frame
        file_lf = ttk.LabelFrame(left_frame, text="  1. Select Image  ")
        file_lf.pack(fill=tk.X, padx=5, pady=5)

        file_select_frame = ttk.Frame(file_lf)
        file_select_frame.pack(fill=tk.X, padx=10, pady=10)

        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_btn = ttk.Button(file_select_frame, text="Browse...", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT)

        # Image Info Frame
        info_lf = ttk.LabelFrame(left_frame, text="  2. Image Details  ")
        info_lf.pack(fill=tk.X, padx=5, pady=5)

        info_grid = ttk.Frame(info_lf)
        info_grid.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(info_grid, text="Original Format:", style="Dim.TLabel").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_format = ttk.Label(info_grid, text="-")
        self.lbl_format.grid(row=0, column=1, sticky="w", padx=10, pady=2)

        ttk.Label(info_grid, text="Original Size:", style="Dim.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_size = ttk.Label(info_grid, text="-")
        self.lbl_size.grid(row=1, column=1, sticky="w", padx=10, pady=2)

        # Resize Parameters Frame
        params_lf = ttk.LabelFrame(left_frame, text="  3. Resize Options  ")
        params_lf.pack(fill=tk.X, padx=5, pady=5)

        params_grid = ttk.Frame(params_lf)
        params_grid.pack(fill=tk.X, padx=10, pady=10)

        # Keep Aspect Ratio Checkbox
        self.keep_aspect_var = tk.BooleanVar(value=True)
        self.keep_aspect_cb = ttk.Checkbutton(
            params_grid, 
            text="Keep Aspect Ratio", 
            variable=self.keep_aspect_var,
            command=self.on_keep_aspect_changed
        )
        self.keep_aspect_cb.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Target Width
        ttk.Label(params_grid, text="Width (px):").grid(row=1, column=0, sticky="w", pady=5)
        self.width_var = tk.StringVar()
        self.width_var.trace_add("write", self.on_width_changed)
        self.width_entry = ttk.Entry(params_grid, textvariable=self.width_var, width=12)
        self.width_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        # Target Height
        ttk.Label(params_grid, text="Height (px):").grid(row=2, column=0, sticky="w", pady=5)
        self.height_var = tk.StringVar()
        self.height_var.trace_add("write", self.on_height_changed)
        self.height_entry = ttk.Entry(params_grid, textvariable=self.height_var, width=12)
        self.height_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # Resampling Combobox
        ttk.Label(params_grid, text="Resampling:").grid(row=3, column=0, sticky="w", pady=5)
        self.resample_var = tk.StringVar(value="Bicubic")
        self.resample_combo = ttk.Combobox(
            params_grid, 
            textvariable=self.resample_var, 
            values=["Nearest", "Bilinear", "Bicubic", "Lanczos"],
            state="readonly",
            width=15
        )
        self.resample_combo.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        # --- Status Line ---
        self.status_var = tk.StringVar(value="Load an image to get started.")
        self.status_lbl = ttk.Label(self, textvariable=self.status_var, style="Dim.TLabel")
        self.status_lbl.pack(anchor=tk.W, padx=16, pady=(4, 2))
        hsep(self)

        # --- Bottom toolbar ---
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=12, pady=(4, 12))

        self.resize_btn = ttk.Button(bar, text="▶  Resize Image", style="Accent.TButton", command=self.resize_image)
        self.resize_btn.pack(side=tk.LEFT)

        self.save_btn = ttk.Button(bar, text="Save Resized Image...", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT, padx=(8, 0))

        ttk.Button(bar, text="Clear All", style="Danger.TButton", command=self.clear).pack(side=tk.LEFT, padx=(8, 0))

    def _set_status(self, msg, color=STATUS_DIM):
        self.status_var.set(msg)
        self.status_lbl.configure(foreground=color)

    def browse_file(self):
        filetypes = (
            ("Image files", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
            ("All files", "*.*")
        )
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            self.file_path_var.set(file_path)
            self.load_image(file_path)

    def load_image(self, file_path):
        try:
            img = Image.open(file_path)
            self.original_image = img
            self.resized_image = None
            w, h = img.size
            self.aspect_ratio = w / h

            self.lbl_format.config(text=img.format or "Unknown")
            self.lbl_size.config(text=f"{w} x {h} px")

            # Update entry fields silently
            self._updating = True
            self.width_var.set(str(w))
            self.height_var.set(str(h))
            self._updating = False

            self.show_preview(img)
            self._set_status(f"✓ Image loaded successfully: {w}x{h} px", STATUS_OK)
        except Exception as e:
            self._set_status(f"✗ Failed to load image: {e}", STATUS_ERR)
            messagebox.showerror("Error", f"Could not load image: {e}")

    def show_preview(self, img):
        if not img:
            return

        # Get preview area dimensions (or use dynamic sizing but let's default to max 450x450 for scaling)
        max_w, max_h = 450, 450
        w, h = img.size
        
        # Calculate fitting size keeping aspect ratio
        scale = min(max_w / w, max_h / h)
        if scale < 1.0:
            preview_w = int(w * scale)
            preview_h = int(h * scale)
        else:
            preview_w = w
            preview_h = h

        try:
            preview_img = img.resize((preview_w, preview_h), Image.Resampling.BILINEAR)
            self.preview_photo = ImageTk.PhotoImage(preview_img)
            self.preview_label.config(image=self.preview_photo, text="")
        except Exception as e:
            self._set_status(f"✗ Preview scaling error: {e}", STATUS_ERR)

    def on_keep_aspect_changed(self):
        if self.keep_aspect_var.get() and self.original_image:
            try:
                w = int(self.width_var.get())
                self._updating = True
                self.height_var.set(str(int(w / self.aspect_ratio)))
                self._updating = False
            except ValueError:
                pass

    def on_width_changed(self, *args):
        if self._updating:
            return
        if self.keep_aspect_var.get() and self.original_image:
            try:
                val = self.width_var.get()
                if val:
                    w = int(val)
                    self._updating = True
                    self.height_var.set(str(max(1, int(w / self.aspect_ratio))))
                    self._updating = False
            except ValueError:
                pass

    def on_height_changed(self, *args):
        if self._updating:
            return
        if self.keep_aspect_var.get() and self.original_image:
            try:
                val = self.height_var.get()
                if val:
                    h = int(val)
                    self._updating = True
                    self.width_var.set(str(max(1, int(h * self.aspect_ratio))))
                    self._updating = False
            except ValueError:
                pass

    def resize_image(self):
        if not self.original_image:
            self._set_status("✗ No image loaded to resize.", STATUS_ERR)
            messagebox.showwarning("Warning", "Please select and load an image first.")
            return

        try:
            tw_str = self.width_var.get()
            th_str = self.height_var.get()
            if not tw_str or not th_str:
                raise ValueError("Width and Height must be provided.")

            target_w = int(tw_str)
            target_h = int(th_str)

            if target_w <= 0 or target_h <= 0:
                raise ValueError("Dimensions must be positive integers.")

            # Map resampling option
            resample_map = {
                "Nearest": Image.Resampling.NEAREST,
                "Bilinear": Image.Resampling.BILINEAR,
                "Bicubic": Image.Resampling.BICUBIC,
                "Lanczos": Image.Resampling.LANCZOS
            }
            resample_filter = resample_map.get(self.resample_var.get(), Image.Resampling.BICUBIC)

            # Perform actual resizing
            self.resized_image = self.original_image.resize((target_w, target_h), resample_filter)
            self.show_preview(self.resized_image)
            self._set_status(f"✓ Resized image to {target_w}x{target_h} px. Click 'Save Resized Image...' to export.", STATUS_OK)
        except ValueError as ve:
            self._set_status(f"✗ Invalid dimensions: {ve}", STATUS_ERR)
            messagebox.showerror("Error", f"Invalid dimensions: {ve}")
        except Exception as e:
            self._set_status(f"✗ Resizing failed: {e}", STATUS_ERR)
            messagebox.showerror("Error", f"Resizing failed: {e}")

    def save_image(self):
        # We can either save the resized image, or fallback to original if not yet resized but with custom sizes
        img_to_save = self.resized_image or self.original_image
        if not img_to_save:
            self._set_status("✗ No image available to save.", STATUS_ERR)
            messagebox.showwarning("Warning", "No image is available to save.")
            return

        # Choose where to save
        filetypes = (
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("WebP files", "*.webp"),
            ("BMP files", "*.bmp"),
            ("All files", "*.*")
        )
        
        # Get extension of original image if possible to set default
        orig_ext = ".png"
        if self.original_image and self.original_image.format:
            orig_ext = f".{self.original_image.format.lower()}"
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=orig_ext,
            filetypes=filetypes,
            title="Save Resized Image As"
        )

        if save_path:
            try:
                # If target was never manually resized, resize it before saving using specified dimensions
                if not self.resized_image:
                    self.resize_image()
                    img_to_save = self.resized_image
                    if not img_to_save:
                        return

                # Convert to RGB if saving as JPEG and format is RGBA
                if save_path.lower().endswith(('.jpg', '.jpeg')) and img_to_save.mode in ('RGBA', 'LA'):
                    img_to_save = img_to_save.convert('RGB')

                img_to_save.save(save_path)
                self._set_status(f"✓ Successfully saved image to: {os.path.basename(save_path)}", STATUS_OK)
                messagebox.showinfo("Success", f"Image saved successfully to:\n{save_path}")
            except Exception as e:
                self._set_status(f"✗ Failed to save image: {e}", STATUS_ERR)
                messagebox.showerror("Error", f"Could not save image: {e}")

    def clear(self):
        self.original_image = None
        self.resized_image = None
        self.preview_image = None
        self.preview_label.config(image="", text="No image loaded")
        self.file_path_var.set("")
        self.lbl_format.config(text="-")
        self.lbl_size.config(text="-")
        
        self._updating = True
        self.width_var.set("")
        self.height_var.set("")
        self._updating = False
        
        self._set_status("Load an image to get started.")
