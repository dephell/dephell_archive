# external
import pytest

# project
from dephell_archive._stream import _dir_list


@pytest.mark.parametrize('paths, results', [
    ([], []),
    ([''], []),
    (['foo'], []),
    (['foo', 'bar'], []),
    (['/'], []),
    (['foo/'], ['foo']),
    (['foo/', 'foo/'], ['foo']),
    (['foo/bar'], ['foo']),
    (['foo', 'foo/bar'], ['foo']),
    (['foo/bar', 'foo/bar'], ['foo']),
    (['foo/bar', 'baz/lol'], ['foo', 'baz']),
    (['foo/bar', 'baz/lol', 'foo/bar'], ['foo', 'baz']),
    (['foo/bar/baz'], ['foo', 'foo/bar']),
    (['foo/bar/baz/a'], ['foo', 'foo/bar', 'foo/bar/baz']),
])
def test_dir_list(paths, results):
    assert _dir_list(filelist=paths) == set(results)
