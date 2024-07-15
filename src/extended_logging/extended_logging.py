import ast
import logging
import os
import sys
from datetime import datetime
import ecs_logging

import json_log_formatter

from src.extended_logging.const import LogFormat


class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message: str, extra: dict, record: logging.LogRecord) -> dict:
        # Modfify this method to add fields to the log
        extra["message"] = message

        # Include builtins
        extra["level"] = record.levelname
        extra["logger_name"] = record.name

        if "time" not in extra:
            extra["time"] = datetime.utcnow()

        if record.exc_info:
            extra["exc_info"] = self.formatException(record.exc_info)

        return extra


class InvalidLogFormat(Exception):
    pass


def get_logger(logger_name: str = None, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    if logger_name:
        # if we create a named logger set propagate to False to not double any logs since the root logger will print
        # as well
        logger.propagate = False

    if level is not None:
        logger.setLevel(level)
    log_format = LogFormat(os.getenv("LOG_FORMAT", LogFormat.JSON))

    if log_format == LogFormat.JSON and not logger.handlers:
        formatter = CustomisedJSONFormatter()
    elif log_format == LogFormat.BASIC and not logger.handlers:
        formatter = logging.Formatter(logging.BASIC_FORMAT)
    elif log_format == LogFormat.ECS and not logger.handlers:
        formatter = ecs_logging.StdlibFormatter()
    else:
        raise InvalidLogFormat("Invalid log format")

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
