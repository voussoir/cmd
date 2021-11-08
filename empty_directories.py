import argparse
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable

def empty_directories_argparse(args):
    patterns = pipeable.input_many(args.patterns, skip_blank=True, strip=True)
    directories = pathclass.glob_many_directories(patterns)

    for directory in directories:
        if len(directory.listdir()) == 0:
            pipeable.stdout(directory.absolute_path)

    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns', nargs='*', default=['*'])
    parser.set_defaults(func=empty_directories_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
