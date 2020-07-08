import argparse
import os
from PIL import Image
import sys

from voussoirkit import imagetools
from voussoirkit import winglob

def resize(
        filename,
        new_x=None,
        new_y=None,
        *,
        inplace=False,
        nearest_neighbor=False,
        scale=None,
    ):
    i = Image.open(filename)

    (image_width, image_height) = i.size

    if new_x is not None and new_y is not None:
        pass
    elif scale:
        new_x = int(image_width * scale)
        new_y = int(image_height * scale)

    if new_x == 0:
        (new_x, new_y) = imagetools.fit_into_bounds(image_width, image_height, 10000000, new_y)
    if new_y == 0:
        (new_x, new_y) = imagetools.fit_into_bounds(image_width, image_height, new_x, 10000000)

    print(i.size, new_x, new_y)
    if nearest_neighbor:
        i = i.resize( (new_x, new_y), Image.NEAREST)
    else:
        i = i.resize( (new_x, new_y), Image.ANTIALIAS)

    if inplace:
        newname = filename
    else:
        suffix = '_{width}x{height}'.format(width=new_x, height=new_y)
        (base, extension) = os.path.splitext(filename)
        newname = base + suffix + extension
    i.save(newname, quality=100)


def resize_argparse(args):
    filenames = winglob.glob(args.pattern)
    for filename in filenames:
        resize(
            filename,
            args.new_x,
            args.new_y,
            scale=args.scale,
            nearest_neighbor=args.nearest_neighbor,
            inplace=args.inplace,
        )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('pattern')
    parser.add_argument('new_x', nargs='?', type=int, default=None)
    parser.add_argument('new_y', nargs='?', type=int, default=None)
    parser.add_argument('--scale', dest='scale', type=float, default=None)
    parser.add_argument('--nearest', dest='nearest_neighbor', action='store_true')
    parser.add_argument('--inplace', dest='inplace', action='store_true')
    parser.set_defaults(func=resize_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
