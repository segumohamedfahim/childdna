"""Structured Logging Configuration"""

import json
import logging
import sys
from datetime import UTC, datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON."""
        log_obj = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        if hasattr(record, "extra"):
            log_obj.update(record.extra)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logger() -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger("child_dna")
    logger.setLevel(logging.INFO)

    # Prevent duplicate log messages
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    logger.addHandler(handler)
    logger.propagate = False

    return logger


logger = setup_logger()