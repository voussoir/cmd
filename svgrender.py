import argparse
import glob
import os
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import winwhich
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'svgrender')

def svgrender(filepath, scales, destination, scale_suffix=True, axis='x'):
    if isinstance(scales, int):
        scales = [scales]
    elif isinstance(scales, (list, tuple)):
        pass
    else:
        raise TypeError(scales)

    svg_path = pathclass.Path(filepath)
    svg_path.assert_is_file()
    if destination is None:
        destination = svg_path.parent
    else:
        destination = pathclass.Path(destination)
        destination.assert_is_directory()

    if axis == 'x':
        axis = '--export-width={s}'
    else:
        axis = '--export-height={s}'

    for scalar in scales:
        png_name = svg_path.replace_extension('').basename
        if scale_suffix:
            png_name += '_%d' % scalar
        png_path = destination.with_child(png_name).add_extension('png')
        dimension = axis.format(s=scalar)
        print(png_path.absolute_path)

        inkscape = winwhich.which('inkscape')
        command = inkscape + ' "{svg}" --export-png="{png}" {dimension} --export-area-page'
        command = command.format(
            svg=svg_path.absolute_path,
            png=png_path.absolute_path,
            dimension=dimension,
        )
        log.debug(command)
        status = os.system(command)
        if status:
            print('Uh oh...')

def svgrender_argparse(args):
    svg_paths = glob.glob(args.svg_filepath)
    for svg_path in svg_paths:
        svgrender(
            svg_path,
            scales=args.scales,
            destination=args.destination,
            scale_suffix=args.scale_suffix,
            axis='y' if args.y else 'x',
        )

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Calls the Inkscape command line to render svg files to png. A link to Inkscape
        should be on your PATH.
        ''',
    )
    parser.add_argument(
        'svg_filepath',
        help='''
        Input svg file to be rendered.
        ''',
    )
    parser.add_argument(
        'scales',
        type=int,
        nargs='+',
        help='''
        One or more integers. Each integer will be the size of one output file.
        ''',
    )
    parser.add_argument(
        '--destination',
        default=None,
        help='''
        A path to a directory where the png files should be saved. By default,
        they go to the same folder as the svg file.
        ''',
    )
    parser.add_argument(
        '--y',
        dest='y',
        action='store_true',
        help='''
        By default, the scales control the width of the output image.
        Pass this if you want the scales to control the height.
        ''',
    )
    parser.add_argument(
        '--basename_only',
        '--basename-only',
        dest='scale_suffix',
        action='store_false',
        help='''
        By default, the png filenames will have suffixes like _{scale}.
        Pass this if you want the png to have the same name as the svg file.
        Naturally, this only works if you're only using a single scale.
        ''',
    )
    parser.set_defaults(func=svgrender_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    main(sys.argv[1:])
