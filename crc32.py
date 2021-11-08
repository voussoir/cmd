import argparse
import sys
import zlib

from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'crc32')

def crc32_argparse(args):
    return_status = 0

    patterns = pipeable.input_many(args.patterns, skip_blank=True, strip=True)
    files = pathclass.glob_many_files(patterns)

    for file in files:
        try:
            crc = zlib.crc32(file.read('rb'))
            crc = hex(crc)[2:].rjust(8, '0')
            pipeable.stdout(f'{crc} {file.absolute_path}')
        except Exception as e:
            log.error('%s %s', file, e)
            return_status = 1

    return return_status

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns', nargs='+')
    parser.set_defaults(func=crc32_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
