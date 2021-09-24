import os
import shutil
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable

def main(argv):
    for path in pathclass.glob_many(pipeable.go(argv, skip_blank=True)):
        if path.is_file:
            pipeable.stdout(path.absolute_path)
            os.remove(path.absolute_path)
        elif path.is_dir:
            pipeable.stdout(path.absolute_path)
            shutil.rmtree(path.absolute_path)
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
