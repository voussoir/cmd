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
from voussoirkit import spinal

def prune_shortcuts(recurse=False, autoyes=False):
    if recurse:
        lnks = [file for file in spinal.walk_generator('.') if file.extension == 'lnk']
    else:
        lnks = pathclass.Path('.').glob('*.lnk')

    stale = []
    for lnk in lnks:
        shortcut = winshell.Shortcut(lnk.absolute_path)
        # There are some special shortcuts that do not have a path, but instead
        # trigger some action based on a CLSID that Explorer understands.
        # I can't find this information in the winshell.Shortcut object, so for
        # now let's at least not delete these files.
        if shortcut.path == '':
            continue
        if not os.path.exists(shortcut.path):
            stale.append(lnk)

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
    return prune_shortcuts(recurse=args.recurse, autoyes=args.autoyes)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--recurse', dest='recurse', action='store_true')
    parser.add_argument('--yes', dest='autoyes', action='store_true')
    parser.set_defaults(func=prune_shortcuts_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
