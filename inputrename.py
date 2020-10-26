import os
import sys

from voussoirkit import winglob

import argparse
import sys

def inputrename_argparse(args):
    pattern = f'*{args.keyword}*'

    files = winglob.glob(pattern)
    prev = None
    for file in files:
        print(file)
        this = input('> ')
        if this == '' and prev is not None:
            this = prev
        if this:
            os.rename(file, file.replace(args.keyword, this))
        prev = this

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('keyword')
    parser.set_defaults(func=inputrename_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    try:
        raise SystemExit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        raise SystemExit(1)
