import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        level: str | int

        try:
            level: str = logger.level(record.levelname).name
        except ValueError:
            level: int = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(debug: bool = False, env: str = "dev") -> None:
    logger.remove()
    logger.add(sys.stderr, serialize=env == "dev")
    log_level = logging.DEBUG if debug else logging.INFO

    for name in logging.root.manager.loggerDict:
        if name in ("uvicorn", "watchfiles"):
            uvicorn_logger = logging.getLogger(name)
            uvicorn_logger.handlers.clear()
            uvicorn_logger.setLevel(log_level)
            uvicorn_logger.addHandler(InterceptHandler())
