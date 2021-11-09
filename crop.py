import argparse
import PIL.Image
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable

def crop(file, crops, *, inplace=False, quality=100):
    image = PIL.Image.open(file.absolute_path)
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
        newname = file
    else:
        suffix = '_'.join(str(x) for x in crops)
        suffix = f'_{suffix}'
        base = file.replace_extension('').basename
        newname = file.parent.with_child(base + suffix).add_extension(file.extension)

    pipeable.stdout(newname.absolute_path)
    image.save(newname.absolute_path, exif=image.getexif(), quality=quality)

def crop_argparse(args):
    patterns = pipeable.input(args.pattern, skip_blank=True, strip=True)
    files = pathclass.glob_many_files(patterns)

    for file in files:
        crop(
            file,
            crops=args.crops,
            inplace=args.inplace,
            quality=args.quality,
        )
    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('pattern')
    parser.add_argument('crops', nargs='+', type=int, default=None)
    parser.add_argument('--inplace', action='store_true')
    parser.add_argument('--quality', type=int, default=100)
    parser.set_defaults(func=crop_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
