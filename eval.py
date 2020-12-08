import argparse
import glob
import math
import os
import random
import re
import sys

from voussoirkit import pipeable

def quote(s):
    return '"%s"' % s

def apostrophe(s):
    return "'%s'" % s

def random_hex(length=12):
    randbytes = os.urandom(math.ceil(length / 2))
    token = ''.join('{:02x}'.format(x) for x in randbytes)
    token = token[:length]
    return token

def eval_argparse(args):
    for line in pipeable.input(args.lines):
        x = line
        pipeable.output(eval(args.eval_string))

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('lines')
    parser.add_argument('eval_string')
    parser.set_defaults(func=eval_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
