# built-in
from contextlib import contextmanager, suppress
from pathlib import Path, PurePath
from tarfile import TarFile
from typing import Callable, Iterator, Union
from zipfile import ZipFile

# external
import attr

# app
from ._glob import glob_path
from ._stream import ArchiveStream


EXTRACTORS = {
    '.zip': ZipFile,
    '.whl': ZipFile,
    '.tar': TarFile.taropen,
    '.tar.gz': TarFile.gzopen,
    '.tar.bz2': TarFile.bz2open,
    '.tar.xz': TarFile.xzopen,
}


@attr.s()
class ArchivePath:
    archive_path = attr.ib(type=Path)
    cache_path = attr.ib(type=Path)
    member_path = attr.ib(type=PurePath, factory=PurePath)

    _descriptor = attr.ib(default=None, repr=False)

    # properties

    @property
    def extractor(self) -> Callable:
        extension = ''
        for suffix in reversed(self.archive_path.suffixes):
            extension = suffix + extension
            with suppress(KeyError):
                return EXTRACTORS[extension]
        raise KeyError('Invalid extension: ' + extension)

    @property
    def name(self) -> str:
        return self.member_path.name or self.archive_path.name

    @property
    def parent(self) -> Union['ArchivePath', Path]:
        if self.member_path:
            return self.copy(member_path=self.member_path.parent)
        return self.archive_path

    # context managers

    @contextmanager
    def get_descriptor(self):
        if self._descriptor is not None:
            if hasattr(self._descriptor, 'closed'):
                is_closed = self._descriptor.closed  # tar
            else:
                is_closed = not self._descriptor.fp  # zip
            if not is_closed:
                yield self._descriptor
                return

        with self.extractor(str(self.archive_path)) as descriptor:
            self._descriptor = descriptor
            try:
                yield self._descriptor
            except Exception:
                self._descriptor = None
                raise

    @contextmanager
    def open(self, mode='r'):
        # read from cache
        path = self.cache_path / self.member_path
        if path.exists():
            with path.open() as stream:
                yield stream
        else:
            with self.get_descriptor() as descriptor:
                yield ArchiveStream(
                    descriptor=descriptor,
                    cache_path=self.cache_path,
                    member_path=self.member_path,
                    mode=mode,
                )

    # methods

    def copy(self, **kwargs) -> 'ArchivePath':
        params = attr.asdict(self, recurse=False)
        params.update(kwargs)
        if '_descriptor' in params:
            del params['_descriptor']
        new = type(self)(**params)
        new._descriptor = self._descriptor
        return new

    def iterdir(self, recursive: bool = False) -> Iterator['ArchivePath']:
        with self.get_descriptor() as descriptor:
            if hasattr(descriptor, 'getmembers'):
                members = descriptor.getmembers()   # tar
            else:
                members = descriptor.infolist()     # zip

            # get files
            for member in members:
                name = getattr(member, 'name', None) or member.filename
                yield self.copy(member_path=PurePath(name))

            # get dirs
            names = set()
            for member in members:
                name = getattr(member, 'name', None) or member.filename
                names.add(name)
            dirs = {''}
            for name in names:
                path, _sep, _name = name.rpartition('/')
                if path in dirs or path in names:
                    continue
                dirs.add(path)
                yield self.copy(member_path=PurePath(path))

    def glob(self, pattern: str) -> Iterator['ArchivePath']:
        for path in self.iterdir(recursive=True):
            if glob_path(path=str(path), pattern=pattern):
                yield path

    def exists(self) -> bool:
        path = self.cache_path / self.member_path
        if path.exists():
            return True
        with self.open() as stream:
            return stream.exists()

    def read_bytes(self):
        """
        Open the file in bytes mode, read it, and close the file.
        """
        with self.open(mode='rb') as stream:
            return stream.read()

    def read_text(self):
        """
        Open the file in text mode, read it, and close the file.
        """
        with self.open(mode='r') as stream:
            return stream.read()

    def with_suffix(self, suffix) -> 'ArchivePath':
        return self.copy(member_path=self.member_path.with_suffix(suffix))

    def with_name(self, name) -> 'ArchivePath':
        return self.copy(member_path=self.member_path.with_name(name))

    # magic methods

    def __truediv__(self, part: str) -> 'ArchivePath':
        obj = type(self)(
            archive_path=self.archive_path,
            cache_path=self.cache_path,
            member_path=self.member_path / part,
        )
        obj._descriptor = self._descriptor
        return obj

    def __getattr__(self, name):
        return getattr(self.member_path, name)

    def __str__(self):
        return str(self.member_path)
