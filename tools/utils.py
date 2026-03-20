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

# Load configuration
CONFIG = {}
_config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
try:
    with open(_config_path) as f:
        CONFIG = json.load(f)
except Exception:
    CONFIG = {}

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
                    "description": "Timeout in seconds. Defaults to config.web_fetch_timeout_seconds (10)."
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
                },
                "smtp_timeout": {
                    "type": "number",
                    "description": "SMTP connection timeout in seconds (default from config)."
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

def run_web_get(url: str, timeout: float = None) -> str:
    if timeout is None:
        timeout = CONFIG.get('web_fetch_timeout_seconds', 10)
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

def run_send_email_smtp(to: str, subject: str, body: str, smtp_timeout: float = None) -> str:
    try:
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

        if smtp_timeout is None:
            smtp_timeout = email_cfg.get('smtp_timeout_seconds', 10)

        msg = EmailMessage()
        msg["From"] = username
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(smtp_server, smtp_port, timeout=smtp_timeout) as server:
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