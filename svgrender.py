'''
svgrender
=========

Calls the Inkscape command line to render svg files to png. A link to inkscape
should be on your PATH.

> svgrender svg_file scales <flags>

scales:
    One or more integers. Each integer will be the size of one output file.

--destination:
    A path to a directory where the png files should be saved. By default,
    they go to the same folder as the svg file.

--y:
    By default, the scales control the width of the output image.
    Pass this if you want the scales to control the height.

--basename-only:
    By default, the png filenames will have suffixes like _{scale}.
    Pass this if you want the png to have the same name as the svg file.
    Naturally, this only works if you're only using a single scale.
'''
import argparse
import glob
import os
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import winwhich

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
        command = command.format(svg=svg_path.absolute_path, png=png_path.absolute_path, dimension=dimension)
        #print(command)
        status = os.system(command)
        if status:
            print('Uh oh...')

def svgrender_argparse(args):
    svg_paths = glob.glob(args.svg_filepath)
    scales = [int(x) for x in args.scales]
    for svg_path in svg_paths:
        svgrender(
            svg_path,
            scales,
            destination=args.destination,
            scale_suffix=args.scale_suffix,
            axis='y' if args.y else 'x',
        )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('svg_filepath')
    parser.add_argument('scales', nargs='+')
    parser.add_argument('--destination', nargs='?', default=None)
    parser.add_argument('--y', dest='y', action='store_true')
    parser.add_argument('--basename_only', '--basename-only', dest='scale_suffix', action='store_false')
    parser.set_defaults(func=svgrender_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    main(sys.argv[1:])
