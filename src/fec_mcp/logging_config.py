
import logging
import sys
import os
from logging.handlers import RotatingFileHandler


class SecretFilter(logging.Filter):
    """Masks API key and other secrets from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        api_key = os.getenv("FEC_API_KEY")
        if api_key and api_key in record.getMessage():
            # Collapse args into msg so replacement is safe
            record.msg = record.getMessage().replace(api_key, "***REDACTED***")
            record.args = ()
        return True


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging for the application."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "fec_mcp.log")

    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    secret_filter = SecretFilter()

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter(fmt))
    stderr_handler.addFilter(secret_filter)

    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(fmt))
    file_handler.addFilter(secret_filter)

    logging.basicConfig(level=level, handlers=[stderr_handler, file_handler])

    # Quiet down httpx noise
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
