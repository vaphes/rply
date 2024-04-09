import contextlib
import warnings


class BaseTests(object):
    @contextlib.contextmanager
    def assert_warns(self, cls, message):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            yield
        assert len(w) == 1
        assert w[0].category is cls
        if isinstance(w[0].message, str):
            assert w[0].message == message
        else:
            assert w[0].message.args[0] == message
