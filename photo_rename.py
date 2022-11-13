import argparse
import datetime
import os
import re
import sys

from voussoirkit import imagetools
from voussoirkit import interactive
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import spinal
from voussoirkit import vlogging

log = vlogging.getLogger(__name__)

def makename(file, read_exif=False):
    old = file.replace_extension('').basename
    new = old

    # Already optimized filenames need not apply
    # This is also important when the filename and the exif disagree
    if re.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)_(\d\d)-(\d\d)-(\d\d)(?:x\d+)?$', old) and not read_exif:
        return file

    # Microsoft ICE
    new = re.sub(
        r'^(\d\d\d\d)-(\d\d)-(\d\d)_(\d\d)-(\d\d)-(\d\d)_stitch$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    new = re.sub(
        r'^(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d)_stitch$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    # Android screenshots
    new = re.sub(
        r'^Screenshot_(\d\d\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)(?:_cropped)?$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    new = re.sub(
        r'^Recording_(\d\d\d\d)-(\d\d)-(\d\d)-(\d\d)-(\d\d)-(\d\d)(?:_cropped)?$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    # Terraria screenshots
    new = re.sub(
        r'^Capture (\d\d\d\d)-(\d\d)-(\d\d) (\d\d)_(\d\d)_(\d\d)$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    # OBS screenshots
    new = re.sub(
        r'^Screenshot (\d\d\d\d)-(\d\d)-(\d\d)_(\d\d)-(\d\d)-(\d\d)$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    new = re.sub(
        r'^(\d\d\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    new = re.sub(
        r'^(\d\d\d\d)-(\d\d)-(\d\d)[_-](\d\d)(\d\d)(\d\d)$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    new = re.sub(
        r'^(\d\d\d\d)(\d\d)(\d\d)-(\d\d)_(\d\d)_(\d\d)$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    # LG Android camera
    new = re.sub(
        r'^(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d)(?:_HDR)?$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    # Unihertz Jelly 2 camera
    new = re.sub(
        r'^IMG_(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d)_\d+$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )
    # Jelly videos
    new = re.sub(
        r'^VID_(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d)+$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )
    # Jelly screen recordings
    new = re.sub(
        r'^screen-(\d\d\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)$',
        r'\1-\2-\3_\4-\5-\6',
        new,
    )

    new = re.sub(
        r'^(\d\d\d\d)-(\d\d)-(\d\d)_(\d\d)-(\d\d)-(\d\d)[_-](\d+)$',
        r'\1-\2-\3_\4-\5-\6x\7',
        new,
    )

    new = re.sub(
        r'^(\d\d\d\d)(\d\d)(\d\d)[_-](\d+)$',
        r'\1-\2-\3x\4',
        new,
    )

    new = re.sub(
        r'^(\d\d\d\d)(\d\d)(\d\d) (\w+.*)$',
        r'\1-\2-\3 \4',
        new,
    )

    new = re.sub(
        r'^(\d\d\d\d)(\d\d)(\d\d)$',
        r'\1-\2-\3',
        new,
    )

    # Kakaotalk downloaded photos
    # Unix timestamps, followed by an index if downloaded as bundle
    unix = re.match(r'^(?:kakaotalk_)?(\d{13})(?:[_-](\d))?', new)
    if unix:
        date = datetime.datetime.fromtimestamp(int(unix.group(1)) / 1000)
        f = date.strftime('%Y-%m-%d_%H-%M-%S')
        if unix.group(2):
            f += 'x' + unix.group(2)
        new = re.sub(unix.group(0), f, new)

    # exif comes last because I feel the filename is most important.
    # Especially in cases where the user has edited a photo with software that
    # reset the exif but the filename refers to the original date.
    # I'm sure cases could be made either way but I'm starting here.
    if new == old and read_exif and file.extension in {'jpg', 'jpeg'}:
        new = makename_exif(file, old)

    new = file.parent.with_child(new).add_extension(file.extension)
    return new

def makename_exif(file, fallback):
    dt = imagetools.get_exif_datetime(file)
    if not dt:
        return fallback
    return dt.strftime('%Y-%m-%d_%H-%M-%S')

def makenames(files, read_exif=False):
    pairs = {}
    new_duplicates = {}
    for file in files:
        newname = makename(file, read_exif=read_exif)
        new_duplicates.setdefault(newname, []).append(file)
        if file.basename == newname.basename:
            continue
        pairs[file] = newname

    if not pairs:
        return pairs

    for (new, olds) in list(new_duplicates.items()):
        count = len(olds)
        if count > 1:
            olds.sort()
            new_duplicates.pop(new)
            wanted = new
            zeroes = len(str(len(olds)))
            for (index, old) in enumerate(olds):
                new_base = wanted.replace_extension('').basename + f'x{index+1:0{zeroes}d}'
                new = wanted.parent.with_child(new_base).add_extension(wanted.extension)
                if old.basename == new.basename:
                    del pairs[old]
                    continue
                pairs[old] = new

    return pairs

def photo_rename_argparse(args):
    patterns = pipeable.input_many(args.patterns, skip_blank=True, strip=True)
    if args.recurse:
        files = spinal.walk('.', glob_filenames=patterns, yield_directories=False)
    else:
        files = pathclass.glob_many_files(patterns)

    pairs = makenames(files, read_exif=args.read_exif)
    if not pairs:
        return 0

    for (old, new) in pairs.items():
        print(f'{old.relative_path} -> {new.relative_path}')

    if not (args.autoyes or interactive.getpermission('Okay?', must_pick=True)):
        return 1

    for (old, new) in pairs.items():
        os.rename(old.absolute_path, new.absolute_path)

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns', nargs='+')
    parser.add_argument('--recurse', action='store_true')
    parser.add_argument('--exif', dest='read_exif', action='store_true')
    parser.add_argument('--yes', dest='autoyes', action='store_true')
    parser.set_defaults(func=photo_rename_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
