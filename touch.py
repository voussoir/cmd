import argparse
import os
import sys

from voussoirkit import betterhelp
from voussoirkit import pipeable
from voussoirkit import winglob

def touch_argparse(args):
    patterns = pipeable.input_many(args.patterns, skip_blank=True)
    for pattern in patterns:
        filenames = winglob.glob(pattern)

        if len(filenames) == 0 and not winglob.is_glob(pattern):
            open(pattern, 'a').close()
            pipeable.stdout(pattern)

        for filename in filenames:
            os.utime(filename)
            pipeable.stdout(filename)

    return 0

def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Create blank files, or update mtimes of existing files.
        ''',
    )

    parser.add_argument(
        'patterns',
        type=str,
        nargs='+',
        help='''
        One or more filenames or glob patterns.
        ''',
    )
    parser.add_argument(
        '--sleep',
        type=float,
        default=None,
        help='''
        Sleep for this many seconds between touching each file.
        ''',
    )
    parser.set_defaults(func=touch_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
