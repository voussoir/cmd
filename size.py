import sys

from voussoirkit import spinal
from voussoirkit import pathclass

paths = sys.argv[1:]
paths = [pathclass.Path(p) for p in paths]

total = 0
for path in paths:
    if path.is_file:
        total += path.size
    elif path.is_dir:
        total += spinal.get_dir_size(path)

print(total)
