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
    assert paths[0].member_path.as_posix() == 'dephell/__init__.py'


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


def test_iterdir_recursive_zip(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'dnspython-1.16.0.zip'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    assert 'dnspython-1.16.0' in paths
    assert str(Path('dnspython-1.16.0', 'setup.py')) in paths
    assert str(Path('dnspython-1.16.0', 'dns', '__init__.py')) in paths
    assert str(Path('dnspython-1.16.0', 'dns', 'rdtypes')) in paths
    assert str(Path('dnspython-1.16.0', 'dns', 'rdtypes', 'ANY')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_recursive_zip_with_dirs(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'graphviz-0.13.2.zip'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    assert 'graphviz-0.13.2' in paths
    assert str(Path('graphviz-0.13.2', 'setup.py')) in paths
    assert str(Path('graphviz-0.13.2', 'graphviz', '__init__.py')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_recursive_wheel(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'wheel.whl'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    assert 'dephell' in paths
    assert str(Path('dephell', '__init__.py')) in paths
    assert 'dephell-0.2.0.dist-info' in paths
    assert str(Path('dephell-0.2.0.dist-info', 'WHEEL')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path
