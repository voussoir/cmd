'''
Reverse a string.
'''
import argparse
import sys

def reverse_argparse(args):
    print(''.join(reversed(args.string)))

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('string')
    parser.set_defaults(func=reverse_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
