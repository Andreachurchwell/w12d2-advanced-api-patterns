import logging
import sys

LOG_FORMAT = (
    "%(asctime)s %(levelname)s %(name)s %(message)s request_id=%(request_id)s"
)

class SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return super().format(record)

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(SafeFormatter(LOG_FORMAT))

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # clear any existing handlers (uvicorn reload can stack handlers)
    root.handlers.clear()
    root.addHandler(handler)

logger = logging.getLogger("watchlist-api")