"""
Read, create, and edit PDF files.
"""
import PyPDF2
from io import StringIO

# Read tool
tool_spec_read = {
    "name": "pdf_read",
    "description": "Extract text from a PDF file. Optionally specify page numbers (1-indexed). Returns concatenated text.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the PDF file."
            },
            "pages": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Optional list of page numbers to extract (e.g., [1,2,5]). If omitted, all pages are extracted."
            }
        },
        "required": ["file_path"]
    }
}

def run_read(file_path: str, pages: list = None) -> str:
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            total_pages = len(reader.pages)
            out = StringIO()
            if pages:
                for p in pages:
                    if 1 <= p <= total_pages:
                        out.write(reader.pages[p-1].extract_text() + "\n")
                    else:
                        out.write(f"[Page {p} out of range]\n")
            else:
                for i, page in enumerate(reader.pages):
                    out.write(f"--- Page {i+1} ---\n")
                    out.write(page.extract_text() + "\n")
            text = out.getvalue().strip()
            return text if text else "(PDF has no extractable text)"
    except Exception as e:
        return f"Error: {e}"

# Create blank PDF
tool_spec_create_blank = {
    "name": "pdf_create_blank",
    "description": "Create a new PDF with a specified number of blank pages. Page size: default US Letter (612x792 points).",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path where the PDF will be saved."
            },
            "num_pages": {
                "type": "integer",
                "description": "Number of blank pages to create. Default: 1."
            },
            "width": {
                "type": "number",
                "description": "Page width in points (1/72 inch). Default: 612 (8.5in)."
            },
            "height": {
                "type": "number",
                "description": "Page height in points. Default: 792 (11in)."
            }
        },
        "required": ["file_path"]
    }
}

def run_create_blank(file_path: str, num_pages: int = 1, width: float = 612, height: float = 792) -> str:
    try:
        writer = PyPDF2.PdfWriter()
        for _ in range(num_pages):
            page = PyPDF2.PageObject.create_blank_page(width=width, height=height)
            writer.add_page(page)
        with open(file_path, "wb") as f:
            writer.write(f)
        return f"Created blank PDF with {num_pages} page(s) at {file_path}"
    except Exception as e:
        return f"Error: {e}"

# Merge PDFs
tool_spec_merge = {
    "name": "pdf_merge",
    "description": "Merge multiple PDF files into a single PDF. All pages from each source are concatenated in order.",
    "parameters": {
        "type": "object",
        "properties": {
            "target_file": {
                "type": "string",
                "description": "Path for the merged output PDF."
            },
            "sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of source PDF file paths to merge."
            }
        },
        "required": ["target_file", "sources"]
    }
}

def run_merge(target_file: str, sources: list) -> str:
    try:
        writer = PyPDF2.PdfWriter()
        total_pages = 0
        for src in sources:
            reader = PyPDF2.PdfReader(src)
            for page in reader.pages:
                writer.add_page(page)
                total_pages += 1
            reader.close()
        with open(target_file, "wb") as f:
            writer.write(f)
        return f"Merged {len(sources)} files ({total_pages} pages) into {target_file}"
    except Exception as e:
        return f"Error: {e}"

# Split PDF
tool_spec_split = {
    "name": "pdf_split",
    "description": "Split a PDF into multiple files based on page ranges. Provide either page_ranges (list of [start,end] inclusive, 1-indexed) or split individually by omitting page_ranges.",
    "parameters": {
        "type": "object",
        "properties": {
            "source_file": {
                "type": "string",
                "description": "Path to the source PDF."
            },
            "output_prefix": {
                "type": "string",
                "description": "Prefix for output files; will be numbered (e.g., 'prefix_1.pdf', 'prefix_2.pdf')."
            },
            "page_ranges": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2
                },
                "description": "Optional list of [start, end] page ranges (1-indexed, inclusive). If omitted, each page becomes a separate file."
            }
        },
        "required": ["source_file", "output_prefix"]
    }
}

def run_split(source_file: str, output_prefix: str, page_ranges: list = None) -> str:
    try:
        reader = PyPDF2.PdfReader(source_file)
        total_pages = len(reader.pages)
        outputs = []
        if page_ranges is None:
            # Split each page individually
            for i in range(total_pages):
                writer = PyPDF2.PdfWriter()
                writer.add_page(reader.pages[i])
                out_path = f"{output_prefix}_{i+1}.pdf"
                with open(out_path, "wb") as f:
                    writer.write(f)
                outputs.append(out_path)
            return f"Split into {len(outputs)} single-page PDFs: {outputs}"
        else:
            for idx, (start, end) in enumerate(page_ranges):
                start = max(1, start)
                end = min(total_pages, end)
                if start > end:
                    continue
                writer = PyPDF2.PdfWriter()
                for p in range(start-1, end):
                    writer.add_page(reader.pages[p])
                out_path = f"{output_prefix}_{idx+1}.pdf"
                with open(out_path, "wb") as f:
                    writer.write(f)
                outputs.append(out_path)
            return f"Split into {len(outputs)} PDFs: {outputs}"
    except Exception as e:
        return f"Error: {e}"

# Rotate pages
tool_spec_rotate = {
    "name": "pdf_rotate",
    "description": "Rotate specified pages in a PDF by a multiple of 90 degrees. Requires an output path (can be different from input).",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the source PDF."
            },
            "pages": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of page numbers (1-indexed) to rotate."
            },
            "angle": {
                "type": "integer",
                "description": "Rotation angle in degrees. Must be 90, 180, or 270 (clockwise)."
            },
            "output_path": {
                "type": "string",
                "description": "Path for the output PDF. If omitted, will overwrite the source (dangerous)."
            }
        },
        "required": ["file_path", "pages", "angle"]
    }
}

def run_rotate(file_path: str, pages: list, angle: int, output_path: str = None) -> str:
    if angle % 90 != 0:
        return "Error: angle must be a multiple of 90 (e.g., 90, 180, 270)."
    try:
        reader = PyPDF2.PdfReader(file_path)
        writer = PyPDF2.PdfWriter()
        total_pages = len(reader.pages)
        for i, page in enumerate(reader.pages):
            if i+1 in pages:
                page.rotate(angle)
            writer.add_page(page)
        out_path = output_path or file_path
        with open(out_path, "wb") as f:
            writer.write(f)
        return f"Rotated {len(pages)} page(s) by {angle}° in {out_path}"
    except Exception as e:
        return f"Error: {e}"

# Add watermark
tool_spec_watermark = {
    "name": "pdf_watermark",
    "description": "Add a watermark (from another PDF) onto each page of the target PDF. The watermark PDF should have a single page; it will be overlaid on each page.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the source PDF to watermark."
            },
            "watermark_file": {
                "type": "string",
                "description": "Path to the watermark PDF (single page)."
            },
            "output_path": {
                "type": "string",
                "description": "Path for the watermarked output PDF. If omitted, overwrites source."
            }
        },
        "required": ["file_path", "watermark_file"]
    }
}

def run_watermark(file_path: str, watermark_file: str, output_path: str = None) -> str:
    try:
        reader = PyPDF2.PdfReader(file_path)
        wm_reader = PyPDF2.PdfReader(watermark_file)
        if len(wm_reader.pages) == 0:
            return "Error: watermark file has no pages."
        wm_page = wm_reader.pages[0]
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            page.merge_page(wm_page)
            writer.add_page(page)
        out_path = output_path or file_path
        with open(out_path, "wb") as f:
            writer.write(f)
        return f"Applied watermark from {watermark_file} to {len(reader.pages)} pages in {out_path}"
    except Exception as e:
        return f"Error: {e}"

# Encrypt PDF
tool_spec_encrypt = {
    "name": "pdf_encrypt",
    "description": "Encrypt a PDF with a user password. Optionally set an owner password.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the PDF to encrypt."
            },
            "user_password": {
                "type": "string",
                "description": "User password required to open the PDF."
            },
            "owner_password": {
                "type": "string",
                "description": "Optional owner password for full permissions."
            },
            "output_path": {
                "type": "string",
                "description": "Output path. If omitted, overwrites source."
            }
        },
        "required": ["file_path", "user_password"]
    }
}

def run_encrypt(file_path: str, user_password: str, owner_password: str = None, output_path: str = None) -> str:
    try:
        reader = PyPDF2.PdfReader(file_path)
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(user_password=user_password, owner_password=owner_password)
        out_path = output_path or file_path
        with open(out_path, "wb") as f:
            writer.write(f)
        return f"Encrypted PDF saved to {out_path}"
    except Exception as e:
        return f"Error: {e}"

# Decrypt PDF
tool_spec_decrypt = {
    "name": "pdf_decrypt",
    "description": "Decrypt a PDF if it is protected with a user password. Requires the password.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the encrypted PDF."
            },
            "password": {
                "type": "string",
                "description": "Password to decrypt the PDF."
            },
            "output_path": {
                "type": "string",
                "description": "Path for the decrypted output PDF. If omitted, overwrites source."
            }
        },
        "required": ["file_path", "password"]
    }
}

def run_decrypt(file_path: str, password: str, output_path: str = None) -> str:
    try:
        reader = PyPDF2.PdfReader(file_path)
        if reader.is_encrypted:
            reader.decrypt(password)
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        out_path = output_path or file_path
        with open(out_path, "wb") as f:
            writer.write(f)
        return f"Decrypted PDF saved to {out_path}"
    except Exception as e:
        return f"Error: {e}"

tool_specs = [
    tool_spec_read,
    tool_spec_create_blank,
    tool_spec_merge,
    tool_spec_split,
    tool_spec_rotate,
    tool_spec_watermark,
    tool_spec_encrypt,
    tool_spec_decrypt
]

tools = {
    "pdf_read": run_read,
    "pdf_create_blank": run_create_blank,
    "pdf_merge": run_merge,
    "pdf_split": run_split,
    "pdf_rotate": run_rotate,
    "pdf_watermark": run_watermark,
    "pdf_encrypt": run_encrypt,
    "pdf_decrypt": run_decrypt
}
