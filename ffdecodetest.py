import os
import argparse
import subprocess
import sys

from voussoirkit import betterhelp
from voussoirkit import spinal
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging
from voussoirkit import winwhich

log = vlogging.getLogger(__name__, 'ffdecodetest')

def ffdecodetest_argparse(args):
    FFMPEG = pathclass.Path(winwhich.which('ffmpeg'))
    patterns = pipeable.input_many(args.patterns)
    if args.recurse:
        files = spinal.walk(glob_filenames=patterns)
    else:
        files = (file for pattern in patterns for file in pathclass.glob_files(pattern))

    goods = 0
    bads = 0

    for file in files:
        command = [
            FFMPEG.absolute_path,
            '-i', file.absolute_path,
            '-f', 'null',
            os.devnull,
        ]
        log.debug(command)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        success = True
        for line in process.stdout:
            # If you have more comprehensive tests, let me know.
            if b'Error while decoding' in line or b'broken header' in line:
                success = False
                for line in process.stdout:
                    pass
                break
        process.communicate()
        success = success and process.returncode == 0
        if success:
            log.info(f'{file.absolute_path} ok.')
            goods += 1
        else:
            log.error(f'{file.absolute_path} failed.')
            bads += 1

    if bads > 0:
        log.warning(f'{goods} ok, {bads} failed.')
        return 1
    else:
        log.info(f'{goods} ok, {bads} failed.')
        return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Uses FFMPEG to decode the input files, testing their validity.
        ''',
    )
    parser.add_argument(
        'patterns',
        nargs='+',
    )
    parser.add_argument('--recurse', action='store_true')
    parser.set_defaults(func=ffdecodetest_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
