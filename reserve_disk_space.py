'''
reserve_disk_space
==================

Exits with status of 0 if the disk has the requested amount of space, 1 if not.

> reserve_disk_space reserve [drive]

reserve:
    A string like "50g" or "100 gb"

drive:
    Filepath to the drive you want to check. Defaults to cwd drive.
'''
import argparse
import os
import shutil
import sys

from voussoirkit import betterhelp
from voussoirkit import bytestring
from voussoirkit import dotdict
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'reserve_disk_space')

class NotEnoughSpace(Exception):
    def __init__(self, free, reserve, drive):
        self.free = free
        self.reserve = reserve
        self.drive = drive

def reserve_disk_space(reserve, drive):
    '''
    Returns a dotdict containing these values:
    {
        'free': integer number of free bytes,
        'reserve': integer number of requested bytes,
        'drive': path string representing the drive we checked
    }

    Raises NotEnoughSpace if the amount of free disk space on `drive` is less
    than `free`.
    '''
    drive = os.path.abspath(drive)
    drive = os.path.splitdrive(drive)[0]

    log.debug('Checking drive %s.', drive)
    free = shutil.disk_usage(drive).free

    if free < reserve:
        raise NotEnoughSpace(free=free, reserve=reserve, drive=drive)
    else:
        return dotdict.DotDict(free=free, reserve=reserve, drive=drive)

def reserve_disk_space_argparse(args):
    try:
        status = reserve_disk_space(reserve=bytestring.parsebytes(args.reserve), drive=args.drive)
        free = bytestring.bytestring(status.free)
        reserve = bytestring.bytestring(status.reserve)
        log.info('There is %s available out of %s.', free, reserve)
        return 0
    except NotEnoughSpace as exc:
        free = bytestring.bytestring(exc.free)
        reserve = bytestring.bytestring(exc.reserve)
        log.fatal('Only %s available out of %s.', free, reserve)
        return 1

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('reserve')
    parser.add_argument('drive', nargs='?', default='.')
    parser.set_defaults(func=reserve_disk_space_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
