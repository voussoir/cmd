import argparse
import os
import PIL.Image
import sys

from voussoirkit import pipeable
from voussoirkit import winglob

def crop(filename, crops, *, inplace=False):
    image = PIL.Image.open(filename)
    if len(crops) == 2:
        crops.extend(image.size)

    if crops[0] < 0: crops[0] = image.size[0] + crops[0]
    if crops[1] < 0: crops[1] = image.size[1] + crops[1]
    if crops[2] < 0: crops[2] = image.size[0] + crops[2]
    if crops[3] < 0: crops[3] = image.size[1] + crops[3]
    if crops[2] == 0: crops[2] = image.size[0]
    if crops[3] == 0: crops[3] = image.size[1]

    image = image.crop(crops)
    if inplace:
        newname = filename
    else:
        suffix = '_'.join(str(x) for x in crops)
        suffix = f'_{suffix}'
        (base, extension) = os.path.splitext(filename)
        newname = base + suffix + extension

    pipeable.stdout(newname)
    image.save(newname, exif=image.info.get('exif', b''), quality=100)

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
    parser.add_argument('--inplace', action='store_true')
    parser.set_defaults(func=crop_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
