from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rply.errors import LexingError
from rply.token import SourcePosition, Token

if TYPE_CHECKING:
    from rply.lexergenerator import Match, Rule


@dataclass
class Lexer:
    rules: list[Rule]
    ignore_rules: list[Rule]

    def lex(self, s: str):
        return LexerStream(self, s)


class LexerStream:
    def __init__(self, lexer: Lexer, s: str):
        self.lexer = lexer
        self.s = s
        self.idx = 0

        self._lineno = 1
        self._colno = 1

    def __iter__(self):
        return self

    def _update_pos(self, match: Match):
        self.idx = match.end
        self._lineno += self.s.count("\n", match.start, match.end)
        last_nl = self.s.rfind("\n", 0, match.start)
        if last_nl < 0:
            return match.start + 1
        else:
            return match.start - last_nl

    def next(self):
        while True:
            if self.idx >= len(self.s):
                raise StopIteration
            for rule in self.lexer.ignore_rules:
                match = rule.matches(self.s, self.idx)
                if match is not None:
                    self._update_pos(match)
                    break
            else:
                break

        for rule in self.lexer.rules:
            match = rule.matches(self.s, self.idx)
            if match is not None:
                lineno = self._lineno
                self._colno = self._update_pos(match)
                source_pos = SourcePosition(match.start, lineno, self._colno)
                token = Token(rule.name, self.s[match.start : match.end], source_pos)
                return token
        else:
            raise LexingError("", SourcePosition(self.idx, self._lineno, self._colno))

    def __next__(self):
        return self.next()
