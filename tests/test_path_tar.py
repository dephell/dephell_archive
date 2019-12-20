# built-in
from pathlib import Path

# project
from dephell_archive import ArchivePath


def test_open_tar(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from setuptools import' in content


def test_glob_tar(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('*/setup.py'))
    assert len(paths) == 1
    assert paths[0].as_posix() == 'dephell-0.2.0/setup.py'


def test_glob_dir_tar(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('dephell-*/'))
    assert len(paths) == 1


def test_iterdir_tar(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path
    assert 'dephell-0.2.0' in paths


def test_exists_tar(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    path = path / 'dephell-0.2.0' / 'setup.py'
    assert path.exists() is True

    path = path / 'dephell-0.2.0' / 'not-a-setup.py'
    assert path.exists() is False
