import html
import argparse
import sys

from voussoirkit import betterhelp
from voussoirkit import vlogging
from voussoirkit import pipeable

log = vlogging.getLogger(__name__, 'htmlescape')

def htmlescape_argparse(args):
    text = pipeable.input(args.text, split_lines=False)
    pipeable.stdout(html.escape(text))
    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        ''',
    )
    parser.add_argument(
        'text',
        help='''
        ''',
    )
    parser.set_defaults(func=htmlescape_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
