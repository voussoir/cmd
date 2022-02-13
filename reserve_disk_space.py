import argparse
import sys

from voussoirkit import betterhelp
from voussoirkit import bytestring
from voussoirkit import pathclass
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'reserve_disk_space')

def reserve_disk_space_argparse(args):
    reserve = bytestring.parsebytes(args.reserve)
    drive = pathclass.Path(args.drive)
    try:
        free = drive.assert_disk_space(reserve)
        free = bytestring.bytestring(free)
        reserve = bytestring.bytestring(reserve)
        log.info('There is %s available out of %s.', free, reserve)
        return 0
    except pathclass.NotEnoughSpace as exc:
        free = bytestring.bytestring(exc.free)
        reserve = bytestring.bytestring(exc.reserve)
        log.fatal('Only %s available out of %s.', free, reserve)
        return 1

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Exits with status of 0 if the disk has the requested amount of space, 1 if not.
        ''',
    )
    parser.add_argument(
        'reserve',
        type=str,
        help='''
        A string like "50g" or "100 gb"
        ''',
    )
    parser.add_argument(
        'drive',
        nargs='?',
        default='.',
        help='''
        Filepath to the drive you want to check.
        ''',
    )
    parser.set_defaults(func=reserve_disk_space_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
