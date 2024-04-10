import re

from pytest import raises

from rply import LexerGenerator, LexingError


class TestLexer:
    def test_simple(self):
        lg = LexerGenerator()
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")

        lexer = lg.build()

        stream = lexer.lex("2+3")
        t = stream.next()
        assert t.name == "NUMBER"
        assert t.value == "2"
        t = stream.next()
        assert t.name == "PLUS"
        assert t.value == "+"
        t = stream.next()
        assert t.name == "NUMBER"
        assert t.value == "3"
        assert t.position is not None
        assert t.position.index == 2

        with raises(StopIteration):
            stream.next()

    def test_ignore(self):
        lg = LexerGenerator()
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")
        lg.ignore(r"\s+")

        lexer = lg.build()

        stream = lexer.lex("2 + 3")
        t = stream.next()
        assert t.name == "NUMBER"
        assert t.value == "2"
        t = stream.next()
        assert t.name == "PLUS"
        assert t.value == "+"
        t = stream.next()
        assert t.name == "NUMBER"
        assert t.value == "3"
        assert t.position is not None
        assert t.position.index == 4

        with raises(StopIteration):
            stream.next()

    def test_position(self):
        lg = LexerGenerator()
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")
        lg.ignore(r"\s+")

        lexer = lg.build()

        stream = lexer.lex("2 + 3")
        t = stream.next()
        assert t.position is not None
        assert t.position.line == 1
        assert t.position.column == 1
        t = stream.next()
        assert t.position is not None
        assert t.position.line == 1
        assert t.position.column == 3
        t = stream.next()
        assert t.position is not None
        assert t.position.line == 1
        assert t.position.column == 5
        with raises(StopIteration):
            stream.next()

        stream = lexer.lex("2 +\n    37")
        t = stream.next()
        assert t.position is not None
        assert t.position.line == 1
        assert t.position.column == 1
        t = stream.next()
        assert t.position is not None
        assert t.position.line == 1
        assert t.position.column == 3
        t = stream.next()
        assert t.position is not None
        assert t.position.line == 2
        assert t.position.column == 5
        with raises(StopIteration):
            stream.next()

    def test_newline_position(self):
        lg = LexerGenerator()
        lg.add("NEWLINE", r"\n")
        lg.add("SPACE", r" ")

        lexer = lg.build()

        stream = lexer.lex(" \n ")
        t = stream.next()
        assert t.position is not None
        assert t.position.line == 1
        assert t.position.column == 1
        t = stream.next()
        assert t.position is not None
        assert t.position.line == 1
        assert t.position.column == 2
        t = stream.next()
        assert t.position is not None
        assert t.position.line == 2
        assert t.position.column == 1

    def test_regex_flags(self):
        lg = LexerGenerator()
        lg.add("ALL", r".*", re.DOTALL)

        lexer = lg.build()

        stream = lexer.lex("test\ndotall")
        t = stream.next()
        assert t.position is not None
        assert t.position.line == 1
        assert t.position.column == 1
        assert t.get_value() == "test\ndotall"

        with raises(StopIteration):
            stream.next()

    def test_regex_flags_ignore(self):
        lg = LexerGenerator()
        lg.add("ALL", r".*", re.DOTALL)
        lg.ignore(r".*", re.DOTALL)

        lexer = lg.build()

        stream = lexer.lex("test\ndotall")

        with raises(StopIteration):
            stream.next()

    def test_ignore_recursion(self):
        lg = LexerGenerator()
        lg.ignore(r"\s")

        lexer = lg.build()

        assert list(lexer.lex(" " * 2000)) == []

    def test_error(self):
        lg = LexerGenerator()
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")

        lexer = lg.build()

        stream = lexer.lex("fail")
        with raises(LexingError) as excinfo:
            stream.next()

        assert "SourcePosition(" in repr(excinfo.value)

    def test_error_line_number(self):
        lg = LexerGenerator()
        lg.add("NEW_LINE", r"\n")
        lexer = lg.build()

        stream = lexer.lex("\nfail")
        stream.next()
        with raises(LexingError) as excinfo:
            stream.next()

        assert excinfo.value.source_position.line == 2

    def test_error_column_number(self):
        lg = LexerGenerator()
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")
        lexer = lg.build()
        stream = lexer.lex("1+2+fail")
        stream.next()
        stream.next()
        stream.next()
        stream.next()
        with raises(LexingError) as excinfo:
            stream.next()

        assert excinfo.value.source_position.column == 4
