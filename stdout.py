import argparse
import sys

from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'printstdout')

def printstdout_argparse(args):
    for text in args.texts:
        text = pipeable.input(text)
        for line in text:
            pipeable.stdout(line)

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('texts', nargs='+')
    parser.set_defaults(func=printstdout_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
