import argparse
import itertools
import sys

from voussoirkit import pipeable

def pickn_argparse(args):
    if args.count < 1:
        pipeable.stderr('count must be >= 1.')
        return 1

    lines = pipeable.input(args.source, read_files=True, skip_blank=True, strip=True)

    for line in itertools.islice(lines, args.count):
        pipeable.stdout(line)

    # Exhaust the rest of stdin so we don't get Broken Pipe error
    for line in lines:
        pass

    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source')
    parser.add_argument('count', type=int)
    parser.set_defaults(func=pickn_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
