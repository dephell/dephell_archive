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

    def exists(self) -> bool:
        try:
            if hasattr(self.descriptor, 'getmember'):
                self.descriptor.getmember(str(self.member_path))  # tar
            else:
                self.descriptor.getinfo(str(self.member_path))  # zip
        except KeyError:
            return False
        return True

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
