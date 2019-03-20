# external
import attr


@attr.s()
class ArchiveStream:
    descriptor = attr.ib()
    cache_path = attr.ib()
    member_path = attr.ib()
    mode = attr.ib()

    def exists(self):
        if hasattr(self.descriptor, 'getmember'):
            # tar
            try:
                self.descriptor.getmember(str(self.member_path))
            except KeyError:
                return False
            return True
        else:
            # zip
            member = self.descriptor.getinfo(str(self.member_path))  # i'm not sure
            return bool(member)

    def read(self):
        path = self.cache_path / self.member_path
        if path.exists():
            raise FileExistsError('file created between open and read')

        # extract to cache
        if hasattr(self.descriptor, 'getmember'):
            # tar
            member = self.descriptor.getmember(str(self.member_path))
        else:
            # zip
            member = self.descriptor.getinfo(str(self.member_path))
        self.descriptor.extract(member=member, path=str(self.cache_path))

        # read from cache
        with path.open(self.mode) as stream:
            return stream.read()
