'''
This program deletes windows .lnk files if the path they point to no longer
exists.
'''
import argparse
import os
import send2trash
import sys
import winshell

from voussoirkit import getpermission
from voussoirkit import pathclass

def prune_shortcuts(autoyes=False):
    lnks = pathclass.Path('.').glob('*.lnk')
    stale = [lnk for lnk in lnks if not os.path.exists(winshell.Shortcut(lnk.absolute_path).path)]

    if not stale:
        return

    print(f'The following {len(stale)} will be recycled:')
    for lnk in stale:
        print(lnk.absolute_path)
    print()

    if autoyes or getpermission.getpermission('Is that ok?'):
        for lnk in stale:
            print(lnk.absolute_path)
            send2trash.send2trash(lnk.absolute_path)

def prune_shortcuts_argparse(args):
    return prune_shortcuts(autoyes=args.autoyes)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--yes', dest='autoyes', action='store_true')
    parser.set_defaults(func=prune_shortcuts_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
