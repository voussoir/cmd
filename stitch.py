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

    if args.grid:
        (grid_x, grid_y) = [int(part) for part in args.grid.split('x')]
        if grid_x * grid_y < len(images):
            pipeable.stderr(f'Your grid {grid_x}x{grid_y} is too small for {len(images)} images.')
            return 1
    elif args.vertical:
        grid_x = 1
        grid_y = len(images)
    else:
        grid_x = len(images)
        grid_y = 1

    # We produce a 2D list of images which will become their final arrangement,
    # and calculate the size of each row and column to accommodate the largest
    # member of each.
    arranged_images = [[] for y in range(grid_y)]
    column_widths = [1 for x in range(grid_x)]
    row_heights = [1 for x in range(grid_y)]
    index_x = 0
    index_y = 0
    for image in images:
        arranged_images[index_y].append(image)
        column_widths[index_x] = max(column_widths[index_x], image.size[0])
        row_heights[index_y] = max(row_heights[index_y], image.size[1])
        if args.vertical:
            index_y += 1
            (bump_x, index_y) = divmod(index_y, grid_y)
            index_x += bump_x
        else:
            index_x += 1
            (bump_y, index_x) = divmod(index_x, grid_x)
            index_y += bump_y

    final_width = sum(column_widths) + ((grid_x - 1) * args.gap)
    final_height = sum(row_heights) + ((grid_y - 1) * args.gap)
    background = '#' + args.background.strip('#')
    final_image = PIL.Image.new('RGBA', [final_width, final_height], color=background)

    offset_y = 0
    for (index_y, row) in enumerate(arranged_images):
        offset_x = 0
        for (index_x, image) in enumerate(row):
            pad_x = int((column_widths[index_x] - image.size[0]) / 2)
            pad_y = int((row_heights[index_y] - image.size[1]) / 2)
            final_image.paste(image, (offset_x + pad_x, offset_y + pad_y))
            offset_x += column_widths[index_x]
            offset_x += args.gap
        offset_y += row_heights[index_y]
        offset_y += args.gap

    log.info(args.output)
    final_image.save(args.output)
    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('image_files', nargs='+')
    parser.add_argument(
        '--output',
        metavar='filename',
        required=True,
    )
    parser.add_argument(
        '--grid',
        metavar='AxB',
        help='''
        Stitch the images together in grid of A columns and B rows. Your
        numbers A and B should be such that A*B is larger than the number
        of input images. If you add --horizontal, the images will be arranged
        left-to-right first, then top-to-bottom. If you add --vertical, the
        images will be arranged top-to-bottom first then left-to-right.
        ''',
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
    parser.add_argument(
        '--background',
        type=str,
        default='#00000000',
        help='''
        Background color as a four-channel (R, G, B, A) hex string.
        This color will be seen in the --gap and behind any images that
        already had transparency.
        ''',
    )
    parser.set_defaults(func=stitch_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
