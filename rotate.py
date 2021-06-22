import argparse
import os
import PIL.Image
import sys

from voussoirkit import imagetools
from voussoirkit import pipeable
from voussoirkit import vlogging
from voussoirkit import winglob

log = vlogging.getLogger(__name__, 'rotate')

def rotate_argparse(args):
    if args.angle is None and not args.exif:
        pipeable.stderr('Either an angle or --exif must be provided.')
        return 1

    filenames = winglob.glob(args.pattern)
    for filename in filenames:
        image = PIL.Image.open(filename)

        if args.exif:
            (new_image, exif) = imagetools.rotate_by_exif(image)
            if new_image is image:
                log.debug('%s doesn\'t need exif rotation.', filename)
                continue
            image = new_image
        else:
            exif = image.getexif()
            image = image.rotate(args.angle, expand=True)

        if args.inplace:
            newname = filename
        else:
            if args.exif:
                suffix = f'_exifrot'
            else:
                suffix = f'_{args.angle}'
            (base, extension) = os.path.splitext(filename)
            newname = base + suffix + extension
        pipeable.stdout(newname)
        image.save(newname, exif=exif, quality=args.quality)

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('pattern')
    parser.add_argument('angle', nargs='?', type=int, default=None)
    parser.add_argument('--exif', action='store_true')
    parser.add_argument('--inplace', action='store_true')
    parser.add_argument('--quality', type=int, default=100)
    parser.set_defaults(func=rotate_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
