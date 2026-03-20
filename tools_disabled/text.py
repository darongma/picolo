"""
Read plain text files.
"""
tool_spec = {
    "name": "read_text",
    "description": "Read a plain text file and return its contents. Use for .txt, .md, .csv, .json, .py, etc.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the text file to read."
            }
        },
        "required": ["file_path"]
    }
}

def run(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # Try a different encoding
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"
