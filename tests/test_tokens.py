from rply.token import SourcePosition, Token


class TestTokens(object):
    def test_source_pos(self):
        t = Token("VALUE", "3", SourcePosition(5, 2, 1))
        pos = t.getsourcepos()
        assert pos is not None
        assert pos.lineno == 2

    def test_eq(self):
        t = Token("VALUE", "3", SourcePosition(-1, -1, -1))
        assert not (t == 3)
        assert t != 3


class TestSourcePosition(object):
    def test_source_pos(self):
        sp = SourcePosition(1, 2, 3)
        assert sp.idx == 1
        assert sp.lineno == 2
        assert sp.colno == 3
