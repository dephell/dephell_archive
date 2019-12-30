# built-in
from contextlib import suppress
from pathlib import Path, PurePath
from typing import List, Optional, Set

# external
import attr

# app
from ._cached_property import cached_property


def _dir_list(filelist: List[str]) -> Set[str]:
    # paths starting with '/' or containing '.' are not supported
    dir_list = set()  # type: Set[str]
    for path in filelist:
        while path:
            path, _, _ = path.rpartition('/')
            if not path or path in dir_list:
                break
            dir_list.add(path)
    return dir_list


@attr.s()
class ArchiveStream:
    descriptor = attr.ib()
    cache_path = attr.ib(type=Path)
    member_path = attr.ib(type=PurePath)

    mode = attr.ib(type=str, default='r')
    encoding = attr.ib(type=Optional[str], default=None)

    # private

    @cached_property
    def _is_tar(self) -> bool:
        return hasattr(self.descriptor, 'getmember')

    @cached_property
    def _dir_list(self) -> Set[str]:
        return _dir_list(self.descriptor.namelist())

    @cached_property
    def _info(self):
        path = self.member_path.as_posix()
        with suppress(KeyError):
            if self._is_tar:
                return self.descriptor.getmember(path)
            try:
                return self.descriptor.getinfo(path)  # zip file
            except KeyError:
                return self.descriptor.getinfo(path + '/')  # zip dir
        return None

    @cached_property
    def _is_implicit_dir(self) -> bool:
        # Only zip have implicit dirs
        if self._is_tar:
            return False
        path = self.member_path.as_posix()
        return path in self._dir_list

    # used from ArchivePath

    def exists(self) -> bool:
        return self.is_file() or self.is_dir()

    def is_file(self) -> bool:
        if self._info is None:
            return False
        if self._is_tar:
            return self._info.isfile()
        # zip
        return self._info.filename[-1] != '/'

    def is_dir(self) -> bool:
        if self._info is None:
            return self._is_implicit_dir
        if self._is_tar:
            return self._info.isdir()
        # zip explicit dir entry
        return self._info.filename[-1] == '/'

    # public interface

    def read(self):
        if not self.member_path.name:
            raise NotImplementedError

        path = self.cache_path / self.member_path
        if path.exists():
            raise FileExistsError('file in cache created between open and read')

        # extract to cache
        self.descriptor.extract(member=self._info, path=str(self.cache_path))

        # read from cache
        with path.open(self.mode, encoding=self.encoding) as stream:
            return stream.read()
