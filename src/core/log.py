import logging
import sys

from loguru import logger

from src.config.settings import Settings


class InterceptHandler(logging.Handler):
    """
    Redirect standard logging (uvicorn, fastapi, etc.)
    into Loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where logging originated
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info,
        ).log(level, record.getMessage())


def setup_logging(settings: Settings) -> None:
    log_level = logging.DEBUG if settings.debug else logging.INFO

    logger.remove()

    is_prod = settings.env == "prod"

    # Console
    logger.add(
        sys.stderr,
        level=log_level,
        serialize=is_prod,
        format="{message}"
        if is_prod
        else (
            "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | "
            "{module}:{function}:{line} - {message} | {extra}"
        ),
    )

    # File (JSON)
    logger.add(
        "app.log", level=log_level, serialize=True, rotation="10 MB", retention="7 days"
    )

    logger.configure(
        extra={
            "service": settings.service_name,
            "env": settings.env,
        }
    )

    intercept_handler = InterceptHandler()

    for name in logging.root.manager.loggerDict:
        if name.startswith(("uvicorn", "fastapi", "watchfiles")):
            log = logging.getLogger(name)
            log.handlers = [intercept_handler]
            log.propagate = False
            log.setLevel(log_level)

    logging.getLogger("uvicorn.access").disabled = True
