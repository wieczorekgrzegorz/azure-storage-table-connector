"""Holds environmental variables and function app constants. Sets up custom logger."""

import logging
import os

log = logging.getLogger(name="log")

# declare environment constants
STORAGE_TABLE_CONNECTION_STRING: str = os.environ["STORAGE_TABLE_CONNECTION_STRING"]


ALLOWED_OPERATIONS = [
    "delete",
    "get",
    "get_all",
    "insert",
    "reset",
    "update",
    "upsert",
]
ALLOWED_TABLE_NAMES = ["ClientRules", "ClientConfig", "SessionTokens"]


def logger(
    logging_format: str = "%(levelname)s, %(name)s.%(funcName)s: %(message)s",
    level: int = logging.INFO,
) -> None:
    """
    Sets up custom logger.

    Parameters:
        format (str, optional): Logging format. Defaults to "%(name)s%(funcName)s: %(message)s".
        level (int, optional): Logging level. Defaults to logging.INFO.

    Returns:
        None
    """
    log.debug(msg="Setting up custom logger.")

    log.setLevel(level=level)

    handler = logging.StreamHandler(stream=None)

    formatter = logging.Formatter(fmt=logging_format)
    handler.setFormatter(fmt=formatter)

    if log.hasHandlers():
        log.handlers.clear()

    log.addHandler(hdlr=handler)
