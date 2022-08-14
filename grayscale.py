import argparse
import PIL.Image
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable

def grayscale(filename, *, inplace=False, quality=100):
    filename = pathclass.Path(filename)

    basename = filename.replace_extension('').basename
    if basename.endswith('_gray'):
        return

    if inplace:
        new_filename = filename
    else:
        basename += '_gray'
        new_filename = filename.parent.with_child(basename).add_extension(filename.extension)

    image = PIL.Image.open(filename.absolute_path)
    image = image.convert('LA').convert(image.mode)
    image.save(new_filename.absolute_path, exif=image.getexif(), quality=quality)
    return new_filename

def grayscale_argparse(args):
    patterns = pipeable.input_many(args.patterns, skip_blank=True, strip=True)
    files = pathclass.glob_many_files(patterns)
    for file in files:
        new_filename = grayscale(file, inplace=args.inplace, quality=args.quality)
        if new_filename:
            pipeable.stdout(new_filename.absolute_path)

    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns', nargs='+')
    parser.add_argument('--inplace', action='store_true')
    parser.add_argument('--quality', type=int, default=100)
    parser.set_defaults(func=grayscale_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
