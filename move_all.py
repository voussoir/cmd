'''
Move all of the files into the destination directory, aborting the operation if
even a single file collides with a file in the destination.
'''
import sys
import shutil

from voussoirkit import pathclass
from voussoirkit import winglob

argv = sys.argv[1:]

if len(argv) < 2:
    raise TypeError()

patterns = argv[:-1]
files = [file for pattern in patterns for file in winglob.glob(pattern)]
files = [pathclass.Path(file) for file in files]
destination = pathclass.Path(sys.argv[-1])
if not destination.is_dir:
    raise TypeError(destination)

for file in files:
    if destination.with_child(file.basename).exists:
        raise Exception(file.basename)

for file in files:
    new_path = destination.with_child(file.basename)
    print(new_path.absolute_path)
    shutil.move(file.absolute_path, new_path.absolute_path)
