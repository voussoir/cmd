import argparse
import PIL.Image
import PIL.ImageSequence
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'imagesequence_to_images')

def imagesequence_to_images_argparse(args):
    for input_file in pathclass.glob_many_files(args.input_files):
        input_file = pathclass.Path(input_file)
        basename = input_file.replace_extension('').basename
        input_image = PIL.Image.open(input_file.absolute_path)

        for (index, image) in enumerate(PIL.ImageSequence.Iterator(input_image)):
            this_png = input_file.parent.with_child(f'{basename}_{index+1:04d}.png')
            pipeable.stdout(this_png.absolute_path)
            image.save(this_png.absolute_path)
    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Some file formats like TIFF can contain multiple images. This program
        extracts them to separate PNG files.
        ''',
    )
    parser.add_argument(
        'input_files',
        nargs='+',
    )
    parser.set_defaults(func=imagesequence_to_images_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
