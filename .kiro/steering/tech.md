# Tech Stack

## Language & Runtime

- Python 3.x (no type annotations used currently)
- No async — everything runs on the tkinter main thread

## GUI Framework

- **tkinter** (standard library) with **ttk** themed widgets
- Custom ttk "clam" theme configured in `theme.py`

## External Libraries

Listed in `requirement.txt`:

- `qrcode==8.2` — QR code generation
- `pillow==12.2.0` — image handling (used by qrcode and binary converter)

## Common Commands

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirement.txt

# Run the application
python main.py
```

## No Build Step

This is a pure Python project — no compilation, bundling, or transpilation. Run directly with the Python interpreter.

## No Test Framework (yet)

There is currently no test suite or test runner configured.
