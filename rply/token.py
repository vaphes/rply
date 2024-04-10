from dataclasses import dataclass, field


@dataclass
class SourcePosition:
    """
    Represents the position of a character in some source string.

    :param index: The index of the character in the source.
    :param line: The number of the line in which the character occurs.
    :param column: The number of the column in which the character occurs.

    The values passed to this object can be retrieved using the identically
    named attributes.
    """

    index: int
    line: int
    column: int


@dataclass
class Token:
    """
    Represents a syntactically relevant piece of text.

    :param name: A string describing the kind of text represented.
    :param value: The actual text represented.
    :param position: A :class:`SourcePosition` object representing the
                       position of the first character in the source from which
                       this token was generated.
    """

    name: str
    value: str
    position: SourcePosition | None = field(default=None, repr=False)

    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return self.name == other.name and self.value == other.value
