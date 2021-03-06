'''
Recompress all jpg images in the current directory.
'''
import argparse
import io
import os
import PIL.Image
import PIL.ImageFile
import string
import sys

from voussoirkit import bytestring
from voussoirkit import imagetools

PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True

def rejpg_argparse(args):
    if args.recurse:
        from voussoirkit import spinal
        walker = spinal.walk_generator()
        files = list(walker)
    else:
        from voussoirkit import pathclass
        files = pathclass.cwd().listdir()
        files = [f for f in files if f.is_file]

    files = [f for f in files if f.extension in ['.jpg', '.jpeg']]
    files = [f.absolute_path for f in files]

    bytes_saved = 0
    remaining_size = 0
    for filename in files:
        print(''.join(c for c in filename if c in string.printable))
        bytesio = io.BytesIO()
        i = PIL.Image.open(filename)

        i = imagetools.rotate_by_exif(i)

        i.save(bytesio, format='jpeg', quality=80)

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

    print('Saved', bytestring.bytestring(bytes_saved))
    print('Remaining are', bytestring.bytestring(remaining_size))

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--recurse', dest='recurse', action='store_true')
    parser.set_defaults(func=rejpg_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
