from dataclasses import dataclass, field


@dataclass
class SourcePosition:
    """
    Represents the position of a character in some source string.

    :param idx: The index of the character in the source.
    :param lineno: The number of the line in which the character occurs.
    :param colno: The number of the column in which the character occurs.

    The values passed to this object can be retrieved using the identically
    named attributes.
    """

    idx: int
    lineno: int
    colno: int


@dataclass
class Token:
    """
    Represents a syntactically relevant piece of text.

    :param name: A string describing the kind of text represented.
    :param value: The actual text represented.
    :param source_pos: A :class:`SourcePosition` object representing the
                       position of the first character in the source from which
                       this token was generated.
    """

    name: str
    value: str
    source_pos: SourcePosition | None = field(default=None, repr=False)

    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return self.name == other.name and self.value == other.value

    def gettokentype(self):
        """
        Returns the type or name of the token.
        """
        return self.name

    def getsourcepos(self):
        """
        Returns a :class:`SourcePosition` instance, describing the position of
        this token's first character in the source.
        """
        return self.source_pos

    def getstr(self):
        """
        Returns the string represented by this token.
        """
        return self.value
