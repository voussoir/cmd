import argparse
import PIL.Image
import sys

from voussoirkit import imagetools
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'rotate')

def rotate_argparse(args):
    if args.angle is None and not args.exif:
        log.fatal('Either an angle or --exif must be provided.')
        return 1

    patterns = pipeable.input(args.pattern, skip_blank=True, strip=True)
    files = pathclass.glob_many(patterns, files=True)

    for file in files:
        image = PIL.Image.open(file.absolute_path)

        if args.exif:
            (new_image, exif) = imagetools.rotate_by_exif(image)
            if new_image is image:
                log.debug('%s doesn\'t need exif rotation.', file.absolute_path)
                continue
            image = new_image
        else:
            exif = image.getexif()
            image = image.rotate(args.angle, expand=True)

        if args.inplace:
            newname = file
        else:
            if args.exif:
                suffix = f'_exifrot'
            else:
                suffix = f'_{args.angle}'

            base = file.replace_extension('').basename
            newname = base + suffix
            newname = file.parent.with_child(newname).add_extension(file.extension)

        pipeable.stdout(newname.absolute_path)
        image.save(newname.absolute_path, exif=exif, quality=args.quality)

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
