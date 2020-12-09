import argparse
import sys

from voussoirkit import pipeable

def shuffle_argparse(args):
    if args.count < 1:
        pipeable.stderr('count must be >= 1.')
        return 1

    lines = pipeable.input(args.source, read_files=True, skip_blank=True, strip=True)
    lines = list(lines)
    lines = lines[:args.count]

    for line in lines:
        pipeable.stdout(line)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source')
    parser.add_argument('count', type=int)
    parser.set_defaults(func=shuffle_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
