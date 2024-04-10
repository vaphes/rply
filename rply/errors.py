from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rply.token import SourcePosition


class ParserGeneratorError(Exception):
    pass


class LexingError(Exception):
    """
    Raised by a Lexer, if no rule matches.
    """

    def __init__(self, message: str, source_position: SourcePosition):
        self.message = message
        self.source_position = source_position

    def getsourcepos(self):
        """
        Returns the position in the source, at which this error occurred.
        """
        return self.source_position

    def __repr__(self):
        return f"LexingError({self.message}, {self.source_position})"


class ParsingError(Exception):
    """
    Raised by a Parser, if no production rule can be applied.
    """

    def __init__(self, message: str, source_position: SourcePosition | None = None):
        self.message = message
        self.source_position = source_position

    def getsourcepos(self):
        """
        Returns the position in the source, at which this error occurred.
        """
        return self.source_position

    def __repr__(self):
        return f"ParsingError({self.message}, {self.source_position})"


class ParserGeneratorWarning(Warning):
    pass
