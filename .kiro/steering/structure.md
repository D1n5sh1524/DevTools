# Project Structure

```
DevTools/
├── main.py                    # Entry point — assembles tabs, header, tool picker
├── theme.py                   # Colour palette constants and ttk theme setup
├── widgets.py                 # Reusable widget: LineNumberedText, scroll linking
├── diff_utils.py              # Diff engine: tokeniser, word/char diff, renderer
├── json_tab.py                # JSON Formatter tab (JsonTab)
├── toon_tab.py                # TOON Formatter tab (ToonTab)
├── compare_tab.py             # Text Compare tab (CompareTab)
├── qr_tab.py                  # QR Code Generator tab (QRCodeTab)
├── binary_convertor_tab.py    # Binary Converter tab (BinaryConvertorTab)
├── uuid_generator_tab.py      # UUID Generator tab (UUIDGeneratorTab)
├── requirement.txt            # pip dependencies
├── README.md                  # Project documentation
└── .kiro/steering/            # AI steering rules (this directory)
```

## Architecture Pattern

- **Tab-per-tool**: Each tool lives in its own `*_tab.py` file and exports a single class that extends `ttk.Frame`.
- **Tool registry**: `main.py` has a `_build_tool_registry()` function. Adding a new tool means creating a tab file and adding one entry there.
- **Shared infrastructure**: `theme.py` provides palette constants and theming; `widgets.py` provides the `LineNumberedText` widget and scroll helpers; `diff_utils.py` provides diffing logic used by the compare tab.

## Conventions

- Tab class names use PascalCase matching the tool name (e.g., `JsonTab`, `CompareTab`).
- Tab files use snake_case with a `_tab.py` suffix.
- Constructor signatures: simple tabs take `(parent)`, tabs needing root window access take `(parent, controller)` where controller is the root `Tk` instance.
- UI building logic goes in a `_build()` or `create_widgets()` method called from `__init__`.
- Palette colours and fonts are imported from `theme.py` — never hard-coded in tab files (some older tabs violate this).
