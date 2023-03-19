'''
Recompress jpeg images to save disk space.
'''
import argparse
import io
import os
import PIL.Image
import PIL.ImageFile
import sys

from voussoirkit import bytestring
from voussoirkit import imagetools
from voussoirkit import pipeable
from voussoirkit import spinal
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'rejpg')

PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True

def compress_to_filesize(image, target_size, *, exif=None):
    lower = 1
    lower_bio = None
    upper = 100
    current = 100
    while True:
        # print(lower, current, upper)
        if lower == (upper - 1):
            break
        bio = io.BytesIO()
        image.save(bio, format='jpeg', exif=exif, quality=current)
        bio.seek(0)
        size = len(bio.read())
        if size > target_size:
            upper = current
        if size <= target_size:
            lower = current
            lower_bio = bio
        current = (lower + upper) // 2

    if lower_bio is None:
        raise RuntimeError(f'Could not compress below {target_size}')

    return lower_bio

def rejpg_argparse(args):
    patterns = pipeable.input_many(args.patterns, skip_blank=True, strip=True)
    files = spinal.walk(recurse=args.recurse, glob_filenames=patterns)

    files = [f.absolute_path for f in files]

    bytes_saved = 0
    remaining_size = 0
    for filename in files:
        log.info('Processing %s.', filename)
        image = PIL.Image.open(filename)
        icc_profile = image.info.get('icc_profile')

        (image, exif) = imagetools.rotate_by_exif(image)

        if args.filesize:
            target_size = bytestring.parsebytes(args.filesize)
            bytesio = compress_to_filesize(image, target_size, exif=exif)
        else:
            bytesio = io.BytesIO()
            image.save(bytesio, format='jpeg', exif=exif, quality=args.quality, icc_profile=icc_profile)

        bytesio.seek(0)
        new_bytes = bytesio.read()
        old_size = os.path.getsize(filename)
        new_size = len(new_bytes)
        remaining_size += new_size
        if new_size < old_size:
            bytes_saved += (old_size - new_size)
            f = open(filename, 'wb')
            f.write(new_bytes)
            f.close()

    log.info('Saved %s.', bytestring.bytestring(bytes_saved))
    log.info('Remaining are %s.', bytestring.bytestring(remaining_size))
    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns', nargs='+', default={'*.jpg', '*.jpeg'})
    parser.add_argument('--quality', type=int, default=80)
    parser.add_argument('--filesize', type=str, default=None)
    parser.add_argument('--recurse', action='store_true')
    parser.set_defaults(func=rejpg_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
