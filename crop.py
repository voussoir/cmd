import argparse
import os
from PIL import Image
import sys

from voussoirkit import winglob

def crop(filename, crops, *, inplace=False):
    print(crops)
    i = Image.open(filename)
    if len(crops) == 2:
        crops.extend(i.size)
    i = i.crop(crops)
    if inplace:
        newname = filename
    else:
        suffix = '_'.join(str(x) for x in crops)
        suffix = f'_{suffix}'
        (base, extension) = os.path.splitext(filename)
        newname = base + suffix + extension
    i.save(newname, quality=100)


def crop_argparse(args):
    filenames = winglob.glob(args.pattern)
    for filename in filenames:
        crop(
            filename,
            crops=args.crops,
            inplace=args.inplace,
        )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('pattern')
    parser.add_argument('crops', nargs='+', type=int, default=None)
    parser.add_argument('--inplace', dest='inplace', action='store_true')
    parser.set_defaults(func=crop_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
