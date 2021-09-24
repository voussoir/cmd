import argparse
import sys

from voussoirkit import pipeable

def sorted_argparse(args):
    lines = pipeable.input(args.source, read_files=True, skip_blank=True, strip=True)
    lines = list(lines)
    if args.nocase:
        lines.sort(key=lambda x: x.lower())
    else:
        lines.sort()

    for line in lines:
        pipeable.stdout(line)

    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source')
    parser.add_argument('--nocase', action='store_true')
    parser.set_defaults(func=sorted_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
