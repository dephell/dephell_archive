from contextlib import suppress
from pathlib import Path, PurePath
from typing import Optional, List, Set

# external
import attr

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
    _dir_list = attr.ib(default=None)

    # private

    @cached_property
    def _is_tar(self) -> bool:
        return hasattr(self.descriptor, 'getmember')

    def _get_info(self):
        path = self.member_path.as_posix()
        with suppress(KeyError):
            if self._is_tar:
                return self.descriptor.getmember(path)
            try:
                return self.descriptor.getinfo(path)  # zip file
            except KeyError:
                return self.descriptor.getinfo(path + '/')  # zip dir
        return None

    def _is_implicit_dir(self) -> bool:
        # Only zip have implicit dirs
        if self._is_tar:
            return False
        if self._dir_list is None:
            self._dir_list = _dir_list(self.descriptor.namelist())
        path = self.member_path.as_posix()
        return path in self._dir_list

    # used from ArchivePath

    def exists(self) -> bool:
        return self.is_file() or self.is_dir()

    def is_file(self) -> bool:
        info = self._get_info()
        if info is None:
            return False
        if self._is_tar:
            return info.isfile()
        # zip
        return info.filename[-1] != '/'

    def is_dir(self) -> bool:
        info = self._get_info()
        if info is None:
            return self._is_implicit_dir()
        if self._is_tar:
            return info.isdir()
        # zip explicit dir entry
        return info.filename[-1] == '/'

    # public interface

    def read(self):
        if not self.member_path.name:
            raise NotImplementedError

        path = self.cache_path / self.member_path
        if path.exists():
            raise FileExistsError('file in cache created between open and read')

        # extract to cache
        if self._is_tar:
            member = self.descriptor.getmember(self.member_path.as_posix())
        else:
            member = self.descriptor.getinfo(self.member_path.as_posix())
        self.descriptor.extract(member=member, path=str(self.cache_path))

        # read from cache
        with path.open(self.mode, encoding=self.encoding) as stream:
            return stream.read()
