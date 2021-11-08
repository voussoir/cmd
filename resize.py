'''
resize
======

Resize image files.

pattern:
    Glob pattern for input files.

new_w,
new_h:
    New dimensions for the image. If either of these is 0, then that
    dimension will be calculated by resizing the other side while keeping the
    aspect ratio.

--inplace:
    Overwrite the input files, instead of creating _WxH names.

--nearest:
    Use nearest-neighbor scaling to preserve pixelated images.

--only_shrink:
    If the input image is smaller than the requested dimensions, do nothing.
    Useful when globbing in a directory with many differently sized images.

--scale X:
    Use this option instead of new_w, new_h. Scale the image by factor X.

--quality X:
    JPEG compression quality.
'''
import argparse
import PIL.Image
import sys

from voussoirkit import betterhelp
from voussoirkit import imagetools
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'resize')

def resize(
        filename,
        new_w=None,
        new_h=None,
        *,
        inplace=False,
        nearest_neighbor=False,
        only_shrink=False,
        scale=None,
        quality=100,
    ):
    file = pathclass.Path(filename)
    image = PIL.Image.open(file.absolute_path)

    (image_width, image_height) = image.size

    if new_w is not None and new_h is not None:
        pass
    elif scale:
        new_w = int(image_width * scale)
        new_h = int(image_height * scale)

    if new_w == 0:
        (new_w, new_h) = imagetools.fit_into_bounds(
            image_width,
            image_height,
            10000000,
            new_h,
            only_shrink=only_shrink,
        )
    if new_h == 0:
        (new_w, new_h) = imagetools.fit_into_bounds(
            image_width,
            image_height,
            new_w,
            10000000,
            only_shrink=only_shrink,
        )

    log.debug('Resizing %s to %dx%d.', file.absolute_path, new_w, new_h)
    if nearest_neighbor:
        image = image.resize( (new_w, new_h), PIL.Image.NEAREST)
    else:
        image = image.resize( (new_w, new_h), PIL.Image.ANTIALIAS)

    if inplace:
        new_name = file
    else:
        suffix = '_{width}x{height}'.format(width=new_w, height=new_h)
        base = file.replace_extension('').basename
        new_name = base + suffix + file.extension.with_dot
        new_name = file.parent.with_child(new_name)

    if new_name.extension == '.jpg':
        image = image.convert('RGB')

    pipeable.stdout(new_name.absolute_path)
    image.save(new_name.absolute_path, exif=image.info.get('exif', b''), quality=quality)

def resize_argparse(args):
    patterns = pipeable.input(args.pattern, skip_blank=True, strip=True)
    files = pathclass.glob_many_files(patterns)
    for file in files:
        resize(
            file,
            args.new_w,
            args.new_h,
            inplace=args.inplace,
            nearest_neighbor=args.nearest_neighbor,
            only_shrink=args.only_shrink,
            scale=args.scale,
            quality=args.quality,
        )

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('pattern')
    parser.add_argument('new_w', nargs='?', type=int, default=None)
    parser.add_argument('new_h', nargs='?', type=int, default=None)
    parser.add_argument('--inplace', action='store_true')
    parser.add_argument('--nearest', dest='nearest_neighbor', action='store_true')
    parser.add_argument('--only_shrink', '--only-shrink', action='store_true')
    parser.add_argument('--scale', type=float, default=None)
    parser.add_argument('--quality', type=int, default=100)
    parser.set_defaults(func=resize_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
