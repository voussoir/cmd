import argparse
import os
from PIL import Image
import sys

from voussoirkit import imagetools
from voussoirkit import pathclass
from voussoirkit import winglob

def resize(
        filename,
        new_x=None,
        new_y=None,
        *,
        inplace=False,
        nearest_neighbor=False,
        only_shrink=False,
        scale=None,
        quality=100,
    ):
    file = pathclass.Path(filename)
    i = Image.open(file.absolute_path)

    (image_width, image_height) = i.size

    if new_x is not None and new_y is not None:
        pass
    elif scale:
        new_x = int(image_width * scale)
        new_y = int(image_height * scale)

    if new_x == 0:
        (new_x, new_y) = imagetools.fit_into_bounds(
            image_width,
            image_height,
            10000000,
            new_y,
            only_shrink=only_shrink,
        )
    if new_y == 0:
        (new_x, new_y) = imagetools.fit_into_bounds(
            image_width,
            image_height,
            new_x,
            10000000,
            only_shrink=only_shrink,
        )

    print(i.size, new_x, new_y)
    if nearest_neighbor:
        i = i.resize( (new_x, new_y), Image.NEAREST)
    else:
        i = i.resize( (new_x, new_y), Image.ANTIALIAS)

    if inplace:
        new_name = file
    else:
        suffix = '_{width}x{height}'.format(width=new_x, height=new_y)
        base = file.replace_extension('').basename
        new_name = base + suffix + file.extension.with_dot
        new_name = file.parent.with_child(new_name)

    if new_name.extension == '.jpg':
        i = i.convert('RGB')

    i.save(new_name.absolute_path, quality=quality)


def resize_argparse(args):
    filenames = winglob.glob(args.pattern)
    for filename in filenames:
        resize(
            filename,
            args.new_x,
            args.new_y,
            inplace=args.inplace,
            nearest_neighbor=args.nearest_neighbor,
            only_shrink=args.only_shrink,
            scale=args.scale,
            quality=args.quality,
        )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('pattern')
    parser.add_argument('new_x', nargs='?', type=int, default=None)
    parser.add_argument('new_y', nargs='?', type=int, default=None)
    parser.add_argument('--inplace', action='store_true')
    parser.add_argument('--nearest', dest='nearest_neighbor', action='store_true')
    parser.add_argument('--only_shrink', '--only-shrink', action='store_true')
    parser.add_argument('--scale', type=float, default=None)
    parser.add_argument('--quality', type=int, default=100)
    parser.set_defaults(func=resize_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
