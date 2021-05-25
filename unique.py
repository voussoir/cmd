import argparse
import sys

from voussoirkit import pipeable

def unique_argparse(args):
    lines = pipeable.input(args.source, read_files=True, skip_blank=True)
    seen = set()
    for line in lines:
        if line not in seen:
            pipeable.stdout(line)
            seen.add(line)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source')
    parser.set_defaults(func=unique_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
