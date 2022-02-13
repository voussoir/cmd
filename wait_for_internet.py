import argparse
import sys

from voussoirkit import betterhelp
from voussoirkit import networktools
from voussoirkit import vlogging

def wait_for_internet_argparse(args):
    try:
        networktools.wait_for_internet(timeout=args.timeout)
        return 0
    except networktools.NoInternet:
        return 1

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        This program will block until internet access is available. It can be useful to
        run this program before running another program that expects an internet
        connection.
        ''',
    )
    parser.add_argument(
        'timeout',
        type=int,
        help='''
        An integer number of seconds, after which to give up and return 1.
        ''',
    )
    parser.set_defaults(func=wait_for_internet_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
