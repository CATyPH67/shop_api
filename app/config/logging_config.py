from datetime import datetime
import logging
from logging.config import dictConfig
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": JsonFormatter}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "/app/logs/shop_api.log",
            "maxBytes": 10485760,  # 10 мб
            "backupCount": 5,
        },
    },
    "loggers": {
        "shop_api": {
            "handlers": ["console", "rotating_file"],
            "level": "DEBUG", 
            "propagate": False
        },
    },
    "root": {
        "handlers": ["console"], "level": "DEBUG"
    },
}

dictConfig(log_config)

logger = logging.getLogger("shop_api")