# external
import pytest

# project
from dephell_archive._glob import glob_path


@pytest.mark.parametrize("path,pattern,ok", [
    ('/lol/', '/lol/', True),
    ('/lol/', '/lal/', False),

    ('lol', '/lol/', True),
    ('lol', '/lal/', False),

    ('/lol/', '/l*', True),
    ('/tol/', '/l*', False),
    ('l', '/l*', True),
    ('lal', '/l*t', False),

    ('lol/lal', '*/lal', True),

    ('lol/lal', '**/lal', True),
    ('lol/lal', 'lol/**', True),
    ('lol/lal', 'lal/**', False),
])
def test_glob_path(path, pattern, ok):
    assert glob_path(path=path, pattern=pattern) is ok
