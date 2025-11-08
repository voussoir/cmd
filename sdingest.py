import shutil
import argparse
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import spinal
from voussoirkit import vlogging
from voussoirkit import windrives
from voussoirkit import progressbars

log = vlogging.getLogger(__name__, 'sdingest')

def sdingest_one(folder):
    cwd = pathclass.cwd()
    for file in folder.walk_files():
        # print(file.absolute_path)
        spinal.copy_file(
            file,
            cwd.with_child(file.basename),
            progressbar=progressbars.Bar1_bytestring,
        )

def sdingest_all():
    dcim = None
    drives = windrives.get_drive_map()
    for (mount, info) in drives.items():
        mount = pathclass.Path(mount)

        # Panasonic HC-X1500/HC-X2000
        panasonic = mount.with_child('PRIVATE').with_child('PANA_GRP').with_child('001YAQAM')
        if panasonic.is_folder:
            sdingest_one(panasonic)
            continue

        # Most cameras
        dcim = mount.with_child('DCIM')
        if dcim.is_folder:
            sdingest_one(dcim)
            continue

        # Sony ICD UX570
        if info.get('name').upper() == 'MEMORY CARD':
            folder = mount.join('PRIVATE\\SONY\\REC_FILE')
            if folder.exists:
                sdingest_one(folder)
                continue

    if dcim is None:
        return 1

def sdingest_argparse(args):
    return sdingest_all()

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        ''',
    )
    parser.set_defaults(func=sdingest_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
