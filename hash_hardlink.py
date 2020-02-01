import hashlib
import os
import send2trash
import sys

from voussoirkit import pathclass
from voussoirkit import spinal

def hash_file(file):
    hasher = hashlib.md5()
    with open(file.absolute_path, 'rb') as handle:
        while True:
            chunk = handle.read(2**20)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def main(argv):
    folders = [pathclass.Path(p) for p in argv]

    drives = set(os.path.splitdrive(folder.absolute_path)[0] for folder in folders)
    if len(drives) != 1:
        raise ValueError('All paths must be on the same drive.')

    inodes = set()
    hashes = {}

    for folder in folders:
        for file in spinal.walk_generator(folder):
            if file.stat.st_ino in inodes:
                # This file is already a hardlink of another file we've seen.
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

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
