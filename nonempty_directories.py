import argparse
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import spinal
from voussoirkit import winglob

def nonempty_directories_argparse(args):
    if args.patterns:
        patterns = pipeable.input_many(args.patterns, skip_blank=True, strip=True)
        directories = (pathclass.Path(d) for pattern in patterns for d in winglob.glob(pattern))
    else:
        directories = pathclass.cwd().listdir()
    directories = (d for d in directories if d.is_dir)

    for directory in directories:
        if len(directory.listdir()) != 0:
            pipeable.stdout(directory.absolute_path)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns', nargs='*')
    parser.set_defaults(func=nonempty_directories_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
