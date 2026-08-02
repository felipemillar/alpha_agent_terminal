import logging
import sys

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # Always output to stderr so stdout can be used purely for JSON output
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
