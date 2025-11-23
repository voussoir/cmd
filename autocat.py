import argparse
import os
import sys
import tempfile

from voussoirkit import betterhelp
from voussoirkit import ffmpegtools
from voussoirkit import pathclass
from voussoirkit import vlogging
from voussoirkit import winglob

log = vlogging.getLogger(__name__, 'autocat')

def autocat_argparse(args):
    if len(args.names) < 3:
        raise ValueError('Should have at least three arguments: two inputs and one output.')

    output_file = pathclass.Path(args.names.pop(-1))
    patterns = args.names

    input_files = list(pathclass.glob_many_files(patterns))
    output_file = ffmpegtools.concatenate(input_files, output_file)
    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        ''',
    )
    parser.add_argument(
        'names',
        nargs='+',
        help='''
        ''',
    )
    parser.set_defaults(func=autocat_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
