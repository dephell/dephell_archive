# built-in
from pathlib import Path

# project
from dephell_archive import ArchivePath

wheel_path = Path(__file__).parent / 'requirements' / 'wheel.whl'


def test_open_zip(tmpdir):
    path = ArchivePath(
        archive_path=wheel_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell' / '__init__.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from .controllers' in content


def test_glob_zip(tmpdir):
    path = ArchivePath(
        archive_path=wheel_path,
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('*/__init__.py'))
    assert len(paths) == 1
    assert paths[0].as_posix() == 'dephell/__init__.py'


def test_exists(tmpdir):
    path = ArchivePath(
        archive_path=wheel_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell' / '__init__.py'
    assert subpath.exists() is True

    subpath = path / 'dephell' / 'some_junk.py'
    assert subpath.exists() is False


def test_is_file(tmpdir):
    path = ArchivePath(
        archive_path=wheel_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell' / '__init__.py'
    assert subpath.is_file() is True

    subpath = path / 'dephell'
    assert subpath.is_file() is False


def test_is_dir(tmpdir):
    path = ArchivePath(
        archive_path=wheel_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell' / '__init__.py'
    assert subpath.is_dir() is False

    subpath = path / 'dephell'
    # assert subpath.is_dir() is True
