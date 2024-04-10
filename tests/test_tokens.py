from rply.token import SourcePosition, Token


class TestTokens(object):
    def test_source_pos(self):
        t = Token("VALUE", "3", SourcePosition(5, 2, 1))
        pos = t.get_position()
        assert pos is not None
        assert pos.line == 2

    def test_eq(self):
        t = Token("VALUE", "3", SourcePosition(-1, -1, -1))
        assert not (t == 3)
        assert t != 3


class TestSourcePosition(object):
    def test_source_pos(self):
        sp = SourcePosition(1, 2, 3)
        assert sp.index == 1
        assert sp.line == 2
        assert sp.column == 3
