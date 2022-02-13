import argparse
import PIL.Image
import sys

from voussoirkit import betterhelp
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'blankimage')

def blankimage_argparse(args):
    if args.width and args.height:
        size = (args.width, args.height)
    else:
        size = (512, 512)

    if args.color:
        color = args.color
    else:
        color = (255, 255, 255, 255)

    image = PIL.Image.new('RGBA', size, color=color)
    for filename in args.names:
        image.save(filename)

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Create a blank image file.
        ''',
    )
    parser.add_argument(
        'names',
        nargs='+',
        help='''
        One or more filenames. The same image will be saved to each.
        ''',
    )
    parser.add_argument(
        '--width',
        default=None,
        type=int,
        help='''
        ''',
    )
    parser.add_argument(
        '--height',
        default=None,
        type=int,
        help='''
        ''',
    )
    parser.add_argument(
        '--color',
        default=None,
        type=str,
        help='''
        A hex color like #fff or #0a0a0a or #ff0000ff.
        ''',
    )
    parser.set_defaults(func=blankimage_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
