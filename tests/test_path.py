# built-in
from pathlib import Path

# project
from dephell_archive import ArchivePath


def test_open_zip(tmpdir, requirements_path: Path):
    path = ArchivePath(
        archive_path=requirements_path / 'wheel.whl',
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell' / '__init__.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from .controllers' in content


def test_open_tar_gz(tmpdir, requirements_path: Path):
    path = ArchivePath(
        archive_path=requirements_path / 'sdist.tar.gz',
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from setuptools import' in content


def test_glob_zip(tmpdir, requirements_path: Path):
    path = ArchivePath(
        archive_path=requirements_path / 'wheel.whl',
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('*/__init__.py'))
    assert len(paths) == 1
    assert paths[0].as_posix() == 'dephell/__init__.py'


def test_glob_tar(tmpdir, requirements_path: Path):
    path = ArchivePath(
        archive_path=requirements_path / 'sdist.tar.gz',
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('*/setup.py'))
    assert len(paths) == 1
    assert paths[0].as_posix() == 'dephell-0.2.0/setup.py'


def test_glob_dir(tmpdir, requirements_path: Path):
    path = ArchivePath(
        archive_path=requirements_path / 'sdist.tar.gz',
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('dephell-*/'))
    assert len(paths) == 1


def test_iterdir(tmpdir, requirements_path: Path):
    path = ArchivePath(
        archive_path=requirements_path / 'sdist.tar.gz',
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path
    assert 'dephell-0.2.0' in paths
