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
    assert subpath.exists() is True
    assert subpath.is_dir() is True


def test_is_dir_explicit_entry(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'graphviz-0.13.2.zip'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'graphviz-0.13.2'
    assert subpath.is_dir() is True

    subpath = subpath / 'graphviz'
    assert subpath.exists() is True
    assert subpath.is_dir() is True

    subpath = subpath / '__init__.py'
    assert subpath.is_dir() is False


def test_iterdir_non_recursive(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'dnspython-1.16.0.zip'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(_recursive=False)]
    assert paths == ['dnspython-1.16.0']


def test_iterdir_recursive(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'dnspython-1.16.0.zip'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(_recursive=True)]

    assert 'dnspython-1.16.0' in paths
    assert str(Path('dnspython-1.16.0', 'setup.py')) in paths
    assert str(Path('dnspython-1.16.0', 'dns', '__init__.py')) in paths
    assert str(Path('dnspython-1.16.0', 'dns', 'rdtypes')) in paths
    assert str(Path('dnspython-1.16.0', 'dns', 'rdtypes', 'ANY')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_subpath_non_recursive(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'dnspython-1.16.0.zip'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dnspython-1.16.0'
    paths = [str(item) for item in subpath.iterdir(_recursive=False)]

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path

    assert 'dns' in paths
    assert 'dnspython.egg-info' in paths
    assert 'setup.py' in paths

    subpath = subpath / 'dns'
    paths = [str(item) for item in subpath.iterdir(_recursive=False)]
    assert 'rdtypes' in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_subpath_recursive(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'dnspython-1.16.0.zip'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dnspython-1.16.0'
    paths = [str(item) for item in subpath.iterdir(_recursive=True)]

    assert 'setup.py' in paths
    assert Path('dnspython-1.16.0', 'dns') not in paths
    assert 'dns' in paths
    assert str(Path('dns', '__init__.py')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_non_recursive_with_dirs(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'graphviz-0.13.2.zip'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(_recursive=False)]
    assert paths == ['graphviz-0.13.2']


def test_iterdir_recursive_with_dirs(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'graphviz-0.13.2.zip'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(_recursive=True)]

    assert 'graphviz-0.13.2' in paths
    assert str(Path('graphviz-0.13.2', 'setup.py')) in paths
    assert str(Path('graphviz-0.13.2', 'graphviz', '__init__.py')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_subpath_non_recursive_with_dirs(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'graphviz-0.13.2.zip'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'graphviz-0.13.2'
    paths = [str(item) for item in subpath.iterdir(_recursive=False)]
    assert 'graphviz' in paths
    assert 'graphviz.egg-info' in paths
    assert 'setup.py' in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path

    subpath = subpath / 'graphviz.egg-info'
    paths = [str(item) for item in subpath.iterdir(_recursive=False)]

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path

    assert set(paths) == {
        'dependency_links.txt',
        'PKG-INFO',
        'requires.txt',
        'SOURCES.txt',
        'top_level.txt',
    }


def test_iterdir_subpath_recursive_with_dirs(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'graphviz-0.13.2.zip'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'graphviz-0.13.2'
    paths = [str(item) for item in subpath.iterdir(_recursive=True)]

    assert 'graphviz' in paths
    assert str(Path('graphviz', '__init__.py')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_non_recursive_wheel(tmpdir):
    path = ArchivePath(
        archive_path=wheel_path,
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(_recursive=False)]
    assert len(paths) == 2
    assert 'dephell' in paths
    assert 'dephell-0.2.0.dist-info' in paths


def test_iterdir_recursive_wheel(tmpdir):
    path = ArchivePath(
        archive_path=wheel_path,
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(_recursive=True)]

    assert 'dephell' in paths
    assert str(Path('dephell', '__init__.py')) in paths
    assert 'dephell-0.2.0.dist-info' in paths
    assert str(Path('dephell-0.2.0.dist-info', 'WHEEL')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path
