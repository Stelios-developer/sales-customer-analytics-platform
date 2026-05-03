import logging
import sys
from app.core.config import settings


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("sales_analytics")
    logger.setLevel(logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = configure_logging()
