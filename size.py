import sys

from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import spinal

@pipeable.ctrlc_return1
def main(argv):
    total = 0
    for path in pipeable.go():
        path = pathclass.Path(path)
        if path.is_file:
            total += path.size
        elif path.is_dir:
            total += spinal.get_dir_size(path)

    print(total)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
