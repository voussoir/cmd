'''
resize
======

Resize image files.

> resize patterns <flags>

patterns:
    One or more glob patterns for input files.
    Uses pipeable to support !c clipboard, !i stdin lines of glob patterns.

flags:
--width X:
--height X:
    New dimensions for the image. If either of these is omitted, then that
    dimension will be calculated automatically based on the aspect ratio.

--break_aspect_ratio:
    If provided, the given --width and --height will be used exactly. You will
    need to provide both --width and --height.

    If omitted, the image will be resized to fit within the bounds provided by
    --width and --height while preserving its aspect ratio.

--output X:
    A string that controls the output filename format. Suppose the input file
    was myphoto.jpg. You can use these variables in your format string:
    {base} = myphoto
    {width} = an integer
    {height} = an integer
    {extension} = .jpg

    You may omit {extension} from your format string and it will automatically
    be added to the end, unless you already provided a different extension.

    If your format string only designates a basename, output files will go to
    the same directory as the corresponding input file. If your string contains
    path separators, all output files will go to that directory.
    The directory
    part is not formatted with the variables.

--inplace:
    Overwrite the input files. Cannot be used along with --output.
    Be careful!

--nearest:
    If provided, use nearest-neighbor scaling to preserve pixelated images.
    If omitted, use antialiased scaling.

--only_shrink:
    If the input image is smaller than the requested dimensions, do nothing.
    Useful when globbing in a directory with many differently sized images.

--quality X:
    JPEG compression quality.

--scale X:
    Scale the image by factor X.
    Use this option instead of --width, --height.
'''
import argparse
import os
import PIL.Image
import sys

from voussoirkit import betterhelp
from voussoirkit import imagetools
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import sentinel
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'resize')

OUTPUT_INPLACE = sentinel.Sentinel('output inplace')
DEFAULT_OUTPUT_FORMAT = '{base}_{width}x{height}{extension}'

def resize_core(
        image,
        height=None,
        only_shrink=False,
        scale=None,
        width=None,
    ):
    pass

def resize(
        filename,
        *,
        destination=None,
        output_format=DEFAULT_OUTPUT_FORMAT,
        height=None,
        keep_aspect_ratio=True,
        nearest_neighbor=False,
        only_shrink=False,
        quality=100,
        scale=None,
        width=None,
    ):
    if scale and (width or height):
        raise ValueError('Cannot use both scale and width/height.')

    file = pathclass.Path(filename)
    image = PIL.Image.open(file.absolute_path)

    (image_width, image_height) = image.size

    if scale:
        width = int(image_width * scale)
        height = int(image_height * scale)
    elif (width and height) and not keep_aspect_ratio:
        # The given width and height will be used exactly.
        pass
    elif (width and height) and keep_aspect_ratio:
        (width, height) = imagetools.fit_into_bounds(
            image_width=image_width,
            image_height=image_height,
            frame_width=width,
            frame_height=height,
            only_shrink=only_shrink,
        )
    elif (width and not height) and keep_aspect_ratio:
        (width, height) = imagetools.fit_into_bounds(
            image_width=image_width,
            image_height=image_height,
            frame_width=width,
            frame_height=10000000,
            only_shrink=only_shrink,
        )
    elif (height and not width) and keep_aspect_ratio:
        (width, height) = imagetools.fit_into_bounds(
            image_width=image_width,
            image_height=image_height,
            frame_width=10000000,
            frame_height=height,
            only_shrink=only_shrink,
        )
    else:
        raise ValueError('Insufficient parameters for resizing. Need width, height, or scale.')

    if output_format is OUTPUT_INPLACE:
        output_file = file
    else:
        output_format = pathclass.normalize_sep(output_format)
        if output_format.endswith(os.sep):
            output_folder = pathclass.Path(output_format)
            output_format = DEFAULT_OUTPUT_FORMAT
        elif os.sep in output_format:
            full = pathclass.Path(output_format)
            output_folder = full.parent
            output_format = full.basename
        else:
            output_folder = file.parent

        output_folder.assert_is_directory()

        base = file.replace_extension('').basename
        if '{extension}' not in output_format:
            known_extensions = PIL.Image.registered_extensions()
            known_extensions = {os.path.normcase(ext) for ext in known_extensions}
            output_norm = os.path.normcase(output_format)
            if not any(output_norm.endswith(ext) for ext in known_extensions):
                output_format += '{extension}'
        output_file = output_format.format(
            base=base,
            width=width,
            height=height,
            extension=file.extension.with_dot,
        )
        output_file = output_folder.with_child(output_file)
        if output_file == file:
            raise ValueError('Cannot overwrite input file without OUTPUT_INPLACE.')

    log.debug('Resizing %s to %dx%d.', file.absolute_path, width, height)
    resampler = PIL.Image.NEAREST if nearest_neighbor else PIL.Image.ANTIALIAS
    image = image.resize( (width, height), resampler)

    if output_file.extension == '.jpg':
        image = image.convert('RGB')

    image.save(output_file.absolute_path, exif=image.getexif(), quality=quality)
    return output_file

def resize_argparse(args):
    if args.inplace and args.output:
        pipeable.stderr('Cannot have both --inplace and --output')
        return 1

    if args.inplace:
        output_format = OUTPUT_INPLACE
    elif args.output:
        output_format = args.output
    else:
        output_format = DEFAULT_OUTPUT_FORMAT

    patterns = pipeable.input_many(args.patterns, skip_blank=True, strip=True)
    files = pathclass.glob_many_files(patterns)
    for file in files:
        output_file = resize(
            file,
            height=args.height,
            keep_aspect_ratio=not args.break_aspect_ratio,
            nearest_neighbor=args.nearest_neighbor,
            only_shrink=args.only_shrink,
            output_format=output_format,
            quality=args.quality,
            scale=args.scale,
            width=args.width,
        )
        pipeable.stdout(output_file.absolute_path)

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns', nargs='+')
    parser.add_argument('--width', type=int, default=None)
    parser.add_argument('--height', type=int, default=None)
    parser.add_argument('--destination', default=None)
    parser.add_argument('--inplace', action='store_true')
    parser.add_argument('--nearest', dest='nearest_neighbor', action='store_true')
    parser.add_argument('--only_shrink', '--only-shrink', action='store_true')
    parser.add_argument('--break_aspect_ratio', '--break-aspect-ratio', action='store_true')
    parser.add_argument('--output', default=None)
    parser.add_argument('--scale', type=float, default=None)
    parser.add_argument('--quality', type=int, default=100)
    parser.set_defaults(func=resize_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
