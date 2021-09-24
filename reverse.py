'''
Reverse a string.
'''
import argparse
import sys

from voussoirkit import pipeable

def reverse_argparse(args):
    text = pipeable.input(args.text, split_lines=False)
    pipeable.stdout(''.join(reversed(text)))
    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('text')
    parser.set_defaults(func=reverse_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
