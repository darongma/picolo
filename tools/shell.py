"""
Shell tool: execute a shell command.
Adds the ability for the agent to run commands on the host system.
"""
import os
import json
import subprocess

# Load configuration
CONFIG = {}
_config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
try:
    with open(_config_path) as f:
        CONFIG = json.load(f)
except Exception:
    CONFIG = {}

tool_spec = {
    "name": "shell",
    "description": "Execute a shell command and return its output. Use for file operations, system queries, etc.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute."
            },
            "timeout": {
                "type": "number",
                "description": "Timeout in seconds. Defaults to config.shell_timeout_seconds (or 30)."
            }
        },
        "required": ["command"]
    }
}

def run(command: str, timeout: int = None) -> str:
    """Run a shell command safely and capture output."""
    if timeout is None:
        timeout = CONFIG.get('shell_timeout_seconds', 30)
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout + result.stderr
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error: {e}"