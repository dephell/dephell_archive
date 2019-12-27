# built-in
from pathlib import Path

# project
from dephell_archive import ArchivePath


sdist_path = Path(__file__).parent / 'requirements' / 'sdist.tar.gz'


def test_open(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
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
    assert paths[0].as_posix() == 'dephell-0.2.0/setup.py'


def test_glob_dir(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('dephell-*/'))
    assert len(paths) == 1


def test_iterdir(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path
    assert 'dephell-0.2.0' in paths


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
