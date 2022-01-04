import send2trash
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable

def main(argv):
    for path in pathclass.glob_many(pipeable.go(argv, skip_blank=True)):
        pipeable.stdout(path.absolute_path)
        try:
            send2trash.send2trash(path)
        except Exception as exc:
            pipeable.stderr(f'Recycling {path.absolute_path} caused an exception:')
            pipeable.stderr(str(exc))
            return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
