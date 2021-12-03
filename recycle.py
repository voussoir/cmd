import send2trash
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable

def main(argv):
    for path in pathclass.glob_many(pipeable.go(argv, skip_blank=True)):
        pipeable.stdout(path.absolute_path)
        send2trash.send2trash(path)
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
