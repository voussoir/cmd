import argparse
import PIL.Image
import sys

from voussoirkit import betterhelp
from voussoirkit import imagetools
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'fuchsiatransparent')

FUCHSIA = (255, 0, 255, 255)
TRANSPARENT = (0, 0, 0, 0)

def fuchsiatransparent_argparse(args):
    patterns = pipeable.input_many(args.patterns)
    files = pathclass.glob_many_files(patterns)
    for file in files:
        image = PIL.Image.open(file.absolute_path)
        if image.mode == 'RGB':
            image = image.convert('RGBA')
        if image.mode == 'RGBA':
            image = imagetools.replace_color(image, FUCHSIA, TRANSPARENT)
        else:
            log.info('Can\'t process %s', file.absolute_path)
            continue

        if args.inplace:
            outpath = file
        else:
            outname = file.replace_extension('').basename + '_transparent'
            outpath = file.parent.with_child(outname).add_extension(file.extension)

        pipeable.stderr(outpath.absolute_path)
        image.save(outpath.absolute_path)
    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Replace #FF00FF colored pixels with transparent.
        ''',
    )
    parser.add_argument(
        'patterns',
        help='''
        One or more glob patterns for input files.
        ''',
    )
    parser.add_argument(
        '--inplace',
        action='store_true',
        help='''
        Overwrite the input file instead of saving it as _transparent.
        ''',
    )
    parser.set_defaults(func=fuchsiatransparent_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
