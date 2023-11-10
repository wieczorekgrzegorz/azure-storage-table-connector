"""custom error class for azure storage table operations"""
import logging

log = logging.getLogger(name="log." + __name__)


class TableOperationsError(Exception):
    """Base class for exceptions in this module."""

    message: str
    summary: str
    repr: str

    def __init__(self, summary: str, message: str) -> None:
        self.summary = summary
        self.message = message
        self.repr = f"{self.summary}: {self.message}"
        super().__init__(self.message)
        log.exception(msg=self.repr, stacklevel=2)

    def __repr__(self) -> str:
        return self.repr
