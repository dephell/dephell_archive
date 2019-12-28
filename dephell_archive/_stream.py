from contextlib import suppress
from pathlib import Path, PurePath
from typing import Optional

# external
import attr


@attr.s(slots=True)
class ArchiveStream:
    descriptor = attr.ib()
    cache_path = attr.ib(type=Path)
    member_path = attr.ib(type=PurePath)

    mode = attr.ib(type=str, default='r')
    encoding = attr.ib(type=Optional[str], default=None)

    def _get_info(self):
        path = self.member_path.as_posix()
        with suppress(KeyError):
            if hasattr(self.descriptor, 'getmember'):
                return self.descriptor.getmember(path)  # tar
            try:
                return self.descriptor.getinfo(path)  # zip file
            except KeyError:
                return self.descriptor.getinfo(path + '/')  # zip dir
        return None

    def exists(self) -> bool:
        return self.is_file() or self.is_dir()

    def is_file(self) -> bool:
        info = self._get_info()
        if info is None:
            return False
        # tar
        if hasattr(info, 'isfile'):
            return info.isfile()
        # zip
        return info.filename[-1] != '/'

    def _is_implicit_dir(self) -> bool:
        # Only zip have implicit dirs
        if not hasattr(self.descriptor, 'getinfo'):
            return False
        path = self.member_path.as_posix() + '/'
        for filename in self.descriptor.namelist():
            if filename.startswith(path):
                return True
        return False

    def is_dir(self) -> bool:
        info = self._get_info()
        if info is None:
            return self._is_implicit_dir()

        # tar
        if hasattr(info, 'isdir'):
            return info.isdir()
        # zip explicit dir entry
        return info.filename[-1] == '/'

    def read(self):
        path = self.cache_path / self.member_path
        if path.exists():
            raise FileExistsError('file in cache created between open and read')

        # extract to cache
        if hasattr(self.descriptor, 'getmember'):
            # tar
            member = self.descriptor.getmember(self.member_path.as_posix())
        else:
            # zip
            member = self.descriptor.getinfo(self.member_path.as_posix())
        self.descriptor.extract(member=member, path=str(self.cache_path))

        # read from cache
        with path.open(self.mode, encoding=self.encoding) as stream:
            return stream.read()
