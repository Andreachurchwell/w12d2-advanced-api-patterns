from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG_PATH = Path("audit.log")

def write_audit_log(message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    AUDIT_LOG_PATH.write_text(
        AUDIT_LOG_PATH.read_text() + f"{timestamp} | {message}\n"
        if AUDIT_LOG_PATH.exists()
        else f"{timestamp} | {message}\n"
    )