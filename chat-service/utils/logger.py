import logging
import os

log_level = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logger():
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=getattr(logging, log_level, logging.INFO),
    )
