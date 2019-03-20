# built-in
from fnmatch import fnmatch


def glob_path(path: str, pattern: str) -> bool:
    pattern_left, sep, pattern_right = pattern.rpartition('**')

    parts = [part for part in path.split('/') if part]
    parts_left = [part for part in pattern_left.split('/') if part]
    parts_right = [part for part in pattern_right.split('/') if part]

    if not sep:
        if len(parts) != len(parts_left) + len(parts_right):
            return False

    for path_part, pattern_part in zip(parts, parts_left):
        if not fnmatch(name=path_part, pat=pattern_part):
            return False

    for path_part, pattern_part in zip(reversed(parts), reversed(parts_right)):
        if not fnmatch(name=path_part, pat=pattern_part):
            return False

    return True
