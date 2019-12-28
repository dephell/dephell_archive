# built-in
from pathlib import Path

# external
import pytest

# project
from dephell_archive import ArchivePath


sdist_path = Path(__file__).parent / 'requirements' / 'sdist.tar.gz'


def test_toplevel(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    assert path.is_dir()
    assert not path.is_file()
    assert path.exists()

    with pytest.raises(IsADirectoryError):
        with path.open():
            pass


def test_toplevel_missing_cache_path(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir), 'missing'),
    )
    assert path.is_dir()
    assert not path.is_file()
    assert path.exists()

    with pytest.raises(IsADirectoryError):
        with path.open():
            pass

    with pytest.raises(NotImplementedError):
        with path.open('w'):
            pass


def test_open(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from setuptools import' in content


def test_open_write(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0'
    with pytest.raises(NotImplementedError):
        with subpath.open('w'):
            pass


def test_open_missing_cache_path(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir), 'missing'),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from setuptools import' in content


def test_glob(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('*/setup.py'))
    assert len(paths) == 1
    assert paths[0].member_path.as_posix() == 'dephell-0.2.0/setup.py'


def test_glob_dir(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('dephell-*/'))
    assert len(paths) == 1


def test_iterdir_non_recursive_tarball(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(_recursive=False)]
    assert paths == ['dephell-0.2.0']


def test_iterdir_recursive_tarball(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(_recursive=True)]

    assert 'dephell-0.2.0' in paths
    assert str(Path('dephell-0.2.0', 'setup.py')) in paths
    assert str(Path('dephell-0.2.0', 'dephell', '__init__.py')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_subpath_non_recursive(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0'
    paths = set(str(item) for item in subpath.iterdir(_recursive=False))
    assert paths == {
        'dephell',
        'dephell.egg-info',
        'PKG-INFO',
        'README.md',
        'setup.cfg',
        'setup.py',
    }
    subpath = subpath / 'dephell.egg-info'
    paths = set(str(item) for item in subpath.iterdir(_recursive=False))
    assert paths == {
        'dependency_links.txt',
        'entry_points.txt',
        'PKG-INFO',
        'requires.txt',
        'SOURCES.txt',
        'top_level.txt',
    }


def test_iterdir_subpath_recursive(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0'
    paths = [str(item) for item in subpath.iterdir(_recursive=True)]

    assert 'dephell' in paths
    assert str(Path('dephell', '__init__.py')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_exists(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    assert subpath.exists() is True

    subpath = path / 'dephell-0.2.0' / 'not-a-setup.py'
    assert subpath.exists() is False


def test_is_file(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    assert subpath.is_file() is True

    subpath = path / 'dephell-0.2.0'
    assert subpath.is_file() is False


def test_is_dir(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    assert subpath.is_dir() is False

    subpath = path / 'dephell-0.2.0'
    assert subpath.is_dir() is True
