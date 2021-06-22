import argparse
import os
import re
import sys

from voussoirkit import interactive
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging
from voussoirkit import winglob

log = vlogging.getLogger(__name__, 'adbinstall')

def natural_sorter(x):
    '''
    Used for sorting files in 'natural' order instead of lexicographic order,
    so that you get 1 2 3 4 5 6 7 8 9 10 11 12 13 ...
    instead of 1 10 11 12 13 2 3 4 5 ...
    Thank you Mark Byers
    http://stackoverflow.com/a/11150413
    '''
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return alphanum_key(x)

def adbinstall_argparse(args):
    patterns = pipeable.input_many(args.apks, skip_blank=True, strip=True)
    apks = [file for pattern in patterns for file in winglob.glob(pattern)]
    installs = []
    for apk in args.apks:
        apk = pathclass.Path(apk)
        if apk.is_dir:
            files = apk.glob('*.apk')
            files.sort(key=lambda x: natural_sorter(x.basename.lower()))
            apk = files[-1]
        installs.append(apk)

    if not args.autoyes:
        for apk in installs:
            print(apk.absolute_path)
        if not interactive.getpermission('Is that okay?', must_pick=True):
            return 1

    for apk in installs:
        command = f'adb install "{apk.absolute_path}"'
        log.info(command)
        os.system(command)

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('apks', nargs='+')
    parser.add_argument('--yes', dest='autoyes', action='store_true')
    parser.set_defaults(func=adbinstall_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
