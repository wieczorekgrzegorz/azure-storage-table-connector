"""custom error class for azure storage table operations"""
import logging

log = logging.getLogger(name="log." + __name__)


class TableOperationsError(Exception):
    """Base class for exceptions in this module."""

    message: str
    summary: str
    string: str

    def __init__(self, summary: str, message: str) -> None:
        self.summary = summary
        self.message = message
        self.string = f"{self.summary}: {self.message}"
        log.error(msg=self.string, stacklevel=2)

    def __repr__(self) -> str:
        return f"TableOperationsError(summary={self.summary}, message={self.message})"

    def __str__(self) -> str:
        return self.string
