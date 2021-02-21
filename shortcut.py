import argparse
import sys
import winshell

from voussoirkit import pathclass

def shortcut(lnk_name, target, start_in=None, icon=None):
    lnk = pathclass.Path(lnk_name)
    if lnk.extension != 'lnk':
        lnk = lnk.add_extension('lnk')

    lnk.assert_not_exists()

    target = pathclass.Path(target)
    target.assert_exists()

    if start_in is not None:
        start_in = pathclass.Path(start_in)
        start_in.assert_is_directory()

    if icon is not None:
        icon = pathclass.Path(icon)
        icon.assert_is_file()

    shortcut = winshell.Shortcut(lnk.absolute_path)
    shortcut.path = target.absolute_path
    if start_in is not None:
        shortcut.working_directory = start_in.absolute_path
    if icon is not None:
        shortcut.icon_location = (icon.absolute_path, 0)

    shortcut.write()
    return lnk

def shortcut_argparse(args):
    try:
        lnk = shortcut(
            lnk_name=args.lnk_name,
            target=args.target,
            start_in=args.start_in,
            icon=args.icon,
        )
        print(lnk.absolute_path)
        return 0
    except pathclass.Exists:
        print(f'{args.lnk_name} already exists.')
        return 1

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('lnk_name')
    parser.add_argument('target')
    parser.add_argument('--start_in', '--start-in', '--startin', default=None)
    parser.add_argument('--icon', default=None)
    parser.set_defaults(func=shortcut_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
