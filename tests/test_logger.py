from app.logger import _make_console_safe


class _StreamWithoutReconfigure:
    pass


class _ReconfigureStream:
    def __init__(self, fail: bool = False):
        self.calls = []
        self.fail = fail

    def reconfigure(self, **kwargs):
        if self.fail:
            raise ValueError("not supported")
        self.calls.append(kwargs)


def test_console_safe_ignores_streams_without_reconfigure():
    _make_console_safe(_StreamWithoutReconfigure())


def test_console_safe_replaces_unencodable_characters():
    stream = _ReconfigureStream()

    _make_console_safe(stream)

    assert stream.calls == [{"errors": "replace"}]


def test_console_safe_swallows_reconfigure_errors():
    _make_console_safe(_ReconfigureStream(fail=True))
