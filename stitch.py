import PIL.Image
import argparse
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import sentinel
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'stitch')

VERTICAL = sentinel.Sentinel('vertical')
HORIZONTAL = sentinel.Sentinel('horizontal')

def stitch_argparse(args):
    patterns = pipeable.input_many(args.image_files, skip_blank=True, strip=True)
    files = pathclass.glob_many_files(patterns)
    images = [PIL.Image.open(file.absolute_path) for file in files]
    if args.vertical:
        direction = VERTICAL
    else:
        direction = HORIZONTAL

    gapcount = len(images) - 1

    if direction is HORIZONTAL:
        width = sum(i.size[0] for i in images) + (gapcount * args.gap)
        height = max(i.size[1] for i in images)
    else:
        width = max(i.size[0] for i in images)
        height = sum(i.size[1] for i in images) + (gapcount * args.gap)

    final_image = PIL.Image.new('RGBA', [width, height])
    offset = 0
    for image in images:
        if direction is VERTICAL:
            final_image.paste(image, (0, offset))
            offset += image.size[1] + args.gap
        else:
            final_image.paste(image, (offset, 0))
            offset += image.size[0] + args.gap

    log.info(args.output)
    final_image.save(args.output)
    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('image_files', nargs='+')
    parser.add_argument(
        '--output',
        required=True,
    )
    parser.add_argument(
        '--horizontal',
        action='store_true',
        help='''
        Stitch the images together horizontally.
        ''',
    )
    parser.add_argument(
        '--vertical',
        action='store_true',
        help='''
        Stitch the images together vertically.
        ''',
    )
    parser.add_argument(
        '--gap',
        type=int,
        default=0,
        help='''
        This many pixels of transparent gap between each row / column.
        ''',
    )
    parser.set_defaults(func=stitch_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
