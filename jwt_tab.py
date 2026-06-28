"""
jwt_tab.py — JWT Encoder and Decoder tab
"""
import tkinter as tk
from tkinter import ttk
import json
import re
import base64
import hmac
import hashlib

from theme import (
    ACCENT, STATUS_OK, STATUS_ERR, STATUS_DIM,
    MONO_FONT, hsep,
)
from widgets import make_lnt

# Algorithm map
HASH_MAP = {
    "HS256": hashlib.sha256,
    "HS384": hashlib.sha384,
    "HS512": hashlib.sha512,
}

def base64url_encode(b: bytes) -> str:
    encoded = base64.urlsafe_b64encode(b)
    return encoded.rstrip(b'=').decode('utf-8')

def base64url_decode(s: str) -> bytes:
    s_bytes = s.encode('utf-8')
    rem = len(s_bytes) % 4
    if rem > 0:
        s_bytes += b'=' * (4 - rem)
    return base64.urlsafe_b64decode(s_bytes)

def sign_jwt(header_segment: str, payload_segment: str, secret: str, algorithm: str = "HS256") -> str:
    signing_input = f"{header_segment}.{payload_segment}".encode('utf-8')
    secret_bytes = secret.encode('utf-8')
    
    if algorithm == "none":
        return ""
    
    hash_fn = HASH_MAP.get(algorithm)
    if not hash_fn:
        raise ValueError(f"Unsupported algorithm {algorithm}")
    
    sig = hmac.new(secret_bytes, signing_input, hash_fn).digest()
    return base64url_encode(sig)


class JWTTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._lock = False
        self._build()
        self._set_default_values()
        # Initial run
        self.encode_token()

    def _build(self):
        # ── Main split pane ───────────────────────────────────────────────────
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 4))

        # ── Left Pane: Encoded Token ──────────────────────────────────────────
        lf_left = ttk.LabelFrame(pane, text="  Encoded (JWT Token)  ")
        pane.add(lf_left, weight=1)

        # Token input
        self.tok_text = make_lnt(lf_left, wrap=tk.CHAR)
        
        # Bottom controls for Token
        left_controls = ttk.Frame(lf_left)
        left_controls.pack(fill=tk.X, padx=12, pady=8)

        ttk.Button(left_controls, text="▶  Decode Token",
                   style="Accent.TButton", command=self.decode_token).pack(side=tk.LEFT)
        ttk.Button(left_controls, text="Copy Token",
                   command=self.copy_token).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(left_controls, text="Clear", style="Danger.TButton",
                   command=self.clear_all).pack(side=tk.LEFT, padx=(8, 0))

        # ── Right Pane: Decoded (Header, Payload, Signature) ──────────────────
        lf_right = ttk.Frame(pane)
        pane.add(lf_right, weight=1)

        right_pane = ttk.PanedWindow(lf_right, orient=tk.VERTICAL)
        right_pane.pack(fill=tk.BOTH, expand=True)

        # Sub-pane 1: Header
        lf_hdr = ttk.LabelFrame(right_pane, text="  Decoded: Header (JSON)  ")
        self.hdr_text = make_lnt(lf_hdr, wrap=tk.WORD)
        right_pane.add(lf_hdr, weight=1)

        # Sub-pane 2: Payload
        lf_pay = ttk.LabelFrame(right_pane, text="  Decoded: Payload (JSON)  ")
        self.pay_text = make_lnt(lf_pay, wrap=tk.WORD)
        right_pane.add(lf_pay, weight=2)

        # Sub-pane 3: Signature & Secret
        lf_sec = ttk.LabelFrame(right_pane, text="  Signature / Secret Verification  ")
        right_pane.add(lf_sec, weight=1)

        # Controls grid inside lf_sec
        sec_grid = ttk.Frame(lf_sec)
        sec_grid.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Row 0: Algorithm and Auto-sync
        ttk.Label(sec_grid, text="Algorithm:", style="Dim.TLabel").grid(row=0, column=0, sticky="w", pady=4)
        self.algo_var = tk.StringVar(value="HS256")
        self.algo_cb = ttk.Combobox(sec_grid, textvariable=self.algo_var, values=["HS256", "HS384", "HS512", "none"], state="readonly", width=10)
        self.algo_cb.grid(row=0, column=1, sticky="w", padx=10, pady=4)
        self.algo_cb.bind("<<ComboboxSelected>>", lambda _e: self._on_ui_change())

        self.autosync_var = tk.BooleanVar(value=True)
        self.autosync_cb = ttk.Checkbutton(sec_grid, text="Auto-Sync on edit", variable=self.autosync_var)
        self.autosync_cb.grid(row=0, column=2, sticky="w", padx=10, pady=4)

        # Row 1: Secret / Key
        ttk.Label(sec_grid, text="HMAC Secret:", style="Dim.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        self.secret_var = tk.StringVar(value="your-256-bit-secret")
        self.secret_entry = ttk.Entry(sec_grid, textvariable=self.secret_var, width=30)
        self.secret_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=10, pady=4)
        self.secret_var.trace_add("write", lambda *_args: self._on_ui_change())

        # Row 2: Encode button and Verification status
        sec_btn_frame = ttk.Frame(sec_grid)
        sec_btn_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        ttk.Button(sec_btn_frame, text="◀  Encode",
                   style="Accent.TButton", command=self.encode_token).pack(side=tk.LEFT)

        self.sig_status_var = tk.StringVar(value="Signature Verified")
        self.sig_status_lbl = ttk.Label(sec_btn_frame, textvariable=self.sig_status_var, font=("Segoe UI", 11, "bold"))
        self.sig_status_lbl.pack(side=tk.LEFT, padx=15)

        # Configure column widths in grid
        sec_grid.columnconfigure(1, weight=1)

        # ── Status Bar ────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Interactive JWT Encoder and Decoder")
        self.status_lbl = ttk.Label(self, textvariable=self.status_var, style="Dim.TLabel")
        self.status_lbl.pack(anchor=tk.W, padx=16, pady=(0, 2))
        hsep(self)

        # ── Bind change events for auto-sync ──────────────────────────────────
        self.tok_text.text.bind("<KeyRelease>", lambda _e: self._on_token_change())
        self.hdr_text.text.bind("<KeyRelease>", lambda _e: self._on_decoded_change())
        self.pay_text.text.bind("<KeyRelease>", lambda _e: self._on_decoded_change())

        # Configure custom highlighting tags
        for editor in [self.hdr_text, self.pay_text]:
            editor.tag_configure("key",  foreground="#1d4ed8", font=(MONO_FONT[0], MONO_FONT[1], "bold"))
            editor.tag_configure("str",  foreground="#166534")
            editor.tag_configure("num",  foreground="#b45309")
            editor.tag_configure("bool", foreground="#7c3aed")
            editor.tag_configure("null", foreground="#dc2626")

    # ── Default state setup ───────────────────────────────────────────────────
    def _set_default_values(self):
        default_hdr = {
            "alg": "HS256",
            "typ": "JWT"
        }
        default_pay = {
            "sub": "1234567890",
            "name": "John Doe",
            "admin": True,
            "iat": 1516239022
        }
        self._write_lnt(self.hdr_text, json.dumps(default_hdr, indent=2))
        self._write_lnt(self.pay_text, json.dumps(default_pay, indent=2))
        self._highlight(self.hdr_text)
        self._highlight(self.pay_text)

    # ── Helper functions ──────────────────────────────────────────────────────
    def _write_lnt(self, widget, text):
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)

    def _set_status(self, msg, color=STATUS_DIM):
        self.status_var.set(msg)
        self.status_lbl.configure(foreground=color)

    def _set_sig_status(self, msg, color=STATUS_OK):
        self.sig_status_var.set(msg)
        self.sig_status_lbl.configure(foreground=color)

    def _highlight(self, lnt_widget):
        txt = lnt_widget.get("1.0", tk.END)
        for tag in ["key", "str", "num", "bool", "null"]:
            lnt_widget.tag_remove(tag, "1.0", tk.END)
        # keys
        for m in re.finditer(r'"(?:[^"\\]|\\.)*"\s*:', txt):
            end_key = m.end() - len(m.group(0)) + len(m.group(0).rstrip(": \t"))
            lnt_widget.tag_add("key", f"1.0+{m.start()}c", f"1.0+{end_key}c")
        # string values
        for m in re.finditer(r':\s*("(?:[^"\\]|\\.)*")', txt):
            lnt_widget.tag_add("str", f"1.0+{m.start(1)}c", f"1.0+{m.end(1)}c")
        # numbers
        for m in re.finditer(r':\s*(-?\d+\.?\d*(?:[eE][+-]?\d+)?)', txt):
            lnt_widget.tag_add("num", f"1.0+{m.start(1)}c", f"1.0+{m.end(1)}c")
        # booleans
        for m in re.finditer(r'\b(true|false)\b', txt):
            lnt_widget.tag_add("bool", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        # null
        for m in re.finditer(r'\bnull\b', txt):
            lnt_widget.tag_add("null", f"1.0+{m.start()}c", f"1.0+{m.end()}c")

    # ── Event handlers for Auto-Sync ──────────────────────────────────────────
    def _on_token_change(self):
        if self.autosync_var.get():
            self.decode_token()

    def _on_decoded_change(self):
        if self.autosync_var.get():
            self.encode_token()

    def _on_ui_change(self):
        if self.autosync_var.get():
            self.encode_token()

    # ── Core encoding / decoding actions ──────────────────────────────────────
    def encode_token(self):
        if self._lock:
            return
        self._lock = True
        try:
            hdr_raw = self.hdr_text.get("1.0", tk.END).strip()
            pay_raw = self.pay_text.get("1.0", tk.END).strip()
            secret = self.secret_var.get()
            algo = self.algo_var.get()

            if not hdr_raw or not pay_raw:
                self._lock = False
                return

            # Validate Header JSON
            try:
                hdr_obj = json.loads(hdr_raw)
            except json.JSONDecodeError as e:
                self._set_status(f"✗ Header JSON error: {str(e)}", STATUS_ERR)
                self._set_sig_status("Encoding Failed: Invalid Header", STATUS_ERR)
                self._lock = False
                return

            # Ensure algorithm aligns
            hdr_obj["alg"] = algo
            # Rewrite header in display without resetting focus/scroll if possible
            # Wait, updating it on key release might overwrite what user is typing.
            # We only write back if alg changed to avoid interrupting typing.
            if hdr_obj.get("alg") != algo or "alg" not in hdr_obj:
                hdr_compact_show = json.dumps(hdr_obj, indent=2)
                self._write_lnt(self.hdr_text, hdr_compact_show)
                self._highlight(self.hdr_text)

            # Validate Payload JSON
            try:
                pay_obj = json.loads(pay_raw)
            except json.JSONDecodeError as e:
                self._set_status(f"✗ Payload JSON error: {str(e)}", STATUS_ERR)
                self._set_sig_status("Encoding Failed: Invalid Payload", STATUS_ERR)
                self._lock = False
                return

            # Pretty syntax highlighting on the right panes
            self._highlight(self.hdr_text)
            self._highlight(self.pay_text)

            # Construct JWT
            hdr_compact = json.dumps(hdr_obj, separators=(',', ':'), ensure_ascii=False)
            pay_compact = json.dumps(pay_obj, separators=(',', ':'), ensure_ascii=False)

            hdr_b64 = base64url_encode(hdr_compact.encode('utf-8'))
            pay_b64 = base64url_encode(pay_compact.encode('utf-8'))
            sig_b64 = sign_jwt(hdr_b64, pay_b64, secret, algo)

            token = f"{hdr_b64}.{pay_b64}.{sig_b64}"
            self._write_lnt(self.tok_text, token)

            self._set_status("✓ JWT token successfully encoded and updated.", STATUS_OK)
            self._set_sig_status("✓ Signature Verified", STATUS_OK)
        except Exception as e:
            self._set_status(f"✗ Encoding error: {str(e)}", STATUS_ERR)
            self._set_sig_status("✗ Error", STATUS_ERR)
        finally:
            self._lock = False

    def decode_token(self):
        if self._lock:
            return
        self._lock = True
        try:
            token = self.tok_text.get("1.0", tk.END).strip()
            if not token:
                self._lock = False
                return

            parts = token.split('.')
            if len(parts) != 3:
                self._set_status("✗ Invalid JWT format. Must contain 3 dot-separated parts.", STATUS_ERR)
                self._set_sig_status("✗ Invalid Token Structure", STATUS_ERR)
                self._lock = False
                return

            # 1. Decode Header
            try:
                hdr_bytes = base64url_decode(parts[0])
                hdr_obj = json.loads(hdr_bytes.decode('utf-8'))
                self._write_lnt(self.hdr_text, json.dumps(hdr_obj, indent=2))
                self._highlight(self.hdr_text)
            except Exception as e:
                self._set_status(f"✗ Failed to decode Header: {str(e)}", STATUS_ERR)
                self._set_sig_status("✗ Decode Failed", STATUS_ERR)
                self._lock = False
                return

            # 2. Decode Payload
            try:
                pay_bytes = base64url_decode(parts[1])
                pay_obj = json.loads(pay_bytes.decode('utf-8'))
                self._write_lnt(self.pay_text, json.dumps(pay_obj, indent=2))
                self._highlight(self.pay_text)
            except Exception as e:
                self._set_status(f"✗ Failed to decode Payload: {str(e)}", STATUS_ERR)
                self._set_sig_status("✗ Decode Failed", STATUS_ERR)
                self._lock = False
                return

            # Update Algorithm Combobox selection to match header
            algo = hdr_obj.get("alg", "HS256")
            if algo in ["HS256", "HS384", "HS512", "none"]:
                self.algo_var.set(algo)
            else:
                self._set_status(f"⚠ Warning: Header algorithm '{algo}' is not natively supported for verification.", STATUS_DIM)

            # 3. Verify Signature
            secret = self.secret_var.get()
            try:
                expected_sig = sign_jwt(parts[0], parts[1], secret, algo)
                actual_sig = parts[2]
                
                if algo == "none":
                    self._set_sig_status("⚠ Unsecured Token (none)", STATUS_DIM)
                    self._set_status("✓ Token successfully decoded (unsecured/no signature).", STATUS_OK)
                elif hmac.compare_digest(expected_sig.encode('utf-8'), actual_sig.encode('utf-8')):
                    self._set_sig_status("✓ Signature Verified", STATUS_OK)
                    self._set_status("✓ Token successfully decoded and signature verified.", STATUS_OK)
                else:
                    self._set_sig_status("✗ Invalid Signature", STATUS_ERR)
                    self._set_status("✗ Signature verification failed. Secret might be wrong.", STATUS_ERR)
            except Exception as e:
                self._set_sig_status("✗ Signature Verification Error", STATUS_ERR)
                self._set_status(f"✗ Signature error: {str(e)}", STATUS_ERR)

        except Exception as e:
            self._set_status(f"✗ Decoding error: {str(e)}", STATUS_ERR)
            self._set_sig_status("✗ Error", STATUS_ERR)
        finally:
            self._lock = False

    def copy_token(self):
        txt = self.tok_text.get("1.0", tk.END).strip()
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            self._set_status("✓ Token copied to clipboard!", ACCENT)

    def clear_all(self):
        self._write_lnt(self.tok_text, "")
        self._write_lnt(self.hdr_text, "")
        self._write_lnt(self.pay_text, "")
        self.secret_var.set("")
        self._set_sig_status("Cleared", STATUS_DIM)
        self._set_status("Paste an encoded token on the left, or edit the decoded JSON on the right.", STATUS_DIM)
