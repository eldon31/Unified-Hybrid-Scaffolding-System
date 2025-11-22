import logging
import json
import sys
import uuid
import datetime
from typing import Any, Dict

# Global Trace ID
_TRACE_ID = str(uuid.uuid4())

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings fitting the observability/metrics.md spec.
    Schema:
    {
      "level": "INFO | WARN | ERROR",
      "timestamp": "ISO-8601",
      "service": "scaffold-engine",
      "module": "dependency_graph",
      "trace_id": "<correlation_id>",
      "message": "Human readable event description",
      "context": { ... }
    }
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "level": record.levelname,
            "timestamp": datetime.datetime.fromtimestamp(record.created).isoformat(),
            "service": "scaffold-engine",
            "module": record.name,
            "trace_id": _TRACE_ID,
            "message": record.getMessage(),
        }

        # Add context if present in extra fields
        if hasattr(record, "context"):
            log_record["context"] = record.context

        return json.dumps(log_record)

def setup_logging(module_name: str = "root", level: int = logging.INFO):
    """
    Sets up the root logger with JSON formatter.
    This should be called once at the entry point.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    # Remove existing handlers to avoid duplication if called multiple times
    if root.handlers:
        root.handlers = []

    root.addHandler(handler)
    root.setLevel(level)

    return logging.getLogger(module_name)

def get_logger(module_name: str):
    """
    Returns a logger with the given name.
    """
    return logging.getLogger(module_name)
