import argparse
import hashlib
import os
import send2trash
import sys

from voussoirkit import bytestring
from voussoirkit import lazychain
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import spinal
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'hash_hardlink')

def hash_file(file):
    hasher = hashlib.md5()
    with file.open('rb') as handle:
        while True:
            chunk = handle.read(2**20)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

@pipeable.ctrlc_return1
def hash_hardlink_argparse(args):
    paths = [pathclass.Path(p) for p in pipeable.input_many(args.paths, strip=True, skip_blank=True)]
    drives = set(path.stat.st_dev for path in paths)
    if len(drives) != 1:
        raise ValueError('All paths must be on the same drive.')

    files = lazychain.LazyChain()
    for path in paths:
        if path.is_file:
            files.append(path)
        elif path.is_dir:
            files.extend(spinal.walk(path))

    inodes = set()
    hashes = {}

    if args.if_larger_than:
        larger = bytestring.parsebytes(args.if_larger_than)
    else:
        larger = None

    for file in files:
        if file.stat.st_ino in inodes:
            # This file is already a hardlink of another file we've seen.
            continue
        if larger is not None and file.size < larger:
            continue
        inodes.add(file.stat.st_ino)
        h = hash_file(file)
        print(file.absolute_path, h)
        hashes.setdefault(h, []).append(file)

    hashes = {h: files for (h, files) in hashes.items() if len(files) > 1}

    for (h, files) in hashes.items():
        leader = files.pop(0)
        for follower in files:
            print(f'{leader.absolute_path} -> {follower.absolute_path}')
            send2trash.send2trash(follower.absolute_path)
            os.link(leader.absolute_path, follower.absolute_path)

def main(argv):
    argv = vlogging.main_level_by_argv(argv)

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('paths', nargs='+')
    parser.add_argument('--if_larger_than', '--if-larger-than', default=None)
    parser.set_defaults(func=hash_hardlink_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
