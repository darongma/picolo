"""
Shell tool: execute a shell command.
Adds the ability for the agent to run commands on the host system.
"""
import subprocess

tool_spec = {
    "name": "shell",
    "description": "Execute a shell command and return its output. Use for file operations, system queries, etc.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute."
            }
        },
        "required": ["command"]
    }
}

def run(command: str) -> str:
    """Run a shell command safely and capture output."""
    try:
        # timeout=30 seconds to prevent hangs
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 30 seconds"
    except Exception as e:
        return f"Error: {e}"
