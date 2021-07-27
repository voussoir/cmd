'''
Print input lines in reverse order.
'''
import argparse
import sys

from voussoirkit import pipeable

def reverse_argparse(args):
    lines = list(pipeable.input(args.lines))
    lines.reverse()
    print('\n'.join(lines))

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('lines')
    parser.set_defaults(func=reverse_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
