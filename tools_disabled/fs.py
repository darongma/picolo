"""
Filesystem utilities: list files, check existence, get file size.
"""
import os

tool_specs = [
    {
        "name": "file_exists",
        "description": "Check if a file or directory exists.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to check."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_files",
        "description": "List files in a directory. Optionally filter by extension.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list. Default: current working directory."
                },
                "pattern": {
                    "type": "string",
                    "description": "Optional glob pattern, e.g., '*.pdf' or 'report_*'. Default: list all files."
                }
            }
        }
    },
    {
        "name": "file_size",
        "description": "Get the size of a file in bytes.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file."
                }
            },
            "required": ["file_path"]
        }
    }
]

def run_file_exists(path: str) -> str:
    return "true" if os.path.exists(path) else "false"

def run_list_files(directory: str = ".", pattern: str = None) -> str:
    import fnmatch
    try:
        entries = os.listdir(directory)
        if pattern:
            entries = [e for e in entries if fnmatch.fnmatch(e, pattern)]
        # separate files and dirs
        files = []
        dirs = []
        for e in entries:
            full = os.path.join(directory, e)
            if os.path.isdir(full):
                dirs.append(e + "/")
            else:
                files.append(e)
        out = []
        if dirs:
            out.append("Directories:\n" + "\n".join(sorted(dirs)))
        if files:
            out.append("Files:\n" + "\n".join(sorted(files)))
        return "\n".join(out).strip() or "(empty directory)"
    except Exception as e:
        return f"Error: {e}"

def run_file_size(file_path: str) -> str:
    try:
        size = os.path.getsize(file_path)
        return str(size)
    except Exception as e:
        return f"Error: {e}"

# Map of tool name to run function for dynamic registration
tools = {
    "file_exists": run_file_exists,
    "list_files": run_list_files,
    "file_size": run_file_size
}
