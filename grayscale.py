import argparse
import PIL.Image
import sys

from voussoirkit import pathclass
from voussoirkit import winglob

def grayscale(filename, *, inplace=False):
    filename = pathclass.Path(filename)

    basename = filename.replace_extension('').basename
    if basename.endswith('_gray'):
        return

    if inplace:
        new_filename = filename
    else:
        basename += '_gray'
        new_filename = filename.parent.with_child(basename).add_extension(filename.extension)

    image = PIL.Image.open(filename.absolute_path).convert('LA')
    print(f'{new_filename.relative_path}')
    image.save(new_filename.absolute_path)

def grayscale_argparse(args):
    filenames = winglob.glob(args.pattern)
    for filename in filenames:
        grayscale(filename, inplace=args.inplace)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('pattern')
    parser.add_argument('--inplace', action='store_true')
    parser.set_defaults(func=grayscale_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
