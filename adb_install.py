import argparse
import os
import sys

from voussoirkit import interactive
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import stringtools
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'adbinstall')

def adbinstall_argparse(args):
    patterns = pipeable.input_many(args.apks, skip_blank=True, strip=True)
    apks = pathclass.glob_many(patterns, files=True)
    installs = []
    for apk in apks:
        apk = pathclass.Path(apk)
        if apk.is_dir:
            files = apk.glob('*.apk')
            files.sort(key=lambda x: stringtools.natural_sorter(x.basename.lower()))
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

    return 0

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
