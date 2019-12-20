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
        with suppress(KeyError):
            if hasattr(self.descriptor, 'getmember'):
                return self.descriptor.getmember(str(self.member_path))  # tar
            return self.descriptor.getinfo(str(self.member_path))  # zip
        return None

    def exists(self) -> bool:
        return self._get_info() is not None

    def is_file(self) -> bool:
        info = self._get_info()
        if info is None:
            return False
        # tar
        if hasattr(info, 'isfile'):
            return info.isfile()
        # zip
        return info.filename[-1] != '/'

    def is_dir(self) -> bool:
        info = self._get_info()
        if info is None:
            return False
        # tar
        if hasattr(info, 'isdir'):
            return info.isdir()
        # zip
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
