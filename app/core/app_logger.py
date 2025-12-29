import logging
import sys

logger = logging.getLogger("app")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Make sure every log record has request_id so the formatter never crashes
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def setup_logging() -> None:
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s request_id=%(request_id)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)

    # Avoid duplicate handlers during reload
    logger.handlers.clear()
    logger.addHandler(handler)

    # Optional: stop logs from being printed twice
    logger.propagate = False