import contextvars
import logging
from logging.config import dictConfig

user_for_logs_var = contextvars.ContextVar("email", default="anonym or system")

class UserLoggingFilter(logging.Filter):
    def filter(self, record):
        record.username = user_for_logs_var.get()
        return True


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "user_filter": {
            "()": UserLoggingFilter,
        },
    },
    "formatters": {
        "default": {
            "format": "[%(asctime)s] —  %(name)s — %(username)s. %(levelname)s: %(message)s.",
            "datefmt": '%d-%m-%Y, %H:%M:%S',
        },
        "access": {
            "format": "[%(asctime)s] —  %(levelname)s. '%(request_line)s': %(status_code)s",
            "datefmt": '%d-%m-%Y, %H:%M:%S',
        },
    },
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "filters": ["user_filter"],
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/myapp.log",
            "mode": "a",
            "maxBytes": 10 * 1024 * 1024 * 8,
            "backupCount": 5,
            "encoding": "utf-8",
            "filters": ["user_filter"],
        },
    },
    "loggers": {
        "console_logger": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "file_logger": {"handlers": ["file"], "level": "WARNING", "propagate": False},
        "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["console"], "level": "INFO"},
        "uvicorn.access": {"handlers": ["console"], "level": "INFO"},
    },
}

dictConfig(LOGGING_CONFIG)
debug_logger = logging.getLogger("console_logger")