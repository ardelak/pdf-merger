# PDF Merger

Merge PDF files with a template and add watermarks.

## Features

- Merge multiple PDFs with a template document
- Add watermarks with custom text (filename, prefix, postfix)
- Support for non-Latin characters (Cyrillic, etc.) via TTF fonts
- Configurable watermark position and font size

## Requirements

```bash
pip install pypdf reportlab
```

## Usage

Edit the configuration section at the bottom of `merge_pdfs.py`:

```python
FOLDER = Path(".")               # folder containing source PDFs
TEMPLATE = Path("template.pdf")  # template file
OUTPUT = Path("output")          # output subfolder

# Watermark settings
FONT_SIZE = 12
PREFIX = ""          # text before filename
POSTFIX = " - Page"  # text after filename
POSITION = None      # (x, y) tuple or None for auto-position
```

Run:

```bash
python merge_pdfs.py
```

## Output

Merged PDFs are saved to the `output/` folder with prefix `merged_`.