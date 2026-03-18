"""
Utility tools: HTTP fetch, file write/append, email, datetime.
"""
import json
import urllib.request
import urllib.error
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os

tool_specs = [
    {
        "name": "web_get",
        "description": "Fetch the content of a URL and return as text. Supports http and https.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch."
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout in seconds (default: 10)."
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "file_write",
        "description": "Write text content to a file, overwriting any existing content. Use with caution.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write."
                },
                "content": {
                    "type": "string",
                    "description": "Text content to write."
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "file_append",
        "description": "Append text content to a file. Creates the file if it doesn't exist.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to append to."
                },
                "content": {
                    "type": "string",
                    "description": "Text content to append."
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "send_email_smtp",
        "description": "Send an email via SMTP. Requires SMTP server configuration in config.json under 'email' section.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address."
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject."
                },
                "body": {
                    "type": "string",
                    "description": "Plain text body of the email."
                }
            },
            "required": ["to", "subject", "body"]
        }
    },
    {
        "name": "current_time",
        "description": "Get the current date and time. Optionally specify a timezone (e.g., 'America/Los_Angeles', 'UTC').",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone name. Default: system local time."
                }
            }
        }
    }
]

def run_web_get(url: str, timeout: float = 10) -> str:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Picolo/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or 'utf-8'
            return resp.read().decode(charset, errors='replace')
    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"URL Error: {e.reason}"
    except Exception as e:
        return f"Error: {e}"

def run_file_write(file_path: str, content: str) -> str:
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote {len(content)} characters to {file_path}"
    except Exception as e:
        return f"Error: {e}"

def run_file_append(file_path: str, content: str) -> str:
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Appended {len(content)} characters to {file_path}"
    except Exception as e:
        return f"Error: {e}"

def run_send_email_smtp(to: str, subject: str, body: str) -> str:
    # Expect email config in agent config under 'email' key
    # Example config:
    # "email": {
    #   "smtp_server": "smtp.gmail.com",
    #   "smtp_port": 587,
    #   "username": "user@example.com",
    #   "password": "APP_PASSWORD"
    # }
    try:
        # We need to access the agent's config. Since tools are loaded as standalone modules,
        # we cannot directly access the agent's cfg. We can read config from a known location?
        # Better: The agent's config could be passed via environment variable or a known file path.
        # But our tool_spec is static; we need a way to get config.
        # Option: read config.json from the same directory as picolo.py.
        # This is a bit hacky but keeps the tool standalone.
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        if not os.path.exists(config_path):
            return "Error: config.json not found; cannot send email without SMTP configuration"
        with open(config_path) as f:
            cfg = json.load(f)
        email_cfg = cfg.get("email")
        if not email_cfg:
            return "Error: 'email' section missing in config.json"
        smtp_server = email_cfg.get("smtp_server")
        smtp_port = email_cfg.get("smtp_port", 587)
        username = email_cfg.get("username")
        password = email_cfg.get("password")
        if not smtp_server or not username or not password:
            return "Error: incomplete email configuration in config.json"

        msg = EmailMessage()
        msg["From"] = username
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        return "Email sent successfully"
    except Exception as e:
        return f"Error sending email: {e}"

def run_current_time(timezone: str = None) -> str:
    try:
        # If timezone is provided, use zoneinfo (Python 3.9+)
        if timezone:
            try:
                from zoneinfo import ZoneInfo
                tz = ZoneInfo(timezone)
                now = datetime.now(tz)
            except ImportError:
                return "Error: zoneinfo not available (Python 3.9+ required)"
            except Exception as e:
                return f"Error: {e}"
        else:
            now = datetime.now()
        return now.isoformat(sep=' ', timespec='seconds')
    except Exception as e:
        return f"Error: {e}"

# Map
tools = {
    "web_get": run_web_get,
    "file_write": run_file_write,
    "file_append": run_file_append,
    "send_email_smtp": run_send_email_smtp,
    "current_time": run_current_time
}
